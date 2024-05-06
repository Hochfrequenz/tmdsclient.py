"""
The BO model included in a TMDS zaehler
"""

from datetime import datetime
from typing import Optional

from bo4e.enum.sparte import Sparte
from bo4e.enum.strenum import StrEnum
from pydantic import BaseModel

from .zaehlerhersteller import Zaehlerhersteller
from .zaehlwerk import Zaehlwerk


class Zaehlertyp(StrEnum):
    """
    Erweiterung des bo4e.enum.zaehlertyp.Zaehlertyps um Wasserzaehler.
    Orientiert sich an https://github.com/Hochfrequenz/BO4E-dotnet/blob/main/BO4E/ENUM/Zaehlertyp.cs
    (weil BO4E.net im TMDS verwendet wird)
    """

    DREHSTROMZAEHLER = "DREHSTROMZAEHLER"
    # because the enum was not nullable at the first TMDS migration 2020, most meters defaulted to DREHSTROMZAEHLER
    BALGENGASZAEHLER = "BALGENGASZAEHLER"
    DREHKOLBENZAEHLER = "DREHKOLBENZAEHLER"
    SMARTMETER = "SMARTMETER"
    LEISTUNGSZAEHLER = "LEISTUNGSZAEHLER"
    MAXIMUMZAEHLER = "MAXIMUMZAEHLER"
    TURBINENRADGASZAEHLER = "TURBINENRADGASZAEHLER"
    ULTRASCHALLGASZAEHLER = "ULTRASCHALLGASZAEHLER"
    WECHSELSTROMZAEHLER = "WECHSELSTROMZAEHLER"
    MESSDATENREGISTRIERGERAET = "MESSDATENREGISTRIERGERAET"
    ELEKTRONISCHERHAUSHALTSZAEHLER = "ELEKTRONISCHERHAUSHALTSZAEHLER"
    SONDERAUSSTATTUNG = "SONDERAUSSTATTUNG"
    WASSERZAEHLER = "WASSERZAEHLER"
    MODERNEMESSEINRICHTUNG = "MODERNEMESSEINRICHTUNG"


class ZaehlerBoModel(BaseModel):
    """
    The BO model included in a TMDS zaehler
    """

    class Config:
        """
        Configurations for ZaehlerBoModel
        """

        json_encoders = {
            datetime: lambda d: d.isoformat(),  # serialize datetime to timestamp
        }

    boTyp: str
    versionStruktur: str
    zaehlernummer: str
    sparte: Sparte
    zaehlerauspraegung: Optional[str] = None
    zaehlertyp: Optional[Zaehlertyp] = None
    tarifart: Optional[str] = None
    zaehlerkonstante: Optional[int] = None
    eichungBis: Optional[datetime] = None
    letzteEichung: Optional[datetime] = None
    zaehlwerke: Optional[list[Zaehlwerk]] = None
    zaehlerhersteller: Optional[Zaehlerhersteller] = None
    gateway: Optional[str] = None
    fernschaltung: Optional[str] = None
    messwerterfassung: Optional[str] = None
    zaehlergroesse: Optional[str] = None
