import { useMemo } from "react";
import { ConversationMessage, ConversationState } from "../types";

interface ConversationPanelProps {
  conversation: ConversationState | null;
  processing?: boolean;
}

const formatTime = (iso: string) => {
  try {
    return new Date(iso).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch {
    return "";
  }
};

const audioSource = (message: ConversationMessage) => {
  if (!message.audio) {
    return null;
  }
  return `data:${message.audio.mime_type};base64,${message.audio.data}`;
};

export default function ConversationPanel({
  conversation,
  processing = false
}: ConversationPanelProps) {
  const displayMessages = useMemo(() => {
    if (!conversation) {
      return [] as ConversationMessage[];
    }
    return conversation.messages.filter((message) => message.role !== "system");
  }, [conversation]);

  if (!conversation) {
    return (
      <div className="conversation-panel empty">
        <p>Select a scenario to start speaking practice.</p>
      </div>
    );
  }

  const { scenario } = conversation;

  return (
    <div className="conversation-panel">
      <header className="conversation-header">
        <div>
          <h2>{scenario.title}</h2>
          <p className="muted">Partner role: {scenario.partner_role}</p>
        </div>
        {processing && <span className="badge">Generating response…</span>}
      </header>

      <section className="conversation-messages" aria-live="polite">
        {displayMessages.length === 0 && (
          <p className="muted">Start recording to begin the dialogue.</p>
        )}
        {displayMessages.map((message) => {
          const source = audioSource(message);
          return (
            <article key={message.id} className={`bubble ${message.role}`}>
              <div className="bubble-meta">
                <span className="role-label">
                  {message.role === "assistant" ? "Coach" : "You"}
                </span>
                <time>{formatTime(message.created_at)}</time>
              </div>
              {message.text && <p className="bubble-text">{message.text}</p>}
              {source && (
                <audio controls preload="none" src={source}>
                  Your browser does not support audio playback.
                </audio>
              )}
            </article>
          );
        })}
      </section>

      <section className="scenario-support">
        <div>
          <h3>Tips</h3>
          <ul>
            {scenario.tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Phrasebook</h3>
          <ul className="phrasebook">
            {scenario.phrasebook.map((entry) => (
              <li key={entry.english}>
                <span className="phrase-en">{entry.english}</span>
                <span className="phrase-ja">{entry.japanese}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
