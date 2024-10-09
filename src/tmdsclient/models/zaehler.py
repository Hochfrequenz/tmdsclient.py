"""
Model of the Zaehler object of the TMDS
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from bo4e.enum.sparte import Sparte
from pydantic import BaseModel, Field, field_validator

from .utils import create_id_prefix_validator
from .zaehler_bo_model import ZaehlerBoModel, Zaehlertyp


# pylint:disable=missing-function-docstring
class Zaehler(BaseModel):
    """
    Model of the Zaehler object of the TMDS
    """

    class Config:
        """
        Configurations for Zaehler
        """

        json_encoders = {
            datetime: lambda d: d.isoformat(),  # serialize datetime to timestamp
        }

    id: UUID
    externeId: str
    boModel: ZaehlerBoModel
    einbaudatum: Optional[datetime] = None
    ausbaudatum: Optional[datetime] = None
    sperrzustand: str
    is_schmutzwasser_relevant: Optional[bool] = Field(alias="istSchmutzwasserRelevant", default=None)

    # using the forward reference here to avoid a circular imports
    # messlokation: ForwardRef("Messlokation") | None = None  # type:ignore[valid-type]
    # mypy complains about this, but the unittest test_forward_ref_messlokation shows that it works indeed

    # pylint:disable=no-self-argument
    @field_validator("id", mode="before")
    def validate_id(cls, zaehler_id: str) -> Any:
        remove_prefix = create_id_prefix_validator("Zaehler-", is_guid=True, convert_to_uuid=True)
        return remove_prefix(cls, zaehler_id)

    def is_wasser_zaehler(self) -> bool:
        """
        Determines if the zaehler has a 'sparte' or 'zaehlertyp' with wasser-values
        """
        has_wasser_sparte = self.boModel.sparte == Sparte.WASSER
        has_wasser_zaehler_typ = self.boModel.zaehlertyp == Zaehlertyp.WASSERZAEHLER
        return has_wasser_sparte or has_wasser_zaehler_typ
