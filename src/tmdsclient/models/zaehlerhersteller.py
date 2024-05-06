"""
Model representing the zaehlerhersteller
"""

from pydantic import BaseModel

from .partneradresse import Partneradresse


class Zaehlerhersteller(BaseModel):
    """
    Model representing the zaehlerhersteller
    """

    boTyp: str
    versionStruktur: str
    name1: str
    name2: str
    name3: str
    gewerbekennzeichnung: bool
    kontaktweg: list[str]
    partneradresse: Partneradresse
