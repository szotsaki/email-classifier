import re
import sys

import ollama

from .Model import Model


class Classifier:
    def __init__(self, email_structure, categories: list | None = None):
        self._email_structure = email_structure
        self._response = None

        if categories is not None:
            self._categories = categories
        else:
            self._categories = ["primary", "promotion", "social", "notification"]

    def classify(self, model: Model):
        return self._run_llm(model)

    @property
    def response(self):
        return self._response

    def _run_llm(self, model: Model):
        if not self._email_structure["simple_markdown"]:
            print("The provided e-mail is empty, the classifier cannot run on it", file=sys.stderr)
            return None

        if not model.is_available():
            print(f"Requested model {model.model} does not exist locally.", file=sys.stderr)
            return None

        try:
            categories = "'" + "', '".join(self._categories) + "'"
            self._response: ollama.ChatResponse = ollama.chat(model=model.model, think=False, messages=[
                {
                    "role": "user",
                    "content": f"Classify the following e-mail, given in markdown format, into one of the following categories: "
                               f"{categories}. If unsure, output the string 'unsure' verbatim.\n"
                               "Do not reason and omit the thinking process in the response.\n"
                               "The response must contain only one word: one of the listed categories or 'unsure'."
                               f"Email content:\n{self._email_structure["subject"]}\n{self._email_structure["simple_markdown"]}",
                },
            ])

            classification = self._response["message"]["content"].strip()

            # Sometimes the answer is long or thinking is there (even though it's disabled).
            if "\n" in classification:
                classification = classification.splitlines()[-1]

            categories = "|".join(self._categories)
            # This catches the last of the mentions
            classification = re.sub(rf".*({categories}|unsure).*", r"\1", classification)

            if classification in self._categories + ['unsure']:
                return classification

            return "unknown"

        except ollama.ResponseError as e:
            print(f"Could not run Ollama model: {e.error}", file=sys.stderr)
            return None
