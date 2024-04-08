from pydantic import BaseModel, ConfigDict, Field


class Response(BaseModel):
    text: str = Field(description="Text from the request after processing the rules.")

    model_config = ConfigDict(extra="allow")
