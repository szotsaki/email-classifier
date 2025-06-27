import ollama


class Classifier:
    def __init__(self, email_structure):
        self._email_structure = email_structure
        self._response = None

    def classify(self):
        return self._run_llm()

    @property
    def response(self):
        return self._response

    def _run_llm(self, model="mistral:7b", pull_foreign_model=False):
        if not self._email_structure["simple_markdown"]:
            print("The provided e-mail is empty, the classifier cannot run on it")
            return None

        try:
            self._response: ollama.ChatResponse = ollama.chat(model=model, messages=[
                {
                    "role": "user",
                    "content": f"Classify the following e-mail given in markdown format into one of the following four categories: "
                               "'primary', 'promotion', 'social', 'notification'. If unsure, output the string 'unsure' verbatim. "
                               "The response must contain only one word: one of the listed categories or 'unsure'.\n"
                               f"Email content:\n{self._email_structure["subject"]}\n{self._email_structure["simple_markdown"]}",
                },
            ])

            classification = self._response["message"]["content"].strip().replace("'", "")

            return classification
        except ollama.ResponseError as e:
            print(f"Could not run Ollama model: {e.error}")
