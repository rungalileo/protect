from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Response(BaseModel):
    text: str = Field(description="Text from the request after processing the rules.")
    # Status is optional because it is just being added to the response. To maintain
    # backwards compatibility, it is optional. We'll make it required in v0.9.0.
    status: Optional[str] = Field(default=None, description="Status of the request after processing the rules.")

    model_config = ConfigDict(extra="allow")
