import hashlib
import json
import os
from typing import List
from typing import Optional

from julienne.schemas import Schema
from julienne.sinks.base import DataSink


class JsonFileSink(DataSink):
    def __init__(self, directory: str, file_name: Optional[str] = None):
        self.directory = directory
        self.file_name = file_name or "data.json"
        self.file_path = os.path.join(self.directory, self.file_name)

    def process(self, data: List[Schema]):
        with open(self.file_path, "w+") as f:
            json.dump(data, f)


class JsonHashDirSink(DataSink):
    def __init__(self, directory: str):
        self.directory = directory

    def _write_file(self, data: str):
        data_hash = hashlib.sha1(data.encode("utf8")).hexdigest()
        file_path = os.path.join(self.directory, f"{data_hash}.json")
        with open(file_path, "w+") as f:
            f.write(data)

    def process(self, data: List[Schema]):
        for x in data:
            self._write_file(x.json())
