import logging
import math
import sys
import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from julienne import tasks

LOGGER = logging.getLogger(__file__)

Msg = Dict[str, Any]


def time_it(function: Callable[[Msg], Msg], msg: Msg) -> float:
    start = time.perf_counter()
    _ = function(msg)
    return time.perf_counter() - start


def print_test_summary(times: List[float]) -> None:
    test_summary_template = """
    n:     {n}
    total: {total:.7f}s
    min:   {min_time:.7f}ms
    max:   {max_time:.7f}ms
    mean:  {mean_time:.7f}ms
    sd:    {sd:.7f}ms
    """
    n = len(times)
    total = sum(times)
    min_time = min(times)
    max_time = max(times)
    mean_time = total / n
    dev_2 = [(x - mean_time) ** 2 for x in times]
    variance = sum(dev_2) / (n - 1)
    sd = math.sqrt(variance)
    LOGGER.error(
        test_summary_template.format(
            n=n,
            total=total,
            min_time=min_time * 1000,
            max_time=max_time * 1000,
            mean_time=mean_time * 1000,
            sd=sd * 1000,
        )
    )


if __name__ == "__main__":

    LOGGER.error("im python!")
    n = int(sys.argv[2]) if len(sys.argv) == 3 else 1000

    with open(sys.argv[1], "r") as f:
        patient_example_text = f.read()

    LOGGER.error(f"running local test... ({n=})")
    local_times = [
        time_it(tasks.deserialise_serialise, patient_example_text) for _ in range(n)
    ]
    print_test_summary(local_times)

    LOGGER.error(f"running celery test... ({n=})")
    celery_times = [
        time_it(tasks.deserialise_serialise.delay, patient_example_text)
        for _ in range(n)
    ]
    print_test_summary(celery_times)
