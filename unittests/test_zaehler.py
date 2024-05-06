import uuid

from aioresponses import aioresponses

from tmdsclient.models.zaehler import Zaehler


def _get_zaehler_model() -> Zaehler:
    zaehler_dict = {
        "id": uuid.UUID("6b024ea2-82a3-4ae9-be06-01229817373a"),
        "externeId": "Equipmentnummer vom SAP",
        "boModel": {
            "boTyp": "ZAEHLER",
            "versionStruktur": "1",
            "zaehlernummer": "Zaehlernummer 123",
            "sparte": "STROM",
            "zaehlerauspraegung": "EINRICHTUNGSZAEHLER",
            "zaehlertyp": "DREHSTROMZAEHLER",
            "zaehlergroesse": "WASSER_MWZW",
            "tarifart": "EINTARIF",
            "zaehlerkonstante": 1,
            "eichungBis": "2022-01-01T00:00:00+00:00",
            "letzteEichung": "2019-06-01T00:00:00+00:00",
            "zaehlwerke": [
                {
                    "zaehlwerkId": "asdfghhjk",
                    "bezeichnung": "Zaehlwerk0",
                    "richtung": "AUSSP",
                    "obisKennzahl": "1-0:1.8.1",
                    "einheit": "KWH",
                    "schwachlastfaehig": "SCHWACHLASTFAEHIG",
                    "unterbrechbarkeit": "NUV",
                    "vorkommastelle": 5,
                    "nachkommastelle": 6,
                }
            ],
            "zaehlerhersteller": {
                "boTyp": "GESCHAEFTSPARTNER",
                "versionStruktur": "1",
                "name1": "Zaehlermanufaktur Mustermann & Söhne",
                "name2": "Filiale Niedersachen",
                "name3": "⏱ Qualitätszähler seit 1896",
                "gewerbekennzeichnung": True,
                "kontaktweg": ["FAX"],
                "partneradresse": {
                    "postleitzahl": "01097",
                    "ort": "Dresden Neustadt",
                    "strasse": "Ümläét⸺stráßè",
                    "hausnummer": "17a",
                    "landescode": "DE",
                },
            },
            "gateway": "Referenz auf ein verbautes SMGW",
            "fernschaltung": "NICHT_VORHANDEN",
            "messwerterfassung": "MANUELL_AUSGELESENE",
        },
        "einbaudatum": "2020-03-29T01:30:00+00:00",
        "ausbaudatum": "2020-10-25T01:30:00+00:00",
        "sperrzustand": "ENTSPERRT",
    }
    return Zaehler.model_validate(zaehler_dict)


class TestTmdsZaehler:
    async def test_get_zaehler_zaehler_exists_returns_zaehler(self, tmds_client_with_default_auth):
        client, settings = tmds_client_with_default_auth
        zaehler_id = "Zaehler-6b024ea2-82a3-4ae9-be06-01229817373a"

        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{settings.server_url}api/Zaehler/{zaehler_id}"
            mocked_tmds.get(
                mocked_get_url,
                status=200,
                payload=_get_zaehler_model().model_dump(mode="json"),
            )

            # act
            zaehler = await client.get_zaehler(zaehler_id)

            # assert
            assert zaehler is not None
            assert any(zaehler)
            assert zaehler.id == uuid.UUID("6b024ea2-82a3-4ae9-be06-01229817373a")
