from typing import List, Any, Dict

from julienne.executors import execute_flow
from julienne.schemas import Flow, Schema
from julienne.sources.base import DataSource
from julienne.sinks.base import DataSink
from julienne.tasks import run_flow


class Pipeline:
    def __init__(self, source: DataSource, flow: Flow, sink: DataSink):
        self.source = source
        self.flow = flow
        self.sink = sink

    def _coerce_to_input_schema(self, raw: Any, input_schema: type[Schema]) -> Schema:
        if isinstance(raw, input_schema):
            return raw
        if isinstance(raw, Schema):
            return input_schema(**raw.dict())
        if isinstance(raw, dict):
            return input_schema(**raw)
        raise TypeError(f"Unsupported source item type: {type(raw)}")

    def run(self) -> None:
        if not self.flow.blocks:
            return

        input_schema = self.flow.blocks[0].input_schema
        results: List[Schema] = []

        for item in self.source:
            data = self._coerce_to_input_schema(item, input_schema)
            result = execute_flow(self.flow, data)
            if result is not None:
                results.append(result)

        if results:
            self.sink.process(results)

    def run_celery(self) -> None:
        if not self.flow.blocks:
            return

        input_schema = self.flow.blocks[0].input_schema
        results: List[Schema] = []

        for item in self.source:
            data = self._coerce_to_input_schema(item, input_schema)
            async_result = run_flow.delay(self.flow, data)
            result = async_result.get()
            if result is not None:
                results.append(result)

        if results:
            self.sink.process(results)
