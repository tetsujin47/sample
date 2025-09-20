"""Wrapper around the OpenAI ChatGPT voice conversation API."""
from __future__ import annotations

import base64
import logging
from typing import Iterable, List, Optional

from openai import OpenAI
from openai.error import OpenAIError

from .models import AudioPayload
from .state import StoredMessage

LOGGER = logging.getLogger(__name__)


class ChatGPTVoiceClient:
    """Send audio messages to the ChatGPT voice conversation API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        conversation_model: str = "gpt-4o-mini",
        transcription_model: str = "gpt-4o-mini-transcribe",
        response_voice: str = "alloy",
        response_format: str = "wav",
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.conversation_model = conversation_model
        self.transcription_model = transcription_model
        self.response_voice = response_voice
        self.response_format = response_format

    def build_history(self, messages: Iterable[StoredMessage]) -> List[dict]:
        history: List[dict] = []
        for message in messages:
            if message.role not in {"user", "assistant", "system"}:
                continue
            content: List[dict] = []
            if message.text:
                content.append({"type": "input_text", "text": message.text})
            history.append({"role": message.role, "content": content})
        return history

    def _extract_text_and_audio(self, response: object) -> tuple[str, Optional[str]]:
        text_segments: List[str] = []
        audio_data: Optional[str] = None

        output_items = getattr(response, "output", None)
        if output_items:
            for item in output_items:
                contents = getattr(item, "content", [])
                for content in contents:
                    content_type = getattr(content, "type", None)
                    if content_type == "output_text":
                        text_segments.append(getattr(content, "text", ""))
                    elif content_type == "output_audio":
                        audio_info = getattr(content, "audio", None)
                        if audio_info is not None:
                            audio_data = getattr(audio_info, "data", None) or audio_data
        output_text = "".join(text_segments).strip()
        if not output_text:
            output_text = getattr(response, "output_text", "").strip()
        return output_text, audio_data

    def transcribe_user_audio(
        self, audio_bytes: bytes, mime_type: str = "audio/webm"
    ) -> Optional[str]:
        extension = mime_type.split("/")[-1].split(";")[0]
        try:
            transcription = self.client.audio.transcriptions.create(
                model=self.transcription_model,
                file=(f"speech.{extension}", audio_bytes),
            )
        except OpenAIError as exc:  # pragma: no cover - network error handling
            LOGGER.error("OpenAI transcription failed: %s", exc)
            return None
        return getattr(transcription, "text", None)

    def send_audio_message(
        self,
        session_messages: Iterable[StoredMessage],
        audio_bytes: bytes,
        audio_format: str = "webm",
    ) -> tuple[str, Optional[str]]:
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        input_messages = self.build_history(session_messages)
        input_messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "audio": {"format": audio_format, "data": base64_audio},
                    }
                ],
            }
        )

        try:
            response = self.client.responses.create(
                model=self.conversation_model,
                input=input_messages,
                modalities=["text", "audio"],
                audio={"voice": self.response_voice, "format": self.response_format},
            )
        except OpenAIError as exc:  # pragma: no cover - network error handling
            LOGGER.error("OpenAI conversation request failed: %s", exc)
            raise

        text, audio_data = self._extract_text_and_audio(response)
        return text, audio_data

    def build_audio_payload(
        self, audio_b64: Optional[str], mime_type: str
    ) -> Optional[AudioPayload]:
        if not audio_b64:
            return None
        return AudioPayload(mime_type=mime_type, data=audio_b64)

