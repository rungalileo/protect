from typing import Callable, Optional
from uuid import uuid4

from pytest import mark, raises
from requests_mock import POST

from galileo_protect.constants.routes import Routes
from galileo_protect.schemas import Action, PassthroughAction
from galileo_protect.schemas.stage import StageResponse
from galileo_protect.stage import create_stage


class TestCreate:
    @mark.parametrize(
        ["name", "description", "action", "action_enabled"],
        [
            ("stage", "description", None, False),
            ("stage", "description", None, False),
            ("stage", "description", PassthroughAction(), False),
            ("stage", "description", PassthroughAction(), True),
        ],
    )
    def test_simple(
        self,
        set_validated_config: Callable,
        mock_request: Callable,
        name: str,
        description: str,
        action: Optional[Action],
        action_enabled: bool,
    ) -> None:
        config = set_validated_config()
        project_id, stage_id = uuid4(), uuid4()
        response = StageResponse(
            id=stage_id,
            name=name,
            project_id=project_id,
            description=description,
            action=action,
            action_enabled=action_enabled,
        )
        matcher = mock_request(
            POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            project_id=project_id,
            name=name,
            description=description,
            action=action,
            action_elabed=action_enabled,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == "stage"

    @mark.parametrize(
        ["name", "description", "action", "action_enabled"],
        [
            ("stage", "description", None, False),
            ("stage", "description", None, False),
            ("stage", "description", PassthroughAction(), False),
            ("stage", "description", PassthroughAction(), True),
        ],
    )
    def test_project_id_from_config(
        self,
        set_validated_config: Callable,
        mock_request: Callable,
        name: str,
        description: str,
        action: Optional[Action],
        action_enabled: bool,
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(project_id=project_id)
        response = StageResponse(
            id=stage_id,
            name=name,
            project_id=project_id,
            description=description,
            action=action,
            action_enabled=action_enabled,
        )
        matcher = mock_request(
            POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            name=name,
            description=description,
            action=action,
            action_elabed=action_enabled,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == "stage"

    @mark.parametrize(
        ["name", "description", "action", "action_enabled"],
        [
            ("stage", "description", None, False),
            ("stage", "description", None, False),
            ("stage", "description", PassthroughAction(), False),
            ("stage", "description", PassthroughAction(), True),
        ],
    )
    def test_raises_missing_project_id(
        self,
        set_validated_config: Callable,
        name: str,
        description: str,
        action: Optional[Action],
        action_enabled: bool,
    ) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            create_stage(config=config)
        assert str(exc_info.value) == "Project ID must be provided to create a stage."