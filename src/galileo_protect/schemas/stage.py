from typing import Optional

from pydantic import UUID4

from galileo_core.schemas.protect.stage import Stage


class StageResponse(Stage):
    id: UUID4
    version: Optional[int] = None
