from typing import Callable, Union
from uuid import uuid4

from galileo_core.constants.request_method import RequestMethod
from pytest import mark, raises

from galileo_protect.constants.routes import Routes
from galileo_protect.schemas import Action, OverrideAction, PassthroughAction
from galileo_protect.schemas.stage import StageResponse
from galileo_protect.stage import create_stage, pause_stage, resume_stage


class TestCreate:
    @mark.parametrize(
        ["name", "description", "paused"],
        [
            ("stage", "description", False),
            ("stage", "description", True),
            ("stage", "description", False),
            ("stage", "description", True),
        ],
    )
    def test_simple(
        self,
        set_validated_config: Callable,
        mock_request: Callable,
        name: str,
        description: str,
        paused: bool,
    ) -> None:
        config = set_validated_config()
        project_id, stage_id = uuid4(), uuid4()
        response = StageResponse(
            id=stage_id,
            name=name,
            project_id=project_id,
            description=description,
            paused=paused,
        )
        matcher = mock_request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            project_id=project_id,
            name=name,
            description=description,
            pause=paused,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == "stage"

    @mark.parametrize(
        ["name", "description", "paused"],
        [
            ("stage", "description", False),
            ("stage", "description", True),
            ("stage", "description", False),
            ("stage", "description", True),
        ],
    )
    def test_project_id_from_config(
        self, set_validated_config: Callable, mock_request: Callable, name: str, description: str, paused: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(project_id=project_id)
        response = StageResponse(
            id=stage_id,
            name=name,
            project_id=project_id,
            description=description,
            paused=paused,
        )
        matcher = mock_request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            name=name,
            description=description,
            pause=paused,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == "stage"

    @mark.parametrize(
        ["name", "description", "action", "pause"],
        [
            ("stage", "description", OverrideAction(choices=["foo"]), False),
            ("stage", "description", OverrideAction(choices=["foo"]), True),
            ("stage", "description", PassthroughAction(), False),
            ("stage", "description", PassthroughAction(), True),
        ],
    )
    def test_raises_missing_project_id(
        self,
        set_validated_config: Callable,
        name: str,
        description: str,
        action: Action,
        pause: bool,
    ) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            create_stage(config=config)
        assert str(exc_info.value) == "Project ID must be provided to create a stage."


class TestPause:
    @mark.parametrize("pause", ["true", True])
    def test_params(self, set_validated_config: Callable, mock_request: Callable, pause: Union[str, bool]) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config()
        matcher = mock_request(
            RequestMethod.PUT,
            Routes.stage.format(project_id=project_id, stage_id=stage_id),
            params={"pause": pause},
        )
        pause_stage(project_id=project_id, stage_id=stage_id, config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id

    @mark.parametrize("pause", ["true", True])
    def test_project_id_from_config(
        self, set_validated_config: Callable, mock_request: Callable, pause: Union[str, bool]
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(project_id=project_id, stage_id=stage_id)
        matcher = mock_request(
            RequestMethod.PUT,
            Routes.stage.format(project_id=project_id, stage_id=stage_id),
            params={"pause": pause},
        )
        pause_stage(config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id

    def test_raises_missing_project_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            pause_stage(config=config)
        assert str(exc_info.value) == "Project ID must be provided to pause a stage."

    def test_raises_missing_stage_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            pause_stage(project_id=uuid4(), config=config)
        assert str(exc_info.value) == "Stage ID must be provided to pause a stage."


class TestResume:
    @mark.parametrize("pause", ["false", False])
    def test_params(self, set_validated_config: Callable, mock_request: Callable, pause: Union[str, bool]) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config()
        matcher = mock_request(
            RequestMethod.PUT,
            Routes.stage.format(project_id=project_id, stage_id=stage_id),
            params={"pause": pause},
        )
        resume_stage(project_id=project_id, stage_id=stage_id, config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id

    @mark.parametrize("pause", ["false", False])
    def test_project_id_from_config(
        self, set_validated_config: Callable, mock_request: Callable, pause: Union[str, bool]
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(project_id=project_id, stage_id=stage_id)
        matcher = mock_request(
            RequestMethod.PUT,
            Routes.stage.format(project_id=project_id, stage_id=stage_id),
            params={"pause": pause},
        )
        resume_stage(config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id

    def test_raises_missing_project_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            pause_stage(config=config)
        assert str(exc_info.value) == "Project ID must be provided to pause a stage."

    def test_raises_missing_stage_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            pause_stage(project_id=uuid4(), config=config)
        assert str(exc_info.value) == "Stage ID must be provided to pause a stage."
