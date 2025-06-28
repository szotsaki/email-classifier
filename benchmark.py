import argparse
import math
import os
from datetime import timedelta

from classifier.Classifier import Classifier
from classifier.Email import Email
from classifier.Model import Model


class Benchmark:
    def __init__(self, args):
        self._args = args

        if not os.path.isdir(args.directory):
            print(f"Directory '{args.directory}' does not exist.")
            exit(1)

    def run(self):
        self._process_emails()

    def _process_emails(self):
        directory = self._args.directory
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-mail classifier comparator')
    parser.add_argument('directory', help='Path to the directory containing the .eml files', type=str)
    args = parser.parse_args()

    Benchmark(args).run()
