from json import dumps
from typing import Any, List, Optional
from unittest.mock import patch

from galileo_protect.langchain import ProtectParser
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pytest import CaptureFixture, mark

from tests.data import A_TRACE_METADATA_DICT


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
    ["output", "ignore_trigger", "expected_return", "expected_call_count"],
    [
        [dumps({"text": "foo", "status": "NOT_TRIGGERED", **A_TRACE_METADATA_DICT}), False, "foo", 1],
        [dumps({"text": "foo", "status": "NOT_TRIGGERED", **A_TRACE_METADATA_DICT}), True, "foo", 1],
        [dumps({"text": "timeout", "status": "TIMEOUT", **A_TRACE_METADATA_DICT}), False, "timeout", 1],
        [dumps({"text": "timeout", "status": "TIMEOUT", **A_TRACE_METADATA_DICT}), True, "timeout", 1],
        [
            dumps({"text": "not_triggered", "status": "NOT_TRIGGERED", **A_TRACE_METADATA_DICT}),
            False,
            "not_triggered",
            1,
        ],
        [
            dumps({"text": "not_triggered", "status": "NOT_TRIGGERED", **A_TRACE_METADATA_DICT}),
            True,
            "not_triggered",
            1,
        ],
        [
            dumps({"text": "triggering text", "status": "TRIGGERED", **A_TRACE_METADATA_DICT}),
            False,
            "triggering text",
            0,
        ],
        [
            dumps({"text": "triggering text", "status": "TRIGGERED", **A_TRACE_METADATA_DICT}),
            True,
            "triggering text",
            1,
        ],
    ],
)
def test_parser(output: str, ignore_trigger: bool, expected_return: str, expected_call_count: int) -> None:
    # Verify that the ProtectParser invokes the ProtectLLM only if the status is not "TRIGGERED"
    # and ignore_trigger is False.
    parser = ProtectParser(chain=ProtectLLM(), ignore_trigger=ignore_trigger)
    with patch.object(ProtectLLM, "invoke", wraps=parser.chain.invoke) as mock_fn:
        return_value = parser.parser(output)
        assert return_value == expected_return
        assert mock_fn.call_count == expected_call_count


@mark.parametrize(["echo_output", "expected_output"], [[True, "> Raw response: foo\n"], [False, ""]])
def test_echo(echo_output: bool, expected_output: str, capsys: CaptureFixture) -> None:
    """
    Verify that the ProtectParser echoes the output if echo_output is True.
    """
    parser = ProtectParser(chain=ProtectLLM(), echo_output=echo_output)
    parser.parser(dumps({"text": "foo", "status": "NOT_TRIGGERED", **A_TRACE_METADATA_DICT}))
    captured = capsys.readouterr()
    assert captured.out == expected_output
