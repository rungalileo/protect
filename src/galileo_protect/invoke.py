from datetime import timedelta
from typing import Dict, Optional, Sequence

from pydantic import UUID4
from requests import post

from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.schemas import Payload, Request, Ruleset
from galileo_protect.schemas.response import Response


def invoke(
    payload: Payload,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
    project_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    timeout: float = timedelta(minutes=5).total_seconds(),
    metadata: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    config: Optional[ProtectConfig] = None,
) -> Response:
    protect_config: ProtectConfig = config or ProtectConfig.get()
    response_json = protect_config.api_client.request(
        post,
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
    )
    return Response.model_validate(response_json)
