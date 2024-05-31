"""Scraper script for the Anthem website using Selenium."""

import argparse
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

URL = "https://www.anthem.com/ca/provider/policies/clinical-guidelines/updates/"


class AnthemScraper:
    """A class to scrape Anthem site for clinical guidelines."""

    def __init__(self, headful: bool = False):
        self.url = URL
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

    def get_results(self):
        """Get the results from the current page."""
        result_msg = (
            WebDriverWait(self.driver, self.get_random_wait_time())
            .until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'pretend-pagination')]/span")
                )
            )
            .text
        )
        print(result_msg)

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

        while True:
            self.get_results()
            try:
                self.navigate_next_page()
            except TimeoutException:
                print("No more pages or next page button not found.")
                break
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
