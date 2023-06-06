import json
import os
from typing import Any
from typing import Dict
from typing import List

from julienne.sources.base import DataSource, IteratorDataSource

JsonData = Dict[str, Any] | List[Dict[str, Any] | List[Any]]


class JsonArrayFileDataSource(IteratorDataSource):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: List[Dict[str, Any] | List[Any]] = []

    def __iter__(self):
        with open(self.file_path, "r") as f:
            self.data = json.load(f)
        self.n = 0
        return self

    def __next__(self):
        return super().__next__()


class JsonFilesDirDataSource(DataSource):
    def __init__(self, directory: str):
        self.directory = directory
        self.file_paths: List[str] = []

    def _load_file(self, file_path: str) -> JsonData:
        with open(file_path, "r") as f:
            return json.load(f)

    def __iter__(self):
        self.file_paths = sorted(
            [os.path.join(self.directory, x) for x in os.listdir(self.directory)]
        )
        self.n = 0
        return self

    def __next__(self):
        if self.n >= len(self.file_paths):
            raise StopIteration
        row = self._load_file(self.file_paths[self.n])
        self.n += 1
        return row
