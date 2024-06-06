# Machine Learning Engineer Interview Assignment: Development of a Medical Policy Extraction Algorithm

This repository contains the codebase for scraping clinical guidelines from various websites, with a focus on medical policy data collection and standardization.

## Project Structure

- **Makefile**: Contains the commands to set up and run the project.
- **README.md**: Project overview and instructions.
- **ddata**: Directory to store scraped data as JSON files.
  - **anthem**: Subdirectory for Anthem-specific scraped data.
- **pylint.conf**: Configuration file for pylint.
- **requirements.txt**: List of Python dependencies for the project.
- **src**: Main directory containing the scraping and standardization scripts.
  - **\_\_init\_\_.py**: Initialization file for the `src` package.
  - **instructions.py**: Module containing the prompt instructions.
  - **scraper_anthem.py**: Script for scraping the Anthem site.
  - **standardize.py**: Script for standardizing the scraped data.
- **tests**: Directory for test scripts that did not work.
  - **data-collection-oscar.ipynb**: Jupyter notebook for data collection test.
  - **huggingface.ipynb**: Jupyter notebook for Hugging Face test.
  - **scraper_aetna.py**: Test script for scraping the Aetna site.

## Installing the Project

To install the project, you can use the provided Makefile to set up a virtual environment and install the necessary dependencies. Follow these steps:

1. **Clone the Repository**: First, clone the repository to your local machine.

   ```sh
   git clone <repository_url>
   cd <repository_directory>

   ```

2. **Run the Install Command**: Execute the `install` command from the Makefile to set up the project. This command will create a virtual environment, activate it, upgrade pip, and install the required dependencies.

```sh
make install
```

The `install` command performs the following actions:

- Creates a virtual environment named `claritycare-env`.
- Activates the virtual environment.
- Upgrades pip to the latest version.
- Installs the dependencies listed in the `requirements.txt` file.

After running the `install` command, your project will be set up and ready to use. You can then proceed to run the scrapers or any other scripts as needed.

## Commands

### Scrape the Anthem Site

To scrape clinical guidelines from the Anthem site, use the following command:

```sh
python src/scraper_anthem.py --cat <category> [--headful] [--verbose]
```

- `--cat`: Category to filter the guidelines. Choices are `["all"] + ALLOWED_CATEGORIES`.
- `--headful`: Run the browser in headful mode. Optional.
- `--verbose`: Print verbose output. Optional.

Example:

```sh
python src/scraper_anthem.py --cat surgery --headful --verbose
```

### Standardize the Scraped Data

To extract the different criteria logic schemas and output them in JSON format, use the following command:

```sh
python src/standardize.py --model <model> [--string <string>] [--data <data_path>] [--verbose]
```

- `--model`: The model to use for the extraction. Default is `"gpt-4o"`.
- `--string`: The position statement for a medical policy. Optional.
- `--data`: Extract the policy from a JSON file, or a folder containing multiple JSON files. Optional.
- `--verbose`: Print verbose output. Optional.

Example:

```sh
python src/standardize.py --model gpt-4o --data ./ddata/anthem/surgery_policies.json --verbose
```

## Usage Examples

### Scraping Guidelines

1. To scrape all categories in headless mode with verbose output:

   ```sh
   python src/scraper_anthem.py --cat all --verbose
   ```

2. To scrape the "surgery" category in headful mode:

   ```sh
   python src/scraper_anthem.py --cat surgery --headful
   ```

### Standardizing Data

1. To standardize data from a JSON file:

   ```sh
   python src/standardize.py --model gpt-4o --data ./ddata/anthem/surgery_policies.json --verbose
   ```

2. To standardize data from a folder:

   ```sh
   python src/standardize.py --model gpt-4o --data ./ddata/anthem/ --verbose
   ```

3. To extract policy from a given string:

   ```sh
   python src/standardize.py --model gpt-4o --string "Your policy statement here."
   ```

## Dependencies

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

## Notes

- Ensure the path to the geckodriver (for Firefox) or chromedriver (for Chrome) is correctly set in your environment.
- Random delays and custom user-agent strings are used to avoid detection and blocking by the target websites.

## References

For more detailed insights and techniques applied in the project, please refer to the relevant documentation and studies listed in the project files.
