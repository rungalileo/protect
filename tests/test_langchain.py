from typing import Any, List, Optional
from unittest.mock import patch

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pytest import mark

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
