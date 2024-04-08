from typing import Optional

from galileo_core.utils.name import ts_name
from pydantic import UUID4
from requests import post

from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.schemas import Action, Stage
from galileo_protect.schemas.stage import StageResponse


def create_stage(
    project_id: Optional[UUID4] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    action: Optional[Action] = None,
    action_elabed: bool = False,
    config: Optional[ProtectConfig] = None,
) -> StageResponse:
    config = config or ProtectConfig.get()
    project_id = project_id or config.project_id
    if project_id is None:
        raise ValueError("Project ID must be provided to create a stage.")
    name = name or ts_name("stage")
    stage = StageResponse.model_validate(
        config.api_client.request(
            post,
            Routes.stages.format(project_id=project_id),
            json=Stage(
                name=name, project_id=project_id, description=description, action=action, action_enabled=action_elabed
            ).model_dump(mode="json"),
        )
    )
    config.project_id = project_id
    config.stage_id = stage.id
    config.stage_name = stage.name
    config.write()
    return stage
