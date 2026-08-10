from typing import Any

from pydantic import BaseModel, Field


class GenerationRecordBase(BaseModel):
    id: int
    title: str
    prompt: str
    fullPrompt: str
    mood: str | None = None
    genre: str | None = None
    tempo: str | None = None
    key: str | None = None
    instrument: str | None = None
    structure: str | None = None
    status: str
    message: str | None = None
    structuredPlan: dict[str, Any] = Field(
        default_factory=dict
    )
    midiNotes: dict[str, Any] = Field(
        default_factory=dict
    )
    midiFilePath: str | None = None
    blueprintFilePath: str | None = None
    createdAt: int


class UserGenerationRecord(
    GenerationRecordBase
):
    audioFilePath: str | None = None


class AdminGenerationRecord(
    GenerationRecordBase
):
    userEmail: str


class UserGenerationsResponse(BaseModel):
    generations: list[
        UserGenerationRecord
    ] = Field(default_factory=list)


class AdminGenerationsResponse(BaseModel):
    generations: list[
        AdminGenerationRecord
    ] = Field(default_factory=list)


class FileCleanupResult(BaseModel):
    deleted: bool
    filename: str | None = None
    reason: str | None = None


class DeleteGenerationResponse(BaseModel):
    message: str
    generationId: int
    fileCleanup: list[
        FileCleanupResult
    ] = Field(default_factory=list)
