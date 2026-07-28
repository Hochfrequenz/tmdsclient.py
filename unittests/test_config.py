import pytest
from pydantic import HttpUrl, ValidationError
from yarl import URL

from tmdsclient.client.config import BasicAuthTmdsConfig, OAuthTmdsConfig, TmdsConfig


def test_validate_url_rejects_non_url_values():
    with pytest.raises(ValueError):
        TmdsConfig.validate_url("not a url instance")  # pylint:disable=no-value-for-parameter


def test_validate_url_rejects_urls_with_more_than_one_path_segment():
    with pytest.raises(ValidationError):
        TmdsConfig(server_url=URL("https://example.com/foo/bar"))


def test_basic_auth_rejects_blank_usr_or_pwd():
    with pytest.raises(ValidationError):
        BasicAuthTmdsConfig(server_url=URL("https://tmds.example.com"), usr="   ", pwd="pw")


def test_oauth_config_requires_credentials_or_bearer_token():
    with pytest.raises(ValidationError):
        OAuthTmdsConfig(
            server_url=URL("https://tmds.example.com"),
            client_id="",
            client_secret="",
            token_url=HttpUrl("https://validate-my-token.inv"),
        )


def test_oauth_config_accepts_empty_bearer_token_alongside_credentials():
    config = OAuthTmdsConfig(
        server_url=URL("https://tmds.example.com"),
        client_id="my-id",
        client_secret="my-secret",
        token_url=HttpUrl("https://validate-my-token.inv"),
        bearer_token="",
    )
    assert config.bearer_token == ""
