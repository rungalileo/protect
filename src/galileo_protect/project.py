from typing import List, Optional

from galileo_core.helpers.project import create_project as core_create_project
from galileo_core.helpers.project import get_project as core_get_project
from galileo_core.helpers.project import get_projects as core_get_projects
from galileo_core.schemas.core.project import (
    DEFAULT_PROJECT_NAME,
    CreateProjectRequest,
    ProjectResponse,
    ProjectType,
)
from pydantic import UUID4

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


def get_project(
    project_id: Optional[UUID4] = None,
    project_name: Optional[str] = None,
    config: Optional[ProtectConfig] = None,
    raise_if_missing: bool = True,
) -> Optional[ProjectResponse]:
    """
    Get a Protect project by either ID or name.

    If both project_id and project_name are provided, project_id will take precedence.

    Parameters
    ----------
    config : GalileoConfig
        Configuration object for the Galileo client.
    project_id : Optional[UUID4], optional
        Project ID, by default None.
    project_name : Optional[str], optional
        Project name, by default None.
    raise_if_missing : bool, optional
        Raise an error if the project is not found, by default True.

    Returns
    -------
    Optional[ProjectResponse]
        Project response object if the project is found, None otherwise.

    Raises
    ------
    ValueError
        If neither project_id nor project_name is provided.
    """
    config = config or ProtectConfig.get()
    return core_get_project(
        config=config,
        project_id=project_id,
        project_name=project_name,
        project_type=ProjectType.protect,
        raise_if_missing=raise_if_missing,
    )
