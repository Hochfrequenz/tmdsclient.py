"""
Module containing the TMDS Anschlussobjekt model
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from tmdsclient.models.adresse import Adresse


class Plattformfaehig(BaseModel):
    """
    Plattformfaehig means that the Anschlussobjekt may be used in the platform.
    This is a time-dependent property.
    """

    von: datetime = Field(alias="von")
    bis: datetime | None = Field(default=None, alias="bis")
    type: str = Field(alias="type")
    entity_id: bool = Field(alias="entityId")
    owner_id: str = Field(alias="ownerId")
    entity: bool = Field(alias="entity")
    start: str = Field(alias="start")


class Anschlussobjekt(BaseModel):
    """
    An Anschlussobjekt in TMDS represents a house (that contains n Flats/Einheiten).
    """

    id: UUID = Field(alias="id")
    externe_id: str = Field(alias="externeId")
    is_migrated_from_isu: bool = Field(alias="isMigratedFromIsu", default=False)
    adresse: Optional[Adresse] = Field(alias="adresse", default=None)
    # einheiten: Optional[list[_AnschlussobjektEinheitZeitscheibe]] = None  # type:ignore[valid-type]
    plattformfaehig: Optional[list[Plattformfaehig]] = None
