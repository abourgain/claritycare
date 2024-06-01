"""Scraper script for the Anthem website using Selenium."""

import argparse
import time
import random

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.anthem.com"
URL = "https://www.anthem.com/ca/provider/policies/clinical-guidelines/updates/"
ALLOWED_CATEGORIES = [
    "ancillarymiscellaneous",
    "medicine",
    "durablemedicalequipment",
    "surgery",
    "laboratory",
    "transplant",
    "therapeuticradiology",
    "radiology",
    "orthoticsprosthetics",
]


class AnthemScraper:
    """A class to scrape Anthem site for clinical guidelines."""

    def __init__(self, headful: bool = False, category: str = "surgery"):
        self.url = URL
        self.base_url = BASE_URL
        self.headless = not headful
        self.category = category
        self.driver = self.setup_driver(headful)

    def get_random_wait_time(self):
        """Get a random wait time between 0.01 and 1 second."""
        return random.uniform(0.01, 1) if self.headless else 0.5

    def setup_driver(self, headful):
        """Set up the Firefox driver."""
        options = webdriver.FirefoxOptions()
        if not headful:
            options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    def close_popup(self):
        """Close the popup modal if it exists."""
        try:
            continue_button = WebDriverWait(
                self.driver, self.get_random_wait_time()
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@class='btn btn-primary' and contains(text(), 'Continue')]",
                    )
                )
            )
            continue_button.click()
        except TimeoutException:
            print("No popup found or popup already handled.")

    def select_filter(self, filter_name, value):
        """Select a filter option by its data-value attribute."""
        filter_button = WebDriverWait(self.driver, self.get_random_wait_time()).until(
            EC.element_to_be_clickable((By.ID, f"{filter_name}_button"))
        )
        filter_button.click()
        time.sleep(self.get_random_wait_time())  # Wait for dropdown to load

        option = WebDriverWait(self.driver, self.get_random_wait_time()).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@data-value='{value}']"))
        )
        option.click()
        time.sleep(self.get_random_wait_time())  # Wait for any updates

    def get_num_results(self):
        """Get the number of results displayed on the page."""
        result_msg = (
            WebDriverWait(self.driver, self.get_random_wait_time())
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'pretend-pagination')]/span",
                    )
                )
            )
            .text
        )
        num_results = int(result_msg.split(" ")[-1])
        print(f"Number of results: {num_results}")
        return num_results

    def get_item_links(self):
        """Get the link to each item on the page."""
        item_links = []
        items = self.driver.find_elements(
            By.CSS_SELECTOR, ".news-item-wrapper .article-headline a"
        )
        for item in items:
            link = item.get_attribute("href")
            if link.split("/")[-1][:2] != "mp":
                raise ValueError(
                    "Problem with Medical Policy filter! Expected 'mp_...'"
                )
            if link.startswith("/"):
                link = self.base_url + link
            item_links.append(link)
        return item_links

    def extract_details(self):
        """Extract the details of the document."""
        try:
            # Wait for the 'docDetails' table to load
            doc_details_table = WebDriverWait(
                self.driver, self.get_random_wait_time()
            ).until(EC.visibility_of_element_located((By.ID, "docDetails")))

            # Extracting details
            subject = (
                doc_details_table.find_element(By.XPATH, ".//tr[1]/td")
                .text.replace("Subject: ", "")
                .strip()
            )
            document_number = (
                doc_details_table.find_element(By.XPATH, ".//tr[2]/td[1]")
                .text.replace("Document #: ", "")
                .strip()
            )
            publish_date = (
                doc_details_table.find_element(By.XPATH, ".//tr[2]/td[2]")
                .text.replace("Publish Date: ", "")
                .strip()
            )
            status = (
                doc_details_table.find_element(By.XPATH, ".//tr[3]/td[1]")
                .text.replace("Status: ", "")
                .strip()
            )
            last_review_date = (
                doc_details_table.find_element(By.XPATH, ".//tr[3]/td[2]")
                .text.replace("Last Review Date: ", "")
                .strip()
            )

            return {
                "subject": subject,
                "document_number": document_number,
                "publish_date": publish_date,
                "status": status,
                "last_review_date": last_review_date,
            }
        except TimeoutException:
            print("Failed to find the document details table.")
            return {}

    def extract_position_statement(self):
        """Extract the content under the 'Position Statement' heading."""
        try:
            # Locate the 'Position Statement' heading to ensure we are extracting the right paragraph
            position_heading = WebDriverWait(
                self.driver, self.get_random_wait_time()
            ).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//strong[contains(text(), 'Position Statement')]")
                )
            )
            # Collect all subsequent siblings until the next <table> is encountered
            content_elements = self.driver.execute_script(
                """
                var heading = arguments[0];
                var collect = false;
                var content = [];
                var elements = document.body.getElementsByTagName('*');
                for (var elem of elements) {
                    if (elem === heading) {
                        collect = true;
                        continue;
                    }
                    if (collect) {
                        if (elem.tagName === 'TABLE') break;
                        if (['P', 'UL', 'LI'].includes(elem.tagName)) {
                            content.push(elem.outerHTML);
                        }
                    }
                }
                return content;
                """,
                position_heading,
            )

            if not content_elements:
                raise ValueError("No content was extracted.")

            return "\n".join(content_elements)
        except TimeoutException:
            print("Position Statement not found or page format different.")
            return ""
        except ValueError as e:
            print(f"An error occurred: {e}")
            return ""

    def visit_item_pages(self, item_links):
        """Visit each item page and process it as needed."""
        main_window = self.driver.current_window_handle  # Store the main window handle
        policies = []
        for link in item_links:
            self.driver.execute_script("window.open('');")  # Open a new tab
            self.driver.switch_to.window(
                self.driver.window_handles[1]
            )  # Switch to the new tab
            self.driver.get(link)
            time.sleep(self.get_random_wait_time())  # Allow page to load

            # Extract the document details and the 'Position Statement' content
            policy = self.extract_details()
            content = self.extract_position_statement()
            policy["content"] = content

            policies.append(policy)

            print(f"Visited: {link}")
            self.driver.close()  # Close the current tab
            self.driver.switch_to.window(main_window)  # Switch back to the main window
        return policies

    def navigate_next_page(self):
        """Navigate to the next page."""
        next_page_link = WebDriverWait(self.driver, self.get_random_wait_time()).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@aria-label, 'Go to Next Page')]")
            )
        )
        next_page_link.click()
        time.sleep(self.get_random_wait_time())  # Allow page to load

    def scrape(self):
        """Scrape the Anthem site for clinical guidelines."""
        self.driver.get(self.url)
        time.sleep(self.get_random_wait_time())  # Allow page to load
        self.close_popup()
        self.select_filter("formsDocTypeFilter", "medicalpolicy")
        self.select_filter("categoryFilter", self.category)
        num_results = self.get_num_results()

        visited_links = set()
        policies = []
        while True:
            try:
                item_links = self.get_item_links()
                visited_links.update(item_links)
                policies.extend(self.visit_item_pages(item_links))
                self.navigate_next_page()
            except ValueError as e:
                print(e)
                break
            except TimeoutException:
                print("No more pages or next page button not found.")
                break
        assert len(visited_links) == num_results, "Some items were not visited."

        # Save the policies to a JSON file
        df = pd.DataFrame(policies)
        df.to_json(
            f"./ddata/anthem/{self.category}_policies.json",
            orient="records",
            lines=True,
        )


def main():
    """Run the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Anthem site for clinical guidelines."
    )
    parser.add_argument(
        "--cat",
        type=str,
        default="surgery",
        help="Category to filter the guidelines.",
        choices=["all"] + ALLOWED_CATEGORIES,
    )
    parser.add_argument(
        "--headful", action="store_true", help="Run browser in headful mode."
    )
    args = parser.parse_args()

    if args.cat == "all":
        for cat in ALLOWED_CATEGORIES:
            scraper = AnthemScraper(headful=args.headful, category=cat)
            scraper.scrape()
    else:
        scraper = AnthemScraper(headful=args.headful, category=args.cat)
        scraper.scrape()


if __name__ == "__main__":
    main()
