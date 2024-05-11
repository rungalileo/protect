from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

from pytest import mark

from galileo_protect.invoke import ainvoke, invoke
from galileo_protect.langchain import ProtectTool
from galileo_protect.schemas import Payload, Rule, RuleOperator, Ruleset
from galileo_protect.schemas.invoke import Response
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
@mark.parametrize(
    "rulesets",
    [
        # Single ruleset with a single rule.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            )
        ],
        # Single ruleset with multiple rules.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    ),
                    Rule(
                        metric="tone",
                        operator=RuleOperator.lt,
                        target_value=0.8,
                    ),
                ]
            ),
        ],
        # Single ruleset with an unknown metric.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="unknown",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            )
        ],
        # Multiple rulesets with a single rule each.
        [
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.gt,
                        target_value=0.5,
                    )
                ]
            ),
            Ruleset(
                rules=[
                    Rule(
                        metric="toxicity",
                        operator=RuleOperator.lt,
                        target_value=0.8,
                    )
                ]
            ),
        ],
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
            # metadata=metadata,
            # headers=headers,
        )
        response = tool.run(payload.model_dump())
        assert isinstance(response, dict)
        assert response.get("text") is not None
        assert response.get("status") == "NOT_TRIGGERED"
        assert mock_invoke.called
