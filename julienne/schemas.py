from typing import Callable
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from uuid import uuid4

from pydantic import UUID4
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from pydantic.generics import GenericModel


class Schema(BaseModel):
    class Config:
        orm_mode = True


G_Input = TypeVar("G_Input", bound=Schema)
G_Output = TypeVar("G_Output", bound=Schema | None)


class UniqueNamed(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid4)
    name: str = Field(default=None)

    @validator("name", always=True)
    def validate_name(cls, value, values):
        if value:
            return value
        if uuid := values.get("uuid"):
            return f"{__class__.__name__}: {uuid}"


class Block(UniqueNamed, GenericModel, Generic[G_Input, G_Output]):
    input_schema: Type[G_Input]
    output_schema: Type[G_Output]
    function: Callable[[G_Input], G_Output]


class Flow(UniqueNamed):
    blocks: list[Block]
