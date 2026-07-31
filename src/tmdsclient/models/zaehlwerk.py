"""
Model representing a Zaehlwerk
"""

from pydantic import BaseModel

from .bo4e_stub import Mengeneinheit


class Zaehlwerk(BaseModel):
    """
    Model representing a Zaehlwerk
    """

    zaehlwerkId: str | None = None
    bezeichnung: str | None = None
    richtung: str | None = None
    obisKennzahl: str
    einheit: Mengeneinheit | None = None
    schwachlastfaehig: str | None = None
    unterbrechbarkeit: str | None = None
    vorkommastelle: int | None = None
    nachkommastelle: int | None = None
