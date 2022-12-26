# Julienne

Julienne is an integration engine written in python using the [celery](https://github.com/celery/celery) to enable higher through put.

The idea is that you can compose a set of python actions into a `flow` which is then pushed into a celery worker for execution. Using this method we can theoretically scale horizontaly quite well while only introducing a few extra milliseconds of latency. This level of latency may not be acceptable for all use cases, however, in the interests of scalability, this is a sacrifice we unfortunately have to make.

> Currently this software is just some code testing different celery settings. Its not an integration engin yet!

## Usage

```bash
poetry run python -m julienne
```

## Authors

* [PattyC](https://github.com/schlerp)
