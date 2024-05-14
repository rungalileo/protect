from json import dumps
from typing import Any, List, Optional
from unittest.mock import patch

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pytest import CaptureFixture, mark

from galileo_protect.langchain import ProtectParser


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
        [dumps({"text": "foo"}), False, "foo", 1],
        [dumps({"text": "foo"}), True, "foo", 1],
        [dumps({"text": "timeout", "status": "TIMEOUT"}), False, "timeout", 1],
        [dumps({"text": "timeout", "status": "TIMEOUT"}), True, "timeout", 1],
        [dumps({"text": "success", "status": "SUCCESS"}), False, "success", 1],
        [dumps({"text": "success", "status": "SUCCESS"}), True, "success", 1],
        [dumps({"text": "triggered", "status": "TRIGGERED"}), False, "triggered", 0],
        [dumps({"text": "triggered", "status": "TRIGGERED"}), True, "triggered", 1],
    ],
)
def test_parser(output: str, ignore_trigger: bool, expected_return: str, expected_call_count: int) -> None:
    parser = ProtectParser(chain=ProtectLLM(), ignore_trigger=ignore_trigger)
    with patch.object(ProtectLLM, "invoke", wraps=parser.chain.invoke) as mock_fn:
        return_value = parser.parser(output)
        assert return_value == expected_return
        assert mock_fn.call_count == expected_call_count


@mark.parametrize(["echo_output", "expected_output"], [[True, "> Raw response: foo\n"], [False, ""]])
def test_echo(echo_output: bool, expected_output: str, capsys: CaptureFixture) -> None:
    parser = ProtectParser(chain=ProtectLLM(), echo_output=echo_output)
    parser.parser(dumps({"text": "foo"}))
    captured = capsys.readouterr()
    assert captured.out == expected_output
