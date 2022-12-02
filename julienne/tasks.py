import json
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import TypeVar

from julienne.celery import app
from julienne.executors import execute_flow
from julienne.schemas import Flow

R = TypeVar


@app.task
def deserialise_serialise(msg: str) -> str:
    deserialised: Dict[str, Any] = json.loads(msg)
    return json.dumps(deserialised)


@app.task
def run_arbitrary_func(
    function: Callable[..., R], *args: List[Any], **kwargs: Dict[str, Any]
) -> R:
    return function(*args, **kwargs)


@app.task
def run_flow(flow: Flow, data: Any) -> bool:
    return execute_flow(flow=flow, data=data)
