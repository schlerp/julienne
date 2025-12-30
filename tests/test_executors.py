import logging
from datetime import datetime

from julienne import executors
from julienne import schemas
from julienne.exceptions import InvalidInputDataException


class Person(schemas.Schema):
    first_name: str
    last_name: str
    dob: datetime


class PersonNoDOB(schemas.Schema):
    first_name: str
    last_name: str


def strip_dob(person: Person) -> PersonNoDOB:
    data = person.dict()
    data.pop("dob")
    return PersonNoDOB(**data)


def test_execute_block_happy_path(caplog):
    block = schemas.Block[Person, PersonNoDOB](
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    person = Person(first_name="First", last_name="Last", dob=datetime.now())

    with caplog.at_level(logging.DEBUG):
        result = executors.execute_block(block=block, data=person)

    assert isinstance(result, PersonNoDOB)
    assert result.first_name == person.first_name
    assert result.last_name == person.last_name
    assert "executing block: [Remove DOB]" in caplog.text


def test_execute_block_invalid_input_type():
    block = schemas.Block[Person, PersonNoDOB](
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    not_a_person = PersonNoDOB(first_name="First", last_name="Last")

    try:
        executors.execute_block(block=block, data=not_a_person)  # type: ignore[arg-type]
    except InvalidInputDataException:
        assert True
    else:
        assert False, "Expected InvalidInputDataException was not raised"


def test_execute_flow_returns_final_data():
    block = schemas.Block[Person, PersonNoDOB](
        name="[Remove DOB]",
        input_schema=Person,
        output_schema=PersonNoDOB,
        function=strip_dob,
    )
    flow = schemas.Flow(name="<Test Flow>", blocks=[block])
    person = Person(first_name="First", last_name="Last", dob=datetime.now())

    result = executors.execute_flow(flow=flow, data=person)

    assert isinstance(result, PersonNoDOB)
    assert result.first_name == person.first_name
    assert result.last_name == person.last_name
