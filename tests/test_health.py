from typing import Callable

from galileo_protect.health import healthcheck


def test_health(set_validated_config: Callable) -> None:
    set_validated_config()
    healthcheck_response = healthcheck()
    assert isinstance(healthcheck_response, dict)
