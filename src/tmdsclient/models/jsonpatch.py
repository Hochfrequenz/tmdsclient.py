"""models for RFC6902"""

from typing import Any, Literal, TypeAlias, TypedDict

Operations: TypeAlias = Literal["add", "remove", "replace", "move", "copy", "test"]


class Operation(TypedDict):
    """a single operation inside a JsonPatch"""

    op: Operations
    value: Any
    path: str


JsonPatch: TypeAlias = list[Operation]
