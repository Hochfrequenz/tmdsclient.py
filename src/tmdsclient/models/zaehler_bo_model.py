"""
The BO model included in a TMDS zaehler
"""

from collections.abc import Callable
from datetime import datetime
from typing import ClassVar

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

        json_encoders: ClassVar[dict[type[datetime], Callable[[datetime], str]]] = {
            datetime: lambda d: d.isoformat(),  # serialize datetime to timestamp
        }

    boTyp: str
    versionStruktur: str
    zaehlernummer: str
    sparte: Sparte
    zaehlerauspraegung: str | None = None
    zaehlertyp: Zaehlertyp | None = None
    tarifart: str | None = None
    zaehlerkonstante: int | None = None
    eichungBis: datetime | None = None
    letzteEichung: datetime | None = None
    zaehlwerke: list[Zaehlwerk] | None = None
    zaehlerhersteller: Zaehlerhersteller | None = None
    gateway: str | None = None
    fernschaltung: str | None = None
    messwerterfassung: str | None = None
    zaehlergroesse: str | None = None
