import type { Finding } from "../api/client";
import { DefensiveGuidancePanel } from "./DefensiveGuidancePanel";
import { EvidenceSourceBadge } from "./EvidenceSourceBadge";
import { evidenceSourceLabel, formatValue, statusLabels } from "./reportLabels";

type FindingCardProps = {
  finding: Finding;
};

export function FindingCard({ finding }: FindingCardProps) {
  return (
    <article className={`finding-card finding-card--${finding.status}`}>
      <div className="finding-card__header">
        <div>
          <p className="finding-card__label">{statusLabels[finding.status]}</p>
          <h3>{finding.home_title}</h3>
        </div>
        <div className="finding-card__badges">
          <EvidenceSourceBadge finding={finding} />
          <span className="severity-pill">{formatValue(finding.severity)}</span>
        </div>
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
          <dd>{evidenceSourceLabel(finding)}</dd>
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
        <summary>More Detail</summary>
        <div className="detail-stack">
          {finding.technical_title ? (
            <section>
              <h4>Detailed title</h4>
              <p className="muted">{finding.technical_title}</p>
            </section>
          ) : null}

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

          <DefensiveGuidancePanel finding={finding} />

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
