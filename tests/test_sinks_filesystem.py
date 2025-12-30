import json
from typing import List

from julienne.schemas import Schema
from julienne.sinks.filesystem import JsonLinesSink


class DummySchema(Schema):
    value: int


def test_json_lines_sink_writes_one_json_per_line(tmp_path):
    output_file = tmp_path / "errors.jsonl"
    sink = JsonLinesSink(str(output_file))

    items: List[Schema] = [DummySchema(value=1), DummySchema(value=2)]

    sink.process(items)

    assert output_file.exists()
    lines = output_file.read_text().strip().split("\n")
    assert len(lines) == 2

    decoded = [json.loads(line) for line in lines]
    assert decoded == [{"value": 1}, {"value": 2}]
