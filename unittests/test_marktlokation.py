from aioresponses import aioresponses


class TestTmdsMarktlokation:
    async def test_get_messlokation_returns_messlokation(self, tmds_client_with_default_auth):
        client, settings = tmds_client_with_default_auth
        marktlokation_id = "88223254274"

        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{settings.server_url}api/Marktlokation/{marktlokation_id}"
            mocked_tmds.get(
                mocked_get_url,
                status=200,
                payload={
                    "id": "88223254274",
                    "datumErzeugt": "2024-10-28T10:02:44.511437+00:00",
                    "datumGeaendert": "2024-10-28T10:02:44.511437+00:00",
                    "boModel": {
                        "boTyp": "MARKTLOKATION",
                        "versionStruktur": "1",
                        "timestamp": "2024-10-28T10:02:44.521633Z",
                        "guid": "81267ccd-ae9f-46e7-8af3-92104572f1d4",
                        "marktlokationsId": "88223254274",
                        "sparte": "STROM",
                        "energierichtung": "AUSSP",
                        "bilanzierungsmethode": "SLP",
                        "verbrauchsart": "KL",
                        "netzebene": "NSP",
                        "bilanzierungsgebiet": "11YN10000762-01E",
                        "lokationsadresse": {
                            "timestamp": "2024-10-28T10:02:44.521633+00:00",
                            "guid": "3c8234bf-58a1-41ee-b8e3-bf887c0ba0b1",
                            "postleitzahl": "28329",
                            "ort": "Bremen",
                            "strasse": "Grolmanstraße",
                            "hausnummer": "77",
                            "landescode": "DE",
                        },
                        "regelzone": "10YDE-EON------1",
                        "zeitreihentyp": "SLS",
                        "zaehlwerke": [
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "70c655e1-e338-4159-9275-aaf86f2c75d5",
                                "obisKennzahl": "1-1:1.29.0",
                                "verbrauchsart": "KL",
                                "unterbrechbarkeit": "NUV",
                                "anzahlAblesungen": 1,
                            }
                        ],
                        "zaehlwerkeBeteiligteMarktrolle": [],
                        "verbrauchsmenge": [
                            {
                                "type": "VERANSCHLAGTEJAHRESMENGE",
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "1d5588c0-f5fd-4e41-8a8c-3fe20f142d21",
                                "obiskennzahl": "",
                                "wert": 2000.0,
                                "einheit": "KWH",
                            }
                        ],
                        "messtechnischeEinordnung": "KME_MME",
                        "netznutzungsabrechnungsdaten": [
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "14593184-a6a6-4129-8fe3-a869a86febaa",
                                "artikelId": "1-02-0-001",
                                "artikelIdTyp": "ARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "1c441a5a-4b5f-4d09-b589-dc0fa13c8565",
                                "artikelId": "1-02-0-002",
                                "artikelIdTyp": "ARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "d8071651-3980-4363-9b84-7b8370c8ba3f",
                                "artikelId": "1-08-4-002",
                                "artikelIdTyp": "ARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "6bf74066-d91e-473b-9e5e-d7a456deff99",
                                "artikelId": "1-10-1",
                                "artikelIdTyp": "GRUPPENARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "54e7b18c-85b9-4995-9ae9-6bac7ebfc7eb",
                                "artikelId": "1-10-2",
                                "artikelIdTyp": "GRUPPENARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                            {
                                "timestamp": "2024-10-28T10:02:44.521633+00:00",
                                "guid": "c8ae23dd-6754-4a31-aceb-fe5641adbfcc",
                                "artikelId": "1-10-4",
                                "artikelIdTyp": "GRUPPENARTIKELID",
                                "gemeinderabatt": 0.0,
                                "zuschlag": 0.0,
                            },
                        ],
                        "sperrstatus": "ENTSPERRT",
                    },
                    "messlokationen": [],
                },
            )
            malo = await client.get_marktlokation(marktlokation_id)

            # assert
            assert malo is not None
            assert malo.id == marktlokation_id
            assert not malo.id.startswith("Marktlokation-")
            assert any(malo.bo_model.netznutzungsabrechnungsdaten)
