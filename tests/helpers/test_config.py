from unittest.mock import Mock
from uuid import uuid4

from galileo_protect.helpers.config import ProtectConfig
from tests.data import A_CONSOLE_URL, A_STAGE_NAME


def test_reset(mock_healthcheck: Mock) -> None:
    config = ProtectConfig(console_url=A_CONSOLE_URL, project_id=uuid4(), stage_name=A_STAGE_NAME, stage_id=uuid4())
    assert config.console_url.unicode_string() == A_CONSOLE_URL
    assert config.project_id is not None
    assert config.stage_name == A_STAGE_NAME
    assert config.stage_id is not None
    config.reset()
    assert config.console_url.unicode_string() == A_CONSOLE_URL
    assert config.project_id is None
    assert config.stage_name is None
    assert config.stage_id is None
