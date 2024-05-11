from typing import Any, Callable, List, Optional
from unittest.mock import Mock, patch
from uuid import uuid4

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pytest import mark

from galileo_protect.langchain import ProtectParser, ProtectTool
from galileo_protect.schemas import Payload, Rule, RuleOperator, Ruleset
from tests.data import A_PROTECT_INPUT, A_STAGE_NAME


class ProtectLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "protect"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return prompt


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
def test_tool_run(
    mock_invoke: Mock,
    set_validated_config: Callable,
    include_project_id: bool,
    include_stage_name: bool,
    include_stage_id: bool,
    payload: Payload,
    rulesets: List[Ruleset],
    timeout: float,
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
    )
    response = tool.run(payload.model_dump())
    assert isinstance(response, dict)
    assert response.get("text") is not None
    assert response.get("status") is not None


@mark.parametrize(
    ["output", "expected_return", "expected_call_count"],
    [
        [{"text": "foo"}, "foo", 1],
        [{"text": "timeout", "status": "TIMEOUT"}, "timeout", 1],
        [{"text": "success", "status": "SUCCESS"}, "success", 1],
        [{"text": "triggered", "status": "TRIGGERED"}, "triggered", 0],
    ],
)
def test_parser(output: dict, expected_return: str, expected_call_count: int) -> None:
    parser = ProtectParser(chain=ProtectLLM())
    with patch.object(ProtectLLM, "invoke", wraps=parser.chain.invoke) as mock_fn:
        return_value = parser.parser(output)
        assert return_value == expected_return
        assert mock_fn.call_count == expected_call_count
