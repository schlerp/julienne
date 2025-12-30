import json
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List

from julienne.celery import app
from julienne.pipeline import Pipeline
from julienne.schemas import Block, Flow, Schema
from julienne.sources.base import IteratorDataSource
from julienne.sources.filesystem import JsonArrayFileDataSource
from julienne.sinks.base import DataSink
from julienne.sinks.filesystem import JsonHashDirSink


class Person(Schema):
    first_name: str
    last_name: str
    dob: datetime


class PersonNoDOB(Schema):
    first_name: str
    last_name: str


def strip_dob(person: Person) -> PersonNoDOB:
    data = person.dict()
    data.pop("dob")
    return PersonNoDOB(**data)


class CollectSink(DataSink):
    def __init__(self) -> None:
        self.items: List[Schema] = []

    def process(self, data: List[Schema]) -> None:
        self.items.extend(data)


def test_pipeline_runs_flow_over_iterator_source():
    raw_items: List[Dict[str, Any]] = [
        {"first_name": "First", "last_name": "Last", "dob": datetime.now()}
        for _ in range(3)
    ]
    source = IteratorDataSource(raw_items)

    block: Block[Person, PersonNoDOB] = Block(
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    flow = Flow(name="<Test Flow>", blocks=[block])

    sink = CollectSink()
    pipeline = Pipeline(source=source, flow=flow, sink=sink)

    pipeline.run()

    assert len(sink.items) == 3
    assert all(isinstance(item, PersonNoDOB) for item in sink.items)
    assert all(not hasattr(item, "dob") for item in sink.items)


def test_pipeline_accepts_schema_instances_from_source():
    people = [
        Person(first_name="First", last_name="Last", dob=datetime.now())
        for _ in range(2)
    ]
    # IteratorDataSource expects list of dicts, so we build a simple custom source here.

    class PersonSource:
        def __init__(self, items: List[Person]):
            self.items = items

        def __iter__(self):
            self._idx = 0
            return self

        def __next__(self) -> Person:
            if self._idx >= len(self.items):
                raise StopIteration
            item = self.items[self._idx]
            self._idx += 1
            return item

    source = PersonSource(people)

    block: Block[Person, PersonNoDOB] = Block(
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    flow = Flow(name="<Test Flow>", blocks=[block])

    sink = CollectSink()
    pipeline = Pipeline(source=source, flow=flow, sink=sink)

    pipeline.run()

    assert len(sink.items) == 2
    assert all(isinstance(item, PersonNoDOB) for item in sink.items)


def test_filesystem_end_to_end_pipeline(tmp_path):
    input_file = tmp_path / "people.json"
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    people_payload = [
        {"first_name": "First", "last_name": "Last", "dob": datetime.now().isoformat()},
        {"first_name": "Foo", "last_name": "Bar", "dob": datetime.now().isoformat()},
    ]

    with input_file.open("w") as f:
        json.dump(people_payload, f)

    source = JsonArrayFileDataSource(str(input_file))

    block: Block[Person, PersonNoDOB] = Block(
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    flow = Flow(name="<FS Flow>", blocks=[block])

    sink = JsonHashDirSink(str(output_dir))
    pipeline = Pipeline(source=source, flow=flow, sink=sink)

    pipeline.run()

    written_files = list(output_dir.glob("*.json"))
    assert len(written_files) == 2

    loaded = [json.loads(p.read_text()) for p in written_files]
    assert all("dob" not in item for item in loaded)


def test_pipeline_run_celery_eager_mode(monkeypatch):
    raw_items: List[Dict[str, Any]] = [
        {"first_name": "First", "last_name": "Last", "dob": datetime.now()}
        for _ in range(3)
    ]
    source = IteratorDataSource(raw_items)

    block: Block[Person, PersonNoDOB] = Block(
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    flow = Flow(name="<Celery Test Flow>", blocks=[block])

    sink = CollectSink()
    pipeline = Pipeline(source=source, flow=flow, sink=sink)

    # Enable eager mode so Celery tasks run synchronously during the test.
    previous_eager = app.conf.task_always_eager
    app.conf.task_always_eager = True
    try:
        pipeline.run_celery()
    finally:
        app.conf.task_always_eager = previous_eager

    assert len(sink.items) == 3
    assert all(isinstance(item, PersonNoDOB) for item in sink.items)
    assert all(not hasattr(item, "dob") for item in sink.items)
