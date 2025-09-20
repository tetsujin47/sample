"""FastAPI backend for the English conversation practice web app."""
from __future__ import annotations

import base64
import logging
import os
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from openai.error import OpenAIError

from .chatgpt_voice import ChatGPTVoiceClient
from .models import (
    ConversationState,
    CreateConversationRequest,
    ScenarioListResponse,
    ScenarioResource,
    VoiceMessageResponse,
)
from .state import ConversationStore

LOGGER = logging.getLogger(__name__)

app = FastAPI(title="English Conversation Practice API", version="1.0.0")

allowed_origins = os.getenv("FRONTEND_ORIGINS", "*")
origins: List[str]
if allowed_origins == "*":
    origins = ["*"]
    allow_credentials = False
else:
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ConversationStore()
voice_client = ChatGPTVoiceClient(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/api/scenarios", response_model=ScenarioListResponse)
def list_scenarios() -> ScenarioListResponse:
    return ScenarioListResponse(
        scenarios=[
            ScenarioResource.from_dataclass(scenario)
            for scenario in store.list_scenarios()
        ]
    )


@app.post("/api/conversations", response_model=ConversationState)
def create_conversation(
    payload: CreateConversationRequest,
) -> ConversationState:
    try:
        session = store.create_session(payload.scenario_id)
    except KeyError as exc:  # pragma: no cover - simple error mapping
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return session.to_state()


@app.get("/api/conversations/{session_id}", response_model=ConversationState)
def get_conversation(session_id: str) -> ConversationState:
    try:
        return store.conversation_state(session_id)
    except KeyError as exc:  # pragma: no cover - simple error mapping
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post("/api/conversations/{session_id}/voice", response_model=VoiceMessageResponse)
async def submit_voice_message(
    session_id: str,
    file: UploadFile = File(...),
) -> VoiceMessageResponse:
    try:
        session = store.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No audio provided."
        )

    mime_type = file.content_type or "audio/webm"
    audio_format = mime_type.split("/")[-1].split(";")[0]
    if audio_format == "mpeg":  # browsers sometimes report mp3 as audio/mpeg
        audio_format = "mp3"

    transcript = voice_client.transcribe_user_audio(audio_bytes, mime_type)
    try:
        assistant_text, assistant_audio = voice_client.send_audio_message(
            session.messages, audio_bytes, audio_format=audio_format
        )
    except OpenAIError as exc:  # pragma: no cover - network error handling
        LOGGER.error("Voice conversation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI voice conversation request failed.",
        ) from exc

    user_audio_payload = voice_client.build_audio_payload(
        base64.b64encode(audio_bytes).decode("utf-8"), mime_type
    )
    store.append_message(session_id, role="user", text=transcript or "", audio=user_audio_payload)

    assistant_audio_payload = voice_client.build_audio_payload(
        assistant_audio, f"audio/{voice_client.response_format}"
    )
    store.append_message(
        session_id,
        role="assistant",
        text=assistant_text or "",
        audio=assistant_audio_payload,
    )

    return VoiceMessageResponse(
        conversation=store.conversation_state(session_id),
        transcript=transcript,
    )


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app"]

