import sys

import ollama


class Model:
    def __init__(self, model: str, pull: bool = False):
        self._model = model
        self._pull = pull

    @property
    def model(self) -> str:
        return self._model

    def is_available(self) -> bool:
        current_models = ollama.list().models
        return len(list(filter(lambda m: m.model == self._model, current_models))) > 0

    def pull(self) -> bool:
        try:
            print(f'Retrieving model "{self._model}"...')
            ollama.pull(self._model)
        except ollama.ResponseError as e:
            print(f'Could not pull model "{self._model}": {e.error}', file=sys.stderr)
            return False

        return True
