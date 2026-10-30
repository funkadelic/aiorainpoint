"""Shared test utility functions for the RainPoint client tests.

``make_mock_session_client`` and ``mock_json_response`` build a real
``RainPointClient`` wired to a mocked aiohttp session, for tests that need to
assert on the exact JSON body a real client method builds rather than on a
mocked call.
"""

from unittest.mock import AsyncMock, MagicMock

from aiorainpoint import RainPointClient


def make_mock_session_client() -> RainPointClient:
    """Create a real RainPointClient with a mocked aiohttp session.

    Constructor args: area_code, email, password, session. ``_token`` is set
    directly so ``_auth_headers()`` does not raise.
    """
    mock_session = MagicMock()
    client = RainPointClient(
        area_code="1",
        email="test@example.com",
        password="testpass",
        session=mock_session,
    )
    client._token = "fake-token-for-test"
    return client


def mock_json_response(json_data: dict, status: int = 200) -> AsyncMock:
    """Create a mock aiohttp response context manager returning json_data."""
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_data)
    # aiohttp uses async context manager for session.post()
    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    return mock_cm
