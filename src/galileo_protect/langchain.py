from typing import Any, Dict, Optional, Sequence, Type

from langchain_core.runnables.base import Runnable
from langchain_core.tools import BaseTool
from pydantic import UUID4, BaseModel, ConfigDict
from pydantic.v1 import BaseModel as BaseModelV1

from galileo_protect.constants.invoke import TIMEOUT
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.invoke import ainvoke, invoke
from galileo_protect.schemas import Payload, Ruleset


class PayloadV1(BaseModelV1):
    input: Optional[str] = None
    output: Optional[str] = None


class ProtectTool(BaseTool):
    name: str = "GalileoProtect"
    description: str = (
        "Protect your LLM applications from harmful content using Galileo Protect. "
        "This tool is a wrapper around Galileo's Protect API, can be used to scan text "
        "for harmful content, and can be used to trigger actions based on the results."
        "The tool can be used synchronously or asynchronously, on the input text or output text,"
        "and can be configured with a set of rulesets to evaluate on."
    )
    args_schema: Type[BaseModelV1] = PayloadV1

    prioritized_rulesets: Optional[Sequence[Ruleset]] = None
    project_id: Optional[UUID4] = None
    stage_name: Optional[str] = None
    stage_id: Optional[UUID4] = None
    timeout: float = TIMEOUT
    config: Optional[ProtectConfig] = None

    def _run(self, input: Optional[str] = None, output: Optional[str] = None) -> Dict[str, Any]:
        """Use the tool."""
        payload = Payload(input=input, output=output)
        return invoke(
            payload=payload,
            prioritized_rulesets=self.prioritized_rulesets,
            project_id=self.project_id,
            stage_name=self.stage_name,
            stage_id=self.stage_id,
            timeout=self.timeout,
            config=self.config,
        ).model_dump()

    async def _arun(self, input: Optional[str] = None, output: Optional[str] = None) -> Dict[str, Any]:
        """Use the tool asynchronously."""
        payload = Payload(input=input, output=output)
        response = await ainvoke(
            prioritized_rulesets=self.prioritized_rulesets,
            payload=payload,
            project_id=self.project_id,
            stage_name=self.stage_name,
            stage_id=self.stage_id,
            timeout=self.timeout,
            config=self.config,
        )
        return response.model_dump()


class ProtectParser(BaseModel):
    chain: Runnable

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def parser(self, output: Dict[str, Any]) -> str:
        text = output.get("text", "")
        if output.get("status") == "TRIGGERED":
            return text
        else:
            return self.chain.invoke(text)
