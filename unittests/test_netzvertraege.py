import asyncio
import json
import logging
import uuid
from pathlib import Path

import pytest
from aiohttp import ClientResponseError
from aioresponses import CallbackResult, aioresponses
from jsonpatch import JsonPatch  # type:ignore[import]

from tmdsclient.models.netzvertrag import Bo4eVertrag, Netzvertrag, Vertragsstatus, Vertragsteil


class TestGetNetzvertraege:
    """
    A class with pytest unit tests.
    """

    async def test_get_all_netzvertrag_ids(self, tmds_client_with_default_auth):
        all_ids = [{"interneId": str(uuid.uuid4()), "externeId": "fooo"} for _ in range(123)] + [
            {"interneId": str(uuid.uuid4())} for _ in range(2)
        ]
        # the external ID is not always filled
        client, tmds_config = tmds_client_with_default_auth
        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/allIds"
            mocked_tmds.get(mocked_get_url, status=200, payload={"Netzvertrag": all_ids})
            actual = await client.get_all_netzvertrag_ids()
        assert isinstance(actual, list)
        assert all(isinstance(x, uuid.UUID) for x in actual)

    # pylint:disable=too-many-locals
    @pytest.mark.parametrize("with_http_500", [True, False])
    @pytest.mark.parametrize("as_generator", [True, False])
    async def test_get_all_netzvertraege(
        self, with_http_500: bool, as_generator: bool, tmds_client_with_default_auth, caplog
    ):
        caplog.set_level(logging.INFO)
        size = 234
        index_of_error = 123 if with_http_500 else None
        all_ids = [{"interneId": str(uuid.uuid4()), "externeId": "fooo"} for _ in range(size)]
        netzvertrag_json_file = Path(__file__).parent / "example_data" / "single_netzvertrag.json"
        with open(netzvertrag_json_file, "r", encoding="utf-8") as infile:
            netzvertrag_json = json.load(infile)
        client, tmds_config = tmds_client_with_default_auth
        result_list: list[Netzvertrag]
        with aioresponses() as mocked_tmds:
            mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/allIds"
            mocked_tmds.get(mocked_get_url, status=200, payload={"Netzvertrag": all_ids})
            for index, _id_pair in enumerate(all_ids):
                mocked_get_url = f"{tmds_config.server_url}api/Netzvertrag/{_id_pair['interneId']}"
                repeat_mock = with_http_500 and 200 > index >= 100  # because 123 is in the second size 100 chunk
                if index_of_error is not None and index == index_of_error:
                    mocked_tmds.get(mocked_get_url, status=500, payload="fatal shit", repeat=repeat_mock)
                else:
                    _netzvertrag_json = netzvertrag_json.copy()
                    _netzvertrag_json["id"] = _id_pair["interneId"]
                    mocked_tmds.get(mocked_get_url, status=200, payload=_netzvertrag_json, repeat=repeat_mock)
            actual = await client.get_all_netzvertraege(as_generator=as_generator)
            if as_generator:  # needs to happen inside aioresponses block
                result_list = []
                while True:
                    try:
                        nv = await anext(actual)
                        result_list.append(nv)
                    except StopAsyncIteration:
                        break
                    except (ClientResponseError, asyncio.TimeoutError):
                        # some error handling goes here in the calling code
                        pass
        if not as_generator:  # outside aioresponses block
            result_list = actual
        assert isinstance(result_list, list)
        assert all(isinstance(x, Netzvertrag) for x in result_list)
        expected_size = size if not with_http_500 else size - 1
        assert len(result_list) == expected_size
        assert any(m for m in caplog.messages if f"Successfully downloaded {expected_size} Netzvertraege" in str(m))

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
        assert any(actual.bo_model.vertragsteile)
        assert all(isinstance(x, Vertragsteil) for x in actual.bo_model.vertragsteile)
        assert all(x.lokation is not None for x in (vt for vt in actual.bo_model.vertragsteile))
        assert all(x.guid is not None for x in (vt for vt in actual.bo_model.vertragsteile))
        assert all(x.jahresverbrauchsprognose.wert is not None for x in (vt for vt in actual.bo_model.vertragsteile))

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
        assert actual[0].marktlokation.id == "97149628801"
        assert any(
            actual[0].marktlokation.model_extra
        ), "Unmapped properties should be stored in model_extra (Marktlokation)"

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
