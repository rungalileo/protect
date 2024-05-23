from typing import Callable
from uuid import uuid4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.core.project import ProjectType

from galileo_protect.project import create_project


def test_create_project(set_validated_config: Callable, mock_request: Callable) -> None:
    config = set_validated_config()
    project_name = "foo-bar"
    project_id = uuid4()
    matcher_get = mock_request(RequestMethod.GET, CoreRoutes.projects + f"?project_name={project_name}", json=[])
    matcher_post = mock_request(
        RequestMethod.POST,
        CoreRoutes.projects,
        json={"id": str(project_id), "type": ProjectType.protect, "name": project_name},
    )
    create_project(name=project_name, config=config)
    assert matcher_get.called
    assert matcher_post.called
    # Verify that the project ID was set in the config.
    assert config.project_id is not None
    assert config.project_id == project_id
