# mypy: disable-error-code=syntax
# We need to ignore syntax errors until https://github.com/python/mypy/issues/17535 is resolved.
from typing import Any, Optional

from pydantic import UUID4

from galileo_core.schemas.base_config import GalileoConfig


class ProtectConfig(GalileoConfig):
    # Config file for this project.
    config_filename: str = "protect-config.json"

    # Protect specific configuration.
    project_id: Optional[UUID4] = None
    project_name: Optional[str] = None
    stage_id: Optional[UUID4] = None
    stage_name: Optional[str] = None
    stage_version: Optional[int] = None

    def reset(self) -> None:
        self.project_id = None
        self.project_name = None
        self.stage_id = None
        self.stage_name = None
        self.stage_version = None

        global _protect_config
        _protect_config = None

        super().reset()

    @classmethod
    def get(cls, **kwargs: Any) -> "ProtectConfig":
        global _protect_config
        _protect_config = cls._get(_protect_config, **kwargs)  # type: ignore[arg-type]
        return _protect_config


_protect_config: Optional[ProtectConfig] = None
