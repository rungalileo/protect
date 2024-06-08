from typing import List, Optional

from galileo_core.helpers.project import create_project as core_create_project
from galileo_core.helpers.project import get_projects as core_get_projects
from galileo_core.schemas.core.project import (
    DEFAULT_PROJECT_NAME,
    CreateProjectRequest,
    ProjectResponse,
    ProjectType,
)

from galileo_protect.helpers.config import ProtectConfig


def create_project(name: str = DEFAULT_PROJECT_NAME, config: Optional[ProtectConfig] = None) -> ProjectResponse:
    """
    Create a new Protect project.

    Parameters
    ----------
    name : str, optional
        Name of the project, by default `project` with a timestamp.
    config : Optional[ProtectConfig], optional
        Protect config, by default it will be taken from the env vars or the local
        config file.

    Returns
    -------
    ProjectResponse
        Project creation response.
    """
    config = config or ProtectConfig.get()
    project = core_create_project(config=config, request=CreateProjectRequest(name=name, type=ProjectType.protect))
    config.project_id = project.id
    config.write()
    return project


def get_projects(config: Optional[ProtectConfig] = None) -> List[ProjectResponse]:
    """
    Get all Protect projects.

    Parameters
    ----------
    config : Optional[ProtectConfig], optional
        Protect config, by default it will be taken from the env vars or the local
        config file.

    Returns
    -------
    List[ProjectResponse]
        List of Protect projects.
    """
    config = config or ProtectConfig.get()
    return core_get_projects(config=config, project_type=ProjectType.protect)
