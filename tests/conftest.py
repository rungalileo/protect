from pathlib import Path
from typing import Callable, Generator, List, Optional
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from pytest import FixtureRequest, MonkeyPatch, fixture

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.core.user import User
from galileo_core.schemas.core.user_role import UserRole
from galileo_core.schemas.protect.response import Response, TraceMetadata
from galileo_core.schemas.protect.rule import Rule, RuleOperator
from galileo_core.schemas.protect.ruleset import Ruleset
from galileo_protect.constants.routes import Routes
from galileo_protect.schemas.config import Config
from tests.data import A_CONSOLE_URL, A_JWT_TOKEN, A_PROTECT_INPUT


@fixture
def tmp_home_dir(monkeypatch: MonkeyPatch, tmp_path: Path) -> Generator[Path, None, None]:
    monkeypatch.setenv("HOME", tmp_path.as_posix())
    yield tmp_path
    monkeypatch.delenv("HOME")


@fixture
def mock_get_current_user(mock_request: Mock) -> Generator[None, None, None]:
    matcher = mock_request(
        RequestMethod.GET,
        CoreRoutes.current_user,
        json=User.model_validate({"id": uuid4(), "email": "user@example.com", "role": UserRole.user}).model_dump(
            mode="json"
        ),
    )
    yield
    assert matcher.called


@fixture(autouse=True)
def mock_decode_jwt() -> Generator[Mock, None, None]:
    with patch("galileo_core.schemas.base_config.jwt_decode") as _fixture:
        _fixture.return_value = dict(exp=float("inf"))
        yield _fixture


@fixture
def mock_healthcheck(mock_request: Mock) -> Generator[None, None, None]:
    matcher = mock_request(RequestMethod.GET, CoreRoutes.healthcheck, json={})
    yield
    assert matcher.called


@fixture
def set_validated_config(tmp_home_dir: Path, mock_healthcheck: None, mock_get_current_user: Mock) -> Callable:
    def curry(
        project_id: Optional[UUID] = None,
        stage_id: Optional[UUID] = None,
        stage_name: Optional[str] = None,
    ) -> Config:
        return Config.set(
            console_url=A_CONSOLE_URL,
            jwt_token=A_JWT_TOKEN,
            project_id=project_id,
            stage_id=stage_id,
            stage_name=stage_name,
        )

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


@fixture(
    params=[
        # Single ruleset with a single rule.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            )
        ],
        # Single ruleset with multiple rules.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    ),
                    Rule(
                        metric="tone",
                        operator=RuleOperator.lt,
                        target_value=0.8,
                    ),
                ]
            ),
        ],
        # Single ruleset with an unknown metric.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="unknown",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            )
        ],
        # Multiple rulesets with a single rule each.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            ),
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.lt,
                        target_value=0.8,
                    )
                ]
            ),
        ],
    ],
)
def rulesets(request: FixtureRequest) -> List[Ruleset]:
    return request.param
