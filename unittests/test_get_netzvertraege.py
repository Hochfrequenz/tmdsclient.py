import json
import uuid
from pathlib import Path

from aioresponses import aioresponses

from tmdsclient.models.netzvertrag import Bo4eVertrag, Netzvertrag, Vertragsstatus


class TestGetNetzvertraege:
    """
    A class with pytest unit tests.
    """

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

    def test_netzvertrag_can_be_instantiated_using_field_names(self):
        dummy_bo4e_vertrag = Bo4eVertrag.construct()
        nv = Netzvertrag(bo_model=dummy_bo4e_vertrag, id=uuid.uuid4())
        assert nv.bo_model is not None

    def test_netzvertrag_can_be_instantiated_using_alias(self):
        dummy_bo4e_vertrag = Bo4eVertrag.construct()
        nv = Netzvertrag(boModel=dummy_bo4e_vertrag, id=uuid.uuid4())
        assert nv.bo_model is not None
