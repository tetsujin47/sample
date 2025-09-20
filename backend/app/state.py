"""In-memory conversation state management for the practice app."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from .conversation_data import SCENARIOS, Scenario
from .models import AudioPayload, ConversationState, Message, ScenarioResource


@dataclass
class StoredMessage:
    id: str
    role: str
    text: str = ""
    audio: Optional[AudioPayload] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_model(self) -> Message:
        return Message(
            id=self.id,
            role=self.role,  # type: ignore[arg-type]
            text=self.text,
            audio=self.audio,
            created_at=self.created_at,
        )


@dataclass
class ConversationSession:
    session_id: str
    scenario: Scenario
    messages: List[StoredMessage] = field(default_factory=list)

    def to_state(self) -> ConversationState:
        return ConversationState(
            session_id=self.session_id,
            scenario=ScenarioResource.from_dataclass(self.scenario),
            messages=[message.to_model() for message in self.messages],
        )


class ConversationStore:
    """Maintain active conversation sessions in memory."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationSession] = {}

    def list_scenarios(self) -> List[Scenario]:
        return list(SCENARIOS)

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        for scenario in SCENARIOS:
            if scenario.id == scenario_id:
                return scenario
        return None

    def create_session(self, scenario_id: Optional[str] = None) -> ConversationSession:
        scenario = self.get_scenario(scenario_id) if scenario_id else SCENARIOS[0]
        if scenario is None:
            raise KeyError(f"Unknown scenario id: {scenario_id}")

        session_id = str(uuid4())
        session = ConversationSession(session_id=session_id, scenario=scenario)
        system_prompt = (
            "You are role-playing as the {role} in the '{title}' scenario. "
            "Stay true to the situation: {description}. Provide warm, "
            "encouraging replies that invite the learner to keep speaking. "
            "Offer gentle corrections when necessary and guide the "
            "conversation toward these goals: {goals}."
        ).format(
            role=scenario.partner_role,
            title=scenario.title,
            description=scenario.description,
            goals=", ".join(scenario.goals),
        )
        session.messages.append(
            StoredMessage(id=str(uuid4()), role="system", text=system_prompt)
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session: {session_id}")
        return self._sessions[session_id]

    def append_message(
        self,
        session_id: str,
        role: str,
        text: str = "",
        audio: Optional[AudioPayload] = None,
    ) -> StoredMessage:
        session = self.get_session(session_id)
        message = StoredMessage(id=str(uuid4()), role=role, text=text, audio=audio)
        session.messages.append(message)
        return message

    def replace_messages(
        self, session_id: str, messages: Iterable[StoredMessage]
    ) -> None:
        session = self.get_session(session_id)
        session.messages = list(messages)

    def conversation_state(self, session_id: str) -> ConversationState:
        return self.get_session(session_id).to_state()

