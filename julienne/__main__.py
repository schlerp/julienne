import argparse
import logging
from datetime import datetime
from typing import List, Optional

from julienne.pipeline import Pipeline
from julienne.schemas import Block, Flow, Schema
from julienne.sinks.filesystem import JsonHashDirSink, JsonLinesSink
from julienne.sources.filesystem import JsonArrayFileDataSource


LOGGER = logging.getLogger(__name__)


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


def build_demo_flow() -> Flow:
    block: Block[Person, PersonNoDOB] = Block(
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    return Flow(name="<Demo Flow>", blocks=[block])


def run_demo_filesystem(
    input_json: str,
    output_dir: str,
    error_jsonl: Optional[str] = None,
) -> None:
    source = JsonArrayFileDataSource(input_json)
    flow = build_demo_flow()
    sink = JsonHashDirSink(output_dir)
    error_sink = JsonLinesSink(error_jsonl) if error_jsonl is not None else None

    pipeline = Pipeline(source=source, flow=flow, sink=sink, error_sink=error_sink)
    pipeline.run()


def main(argv: List[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="julienne", description="Julienne integration engine demo CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_fs = subparsers.add_parser("demo-filesystem", help="Run a simple filesystem-based demo pipeline")
    demo_fs.add_argument("--input-json", required=True, help="Path to input JSON array file")
    demo_fs.add_argument("--output-dir", required=True, help="Directory to write output JSON files")
    demo_fs.add_argument(
        "--error-jsonl",
        help="Optional path to write per-record errors as JSON lines",
    )

    args = parser.parse_args(argv)

    if args.command == "demo-filesystem":
        run_demo_filesystem(
            input_json=args.input_json,
            output_dir=args.output_dir,
            error_jsonl=args.error_jsonl,
        )


if __name__ == "__main__":
    main()
