import json
import uuid
from pathlib import Path

from aioresponses import CallbackResult, aioresponses
from jsonpatch import JsonPatch  # type:ignore[import]

from tmdsclient.models.netzvertrag import Bo4eVertrag, Netzvertrag, Vertragsstatus


class TestGetNetzvertraege:
    """
    A class with pytest unit tests.
    """

    async def test_get_netzvertrag_by_id(self, tmds_client_with_default_auth):
        netzvertrag_json_file = Path(__file__).parent / "example_data" / "single_netzvertrag.json"
        with open(netzvertrag_json_file, "r", encoding="utf-8") as infile:
            netzvertrag_json = json.load(infile)
        nv_id = uuid.UUID("3e15bf73-ea1b-4f50-8f18-3288074a4fec")
        client, tmds_config = tmds_client_with_default_auth
        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/{nv_id}"
            mocked_tmds.get(mocked_get_url, status=200, payload=netzvertrag_json)
            actual = await client.get_netzvertrag_by_id(nv_id)
        assert isinstance(actual, Netzvertrag)

    async def test_get_netzvertraege_by_melo(self, tmds_client_with_default_auth):
        netzvertraege_json_file = Path(__file__).parent / "example_data" / "list_of_netzvertraege.json"
        with open(netzvertraege_json_file, "r", encoding="utf-8") as infile:
            netzvertraege_json = json.load(infile)
        melo_id = "DE0011122233344455566677788899900"
        client, tmds_config = tmds_client_with_default_auth
        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/find?messlokation={melo_id}"
            mocked_tmds.get(mocked_get_url, status=200, payload=netzvertraege_json)
            actual = await client.get_netzvertraege_for_melo(melo_id)
        assert isinstance(actual, list)
        assert all(isinstance(x, Netzvertrag) for x in actual)
        assert actual[0].bo_model.vertragsbeginn is not None
        assert isinstance(actual[0].bo_model.vertragstatus, Vertragsstatus)
        assert any(actual[0].model_extra), "Unmapped properties should be stored in model_extra (Netzvertrag)"
        assert any(actual[0].bo_model.model_extra), "Unmapped properties should be stored in model_extra (Bo4eVertrag)"

    async def test_update_netzvertrag(self, tmds_client_with_default_auth):
        netzvertrag_json_file = Path(__file__).parent / "example_data" / "single_netzvertrag.json"
        with open(netzvertrag_json_file, "r", encoding="utf-8") as infile:
            netzvertrag_json = json.load(infile)

        nv_id = uuid.UUID("3e15bf73-ea1b-4f50-8f18-3288074a4fec")
        client, tmds_config = tmds_client_with_default_auth

        def set_status_to_storniert(nv: Netzvertrag) -> None:
            assert nv.bo_model is not None
            nv.bo_model.vertragstatus = Vertragsstatus.STORNIERT

        def patch_endpoint_callback(url, **kwargs):  # pylint:disable=unused-argument
            request_body = kwargs["json"]
            json_patch = JsonPatch(request_body)
            modified_netzvertrag_json = netzvertrag_json.copy()
            result = json_patch.apply(modified_netzvertrag_json)
            return CallbackResult(status=200, payload=result)

        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/{nv_id}"
            mocked_tmds.get(mocked_get_url, status=200, payload=netzvertrag_json)
            mocked_patch_url = f"{tmds_config.server_url}api/v2/Netzvertrag/{nv_id}"
            mocked_tmds.patch(mocked_patch_url, callback=patch_endpoint_callback)
            actual = await client.update_netzvertrag(nv_id, [set_status_to_storniert])
        assert isinstance(actual, Netzvertrag)
        assert actual.bo_model.vertragstatus == Vertragsstatus.STORNIERT

    def test_netzvertrag_can_be_instantiated_using_field_names(self):
        dummy_bo4e_vertrag = Bo4eVertrag.construct()
        nv = Netzvertrag(bo_model=dummy_bo4e_vertrag, id=uuid.uuid4())
        assert nv.bo_model is not None

    def test_netzvertrag_can_be_instantiated_using_alias(self):
        dummy_bo4e_vertrag = Bo4eVertrag.construct()
        nv = Netzvertrag(boModel=dummy_bo4e_vertrag, id=uuid.uuid4())
        assert nv.bo_model is not None
