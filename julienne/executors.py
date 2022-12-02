import logging

from julienne.exceptions import InvalidInputDataException
from julienne.schemas import Block
from julienne.schemas import Flow
from julienne.schemas import G_Input
from julienne.schemas import G_Output
from julienne.schemas import Schema

LOGGER = logging.getLogger(__name__)


def execute_block(block: Block[G_Input, G_Output], data: G_Input) -> G_Output:
    if type(data) != block.input_schema:
        LOGGER.error(
            f"{data}, {block.input_schema}, {type(data) == block.input_schema}"
        )
        raise InvalidInputDataException("aww shiet..")
    LOGGER.debug(f"executing block: {block.name}")
    result: G_Output = block.function(data)
    return result


def execute_flow(flow: Flow, data: Schema) -> bool:
    try:
        for block in flow.blocks:
            data = execute_block(block=block, data=data)
        return True
    except Exception:
        LOGGER.exception(f"{flow.name} failed to run with the following exception!")
        return False
