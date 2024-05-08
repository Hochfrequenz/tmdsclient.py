import uuid
from datetime import datetime, timezone

from aioresponses import aioresponses
from yarl import URL


class TestTmdsAnschlussobjekt:
    async def test_anschlussobjekt_set_plattform(self, tmds_client_with_default_auth):
        client, tmds_settings = tmds_client_with_default_auth
        external_ao_id = "10024649"
        event_id = str(uuid.uuid4())
        with aioresponses() as mocked_tmds:
            # pylint:disable=line-too-long
            post_url = f"{tmds_settings.server_url}api/Anschlussobjekt/{external_ao_id}/setPlattform?plattformfaehig=true&aenderungsdatum=2000-01-01T00%253A00%253A00%252B00%253A00"
            mocked_tmds.post(
                post_url,
                status=200,
                headers={"x-event-id": event_id},
            )
            has_been_handled_url = f"{tmds_settings.server_url}api/Event/hasBeenHandled/{event_id}"
            mocked_tmds.get(has_been_handled_url, status=200, payload="true")
            actual = await client.set_plattformfaehigkeit(
                external_ao_id, is_plattformfaehig=True, change_date=datetime(2000, 1, 1, tzinfo=timezone.utc)
            )
        assert actual is True
