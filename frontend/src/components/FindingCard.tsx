import type { Finding } from "../api/client";

type FindingCardProps = {
  finding: Finding;
};

const statusLabels: Record<Finding["status"], string> = {
  good: "Good",
  review: "Review",
  fix_soon: "Fix Soon",
  needs_attention: "Needs Attention",
  unable_to_check: "Unable to Check",
};

function formatValue(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function sourceLabel(finding: Finding) {
  if (finding.tags.includes("device-inventory")) {
    return "Device Inventory Helper";
  }
  if (finding.tags.includes("network-awareness")) {
    return "Local Network Awareness";
  }
  if (finding.tags.includes("questionnaire")) {
    return "Questionnaire";
  }
  if (finding.tags.includes("unsupported-platform")) {
    return "Unsupported Platform";
  }
  if (finding.evidence.some((item) => item.source.toLowerCase().includes("runtime"))) {
    return "Runtime Context";
  }
  if (finding.tags.includes("demo")) {
    return "Demo";
  }
  return "Local Device";
}

function adminLabel(requiresAdmin: boolean) {
  return requiresAdmin ? "Likely admin" : "Usually no admin";
}

export function FindingCard({ finding }: FindingCardProps) {
  return (
    <article className={`finding-card finding-card--${finding.status}`}>
      <div className="finding-card__header">
        <div>
          <p className="finding-card__label">{statusLabels[finding.status]}</p>
          <h3>{finding.home_title}</h3>
        </div>
        <span className="severity-pill">{formatValue(finding.severity)}</span>
      </div>

      <dl className="finding-meta" aria-label={`${finding.home_title} details`}>
        <div>
          <dt>Platform</dt>
          <dd>{formatValue(finding.platform)}</dd>
        </div>
        <div>
          <dt>Category</dt>
          <dd>{formatValue(finding.category)}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>{formatValue(finding.confidence)}</dd>
        </div>
        <div>
          <dt>Difficulty</dt>
          <dd>{formatValue(finding.difficulty)}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{sourceLabel(finding)}</dd>
        </div>
      </dl>

      <div className="finding-copy">
        <p>{finding.why_it_matters}</p>
        <p>
          <strong>Next step:</strong> {finding.recommended_action}
        </p>
        {finding.estimated_time_minutes ? (
          <p>
            <strong>Estimated time:</strong> about {finding.estimated_time_minutes} minutes
          </p>
        ) : null}
      </div>

      <details className="technical-details">
        <summary>Technical details</summary>
        <div className="detail-stack">
          <section>
            <h4>Evidence</h4>
            {finding.evidence.map((item) => (
              <dl className="detail-list" key={`${finding.id}-${item.source}-${item.observed_value}`}>
                <div>
                  <dt>Source</dt>
                  <dd>{item.source}</dd>
                </div>
                <div>
                  <dt>Method</dt>
                  <dd>{item.method}</dd>
                </div>
                <div>
                  <dt>Observed</dt>
                  <dd>{item.observed_value}</dd>
                </div>
                <div>
                  <dt>Expected</dt>
                  <dd>{item.expected_value}</dd>
                </div>
                {item.notes ? (
                  <div>
                    <dt>Notes</dt>
                    <dd>{item.notes}</dd>
                  </div>
                ) : null}
              </dl>
            ))}
          </section>

          <section>
            <h4>D3FEND-Informed Guidance</h4>
            <p className="guidance-context">
              Educational defensive mapping, not a certification or guarantee of protection.
            </p>
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
          </section>

          {finding.attack_context.length > 0 ? (
            <section>
              <h4>ATT&CK Context</h4>
              <ul className="guidance-list">
                {finding.attack_context.map((context) => (
                  <li key={`${finding.id}-${context.technique_id ?? context.technique_name}`}>
                    <span>Educational only</span>
                    <strong>{context.technique_name ?? context.tactic ?? "Context"}</strong>
                    <p>{context.explanation}</p>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      </details>
    </article>
  );
}
