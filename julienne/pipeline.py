from typing import List, Any, Dict, Optional

from julienne.executors import execute_flow
from julienne.schemas import Flow, Schema, PipelineItemError
from julienne.sources.base import DataSource
from julienne.sinks.base import DataSink
from julienne.tasks import run_flow


class Pipeline:
    def __init__(
        self,
        source: DataSource,
        flow: Flow,
        sink: DataSink,
        error_sink: Optional[DataSink] = None,
    ):
        self.source = source
        self.flow = flow
        self.sink = sink
        self.error_sink = error_sink

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
        errors: List[Schema] = []

        for idx, item in enumerate(self.source):
            try:
                data = self._coerce_to_input_schema(item, input_schema)
                result = execute_flow(self.flow, data)
                if result is not None:
                    results.append(result)
            except Exception as exc:  # pragma: no cover - exercised via tests
                if self.error_sink is not None:
                    errors.append(
                        PipelineItemError(
                            flow_name=self.flow.name,
                            error=str(exc),
                            item_index=idx,
                            item=item if isinstance(item, dict) else {},
                        )
                    )

        if results:
            self.sink.process(results)
        if errors and self.error_sink is not None:
            self.error_sink.process(errors)

    def run_celery(self) -> None:
        if not self.flow.blocks:
            return

        input_schema = self.flow.blocks[0].input_schema
        results: List[Schema] = []
        errors: List[Schema] = []

        for idx, item in enumerate(self.source):
            try:
                data = self._coerce_to_input_schema(item, input_schema)
                async_result = run_flow.delay(self.flow, data)
                result = async_result.get()
                if result is not None:
                    results.append(result)
            except Exception as exc:
                if self.error_sink is not None:
                    if isinstance(item, Schema):
                        item_dict: Dict[str, Any] = item.dict()
                    elif isinstance(item, dict):
                        item_dict = item
                    else:
                        item_dict = {"value": str(item)}
                    errors.append(
                        PipelineItemError(
                            flow_name=self.flow.name,
                            error=str(exc),
                            item_index=idx,
                            item=item_dict,
                        )
                    )

        if results:
            self.sink.process(results)
        if errors and self.error_sink is not None:
            self.error_sink.process(errors)
