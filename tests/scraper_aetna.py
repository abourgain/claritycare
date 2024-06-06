"""Scraper script for the Anthem website using Selenium."""

import argparse
import json
import time
import random

from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.aetna.com/cpb/medical/data/"
URL = "https://www.aetna.com/health-care-professionals/clinical-policy-bulletins/medical-clinical-policy-bulletins/medical-clinical-policy-bulletins-search-results.html?query={}"
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

    def __init__(
        self, headful: bool = False, category: str = "surgery", verbose: bool = False
    ):
        self.url = URL.format(category)
        self.base_url = BASE_URL
        self.headless = not headful
        self.category = category
        self.verbose = verbose
        self.driver = self.setup_driver(headful)

    def get_random_wait_time(self):
        """Get a random wait time between 0.01 and 1 second."""
        return random.uniform(0.01, 1) if self.headless else 0.5

    def setup_driver(self, headful):
        """Set up the Firefox driver."""
        options = webdriver.FirefoxOptions()
        if not headful:
            options.add_argument("--headless")

        options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        )

        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        return driver

    def close_popup(self):
        """Close the popup modal if it exists."""
        try:
            continue_button = WebDriverWait(
                self.driver, self.get_random_wait_time()
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//a[@class='modalContinueBtn btn--primary type__btn--primary' and contains(text(), 'I accept')]",
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
                        "//p[@class='sr_results_message']",
                    )
                )
            )
            .text
        )
        num_results = int(result_msg.split(" ")[4])
        print(f"Number of results: {num_results}")
        return num_results

    def get_item_links(self):
        """Get the link to each item on the page."""
        item_links = []
        items = self.driver.find_elements(
            By.CSS_SELECTOR, ".sr_list_element .link__headline"
        )
        for item in items:
            link = item.get_attribute("href")
            if not link.startswith(BASE_URL):
                raise ValueError(
                    f"Problem with Medical Policy filter! Expected URL to start with '{BASE_URL}'"
                )
            item_links.append(link)
            print(f"-> Found: {link}")  # TO BE REMOVED
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

    def extract_policy(self):
        """Extract the content under the 'Position Statement' heading."""
        try:
            policy_section = self.driver.find_element(
                By.XPATH,
                "//h2[@class='policyHead' and contains(text(), 'Policy')]/following-sibling::ol",
            )
            content = policy_section.get_attribute("outerHTML")

            if not content:
                raise ValueError("No content was extracted.")
            return content

        except TimeoutException:
            print("Position Statement not found or page format different.")
            return ""
        except ValueError as exception:
            print(f"An error occurred: {exception}")
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

            # verify the page is loaded
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "docDetails"))
                )
                print("Page loaded properly.")
            except TimeoutException:
                print("Page did not load properly.")
                self.driver.close()

            # Extract the document details and the 'Position Statement' content
            policy = {"url": link}
            # policy = {**policy, **self.extract_details()} # TO BE REPUT !!!
            content = self.extract_policy()
            print(content)
            policy["html_content"] = content

            policies.append(policy)

            print(f"-> Visited: {link}")
            self.driver.close()  # Close the current tab
            self.driver.switch_to.window(main_window)  # Switch back to the main window
        return policies

    def navigate_next_page(self):
        """Navigate to the next page."""
        clicked = False
        trial = 0
        while not clicked:
            try:
                next_page_link = WebDriverWait(
                    self.driver, self.get_random_wait_time()
                ).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(@aria-label, 'Go to Next Page')]")
                    )
                )
                next_page_link.click()
                clicked = True
            except selenium.common.exceptions.ElementClickInterceptedException:
                trial += 1
                if self.verbose:
                    print(f"! Failed to click next page link. Trial {trial}.")
            time.sleep(self.get_random_wait_time())  # Allow page to load

    @staticmethod
    def clean_html(html):
        """Clean the HTML content."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove specific tags but keep their content
        for tag in soup.find_all(["strong", "em", "div", "p"]):
            tag.unwrap()

        return str(soup)

    def scrape(self):
        """Scrape the Anthem site for clinical guidelines."""
        if self.verbose:
            print(f"Scraping Anthem site for {self.category} guidelines.")
        self.driver.get(self.url)
        time.sleep(self.get_random_wait_time())  # Allow page to load
        time.sleep(30)  # TO BE REMOVED
        self.close_popup()
        time.sleep(5)  # TO BE REMOVED
        num_results = self.get_num_results()
        time.sleep(5)  # TO BE REMOVED

        visited_links = set()
        policies = []
        while True:
            try:
                item_links = self.get_item_links()
                visited_links.update(item_links)
                policies.extend(self.visit_item_pages(item_links))
                # self.navigate_next_page()
            except ValueError as exception:
                print(exception)
                break
            except TimeoutException:
                print("No more pages or next page button not found.")
                break
        assert len(visited_links) == num_results, "Some items were not visited."

        # Clean the HTML content
        for policy in policies:
            policy["content"] = self.clean_html(policy["html_content"])

        # Save the policies to a JSON file without pandas
        with open(
            f"./ddata/anthem/{self.category}_policies.json", "w", encoding="utf-8"
        ) as file:
            json.dump(policies, file, indent=2)


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
    parser.add_argument("--verbose", action="store_true", help="Print verbose output.")
    args = parser.parse_args()

    if args.cat == "all":
        for cat in ALLOWED_CATEGORIES:
            scraper = AnthemScraper(
                headful=args.headful, category=cat, verbose=args.verbose
            )
            scraper.scrape()
    else:
        scraper = AnthemScraper(
            headful=args.headful, category=args.cat, verbose=args.verbose
        )
        scraper.scrape()


if __name__ == "__main__":
    main()
