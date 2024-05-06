"""
Model representing the partneradresse
"""

from pydantic import BaseModel


class Partneradresse(BaseModel):
    """
    Model representing the partneradresse
    """

    postleitzahl: str
    ort: str
    strasse: str
    hausnummer: str
    landescode: str
