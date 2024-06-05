from typing import Callable, Union
from uuid import uuid4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes as CoreRoutes
from galileo_core.schemas.core.project import ProjectResponse, ProjectType
from pytest import mark, raises

from galileo_protect.constants.routes import Routes
from galileo_protect.schemas.stage import StageResponse
from galileo_protect.stage import create_stage, get_stage, pause_stage, resume_stage
from tests.data import A_PROJECT_NAME, A_STAGE_NAME


class TestCreate:
    @mark.parametrize(
        ["description", "pause"],
        [("description", False), ("description", True), ("description", False), ("description", True)],
    )
    def test_simple(
        self, set_validated_config: Callable, mock_request: Callable, description: str, pause: bool
    ) -> None:
        config = set_validated_config()
        project_id, stage_id = uuid4(), uuid4()
        response = StageResponse(
            id=stage_id,
            name=A_STAGE_NAME,
            project_id=project_id,
            description=description,
            paused=pause,
        )
        matcher = mock_request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            project_id=project_id,
            name=A_STAGE_NAME,
            description=description,
            pause=pause,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == A_STAGE_NAME

    @mark.parametrize(
        ["description", "pause"],
        [("description", False), ("description", True), ("description", False), ("description", True)],
    )
    def test_project_id_from_config(
        self, set_validated_config: Callable, mock_request: Callable, description: str, pause: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(project_id=project_id)
        response = StageResponse(
            id=stage_id,
            name=A_STAGE_NAME,
            project_id=project_id,
            description=description,
            paused=pause,
        )
        matcher = mock_request(
            RequestMethod.POST,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        create_stage(
            name=A_STAGE_NAME,
            description=description,
            pause=pause,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id is not None
        assert config.stage_id == stage_id
        assert config.stage_name is not None
        assert config.stage_name == A_STAGE_NAME

    def test_raises_missing_project_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            create_stage(config=config)
        assert str(exc_info.value) == "Project ID must be provided to create a stage."


class TestGet:
    @mark.parametrize(["include_stage_id", "include_stage_name"], [(True, True), (True, False), (False, True)])
    def test_project_id_params(
        self, set_validated_config: Callable, mock_request: Callable, include_stage_id: bool, include_stage_name: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config()
        response = StageResponse(id=stage_id, name=A_STAGE_NAME, project_id=project_id)
        matcher = mock_request(
            RequestMethod.GET,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        get_stage(
            project_id=project_id,
            stage_id=stage_id if include_stage_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
            config=config,
        )
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id
        assert config.stage_name == A_STAGE_NAME

    @mark.parametrize(["include_stage_id", "include_stage_name"], [(True, True), (True, False), (False, True)])
    def test_project_id_config(
        self, set_validated_config: Callable, mock_request: Callable, include_stage_id: bool, include_stage_name: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(
            project_id=project_id,
            stage_id=stage_id if include_stage_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
        )
        response = StageResponse(id=stage_id, name=A_STAGE_NAME, project_id=project_id)
        matcher = mock_request(
            RequestMethod.GET,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        get_stage(config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id
        assert config.stage_name == A_STAGE_NAME

    @mark.parametrize(["include_stage_id", "include_stage_name"], [(True, True), (True, False), (False, True)])
    def test_project_name_params(
        self, set_validated_config: Callable, mock_request: Callable, include_stage_id: bool, include_stage_name: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config()
        response = StageResponse(id=stage_id, name=A_STAGE_NAME, project_id=project_id)
        matcher_project = mock_request(
            RequestMethod.GET,
            CoreRoutes.projects,
            params=dict(project_name=A_PROJECT_NAME),
            json=[
                ProjectResponse(id=project_id, type=ProjectType.protect, name=A_PROJECT_NAME).model_dump(mode="json")
            ],
        )
        matcher = mock_request(
            RequestMethod.GET,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        get_stage(
            project_name=A_PROJECT_NAME,
            stage_id=stage_id if include_stage_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
            config=config,
        )
        assert matcher.called
        assert matcher_project.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id
        assert config.stage_name == A_STAGE_NAME

    @mark.parametrize(["include_stage_id", "include_stage_name"], [(True, True), (True, False), (False, True)])
    def test_project_name_config(
        self, set_validated_config: Callable, mock_request: Callable, include_stage_id: bool, include_stage_name: bool
    ) -> None:
        project_id, stage_id = uuid4(), uuid4()
        config = set_validated_config(
            project_id=project_id,
            stage_id=stage_id if include_stage_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
        )
        response = StageResponse(id=stage_id, name=A_STAGE_NAME, project_id=project_id)
        matcher = mock_request(
            RequestMethod.GET,
            Routes.stages.format(project_id=project_id),
            json=response.model_dump(mode="json"),
        )
        get_stage(project_name=A_PROJECT_NAME, config=config)
        assert matcher.called
        assert config.project_id == project_id
        assert config.stage_id == stage_id
        assert config.stage_name == A_STAGE_NAME

    def test_no_project_id(self, set_validated_config: Callable) -> None:
        config = set_validated_config()
        with raises(ValueError) as exc_info:
            get_stage(config=config)
        assert str(exc_info.value) == "Project ID or name must be provided to get a stage."

    def test_no_stage_id_or_name(self, set_validated_config: Callable) -> None:
        config = set_validated_config(project_id=uuid4())
        with raises(ValueError) as exc_info:
            get_stage(config=config)
        assert str(exc_info.value) == "Stage ID or name must be provided to get a stage."


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
