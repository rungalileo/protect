from pathlib import Path
from typing import Callable, Generator, Optional
from unittest.mock import Mock, patch
from uuid import UUID

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.protect.response import Response, TraceMetadata
from pytest import MonkeyPatch, fixture

from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from tests.data import A_CONSOLE_URL, A_JWT_TOKEN, A_PROTECT_INPUT


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
def mock_healthcheck(mock_request: Mock) -> Generator[None, None, None]:
    matcher = mock_request(RequestMethod.GET, CoreRoutes.healthcheck, json={})
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


@fixture
def mock_invoke(mock_request: Mock) -> Generator[None, None, None]:
    matcher = mock_request(
        RequestMethod.POST,
        Routes.invoke,
        json=Response(text=A_PROTECT_INPUT, status="NOT_TRIGGERED", trace_metadata=TraceMetadata()).model_dump(
            mode="json"
        ),
    )
    yield matcher
    assert matcher.called
