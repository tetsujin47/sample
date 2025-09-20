export interface PhrasebookEntry {
  english: string;
  japanese: string;
}

export interface ScenarioTurn {
  prompt: string;
  hints: string[];
  sample_response: string;
  grammar_focus: string;
}

export interface ScenarioResource {
  id: string;
  title: string;
  description: string;
  partner_role: string;
  goals: string[];
  turns: ScenarioTurn[];
  tips: string[];
  phrasebook: PhrasebookEntry[];
}

export interface AudioPayload {
  mime_type: string;
  data: string;
}

export interface ConversationMessage {
  id: string;
  role: "system" | "user" | "assistant";
  text: string;
  audio?: AudioPayload | null;
  created_at: string;
}

export interface ConversationState {
  session_id: string;
  scenario: ScenarioResource;
  messages: ConversationMessage[];
}

export interface VoiceMessageResponse {
  conversation: ConversationState;
  transcript?: string;
}

export interface ScenarioListResponse {
  scenarios: ScenarioResource[];
}
