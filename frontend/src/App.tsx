import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";
import ConversationPanel from "./components/ConversationPanel";
import ScenarioSelector from "./components/ScenarioSelector";
import VoiceRecorder from "./components/VoiceRecorder";
import {
  ConversationState,
  ScenarioListResponse,
  ScenarioResource,
  VoiceMessageResponse
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export default function App() {
  const [scenarios, setScenarios] = useState<ScenarioResource[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState(false);
  const [conversation, setConversation] = useState<ConversationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const fetchScenarios = useCallback(async () => {
    setLoadingScenarios(true);
    try {
      const { data } = await axios.get<ScenarioListResponse>(
        `${API_BASE}/api/scenarios`
      );
      setScenarios(data.scenarios);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load scenarios. Please refresh the page.");
    } finally {
      setLoadingScenarios(false);
    }
  }, []);

  useEffect(() => {
    fetchScenarios();
  }, [fetchScenarios]);

  const startConversation = async (scenarioId: string) => {
    setProcessing(true);
    try {
      const { data } = await axios.post<ConversationState>(
        `${API_BASE}/api/conversations`,
        { scenario_id: scenarioId }
      );
      setConversation(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to start the conversation. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const sendVoiceMessage = async (blob: Blob) => {
    if (!conversation) {
      return;
    }
    setProcessing(true);
    const formData = new FormData();
    formData.append("file", blob, "speech.webm");
    try {
      const { data } = await axios.post<VoiceMessageResponse>(
        `${API_BASE}/api/conversations/${conversation.session_id}/voice`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" }
        }
      );
      setConversation(data.conversation);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(
        "The voice request failed. Ensure the backend is running with a valid OpenAI key."
      );
    } finally {
      setProcessing(false);
    }
  };

  const activeScenarioId = conversation?.scenario.id ?? null;

  const conversationPanel = useMemo(
    () => <ConversationPanel conversation={conversation} processing={processing} />,
    [conversation, processing]
  );

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>English Conversation Practice</h1>
          <p>Role-play everyday English situations with real voice input.</p>
        </div>
        <button
          type="button"
          className="secondary"
          onClick={() => fetchScenarios()}
          disabled={loadingScenarios}
        >
          Refresh Scenarios
        </button>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <ScenarioSelector
            scenarios={scenarios}
            onSelect={startConversation}
            activeScenarioId={activeScenarioId}
            loading={processing || loadingScenarios}
          />
        </aside>
        <section className="content">
          {error && <div className="error-banner">{error}</div>}
          {conversationPanel}
          <VoiceRecorder
            onRecordingComplete={sendVoiceMessage}
            disabled={!conversation}
            processing={processing}
          />
        </section>
      </main>
    </div>
  );
}
