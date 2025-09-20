"""Pydantic models used by the FastAPI backend."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .conversation_data import Scenario


class AudioPayload(BaseModel):
    """Audio content encoded as base64 for transfer to the client."""

    mime_type: str = Field(default="audio/wav", description="Audio MIME type")
    data: str = Field(description="Base64 encoded audio data")


class Message(BaseModel):
    """A message in the conversation history."""

    id: str
    role: Literal["system", "user", "assistant"]
    text: str = ""
    audio: Optional[AudioPayload] = None
    created_at: datetime


class ScenarioTurnModel(BaseModel):
    prompt: str
    hints: List[str] = Field(default_factory=list)
    sample_response: str = ""
    grammar_focus: str = ""


class PhrasebookEntry(BaseModel):
    english: str
    japanese: str


class ScenarioResource(BaseModel):
    id: str
    title: str
    description: str
    partner_role: str
    goals: List[str]
    turns: List[ScenarioTurnModel]
    tips: List[str]
    phrasebook: List[PhrasebookEntry]

    @classmethod
    def from_dataclass(cls, scenario: Scenario) -> "ScenarioResource":
        return cls(
            id=scenario.id,
            title=scenario.title,
            description=scenario.description,
            partner_role=scenario.partner_role,
            goals=list(scenario.goals),
            turns=[
                ScenarioTurnModel(
                    prompt=turn.prompt,
                    hints=list(turn.hints),
                    sample_response=turn.sample_response,
                    grammar_focus=turn.grammar_focus,
                )
                for turn in scenario.turns
            ],
            tips=list(scenario.tips),
            phrasebook=[
                PhrasebookEntry(english=english, japanese=japanese)
                for english, japanese in scenario.phrasebook
            ],
        )


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioResource]


class ConversationState(BaseModel):
    session_id: str
    scenario: ScenarioResource
    messages: List[Message]


class CreateConversationRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Scenario identifier")


class TextMessageRequest(BaseModel):
    message: str


class VoiceMessageResponse(BaseModel):
    conversation: ConversationState
    transcript: Optional[str] = None

