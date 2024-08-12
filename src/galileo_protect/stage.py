from typing import Dict, Optional, Sequence

from pydantic import UUID4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.helpers.project import get_project_from_name
from galileo_core.schemas.protect.ruleset import Ruleset, RulesetsMixin
from galileo_core.schemas.protect.stage import StageType, StageWithRulesets
from galileo_core.utils.name import ts_name
from galileo_protect.constants.routes import Routes
from galileo_protect.schemas.config import Config
from galileo_protect.schemas.stage import StageResponse


def create_stage(
    project_id: Optional[UUID4] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    pause: bool = False,
    type: StageType = StageType.local,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
) -> StageResponse:
    """
    Create a stage.

    Parameters
    ----------
    project_id : Optional[UUID4], optional
        Project ID, by default we will try to get it from the config.
    name : Optional[str], optional
        Stage name, by default created with a timestamp.
    description : Optional[str], optional
        Stage description, by default None.
    pause : bool, optional
        Pause the stage, by default False, i.e. the stage is not paused.
    type : StageType, optional
        Stage type, by default StageType.local.
    prioritized_rulesets : Optional[Sequence[Ruleset]], optional
        Prioritized rulesets, by default None.

    Returns
    -------
    StageResponse
        Stage creation response.

    Raises
    ------
    ValueError
        If the project ID is not provided or found.
    """
    config = Config.get()
    project_id = project_id or config.project_id
    prioritized_rulesets = prioritized_rulesets or list()
    if project_id is None:
        raise ValueError("Project ID must be provided to create a stage.")
    name = name or ts_name("stage")
    stage = StageResponse.model_validate(
        config.api_client.request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=StageWithRulesets.model_validate(
                dict(
                    name=name,
                    project_id=project_id,
                    description=description,
                    paused=pause,
                    type=type,
                    prioritized_rulesets=prioritized_rulesets,
                )
            ).model_dump(mode="json"),
        )
    )
    config.project_id = project_id
    config.stage_id = stage.id
    config.stage_name = stage.name
    config.stage_version = stage.version
    config.write()
    return stage


def get_stage(
    project_id: Optional[UUID4] = None,
    project_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
) -> StageResponse:
    """
    Get a stage by ID or name.

    Parameters
    ----------
    project_id : Optional[UUID4], optional
        Project ID, by default, we will try to get it from the config.
    project_name : Optional[str], optional
        Project name, by default we will try to get it from the server if the project
        ID is not provided.
    stage_id : Optional[UUID4], optional
        Stage ID, by default we will try to get it from the config.
    stage_name : Optional[str], optional
        Stage name, by default we will try to get it from the config.

    Returns
    -------
    StageResponse
        The stage response.

    Raises
    ------
    ValueError
        If the project ID is not provided or found.
    ValueError
        If the stage ID or name is not provided.
    """
    config = Config.get()
    project_id = project_id or config.project_id
    stage_id = stage_id or config.stage_id
    stage_name = stage_name or config.stage_name
    if project_id is None:
        if project_name:
            project = get_project_from_name(project_name=project_name, raise_if_missing=True)
            assert project is not None, "Project should not be None."
            project_id = project.id
        else:
            raise ValueError("Project ID or name must be provided to get a stage.")
    params: Dict[str, str] = dict()
    if stage_id:
        params["stage_id"] = str(stage_id)
    if stage_name:
        params["stage_name"] = stage_name
    if not params:
        raise ValueError("Stage ID or name must be provided to get a stage.")
    stage = StageResponse.model_validate(
        config.api_client.request(RequestMethod.GET, Routes.stages.format(project_id=project_id), params=params)
    )
    config.project_id = project_id
    config.stage_id = stage.id
    config.stage_name = stage.name
    config.write()
    return stage


def update_stage(
    project_id: Optional[UUID4] = None,
    project_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
) -> StageResponse:
    """
    Update a stage by ID or name to create a new version.

    Only applicable for central stages. This will create a new version of the stage
    with the provided rulesets.

    Parameters
    ----------
    project_id : Optional[UUID4], optional
        Project ID, by default we will try to get it from the config.
    project_name : Optional[str], optional
        Project name, by default we will try to get it from the server if the project
        ID is not provided.
    stage_id : Optional[UUID4], optional
        Stage ID, by default we will try to get it from the config.
    stage_name : Optional[str], optional
        Stage name, by default we will try to get it from the config.
    prioritized_rulesets : Optional[Sequence[Ruleset]], optional
        Prioritized rulesets, by default None.

    Returns
    -------
    StageResponse
        The updated stage response.

    Raises
    ------
    ValueError
        If the project ID is not provided or found.
    ValueError
        If the stage ID is not provided or found.
    """
    config = Config.get()
    project_id = project_id or config.project_id
    stage_id = stage_id or config.stage_id
    stage_name = stage_name or config.stage_name
    if project_id is None or stage_id is None:
        got_stage = get_stage(
            project_id=project_id, project_name=project_name, stage_id=stage_id, stage_name=stage_name
        )
        project_id = got_stage.project_id
        stage_id = got_stage.id
    prioritized_rulesets = prioritized_rulesets or list()
    stage = StageResponse.model_validate(
        config.api_client.request(
            RequestMethod.POST,
            Routes.stage.format(project_id=project_id, stage_id=stage_id),
            json=RulesetsMixin.model_validate(dict(prioritized_rulesets=prioritized_rulesets)).model_dump(mode="json"),
        )
    )
    config.project_id = project_id
    config.stage_id = stage.id
    config.stage_name = stage.name
    config.stage_version = stage.version
    config.write()
    return stage


def pause_stage(project_id: Optional[UUID4] = None, stage_id: Optional[UUID4] = None) -> None:
    """
    Pause a stage.

    If the stage is already paused, the rulesets in the stage will not be evaluated.

    Parameters
    ----------
    project_id : Optional[UUID4], optional
        Project ID, by default None and will be taken from the config.
    stage_id : Optional[UUID4], optional
        Stage ID, by default None and will be taken from the config.

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
    config = Config.get()
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


def resume_stage(project_id: Optional[UUID4] = None, stage_id: Optional[UUID4] = None) -> None:
    config = Config.get()
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
