from typing import Dict

from galileo_core.helpers.health import healthcheck as core_healthcheck
from galileo_protect.schemas.config import ProtectConfig


def healthcheck() -> Dict:
    """
    Healthcheck for Protect.

    Returns
    -------
    Dict
        Healthcheck response.
    """
    config = ProtectConfig.get()
    return core_healthcheck(config=config)
