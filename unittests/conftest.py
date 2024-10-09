from typing import AsyncGenerator

import pytest
from pydantic_core import Url
from yarl import URL

from tmdsclient import TmdsClient, TmdsConfig
from tmdsclient.client.config import BasicAuthTmdsConfig, OAuthTmdsConfig
from tmdsclient.client.tmdsclient import BasicAuthTmdsClient, OAuthTmdsClient


@pytest.fixture
async def tmds_client_with_default_auth() -> AsyncGenerator[tuple[TmdsClient, TmdsConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    tmds_config = BasicAuthTmdsConfig(
        server_url=URL("https://tmds.inv/"),
        usr="my-usr",
        pwd="my-pwd",
    )
    client = BasicAuthTmdsClient(tmds_config)
    yield client, tmds_config
    await client.close_session()


@pytest.fixture
async def tmds_client_with_oauth() -> AsyncGenerator[tuple[TmdsClient, TmdsConfig], None]:
    """
    "mention" this fixture in the signature of your test to run the code up to yield before the respective test
    (and the code after yield the test execution)
    :return:
    """
    tmds_config = OAuthTmdsConfig(
        server_url=URL("https://techmasterdata.invalid.de/"),
        client_id="my-client-id",
        client_secret="my-client-secret",
        token_url=Url("https://validate-my-token.inv"),
    )
    client = OAuthTmdsClient(tmds_config)
    yield client, tmds_config
    await client.close_session()
