from typing import Optional

from galileo_core.constants.request_method import RequestMethod
from galileo_core.utils.name import ts_name
from pydantic import UUID4

from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.schemas import Stage
from galileo_protect.schemas.stage import StageResponse


def create_stage(
    project_id: Optional[UUID4] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    pause: bool = False,
    config: Optional[ProtectConfig] = None,
) -> StageResponse:
    config = config or ProtectConfig.get()
    project_id = project_id or config.project_id
    if project_id is None:
        raise ValueError("Project ID must be provided to create a stage.")
    name = name or ts_name("stage")
    stage = StageResponse.model_validate(
        config.api_client.request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=Stage(name=name, project_id=project_id, description=description, paused=pause).model_dump(mode="json"),
        )
    )
    config.project_id = project_id
    config.stage_id = stage.id
    config.stage_name = stage.name
    config.write()
    return stage


def pause_stage(
    project_id: Optional[UUID4] = None, stage_id: Optional[UUID4] = None, config: Optional[ProtectConfig] = None
) -> None:
    """
    Pause a stage.

    If the stage is already paused, the rulesets in the stage will not be evaluated.

    Parameters
    ----------
    project_id : Optional[UUID4], optional
        Project ID, by default None and will be taken from the config.
    stage_id : Optional[UUID4], optional
        Stage ID, by default None and will be taken from the config.
    config : Optional[ProtectConfig], optional
        Protect config, by default None and will be taken from the env vars or the local
        config file.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the project ID is not provided or found.
    ValueError
        If the stage ID is not provided or found.
    """
    config = config or ProtectConfig.get()
    project_id = project_id or config.project_id
    stage_id = stage_id or config.stage_id
    if project_id is None:
        raise ValueError("Project ID must be provided to pause a stage.")
    if stage_id is None:
        raise ValueError("Stage ID must be provided to pause a stage.")
    config.api_client.request(
        RequestMethod.PUT,
        Routes.stage.format(project_id=project_id, stage_id=stage_id),
        params=dict(pause=True),
    )
    config.project_id = project_id
    config.stage_id = stage_id
    config.write()


def resume_stage(
    project_id: Optional[UUID4] = None, stage_id: Optional[UUID4] = None, config: Optional[ProtectConfig] = None
) -> None:
    config = config or ProtectConfig.get()
    project_id = project_id or config.project_id
    stage_id = stage_id or config.stage_id
    if project_id is None:
        raise ValueError("Project ID must be provided to resume a stage.")
    if stage_id is None:
        raise ValueError("Stage ID must be provided to resume a stage.")
    config.api_client.request(
        RequestMethod.PUT,
        Routes.stage.format(project_id=project_id, stage_id=stage_id),
        params=dict(pause=False),
    )
    config.project_id = project_id
    config.stage_id = stage_id
    config.write()
