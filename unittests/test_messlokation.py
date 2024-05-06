from aioresponses import aioresponses


class TestTmdsMesslokation:
    async def test_get_messlokation_returns_messlokation(self, tmds_client_with_default_auth):
        client, settings = tmds_client_with_default_auth
        messlokation_id = "DE0000011111222223333344444555556"

        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{settings.server_url}api/Messlokation/{messlokation_id}"
            mocked_tmds.get(
                mocked_get_url,
                status=200,
                payload={
                    "id": "DE0000011111222223333344444555556",
                    "boModel": {
                        "boTyp": "MESSLOKATION",
                        "versionStruktur": "1",
                        "messlokationsId": "DE0000011111222223333344444555556",
                        "sparte": "STROM",
                        "netzebeneMessung": "MD",
                        "messadresse": {
                            "postleitzahl": "82031",
                            "ort": "Grünwald",
                            "strasse": "Nördliche Münchner Straße",
                            "hausnummer": "27A",
                            "landescode": "DE",
                        },
                        "bilanzierungsmethode": "SLP",
                        "verlustfaktor": 1.1,
                    },
                    "marktlokationen": [
                        {
                            "von": "2020-04-01T00:00:00+00:00",
                            "bis": "2022-04-20T00:00:00+00:00",
                            "entity": {
                                "id": "51238696781",
                                "boModel": {
                                    "boTyp": "MARKTLOKATION",
                                    "versionStruktur": "1",
                                    "marktlokationsId": "51238696781",
                                    "sparte": "GAS",
                                    "energierichtung": "AUSSP",
                                    "bilanzierungsmethode": "PAUSCHAL",
                                    "netzebene": "HD",
                                },
                                "messlokationen": [
                                    {
                                        "von": "2020-04-01T00:00:00+00:00",
                                        "bis": "2020-04-20T00:00:00+00:00",
                                        "entity": {
                                            "id": "DE987654321098765432109865432109",
                                            "boModel": {
                                                "boTyp": "MESSLOKATION",
                                                "versionStruktur": "1",
                                                "messlokationsId": "DE987654321098765432109865432109",
                                                "sparte": "GAS",
                                                "netzebeneMessung": "MD",
                                                "messadresse": {
                                                    "postleitzahl": "82031",
                                                    "ort": "Grünwald",
                                                    "strasse": "Nördliche Münchner Straße",
                                                    "hausnummer": "27A",
                                                    "landescode": "DE",
                                                },
                                                "bilanzierungsmethode": "RLM",
                                                "abrechnungmessstellenbetriebnna": True,
                                                "gasqualitaet": "L_GAS",
                                                "verlustfaktor": 1.1,
                                            },
                                        },
                                        "start": "2020-04-01T00:00:00Z",
                                    }
                                ],
                            },
                            "start": "2020-04-01T00:00:00Z",
                        }
                    ],
                    "einheit": {
                        "id": "973db7b0-19a3-449b-8d1c-c30e409d21e3",
                        "externeId": "DasIstEineIdVomSap",
                        "lagezusatz": "Drittes Stockwerk links",
                        "messlokationen": [
                            {
                                "von": "2020-04-01T00:00:00+00:00",
                                "bis": "2022-04-20T00:00:00+00:00",
                                "ownerId": "00000000-0000-0000-0000-000000000000",
                                "entity": {
                                    "id": "DE987654321098765432109865432109",
                                    "boModel": {
                                        "boTyp": "MESSLOKATION",
                                        "versionStruktur": "1",
                                        "messlokationsId": "DE987654321098765432109865432109",
                                        "sparte": "STROM",
                                        "netzebeneMessung": "MD",
                                        "messadresse": {
                                            "postleitzahl": "82031",
                                            "ort": "Grünwald",
                                            "strasse": "Nördliche Münchner Straße",
                                            "hausnummer": "27A",
                                            "landescode": "DE",
                                        },
                                        "bilanzierungsmethode": "SLP",
                                        "verlustfaktor": 1.1,
                                    },
                                    "marktlokationen": [
                                        {
                                            "von": "2020-04-01T00:00:00+00:00",
                                            "bis": "2022-04-20T00:00:00+00:00",
                                            "entity": {
                                                "id": "51238696781",
                                                "boModel": {
                                                    "boTyp": "MARKTLOKATION",
                                                    "versionStruktur": "1",
                                                    "marktlokationsId": "51238696781",
                                                    "sparte": "GAS",
                                                    "energierichtung": "AUSSP",
                                                    "bilanzierungsmethode": "PAUSCHAL",
                                                    "netzebene": "HD",
                                                },
                                                "messlokationen": [
                                                    {
                                                        "von": "2020-04-01T00:00:00+00:00",
                                                        "bis": "2020-04-20T00:00:00+00:00",
                                                        "entity": {
                                                            "id": "DE987654321098765432109865432109",
                                                            "boModel": {
                                                                "boTyp": "MESSLOKATION",
                                                                "versionStruktur": "1",
                                                                "messlokationsId": "DE987654321098765432109865432109",
                                                                "sparte": "GAS",
                                                                "netzebeneMessung": "MD",
                                                                "messadresse": {
                                                                    "postleitzahl": "82031",
                                                                    "ort": "Grünwald",
                                                                    "strasse": "Nördliche Münchner Straße",
                                                                    "hausnummer": "27A",
                                                                    "landescode": "DE",
                                                                },
                                                                "bilanzierungsmethode": "RLM",
                                                                "abrechnungmessstellenbetriebnna": True,
                                                                "gasqualitaet": "L_GAS",
                                                                "verlustfaktor": 1.1,
                                                            },
                                                        },
                                                        "start": "2020-04-01T00:00:00Z",
                                                    }
                                                ],
                                            },
                                            "start": "2020-04-01T00:00:00Z",
                                        }
                                    ],
                                },
                                "start": "2020-04-01T00:00:00Z",
                            }
                        ],
                    },
                },
            )

            # act
            melo = await client.get_messlokation(messlokation_id)

            # assert
            assert melo is not None
            assert any(melo)
            assert melo.id == messlokation_id
            assert not melo.id.startswith("Messlokation-")
