"""contains the actual client"""

import asyncio
import logging
import uuid
from abc import ABC
from datetime import datetime, timedelta
from typing import AsyncGenerator, Callable, Literal, Optional, overload

from aiohttp import BasicAuth, ClientResponseError, ClientSession, ClientTimeout
from more_itertools import chunked
from yarl import URL

from tmdsclient.client.config import BasicAuthTmdsConfig, OAuthTmdsConfig, TmdsConfig
from tmdsclient.client.oauth import _OAuthHttpClient, token_is_valid
from tmdsclient.models import AllIdsResponse
from tmdsclient.models.messlokation import Messlokation
from tmdsclient.models.netzvertrag import Netzvertrag, _ListOfNetzvertraege
from tmdsclient.models.patches import build_json_patch_document
from tmdsclient.models.zaehler import Zaehler

_logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 100


def _log_chunk_success(chunk_size: int, total_size: int, chunk_idx: int, chunk_length: int) -> None:
    _logger.info(
        "Downloaded Netzvertrag (%i/%i) / chunk %i/%i",
        chunk_size * chunk_idx + chunk_length,
        total_size,
        chunk_idx + 1,
        total_size // chunk_size + 1,
    )


_retry_worthy_http_status_codes = {500, 502}
"""
if a GET request fails with one of these status codes, it might be worth retrying and the error code might simply be
due to high load
"""


