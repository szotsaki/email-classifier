import argparse
import math
import os
import sys
from datetime import timedelta

from classifier.Classifier import Classifier
from classifier.Email import Email
from classifier.Model import Model


class Benchmark:
    def __init__(self, args):
        self._args = args

        self._subj_len = 50

        if not os.path.isdir(args.directory):
            print(f"Directory '{args.directory}' does not exist.")
            exit(1)

    def run(self) -> None:
        self._pull_foreign_models()
        self._process_emails()

    def _pull_foreign_models(self) -> None:
        for model in self._args.models:
            model = Model(model)
            if not model.is_available():
                if not model.pull():
                    print("Could not retrieve all the requested models. Benchmark is now exiting.", file=sys.stderr)
                    exit(1)

    def _process_emails(self) -> None:
        print(f"{"Subject":{self._subj_len + 1}s}", end="")
        for model in self._args.models:
            print(f"{model:21s}", end="")
        print()
        print("-" * (self._subj_len + 1) + "-" * ((len(self._args.models) * 21) - 1))

        directory = self._args.directory
        for filename in os.listdir(directory):
            if filename.endswith(".eml"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'rb') as file:
                    email_structure = Email(file.read()).parse()
                    classifier = Classifier(email_structure)

                    short_subject = email_structure["subject"][:self._subj_len]
                    print(f"{short_subject:{self._subj_len + 1}s}", end="", flush=True)

                    for model in self._args.models:
                        model = Model(model)
                        classification = classifier.classify(model)
                        if classification is not None:
                            response = classifier.response
                            duration = str(timedelta(seconds=math.ceil(response["total_duration"] / (10 ** 9))))
                            print(f"{classification:13s}{duration:8s}", end="", flush=True)
                        else:
                            print(f"{"-":13s} {"-":8s}", end="", flush=True)

                    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-mail classifier comparator')
    parser.add_argument('directory', help='Path to the directory containing the .eml files', type=str)
    parser.add_argument('-m', '--models', nargs='+',
                        help='Models to benchmark. Example: "mistral:7b deepseek-r1:8b". Default: mistral:7b',
                        default=["mistral:7b"])
    args = parser.parse_args()

    Benchmark(args).run()
