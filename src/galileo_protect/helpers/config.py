from typing import Optional

from galileo_core.helpers.config import GalileoConfig
from pydantic import UUID4


class ProtectConfig(GalileoConfig):
    # Config file for this project.
    config_filename: str = "protect-config.json"

    # Protect specific configuration.
    project_id: Optional[UUID4] = None
    stage_name: Optional[str] = None
    stage_id: Optional[UUID4] = None
    stage_version: Optional[int] = None

    def reset(self) -> None:
        super().reset()
        self.project_id = None
        self.stage_name = None
        self.stage_id = None
        self.stage_version = None
