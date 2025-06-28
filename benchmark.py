import argparse
import math
import os
from datetime import timedelta

from classifier.Classifier import Classifier
from classifier.Email import Email
from classifier.Model import Model


def process_emails(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".eml"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'rb') as file:
                email_structure = Email(file.read()).parse()
                classifier = Classifier(email_structure)
                classification = classifier.classify(Model("mistral:7b"))
                if classification is not None:
                    response = classifier.response
                    print(
                        f'"{email_structure["subject"]}": '
                        f"{classification} "
                        f"(prompt: {timedelta(seconds=math.ceil(response["prompt_eval_duration"] / (10 ** 9)))}, "
                        f"total: {timedelta(seconds=math.ceil(response["total_duration"] / (10 ** 9)))} sec)"
                    )


def main():
    parser = argparse.ArgumentParser(description='E-mail classifier comparator')
    parser.add_argument('directory', help='Path to the directory containing the .eml files', type=str)
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"The directory '{args.directory}' does not exist.")
        exit(1)

    process_emails(args.directory)


if __name__ == "__main__":
    main()
