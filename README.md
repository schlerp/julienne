# Julienne

Julienne is an integration engine written in python using [Celery](https://github.com/celery/celery) to enable higher throughput.

You compose a set of Python actions into a `Flow`, then run that flow over data from a `DataSource` and into a `DataSink` via a `Pipeline`. Flows can be executed locally or via Celery workers for horizontal scaling.

## Status

This project is still experimental and not production-ready.

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

## Docker / Celery (original experiment)

The original Docker/Celery experiment is still available via the compose setup:

```bash
# gen your ssl key pairs
./scripts/gen_ssl_key_pair.sh

# run docker compose build/tail/teardown
docker-compose up --build --scale worker=2 -d && docker-compose logs -f julienne && docker-compose down -v --remove-orphans
```

## Authors

- [PattyC](https://github.com/schlerp)