class TmdsClient(ABC):
    """
    an async wrapper around the TMDS API
    """

    def __init__(self, config: TmdsConfig):
        self._config = config
        self._session_lock = asyncio.Lock()
        self._session: Optional[ClientSession] = None
        _logger.info("Instantiated TmdsClient with server_url %s", str(self._config.server_url))

    def get_top_level_domain(self) -> URL | None:
        """
        Returns the top level domain of the server_url; this is useful to differentiate prod from test systems.
        If the server_url is an IP address, None is returned.
        """
        # this method is unit tested; check the testcases to understand its branches
        domain_parts = self._config.server_url.host.split(".")  # type:ignore[union-attr]
        if all(x.isnumeric() for x in domain_parts):
            # seems like this is an IP address
            return None
        if not any(domain_parts):
            return self._config.server_url
        tld: str
        if domain_parts[-1] == "localhost":
            tld = ".".join(domain_parts[-1:])
        else:
            tld = ".".join(domain_parts[-2:])
        return URL(self._config.server_url.scheme + "://" + tld)

    async def _get_session(self) -> ClientSession:
        raise NotImplementedError("The inheriting class has to implement this with its respective authentication")

    async def close_session(self) -> None:
        """
        closes the client session
        """
        async with self._session_lock:
            if self._session is not None and not self._session.closed:
                _logger.info("Closing aiohttp session")
                await self._session.close()
                self._session = None

    async def _poll_until_has_been_handled(
        self, tmds_event_id: uuid.UUID, timeout: timedelta = timedelta(seconds=30)
    ) -> bool:
        """
        Polls the /hasBeenHandledEndpoint once per second until the event has been handled
        Returns true if the event has been handled, false if the timeout has been reached.
        """
        url = self._config.server_url / "api/Event" / "hasBeenHandled" / str(tmds_event_id)
        session = await self._get_session()
        timeout_in_seconds: int = int(timeout.total_seconds())
        seconds_left = timeout_in_seconds
        while seconds_left > 0:
            async with session.get(url, ssl=True) as response:
                body = await response.text()
                if body.lower() in {'"true"', "true"}:
                    _logger.debug("Event %s has been handled", tmds_event_id)
                    return True

                _logger.log(5, "Event %s has not been handled yet. Waiting another second", tmds_event_id)
                await asyncio.sleep(1)
                seconds_left -= 1
        _logger.warning("Event %s has not been handled after %s seconds", tmds_event_id, timeout_in_seconds)
        await asyncio.sleep(60)  # slow down. slow down, at least in this thread
        return False

    async def get_netzvertraege_for_melo(self, melo_id: str) -> list[Netzvertrag]:
        """
        provide a melo id, e.g. 'DE1234567890123456789012345678901' and get the corresponding netzvertrag
        """
        if not melo_id:
            raise ValueError("You must not provide an empty melo_id")
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Netzvertrag" / "find" % {"messlokation": melo_id}
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()  # endpoint returns an empty list but no 404
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            _list_of_netzvertraege = _ListOfNetzvertraege.model_validate(response_json)
        return _list_of_netzvertraege.root

    async def get_netzvertrag_by_id(self, nv_id: uuid.UUID) -> Netzvertrag | None:
        """
        provide a UUID, get the matching netzvertrag in return (or None, if 404)
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Netzvertrag" / str(nv_id)
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            try:
                if response.status == 404:
                    return None
                response.raise_for_status()
            finally:
                _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            result = Netzvertrag.model_validate(response_json)
        return result

    async def set_plattformfaehigkeit(
        self, external_ao_id: str, change_date: datetime, is_plattformfaehig: bool = True
    ) -> bool:
        """
        set the plattformfaehigkeit of an Anschlussobjekt; return true on success, false or raises exception on failure
        """
        if change_date.tzinfo is None:
            raise ValueError("change_date must be timezone aware")
        url = (
            self._config.server_url
            / "api"
            / "Anschlussobjekt"
            / external_ao_id
            / "setPlattform"
            % {"aenderungsdatum": change_date.isoformat(), "plattformfaehig": str(is_plattformfaehig).lower()}
        )
        session = await self._get_session()
        async with session.post(url, ssl=True) as response:
            # the beloved tmds api does not consistently return an event id
            id_string = response.headers.get("x-event-id")
        if id_string is None:
            return True
        tmds_event_id = uuid.UUID(id_string)
        return await self._poll_until_has_been_handled(tmds_event_id)

    async def get_all_netzvertrag_ids(self) -> list[uuid.UUID]:
        """
        get all IDs of netzverträge that exist on server side
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Netzvertrag" / "allIds"
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            response.raise_for_status()
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            all_ids_response = AllIdsResponse.model_validate(response_json)
        result = [uuid.UUID(x.interne_id) for x in all_ids_response.root["Netzvertrag"]]
        _logger.info("There are %i Netzvertraege on server side", len(result))
        return result

    def _get_all_netzvertraege_stream(
        self, all_ids: list[uuid.UUID], chunk_size: int
    ) -> AsyncGenerator[Netzvertrag, None]:
        """
        download all netzverträge from TMDS
        """

        async def generator() -> AsyncGenerator[Netzvertrag, None]:
            successfully_downloaded = 0
            for chunk_index, id_chunk in enumerate(chunked(all_ids, chunk_size)):
                get_tasks = [self.get_netzvertrag_by_id(nv_id) for nv_id in id_chunk]
                try:
                    _result_chunk = await asyncio.gather(*get_tasks)
                    for nv in _result_chunk:
                        yield nv  # type:ignore[misc]
                        # this must not be None, because we know the ID exists on server side
                    successfully_downloaded += len(_result_chunk)
                    _log_chunk_success(
                        chunk_size=chunk_size,
                        total_size=len(all_ids),
                        chunk_idx=chunk_index,
                        chunk_length=len(_result_chunk),
                    )
                except (asyncio.TimeoutError, ClientResponseError) as chunk_error:
                    if (
                        isinstance(chunk_error, ClientResponseError)
                        and chunk_error.status not in _retry_worthy_http_status_codes
                    ):
                        raise
                    _logger.warning(
                        "Failed to download chunk %i; Retrying one by one; %s", chunk_index, str(chunk_error)
                    )
                    for _nv_id in id_chunk:
                        # This is a bit dumb; If we had aiostream here, we could create multiple requests at once
                        # and yield from a merged stream. This might be a future improvement... For now it's ok.
                        # With a moderate sized chunk_size it should be fine as there are not that many 500 errors.
                        success_in_this_chunk = 0
                        try:
                            yield await self.get_netzvertrag_by_id(_nv_id)  # type:ignore[misc]
                            # it should not be none here, because we know the ID exists, that would be a server error
                            successfully_downloaded += 1
                            success_in_this_chunk += 1
                        except (asyncio.TimeoutError, ClientResponseError) as single_error:
                            if (
                                isinstance(single_error, ClientResponseError)
                                and single_error.status not in _retry_worthy_http_status_codes
                            ):
                                raise
                            _logger.exception("Failed to download Netzvertrag %s; skipping", _nv_id)
                            continue
                        _log_chunk_success(
                            chunk_size=chunk_size,
                            total_size=len(all_ids),
                            chunk_idx=chunk_index,
                            chunk_length=success_in_this_chunk,
                        )
            _logger.info("Successfully downloaded %i Netzvertraege", successfully_downloaded)

        return generator()
        # This needs to be called to return an AsyncGenerator

    async def _get_all_netzvertraege_list(self, all_ids: list[uuid.UUID], chunk_size: int) -> list[Netzvertrag]:
        result: list[Netzvertrag] = []
        for chunk_index, id_chunk in enumerate(chunked(all_ids, chunk_size)):
            # we probably need to account for the fact that this leads to HTTP 500 errors, let's see
            get_tasks = [self.get_netzvertrag_by_id(nv_id) for nv_id in id_chunk]
            try:
                result_chunk = await asyncio.gather(*get_tasks)
            except ClientResponseError as chunk_client_error:
                if chunk_client_error.status not in _retry_worthy_http_status_codes:
                    raise
                _logger.warning(
                    "Failed to download chunk %i (%s); Retrying 1 by 1", chunk_index, str(chunk_client_error)
                )
                result_chunk = []
                for nv_id in id_chunk:
                    try:
                        nv = await self.get_netzvertrag_by_id(nv_id)
                    except ClientResponseError as single_client_error:
                        if single_client_error.status not in _retry_worthy_http_status_codes:
                            raise
                        _logger.exception("Failed to download Netzvertrag %s; skipping", nv_id)
                        continue
                    assert nv is not None
                    result_chunk.append(nv)
            if any(x is None for x in result_chunk):
                raise ValueError("This must not happen.")
            _log_chunk_success(
                chunk_size=chunk_size, chunk_idx=chunk_index, total_size=len(all_ids), chunk_length=len(result_chunk)
            )
            result.extend(result_chunk)  # type:ignore[arg-type]
        _logger.info("Successfully downloaded %i Netzvertraege", len(result))
        return result

    @overload
    async def get_all_netzvertraege(
        self, as_generator: Literal[False], chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> list[Netzvertrag]: ...

    @overload
    async def get_all_netzvertraege(
        self, as_generator: Literal[True], chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> AsyncGenerator[Netzvertrag, None]: ...

    async def get_all_netzvertraege(
        self, as_generator: bool, chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> list[Netzvertrag] | AsyncGenerator[Netzvertrag, None]:
        """
        download all netzverträge from TMDS
        """
        all_ids = await self.get_all_netzvertrag_ids()

        if as_generator:
            return self._get_all_netzvertraege_stream(all_ids, chunk_size)
        return await self._get_all_netzvertraege_list(all_ids, chunk_size)

    async def update_netzvertrag(
        self, netzvertrag_id: uuid.UUID, changes: list[Callable[[Netzvertrag], None]]
    ) -> Netzvertrag:
        """
        patch the given netzvertrag using the changes
        """
        session = await self._get_session()
        netzvertrag = await self.get_netzvertrag_by_id(netzvertrag_id)
        if netzvertrag is None:
            raise ValueError(f"Netzvertrag with id {netzvertrag_id} not found")
        patch_document = build_json_patch_document(netzvertrag, changes)
        request_url = self._config.server_url / "api" / "v2" / "Netzvertrag" / str(netzvertrag_id)
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] patching %s with body %s", str(request_uuid), request_url, str(patch_document))
        async with session.patch(
            request_url, json=patch_document.patch, headers={"Content-Type": "application/json-patch+json"}
        ) as response:
            response.raise_for_status()
            _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            result = Netzvertrag.model_validate(response_json)
        return result

    async def get_messlokation(self, messlokation_id: str) -> Messlokation | None:
        """
        provide a Messlokation-ID, get the matching MeLo in return (or None, if 404)
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Messlokation" / messlokation_id
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            try:
                if response.status == 404:
                    return None
                response.raise_for_status()
            finally:
                _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            result = Messlokation.model_validate(response_json)
        return result

    async def get_zaehler(self, zaehler_id: uuid.UUID) -> Zaehler | None:
        """
        provide a Zaehler-ID, get the matching Zaehler in return (or None, if 404)
        """
        session = await self._get_session()
        request_url = self._config.server_url / "api" / "Zaehler" / str(zaehler_id)
        request_uuid = uuid.uuid4()
        _logger.debug("[%s] requesting %s", str(request_uuid), request_url)
        async with session.get(request_url) as response:
            try:
                if response.status == 404:
                    return None
                response.raise_for_status()
            finally:
                _logger.debug("[%s] response status: %s", str(request_uuid), response.status)
            response_json = await response.json()
            result = Zaehler.model_validate(response_json)
        return result

    async def set_schmutzwasser_relevanz(self, zaehler_id: uuid.UUID, is_waste_water_relevant: bool) -> bool:
        """
        Set the waste water relevancy of a Zaehler.
        Returns true if the operation was successful.
        """
        url = (
            self._config.server_url
            / "api"
            / "v2"
            / "Zaehler"
            / f"Zaehler-{zaehler_id}"
            / "schmutzwasserRelevanz"
            % {"istRelevant": str(is_waste_water_relevant).lower()}
        )
        _logger.info(
            "Changing Schmutzwasserrelevanz of zaehler %s to %s", str(zaehler_id), str(is_waste_water_relevant)
        )
        session = await self._get_session()
        async with session.post(url, ssl=True) as response:
            response.raise_for_status()
            updated_zaehler = Zaehler.model_validate_json(await response.json())
            return updated_zaehler.is_schmutzwasser_relevant == is_waste_water_relevant


class BasicAuthTmdsClient(TmdsClient):
    """TMDS client with basic auth"""

    def __init__(self, config: BasicAuthTmdsConfig):
        """instantiate by providing a valid config"""
        if not isinstance(config, BasicAuthTmdsConfig):
            raise ValueError("You must provide a valid config")
        super().__init__(config)
        self._auth = BasicAuth(login=config.usr, password=config.pwd)

    async def _get_session(self) -> ClientSession:
        """
        returns a client session (that may be reused or newly created)
        re-using the same (threadsafe) session will be faster than re-creating a new session for every request.
        see https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#how-to-use-the-clientsession
        """
        async with self._session_lock:
            if self._session is None or self._session.closed:
                _logger.info("creating new session")
                self._session = ClientSession(
                    auth=self._auth,
                    timeout=ClientTimeout(60),
                    raise_for_status=True,
                )
            else:
                _logger.log(5, "reusing aiohttp session")  # log level 5 is half as "loud" logging.DEBUG
            return self._session


class OAuthTmdsClient(TmdsClient, _OAuthHttpClient):
    """TMDS client with OAuth"""

    def __init__(self, config: OAuthTmdsConfig):
        if not isinstance(config, OAuthTmdsConfig):
            raise ValueError("You must provide a valid config")
        super().__init__(config)
        _OAuthHttpClient.__init__(
            self,
            base_url=config.server_url,
            oauth_client_id=config.client_id,
            oauth_client_secret=config.client_secret,
            oauth_token_url=str(config.token_url),
        )
        self._oauth_config = config
        self._bearer_token: str | None = config.bearer_token if config.bearer_token else None

    async def _get_session(self) -> ClientSession:
        """
        returns a client session (that may be reused or newly created)
        re-using the same (threadsafe) session will be faster than re-creating a new session for every request.
        see https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#how-to-use-the-clientsession
        """
        async with self._session_lock:
            if self._bearer_token is None:
                self._bearer_token = await self._get_oauth_token()
            elif not token_is_valid(self._bearer_token):
                await self.close_session()
            if self._session is None or self._session.closed:
                _logger.info("creating new session")
                self._session = ClientSession(
                    timeout=ClientTimeout(60),
                    raise_for_status=True,
                    headers={"Authorization": f"Bearer {self._bearer_token}"},
                )
            else:
                _logger.log(5, "reusing aiohttp session")  # log level 5 is half as "loud" logging.DEBUG
            return self._session


__all__ = ["TmdsClient", "OAuthTmdsClient", "BasicAuthTmdsClient"]
