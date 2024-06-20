from typing import Optional, Sequence, Type

from galileo_core.schemas.protect.response import Response
from langchain_core.runnables.base import Runnable
from langchain_core.tools import BaseTool
from pydantic import UUID4, BaseModel, ConfigDict, Field
from pydantic.v1 import BaseModel as BaseModelV1

from galileo_protect.constants.invoke import TIMEOUT
from galileo_protect.invocation import ainvoke, invoke
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

    def _run(self, input: Optional[str] = None, output: Optional[str] = None) -> str:
        """
        Apply the tool synchronously.

        We serialize the response to JSON because that's what `langchain_core` expects
        for tools.
        """
        payload = Payload(input=input, output=output)
        return invoke(
            payload=payload,
            prioritized_rulesets=self.prioritized_rulesets,
            project_id=self.project_id,
            stage_name=self.stage_name,
            stage_id=self.stage_id,
            timeout=self.timeout,
        ).model_dump_json()

    async def _arun(self, input: Optional[str] = None, output: Optional[str] = None) -> str:
        """
        Apply the tool asynchronously.

        We serialize the response to JSON because that's what `langchain_core` expects
        for tools.
        """
        payload = Payload(input=input, output=output)
        response = await ainvoke(
            prioritized_rulesets=self.prioritized_rulesets,
            payload=payload,
            project_id=self.project_id,
            stage_name=self.stage_name,
            stage_id=self.stage_id,
            timeout=self.timeout,
        )
        return response.model_dump_json()


class ProtectParser(BaseModel):
    chain: Runnable = Field(..., description="The chain to trigger if the Protect invocation is not triggered.")
    ignore_trigger: bool = Field(
        default=False,
        description="Ignore the status of the Protect invocation and always trigger the rest of the chain.",
    )
    echo_output: bool = Field(default=False, description="Echo the output of the Protect invocation.")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def parser(self, response_raw_json: str) -> str:
        try:
            response = Response.model_validate_json(response_raw_json)
        except Exception:
            return self.chain.invoke(response_raw_json)
        text = response.text
        if self.echo_output:
            print(f"> Raw response: {text}")
        if response.status == "TRIGGERED" and not self.ignore_trigger:
            return text
        else:
            return self.chain.invoke(text)
