from typing import Callable
from uuid import uuid4

from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.core.project import DEFAULT_PROJECT_NAME, ProjectType
from requests_mock import POST

from galileo_protect.project import create_project


def test_create_project(set_validated_config: Callable, mock_request: Callable) -> None:
    config = set_validated_config()
    project_id = uuid4()
    matcher = mock_request(
        POST,
        CoreRoutes.projects,
        json={"id": str(project_id), "type": ProjectType.protect, "name": DEFAULT_PROJECT_NAME},
    )
    create_project(config=config)
    assert matcher.called
    # Verify that the project ID was set in the config.
    assert config.project_id is not None
    assert config.project_id == project_id
