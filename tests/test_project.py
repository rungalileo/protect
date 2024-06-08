from typing import Callable
from uuid import uuid4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.core.project import ProjectType

from galileo_protect.project import create_project, get_projects
from tests.data import A_PROJECT_NAME


def test_create_project(set_validated_config: Callable, mock_request: Callable) -> None:
    config = set_validated_config()
    project_id = uuid4()
    matcher_get = mock_request(
        RequestMethod.GET, CoreRoutes.projects, params=dict(project_name=A_PROJECT_NAME), json=[]
    )
    matcher_post = mock_request(
        RequestMethod.POST,
        CoreRoutes.projects,
        json={"id": str(project_id), "type": ProjectType.protect, "name": A_PROJECT_NAME},
    )
    create_project(name=A_PROJECT_NAME, config=config)
    assert matcher_get.called
    assert matcher_post.called
    # Verify that the project ID was set in the config.
    assert config.project_id is not None
    assert config.project_id == project_id


def test_get_projects(set_validated_config: Callable, mock_request: Callable) -> None:
    config = set_validated_config()
    project_id = uuid4()
    matcher_get = mock_request(
        RequestMethod.GET,
        CoreRoutes.projects,
        json=[{"id": str(project_id), "type": ProjectType.protect, "name": A_PROJECT_NAME}],
    )

    projects = get_projects(config=config)
    assert matcher_get.called
    assert len(projects) == 1
    assert projects[0].id == project_id
