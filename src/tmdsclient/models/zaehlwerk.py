"""
Model representing a Zaehlwerk
"""

from typing import Optional

from pydantic import BaseModel

from .bo4e_stub import Mengeneinheit


class Zaehlwerk(BaseModel):
    """
    Model representing a Zaehlwerk
    """

    zaehlwerkId: Optional[str] = None
    bezeichnung: Optional[str] = None
    richtung: Optional[str] = None
    obisKennzahl: str
    einheit: Optional[Mengeneinheit] = None
    schwachlastfaehig: Optional[str] = None
    unterbrechbarkeit: Optional[str] = None
    vorkommastelle: Optional[int] = None
    nachkommastelle: Optional[int] = None
