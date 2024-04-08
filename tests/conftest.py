from http import HTTPStatus
from pathlib import Path
from re import Pattern
from typing import Callable, Generator, Optional, Union
from unittest.mock import Mock, patch
from uuid import UUID

from galileo_core.constants.routes import Routes
from pytest import MonkeyPatch, fixture
from requests_mock import GET
from requests_mock.adapter import _Matcher

from galileo_protect.helpers.config import ProtectConfig
from tests.data import A_CONSOLE_URL, A_JWT_TOKEN


@fixture
def tmp_home_dir(monkeypatch: MonkeyPatch, tmp_path: Path) -> Generator[Path, None, None]:
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    yield tmp_path
    monkeypatch.delenv("HOME")


@fixture(autouse=True)
def mock_decode_jwt() -> Generator[Mock, None, None]:
    with patch("galileo_core.helpers.config.jwt_decode") as _fixture:
        _fixture.return_value = dict(exp=float("inf"))
        yield _fixture


@fixture
def mock_request(requests_mock: Mock) -> Callable:
    def curry(
        method: str,
        path: Union[str, Pattern],
        status_code: int = HTTPStatus.OK,
        json: Optional[dict] = None,
        text: Optional[str] = None,
    ) -> _Matcher:
        if isinstance(path, str):
            path = "/" + path
        if not text and not json:
            json = {}
        return requests_mock.request(
            method=method,
            # Match any URL that ends with the path.
            url=path,
            text=text,
            status_code=status_code,
            json=json,
            complete_qs=True,
        )

    return curry


@fixture
def mock_healthcheck(mock_request: Mock) -> Generator[None, None, None]:
    matcher = mock_request(GET, Routes.healthcheck, json={})
    yield
    assert matcher.called


@fixture
def set_validated_config(tmp_home_dir: Path, mock_healthcheck: None) -> Callable:
    def curry(
        project_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        stage_name: Optional[str] = None,
    ) -> ProtectConfig:
        config = ProtectConfig(
            console_url=A_CONSOLE_URL,
            jwt_token=A_JWT_TOKEN,
            project_id=project_id,
            stage_id=stage_id,
            stage_name=stage_name,
        )
        config.write()
        return config

    return curry
