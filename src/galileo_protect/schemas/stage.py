from galileo_core.schemas.protect.stage import Stage
from pydantic import UUID4


class StageResponse(Stage):
    id: UUID4
