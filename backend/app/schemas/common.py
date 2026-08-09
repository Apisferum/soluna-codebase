from pydantic import BaseModel


class RootResponse(BaseModel):
    message: str
    service: str
    version: str


class HealthResponse(BaseModel):
    status: str
    service: str
