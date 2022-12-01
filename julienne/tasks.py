import json
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import TypeVar

from julienne.celery import app

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
