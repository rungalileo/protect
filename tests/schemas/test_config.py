from typing import Callable
from unittest.mock import Mock
from uuid import uuid4

from pydantic import SecretStr

from galileo_protect.schemas.config import ProtectConfig
from tests.data import A_CONSOLE_URL, A_JWT_TOKEN, A_STAGE_NAME


def test_reset(mock_healthcheck: Mock, mock_get_current_user: Mock) -> None:
    ProtectConfig.get(
        console_url=A_CONSOLE_URL, jwt_token=A_JWT_TOKEN, project_id=uuid4(), stage_name=A_STAGE_NAME, stage_id=uuid4()
    )
    config = ProtectConfig.get()
    assert config.console_url.unicode_string() == A_CONSOLE_URL
    assert config.jwt_token == SecretStr(A_JWT_TOKEN)
    assert config.project_id is not None
    assert config.stage_name == A_STAGE_NAME
    assert config.stage_id is not None
    config.reset()
    assert config.project_id is None
    assert config.stage_name is None
    assert config.stage_id is None


def test_global_config(mock_healthcheck: Mock, mock_get_current_user: Mock, set_validated_config: Callable) -> None:
    set_validated_config()
    config = ProtectConfig.get()
    assert config.console_url.unicode_string() == A_CONSOLE_URL
    assert config.jwt_token == SecretStr(A_JWT_TOKEN)
    assert config.project_id is None
    assert config.stage_id is None
    assert config.stage_name is None
