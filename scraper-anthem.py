"""Scraper script for the Anthem website using Selenium."""

import argparse
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.anthem.com"
URL = "https://www.anthem.com/ca/provider/policies/clinical-guidelines/updates/"


class AnthemScraper:
    """A class to scrape Anthem site for clinical guidelines."""

    def __init__(self, headful: bool = False):
        self.url = URL
        self.base_url = BASE_URL
        self.headless = not headful
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

    def visit_item_pages(self, item_links):
        """Visit each item page and process it as needed."""
        main_window = self.driver.current_window_handle  # Store the main window handle
        for link in item_links:
            self.driver.execute_script("window.open('');")  # Open a new tab
            self.driver.switch_to.window(
                self.driver.window_handles[1]
            )  # Switch to the new tab
            self.driver.get(link)
            time.sleep(self.get_random_wait_time())  # Allow page to load
            # Process the item page as needed
            print(f"Visited: {link}")

            self.driver.close()  # Close the current tab
            self.driver.switch_to.window(main_window)  # Switch back to the main window

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
        self.select_filter("categoryFilter", "surgery")
        num_results = self.get_num_results()

        visited_links = set()
        while True:
            try:
                item_links = self.get_item_links()
                visited_links.update(item_links)
                self.visit_item_pages(item_links)
                self.navigate_next_page()
            except ValueError as e:
                print(e)
                break
            except TimeoutException:
                print("No more pages or next page button not found.")
                break
        assert len(visited_links) == num_results, "Some items were not visited."
        self.driver.quit()


def main():
    """Run the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape Anthem site for clinical guidelines."
    )
    parser.add_argument(
        "--headful", action="store_true", help="Run browser in headful mode."
    )
    args = parser.parse_args()

    scraper = AnthemScraper(headful=args.headful)
    scraper.scrape()


if __name__ == "__main__":
    main()
