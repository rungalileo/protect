from typing import Optional

from galileo_core.helpers.project import create_project as core_create_project
from galileo_core.schemas.core.project import (
    DEFAULT_PROJECT_NAME,
    CreateProjectRequest,
    ProjectResponse,
    ProjectType,
)

from galileo_protect.helpers.config import ProtectConfig


def create_project(name: str = DEFAULT_PROJECT_NAME, config: Optional[ProtectConfig] = None) -> ProjectResponse:
    config = config or ProtectConfig.get()
    project = core_create_project(CreateProjectRequest(name=name, type=ProjectType.protect), config)
    config.project_id = project.id
    config.write()
    return project
