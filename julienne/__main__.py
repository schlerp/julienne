import logging
import math
import random
import string
import sys
import time
from datetime import datetime
from typing import Callable
from typing import List

from julienne import tasks
from julienne.schemas import Block
from julienne.schemas import Flow
from julienne.schemas import Schema

logging.basicConfig()
LOGGER = logging.getLogger(__file__)


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


def time_it(function: Callable[[Flow, Schema], bool], *args) -> float:
    start = time.perf_counter()
    _ = function(*args)
    return time.perf_counter() - start


class Person(Schema):
    first_name: str
    last_name: str
    dob: datetime
    big_junk: str = "".join(random.choices(string.ascii_letters, k=1000))


class PersonNoDOB(Schema):
    first_name: str
    last_name: str
    big_junk: str


class PersonCombinedName(Schema):
    combined_name: str
    big_junk: str


def strip_dob(person: Person) -> PersonNoDOB:
    p = person.dict()
    p.pop("dob")
    return PersonNoDOB(**p)


def combine_name(person: PersonNoDOB) -> PersonCombinedName:
    return PersonCombinedName(
        combined_name=f"{person.last_name}, {person.first_name}",
        big_junk=person.big_junk,
    )


def print_person(person: PersonCombinedName) -> None:
    time.sleep(0.0001)
    LOGGER.info(f"{person}")


block1: Block[Person, PersonNoDOB] = Block(
    name="[Remove DOB]",
    input_schema=Person,
    output_schema=PersonNoDOB,
    function=strip_dob,
)

block2: Block[PersonNoDOB, PersonCombinedName] = Block(
    name="[Combine Name]",
    input_schema=PersonNoDOB,
    output_schema=PersonCombinedName,
    function=combine_name,
)

block3: Block[PersonCombinedName, None] = Block(
    name="[Print Person]",
    input_schema=PersonCombinedName,
    output_schema=type(None),
    function=print_person,
)

test_flow = Flow(name="<Mutate Person>", blocks=[block1, block2, block3])


test_person = Person(
    first_name="First",
    last_name="Last",
    dob=datetime.now(),
)


if __name__ == "__main__":
    LOGGER.error("Julienne running!")

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    LOGGER.error(f"running local test... ({n=})")
    local_times = [time_it(tasks.run_flow, test_flow, test_person) for _ in range(n)]
    print_test_summary(local_times)

    LOGGER.error(f"running celery test... ({n=})")
    celery_times = [
        time_it(tasks.run_flow.delay, test_flow, test_person) for _ in range(n)
    ]
    print_test_summary(celery_times)
