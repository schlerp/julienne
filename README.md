# Julienne

Julienne is an integration engine written in python using [Celery](https://github.com/celery/celery) to enable higher throughput.

You compose a set of Python actions into a `Flow`, then run that flow over data from a `DataSource` and into a `DataSink` via a `Pipeline`. Flows can be executed locally or via Celery workers for horizontal scaling.

## Status

This project is still experimental and not production-ready.

## Installation / dependencies

Julienne is configured as a standard Python project using PEP 621, hatchling, and [uv](https://github.com/astral-sh/uv) for dependency management.

- Runtime dependencies are declared in `pyproject.toml` and mirrored in `requirements.txt`.
- A locked set of dependencies (including Celery) is tracked in `uv.lock`.
- You can run commands with dependencies resolved via `uv`:

```bash
uv run pytest
uv run python -m julienne ...
```

## Quickstart (local demo)

Run the test suite (optional but recommended):

```bash
uv run pytest
```

Then run the demo filesystem pipeline via the CLI:

```bash
uv run python -m julienne demo-filesystem \
  --input-json path/to/people.json \
  --output-dir /tmp/julienne-out
```

`people.json` should be a JSON array of objects with at least `first_name`, `last_name`, and `dob` fields. The demo flow removes `dob` from each item and writes one JSON file per record into the output directory.

## Pipelines and Celery

At a lower level, Julienne exposes a `Pipeline` abstraction that wires together a `DataSource`, `Flow`, and `DataSink`.

A simple local pipeline can look like this:

```python
from julienne.pipeline import Pipeline
from julienne.schemas import Block, Flow
from julienne.sources.filesystem import JsonArrayFileDataSource
from julienne.sinks.filesystem import JsonHashDirSink, JsonLinesSink

from your_module import Person, PersonNoDOB, strip_dob

source = JsonArrayFileDataSource("people.json")
block = Block[Person, PersonNoDOB](
    name="[Remove DOB]",
    input_schema=Person,
    output_schema=PersonNoDOB,
    function=strip_dob,
)
flow = Flow(name="<Example Flow>", blocks=[block])
sink = JsonHashDirSink("out_dir")
error_sink = JsonLinesSink("errors.jsonl")

pipeline = Pipeline(source=source, flow=flow, sink=sink, error_sink=error_sink)

# Run locally, in-process
pipeline.run()

# Or run via Celery tasks (requires broker + worker)
pipeline.run_celery()
```

Each failed item is captured as a `PipelineItemError` and written as a single JSON document per line into `errors.jsonl`.

For testing, Celery can be run in *eager* mode so tasks execute synchronously in the same process. See `tests/test_pipeline.py` for an example that temporarily sets `app.conf.task_always_eager = True` while exercising the Celery-backed pipeline.

## Historical Docker / Celery experiment

An earlier version of this project included a Docker/Compose-based Celery setup. That configuration has been removed in favor of a simpler, local-first workflow driven by `uv` and standard Python tooling.

If you need containerization, you can layer your own Docker/Compose setup on top of the current `pyproject.toml`, `requirements.txt`, and `uv.lock`.

## Authors

- [PattyC](https://github.com/schlerp)
