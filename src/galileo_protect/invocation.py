from typing import Dict, Optional, Sequence

from galileo_core.constants.request_method import RequestMethod
from galileo_core.helpers.execution import async_run
from galileo_core.schemas.protect.response import Response
from pydantic import UUID4

from galileo_protect.constants.invoke import TIMEOUT, TIMEOUT_MARGIN
from galileo_protect.constants.routes import Routes
from galileo_protect.helpers.config import ProtectConfig
from galileo_protect.schemas import Payload, Request, Ruleset


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
    """
    Asynchronously invoke Protect with the given payload.

    If using the local stage, the prioritized rulesets should be provided to ensure the
    correct rulesets are used for processing. If using a central stage, the rulesets
    will be fetched from the existing stage definition.

    Project ID and stage name, or stage ID should be provided for all invocations.

    Parameters
    ----------
    payload : Payload
        Payload to be processed.
    prioritized_rulesets : Optional[Sequence[Ruleset]], optional
        Prioritized rulesets to be used for processing. These should only be provided if
        using a local stage, by default None, i.e. empty list.
    project_id : Optional[UUID4], optional
        Project ID to be used for processing, by default None.
    stage_name : Optional[str], optional
        Stage name to be used for processing, by default None.
    stage_id : Optional[UUID4], optional
        Stage ID to be used for processing, by default None.
    timeout : float, optional
        Timeout for the request, by default 10 seconds.
    metadata : Optional[Dict[str, str]], optional
        Metadata to be added when responding, by default None.
    headers : Optional[Dict[str, str]], optional
        Headers to be added to the response, by default None.
    config : Optional[ProtectConfig], optional
        Protect config, by default None which will be taken from the env vars or the
        local config file.

    Returns
    -------
    Response
        Response from the Protect API.
    """
    protect_config: ProtectConfig = config or ProtectConfig.get()
    response_json = await protect_config.api_client.arequest(
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
    """
    Invoke Protect with the given payload.

    If using the local stage, the prioritized rulesets should be provided to ensure the
    correct rulesets are used for processing. If using a central stage, the rulesets
    will be fetched from the existing stage definition.

    Project ID and stage name, or stage ID should be provided for all invocations.

    Parameters
    ----------
    payload : Payload
        Payload to be processed.
    prioritized_rulesets : Optional[Sequence[Ruleset]], optional
        Prioritized rulesets to be used for processing. These should only be provided if
        using a local stage, by default None, i.e. empty list.
    project_id : Optional[UUID4], optional
        Project ID to be used for processing, by default None.
    stage_name : Optional[str], optional
        Stage name to be used for processing, by default None.
    stage_id : Optional[UUID4], optional
        Stage ID to be used for processing, by default None.
    timeout : float, optional
        Timeout for the request, by default 10 seconds.
    metadata : Optional[Dict[str, str]], optional
        Metadata to be added when responding, by default None.
    headers : Optional[Dict[str, str]], optional
        Headers to be added to the response, by default None.
    config : Optional[ProtectConfig], optional
        Protect config, by default None which will be taken from the env vars or the
        local config file.

    Returns
    -------
    Response
        Response from the Protect API.
    """
    return async_run(
        ainvoke(
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
    )
