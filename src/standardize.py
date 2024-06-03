"""Script to extract the different criteria logic schemas for medical policies."""

import os
import argparse
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.instructions import INSTRUCTIONS

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class MedicalPolicyExtractor:
    """Class to extract the different criteria logic schemas for medical policies."""

    def __init__(self):
        load_dotenv()
        self.openai_api_key = OPENAI_API_KEY
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            openai_api_key=self.openai_api_key,
        )
        self.instructions = INSTRUCTIONS
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that follows the following instructions {instructions}.",
                ),
                ("human", "{position_statement}"),
            ]
        )
        self.parser = JsonOutputParser()
        self.chain = self.prompt | self.llm | self.parser

    def extract_policy(self, position_statement):
        """Function to extract the policy from a position statement."""
        return self.chain.invoke(
            {
                "instructions": self.instructions,
                "position_statement": position_statement,
            }
        )

    def extract_policy_from_file(self, file_path: str, verbose: bool = False):
        """Function to extract the policy from a JSON file."""
        # Read the position statement from the json file
        with open(file_path, encoding="utf-8") as file:
            policies = json.load(file)

        if verbose:
            print(f"Extracting {len(policies)} policies from {file_path}")

        # Extract the policy for each medical act
        for policy in policies:
            if verbose:
                print(f"-> Extracting policy for {policy['subject']}")
            position_statement = policy["content"]
            policy["criteria"] = self.extract_policy(position_statement)

        # Save the policies to a JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(policies, file, indent=2)

    def extract_policy_from_folder(self, folder_path: str, verbose: bool = False):
        """Function to extract the policy from a folder containing multiple JSON files."""
        # Get all the json files in the folder
        files = [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".json")
        ]

        # Extract the policy for each file
        for file in files:
            file_path = os.path.join(folder_path, file)
            self.extract_policy_from_file(file_path, verbose)


def main():
    """Function to extract the different criteria logic schemas and output them in JSON format."""
    parser = argparse.ArgumentParser(
        description="Extract the different criteria logic schemas and output them in JSON format."
    )

    parser.add_argument(
        "--string",
        type=str,
        help="The position statement for a medical policy.",
    )

    parser.add_argument(
        "--data",
        type=str,
        help="Extract the policy from a JSON file, or a folder containing multiple JSON files.",
    )

    parser.add_argument(
        "--verbose",
        "-v",  # Changed from "-v" to "--verbose
        action="store_true",
        help="Print verbose output.",
    )

    args = parser.parse_args()

    extractor = MedicalPolicyExtractor()

    if args.data:
        if os.path.isfile(args.data):
            extractor.extract_policy_from_file(args.data, verbose=args.verbose)
        elif os.path.isdir(args.data):
            extractor.extract_policy_from_folder(args.data, verbose=args.verbose)
        else:
            print("The specified data path is invalid.")
        return

    output = extractor.extract_policy(args.string)
    print(output)


if __name__ == "__main__":
    main()
