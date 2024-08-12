from typing import List, Optional

from pydantic import UUID4

from galileo_core.helpers.project import create_project as core_create_project
from galileo_core.helpers.project import get_project as core_get_project
from galileo_core.helpers.project import get_projects as core_get_projects
from galileo_core.schemas.core.project import (
    DEFAULT_PROJECT_NAME,
    CreateProjectRequest,
    ProjectResponse,
    ProjectType,
)
from galileo_protect.schemas.config import Config


def create_project(name: str = DEFAULT_PROJECT_NAME) -> ProjectResponse:
    """
    Create a new Protect project.

    Parameters
    ----------
    name : str, optional
        Name of the project, by default `project` with a timestamp.

    Returns
    -------
    ProjectResponse
        Project creation response.
    """
    config = Config.get()
    project = core_create_project(request=CreateProjectRequest(name=name, type=ProjectType.protect))
    config.project_id = project.id
    config.write()
    return project


def get_projects() -> List[ProjectResponse]:
    """
    Get all Protect projects.

    Returns
    -------
    List[ProjectResponse]
        List of Protect projects.
    """
    return core_get_projects(project_type=ProjectType.protect)


def get_project(
    project_id: Optional[UUID4] = None, project_name: Optional[str] = None, raise_if_missing: bool = True
) -> Optional[ProjectResponse]:
    """
    Get a Protect project by either ID or name.

    If both project_id and project_name are provided, project_id will take precedence.

    Parameters
    ----------
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
    return core_get_project(
        project_id=project_id,
        project_name=project_name,
        project_type=ProjectType.protect,
        raise_if_missing=raise_if_missing,
    )
