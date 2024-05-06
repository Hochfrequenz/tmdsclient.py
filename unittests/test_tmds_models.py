from uuid import UUID

from tmdsclient.models.messlokation import Messlokation
from tmdsclient.models.zaehler import Zaehler


class TestTmdsModels:
    def test_melo_model(self):
        minimal_working_messlokation = Messlokation.model_validate(
            {
                "id": "DE0123456789012345678901234567890",
                "boModel": {
                    "boTyp": "MESSLOKATION",
                    "versionStruktur": 1,
                    "messlokationsId": "DE0123456789012345678901234567890",
                    "sparte": "WASSER",
                    "bilanzierungsmethode": "SLP",
                },
            }
        )
        assert minimal_working_messlokation.id == "DE0123456789012345678901234567890"

    def test_zaehler_model(self):
        minimal_working_zaehler = Zaehler.model_validate(
            {
                "id": "d29f9760-f1bd-4dcb-a0ed-488e42365ddf",
                "externeId": "Equipmentnummer vom SAP",
                "boModel": {
                    "boTyp": "ZAEHLER",
                    "versionStruktur": "1",
                    "zaehlernummer": "Zaehlernummer 123",
                    "zaehlertyp": "WASSERZAEHLER",
                    "zaehlerkonstante": 1,
                    "sparte": "WASSER",
                    "zaehlergroesse": "WASSER_WZ02",
                    "zaehlwerke": [
                        {
                            "zaehlwerkId": "asdfghhjk",
                            "bezeichnung": "Zaehlwerk0",
                            "richtung": "AUSSP",
                            "obisKennzahl": "1-0:1.8.1",
                            "einheit": "KUBIKMETER",
                        }
                    ],
                },
                "einbaudatum": "2020-03-29T01:30:00+00:00",
                "sperrzustand": "ENTSPERRT",
            }
        )
        assert minimal_working_zaehler.id == UUID("d29f9760-f1bd-4dcb-a0ed-488e42365ddf")
