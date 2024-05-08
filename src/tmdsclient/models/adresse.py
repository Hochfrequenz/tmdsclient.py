"""
Adresse is an own TMDS entity
"""

from uuid import UUID

from bo4e.com.adresse import Adresse as Bo4eAdresse
from pydantic import BaseModel, Field


class Adresse(BaseModel):
    """
    Represents an address in TMDS
    """

    id: UUID
    externe_id: str = Field(alias="externeId")
    bo_model: Bo4eAdresse = Field(alias="boModel")
