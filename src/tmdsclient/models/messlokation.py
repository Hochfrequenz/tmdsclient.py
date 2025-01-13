"""
Model of the Messlokation object of the TMDS
"""

from typing import Any, Optional

import pydantic
from bo4e.bo.messlokation import Messlokation as Bo4eMesslokation
from pydantic import BaseModel, field_validator  # pylint:disable=no-name-in-module

from .utils import create_id_prefix_validator
from .zaehler import Zaehler
from .zeitscheibe import create_zeitscheibe_class

_ZeitscheibeMeloZaehler = create_zeitscheibe_class(
    entity_validator=create_id_prefix_validator("Zaehler-", is_guid=True, convert_to_uuid=True),
    owner_validator=create_id_prefix_validator("Messlokation-", is_guid=False, convert_to_uuid=False),
    entity_type=Zaehler,
)


# pylint:disable=missing-function-docstring
class Bo4eMeLoWithoutIdValidation(Bo4eMesslokation):  # type:ignore[override]
    """
    Similar to bo4e messlokation but with no regex validation on the messlokations_id.
    The reason is that the IS-U water melo IDs do not match the regex. 🙄
    """

    messlokations_id: str  #  <-- this overrides the regex-pattern check used in the base class


class Messlokation(BaseModel):
    """
    Model of the Messlokation object of the TMDS
    """

    id: str
    bo_model: Bo4eMeLoWithoutIdValidation = pydantic.Field(alias="boModel")
    zaehler: Optional[list[_ZeitscheibeMeloZaehler]] = None  # type:ignore[valid-type]

    # pylint:disable=no-self-argument
    @field_validator("id", mode="before")
    def validate_id(cls, melo_id: str) -> Any:
        remove_prefix = create_id_prefix_validator("Messlokation-", is_guid=False, convert_to_uuid=False)
        return remove_prefix(cls, melo_id)
