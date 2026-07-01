import type { HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type LocalAuditPanelProps = {
  platformName: string;
  panelKicker: string;
  heading: string;
  description: string;
  runLabel: string;
  loadingLabel: string;
  findingsHeading: string;
  unsupportedTitle: string;
  unsupportedBody: string;
  report: HomeGuardReport | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
};

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function isUnsupportedPlatformReport(report: HomeGuardReport) {
  return report.findings.some((finding) => finding.id.includes("unsupported-platform"));
}

export function LocalAuditPanel({
  platformName,
  panelKicker,
  heading,
  description,
  runLabel,
  loadingLabel,
  findingsHeading,
  unsupportedTitle,
  unsupportedBody,
  report,
  loading,
  error,
  onRun,
}: LocalAuditPanelProps) {
  return (
    <section className="local-audit-panel" aria-labelledby="local-audit-heading">
      <div className="flow-heading">
        <p className="section-kicker">{panelKicker}</p>
        <h2 id="local-audit-heading">{heading}</h2>
        <p className="muted">{description}</p>
      </div>

      <div className="local-boundaries" aria-label={`${platformName} check safety boundaries`}>
        <span>Read-only local checks</span>
        <span>No settings changed</span>
        <span>No network scan</span>
        <span>No data uploaded</span>
      </div>

      <button className="primary-button" type="button" disabled={loading} onClick={onRun}>
        {loading ? loadingLabel : runLabel}
      </button>

      {error ? (
        <div className="loading-panel loading-panel--error">
          <h3>{platformName} report unavailable</h3>
          <p>{error}</p>
        </div>
      ) : null}

      {report ? (
        <section className="results-panel" aria-labelledby="local-results-heading">
          {isUnsupportedPlatformReport(report) ? (
            <div className="unsupported-message">
              <strong>{unsupportedTitle}</strong>
              <p>{unsupportedBody}</p>
            </div>
          ) : null}

          <div className="dashboard-summary">
            <div>
              <p className="section-kicker">{platformName} report</p>
              <h2 id="local-results-heading">Local Audit Result</h2>
              <p className="muted">{report.disclaimer}</p>
            </div>
            <div className="overall-status">
              <span>Overall status</span>
              <strong>{formatStatus(report.summary.overall_status)}</strong>
              {report.summary.overall_score !== null && report.summary.overall_score !== undefined ? (
                <p>{report.summary.overall_score}/100 local score</p>
              ) : null}
            </div>
          </div>

          {report.summary.top_actions.length ? (
            <section className="action-plan" aria-labelledby="local-actions-heading">
              <h2 id="local-actions-heading">Suggested Next Steps</h2>
              <ol>
                {report.summary.top_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ol>
            </section>
          ) : null}

          <section className="safety-notes" aria-labelledby="local-safety-heading">
            <h2 id="local-safety-heading">Safety Notes</h2>
            <ul>
              {report.safety_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </section>

          <section className="findings-section" aria-labelledby="local-findings-heading">
            <h2 id="local-findings-heading">{findingsHeading}</h2>
            <div className="findings-list">
              {report.findings.map((finding) => (
                <FindingCard key={finding.id} finding={finding} />
              ))}
            </div>
          </section>
        </section>
      ) : null}
    </section>
  );
}
