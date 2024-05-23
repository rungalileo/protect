from typing import Dict, Optional, Sequence

from galileo_core.constants.request_method import RequestMethod
from galileo_core.schemas.protect.response import Response
from pydantic import UUID4

from galileo_protect.constants.invoke import TIMEOUT, TIMEOUT_MARGIN
from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.schemas import Payload, Request, Ruleset


def invoke(
    payload: Payload,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
    project_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    timeout: float = TIMEOUT,
    metadata: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    config: Optional[ProtectConfig] = None,
) -> Response:
    protect_config: ProtectConfig = config or ProtectConfig.get()
    response_json = protect_config.api_client.request(
        RequestMethod.POST,
        Routes.invoke,
        json=Request(
            payload=payload,
            rulesets=prioritized_rulesets or [],
            project_id=project_id or protect_config.project_id,
            stage_name=stage_name or protect_config.stage_name,
            stage_id=stage_id or protect_config.stage_id,
            timeout=timeout,
            metadata=metadata,
            headers=headers,
        ).model_dump(mode="json"),
        # Set the read timeout to the maximum of the timeout plus the timeout margin.
        read_timeout=timeout + TIMEOUT_MARGIN,
    )
    return Response.model_validate(response_json)


async def ainvoke(
    payload: Payload,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
    project_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    timeout: float = TIMEOUT,
    metadata: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    config: Optional[ProtectConfig] = None,
) -> Response:
    return invoke(
        payload=payload,
        prioritized_rulesets=prioritized_rulesets,
        project_id=project_id,
        stage_name=stage_name,
        stage_id=stage_id,
        timeout=timeout,
        metadata=metadata,
        headers=headers,
        config=config,
    )
