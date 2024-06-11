from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

from galileo_core.schemas.protect.response import Response
from pytest import mark

from galileo_protect.invoker import ainvoke, invoke
from galileo_protect.langchain import ProtectTool
from galileo_protect.schemas import Payload, Ruleset
from tests.data import A_PROTECT_INPUT, A_STAGE_NAME


@mark.parametrize(
    ["include_project_id", "include_stage_name", "include_stage_id"],
    [
        (True, True, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
        (False, False, True),
    ],
)
@mark.parametrize(
    "payload",
    [
        Payload(input=A_PROTECT_INPUT),
        Payload(output=A_PROTECT_INPUT),
        Payload(input=A_PROTECT_INPUT, output=A_PROTECT_INPUT),
    ],
)
@mark.parametrize("timeout", [5, 60])
@mark.parametrize("metadata", [None, {"key": "value"}])
@mark.parametrize("headers", [None, {"key": "value"}])
class TestInvoke:
    def test_invoke(
        self,
        mock_invoke: Mock,
        set_validated_config: Callable,
        include_project_id: bool,
        include_stage_name: bool,
        include_stage_id: bool,
        payload: Payload,
        rulesets: List[Ruleset],
        timeout: float,
        metadata: dict,
        headers: dict,
    ) -> None:
        config = set_validated_config(
            project_id=uuid4() if include_project_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
            stage_id=uuid4() if include_stage_id else None,
        )
        response = invoke(
            payload=payload,
            prioritized_rulesets=rulesets,
            project_id=config.project_id if include_project_id else None,
            stage_name=config.stage_name if include_stage_name else None,
            stage_id=config.stage_id if include_stage_id else None,
            timeout=timeout,
            metadata=metadata,
            headers=headers,
            config=config,
        )
        assert isinstance(response, Response)
        assert response.text == A_PROTECT_INPUT
        assert mock_invoke.called

    @mark.asyncio
    async def test_ainvoke(
        self,
        mock_invoke: Mock,
        set_validated_config: Callable,
        include_project_id: bool,
        include_stage_name: bool,
        include_stage_id: bool,
        payload: Payload,
        rulesets: List[Ruleset],
        timeout: float,
        metadata: dict,
        headers: dict,
    ) -> None:
        payload = Payload(input=A_PROTECT_INPUT)
        config = set_validated_config(
            project_id=uuid4() if include_project_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
            stage_id=uuid4() if include_stage_id else None,
        )
        response = await ainvoke(
            payload=payload,
            prioritized_rulesets=rulesets,
            project_id=config.project_id if include_project_id else None,
            stage_name=config.stage_name if include_stage_name else None,
            stage_id=config.stage_id if include_stage_id else None,
            timeout=timeout,
            metadata=metadata,
            headers=headers,
            config=config,
        )
        assert isinstance(response, Response)
        assert response.text == A_PROTECT_INPUT
        assert mock_invoke.called

    def test_langchain_tool(
        self,
        mock_invoke: Mock,
        set_validated_config: Callable,
        include_project_id: bool,
        include_stage_name: bool,
        include_stage_id: bool,
        payload: Payload,
        rulesets: List[Ruleset],
        timeout: float,
        metadata: dict,
        headers: dict,
    ) -> None:
        config = set_validated_config(
            project_id=uuid4() if include_project_id else None,
            stage_name=A_STAGE_NAME if include_stage_name else None,
            stage_id=uuid4() if include_stage_id else None,
        )
        tool = ProtectTool(
            prioritized_rulesets=rulesets,
            project_id=config.project_id if include_project_id else None,
            stage_name=config.stage_name if include_stage_name else None,
            stage_id=config.stage_id if include_stage_id else None,
            timeout=timeout,
            config=config,
            # Metadata and headers are not used by the tool since they conflict with the
            # langchain_core tool interface.
            # metadata=metadata,
            # headers=headers,
        )
        response_json = tool.run(payload.model_dump())
        assert isinstance(response_json, str)
        response = Response.model_validate_json(response_json)
        assert response.text is not None
        assert response.status == "NOT_TRIGGERED"
        assert mock_invoke.called
