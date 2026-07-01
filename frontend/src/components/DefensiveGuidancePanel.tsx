import type { Finding } from "../api/client";
import { formatValue } from "./reportLabels";

type DefensiveGuidancePanelProps = {
  finding: Finding;
};

function adminLabel(requiresAdmin: boolean) {
  return requiresAdmin ? "Likely admin" : "Usually no admin";
}

export function DefensiveGuidancePanel({ finding }: DefensiveGuidancePanelProps) {
  return (
    <section>
      <h4>D3FEND-Informed Defensive Guidance</h4>
      <p className="guidance-context">
        D3FEND-informed guidance is educational and does not guarantee protection.
      </p>
      {finding.d3fend_guidance.length ? (
        <ul className="guidance-list">
          {finding.d3fend_guidance.map((guidance) => (
            <li key={`${finding.id}-${guidance.guidance_id ?? guidance.defensive_concept}`}>
              <span>{formatValue(guidance.category)}</span>
              <strong>{guidance.defensive_concept}</strong>
              <p>{guidance.home_action}</p>
              <p>{guidance.rationale}</p>
              <dl className="guidance-meta">
                <div>
                  <dt>Difficulty</dt>
                  <dd>{formatValue(guidance.difficulty)}</dd>
                </div>
                {guidance.estimated_time_minutes ? (
                  <div>
                    <dt>Time</dt>
                    <dd>{guidance.estimated_time_minutes} min</dd>
                  </div>
                ) : null}
                <div>
                  <dt>Admin</dt>
                  <dd>{adminLabel(guidance.requires_admin)}</dd>
                </div>
              </dl>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No D3FEND-informed guidance is attached to this finding.</p>
      )}
    </section>
  );
}
