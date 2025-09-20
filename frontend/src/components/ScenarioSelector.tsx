import { ScenarioResource } from "../types";

interface ScenarioSelectorProps {
  scenarios: ScenarioResource[];
  onSelect: (scenarioId: string) => void;
  activeScenarioId?: string | null;
  loading?: boolean;
}

export default function ScenarioSelector({
  scenarios,
  onSelect,
  activeScenarioId,
  loading = false
}: ScenarioSelectorProps) {
  return (
    <div className="scenario-selector">
      <h2>Practice Scenarios</h2>
      <p className="muted">
        Pick a conversation to begin. Each scenario includes sample prompts, tips,
        and phrasebook entries to support your speaking practice.
      </p>
      <div className="scenario-grid">
        {scenarios.map((scenario) => {
          const isActive = scenario.id === activeScenarioId;
          return (
            <article
              key={scenario.id}
              className={`scenario-card ${isActive ? "active" : ""}`}
            >
              <header>
                <h3>{scenario.title}</h3>
                <span className="partner">Partner: {scenario.partner_role}</span>
              </header>
              <p>{scenario.description}</p>
              <ul className="goal-list">
                {scenario.goals.map((goal) => (
                  <li key={goal}>{goal}</li>
                ))}
              </ul>
              <footer>
                <button
                  type="button"
                  className="primary"
                  onClick={() => onSelect(scenario.id)}
                  disabled={loading || isActive}
                >
                  {isActive ? "In Progress" : "Start Practice"}
                </button>
              </footer>
            </article>
          );
        })}
      </div>
    </div>
  );
}
