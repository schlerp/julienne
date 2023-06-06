from typing import Any
from typing import Dict
from typing import List


class DataSource:  # pragma: no cover
    def __str__(self):
        return f"{self.__class__.__name__}"

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


class IteratorDataSource(DataSource):
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n >= len(self.data):
            raise StopIteration
        row = self.data[self.n]
        self.n += 1
        return row
