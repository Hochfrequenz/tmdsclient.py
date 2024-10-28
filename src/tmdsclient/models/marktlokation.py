"""
Model of the Marktlokation object of the TMDS
"""

from email.policy import default
from typing import Any
from uuid import UUID

import pydantic
from bo4e.bo.marktlokation import Marktlokation as Bo4eMarktlokation
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator  # pylint:disable=no-name-in-module

from .utils import create_id_prefix_validator


class _Netznutzungsabrechnungsdaten(BaseModel):
    """placeholder class until https://github.com/bo4e/BO4E-python/issues/920 is resolved"""

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    timestamp: AwareDatetime | None = Field(default=None)
    guid: UUID | None = Field(default=None)
    artikel_id: str | None = Field(default=None, alias="artikelId", serialization_alias="artikelId")
    artikel_id_typ: str | None = Field(default=None, alias="artikelIdTyp", serialization_alias="artikelIdTyp")


class Bo4eMarktlokationWithNetznutzungsabrechnungsdaten(Bo4eMarktlokation):
    """
    similar to the bo4e marktlokation but with a list of Netznutzungsabrechnungsdaten
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    netznutzungsabrechnungsdaten: list[_Netznutzungsabrechnungsdaten] | None = Field(default=None)


class Marktlokation(BaseModel):
    """
    Model of the Marktlokation object of the TMDS
    """

    id: str
    bo_model: Bo4eMarktlokationWithNetznutzungsabrechnungsdaten = pydantic.Field(alias="boModel")

    # pylint:disable=no-self-argument
    @field_validator("id", mode="before")
    def validate_id(cls, melo_id: str) -> Any:
        remove_prefix = create_id_prefix_validator("Marktlokation-", is_guid=False, convert_to_uuid=False)
        return remove_prefix(cls, melo_id)
