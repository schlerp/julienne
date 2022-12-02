import logging
from typing import List

from julienne.schemas import Schema


class DataSink:
    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def process(self, data: List[Schema]) -> None:
        raise NotImplementedError


class LogDataSink(DataSink):
    def __init__(self, logger_name: str = __name__):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)

    def __str__(self):
        return f"<{self.__class__.__name__}:{self.logger_name}>"

    def process(self, data: List[Schema]):
        for x in data:
            self.logger.info(x)
