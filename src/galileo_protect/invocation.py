from typing import Dict, Optional, Sequence

from pydantic import UUID4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.helpers.execution import async_run
from galileo_core.schemas.protect.response import Response
from galileo_protect.constants.invoke import TIMEOUT, TIMEOUT_MARGIN
from galileo_protect.constants.routes import Routes
from galileo_protect.schemas import Payload, Request, Ruleset
from galileo_protect.schemas.config import Config


async def ainvoke(
    payload: Payload,
    prioritized_rulesets: Optional[Sequence[Ruleset]] = None,
    project_id: Optional[UUID4] = None,
    project_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    timeout: float = TIMEOUT,
    metadata: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
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
    project_name : Optional[str], optional
        Project name to be used for processing, by default None.
    stage_id : Optional[UUID4], optional
        Stage ID to be used for processing, by default None.
    stage_name : Optional[str], optional
        Stage name to be used for processing, by default None.
    timeout : float, optional
        Timeout for the request, by default 10 seconds.
    metadata : Optional[Dict[str, str]], optional
        Metadata to be added when responding, by default None.
    headers : Optional[Dict[str, str]], optional
        Headers to be added to the response, by default None.

    Returns
    -------
    Response
        Response from the Protect API.
    """
    config = Config.get()
    response_json = await config.api_client.arequest(
        RequestMethod.POST,
        Routes.invoke,
        json=Request(
            payload=payload,
            rulesets=prioritized_rulesets or [],
            project_id=project_id or config.project_id,
            project_name=project_name or config.project_name,
            stage_name=stage_name or config.stage_name,
            stage_id=stage_id or config.stage_id,
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
    project_name: Optional[str] = None,
    stage_id: Optional[UUID4] = None,
    stage_name: Optional[str] = None,
    timeout: float = TIMEOUT,
    metadata: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
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
    project_name : Optional[str], optional
        Project name to be used for processing, by default None.
    stage_id : Optional[UUID4], optional
        Stage ID to be used for processing, by default None.
    stage_name : Optional[str], optional
        Stage name to be used for processing, by default None.
    timeout : float, optional
        Timeout for the request, by default 10 seconds.
    metadata : Optional[Dict[str, str]], optional
        Metadata to be added when responding, by default None.
    headers : Optional[Dict[str, str]], optional
        Headers to be added to the response, by default None.

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
            project_name=project_name,
            stage_id=stage_id,
            stage_name=stage_name,
            timeout=timeout,
            metadata=metadata,
            headers=headers,
        )
    )
