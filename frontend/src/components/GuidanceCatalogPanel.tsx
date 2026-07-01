import type { D3FENDCatalogResponse } from "../api/client";

type GuidanceCatalogPanelProps = {
  catalog: D3FENDCatalogResponse;
  onBackToModes: () => void;
};

function formatValue(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function GuidanceCatalogPanel({ catalog, onBackToModes }: GuidanceCatalogPanelProps) {
  return (
    <section className="results-panel" aria-labelledby="guidance-catalog-heading">
      <div className="dashboard-summary">
        <div>
          <p className="section-kicker">Defensive Guidance</p>
          <h2 id="guidance-catalog-heading">D3FEND-Informed Guidance Catalog</h2>
          <p className="muted">{catalog.disclaimer}</p>
          <p className="muted">{catalog.source_note}</p>
        </div>
        <div className="overall-status">
          <span>Catalog entries</span>
          <strong>{catalog.guidance.length}</strong>
          <p>{catalog.version}</p>
        </div>
      </div>

      <div className="guidance-catalog-grid">
        {catalog.guidance.map((entry) => (
          <article className="guidance-catalog-card" key={entry.guidance_id}>
            <div>
              <span>{formatValue(entry.category)}</span>
              <h3>{entry.defensive_concept}</h3>
            </div>
            <p>{entry.home_action}</p>
            <p>{entry.rationale}</p>
            <dl className="guidance-meta">
              <div>
                <dt>Difficulty</dt>
                <dd>{formatValue(entry.difficulty)}</dd>
              </div>
              <div>
                <dt>Time</dt>
                <dd>{entry.estimated_time_minutes} min</dd>
              </div>
              <div>
                <dt>Admin</dt>
                <dd>{entry.requires_admin ? "Likely" : "Usually no"}</dd>
              </div>
            </dl>
            <p className="runtime-note">
              Applies to {entry.applies_to_platforms.map(formatValue).join(", ")}
            </p>
          </article>
        ))}
      </div>

      <button className="secondary-button" type="button" onClick={onBackToModes}>
        Back to Modes
      </button>
    </section>
  );
}
