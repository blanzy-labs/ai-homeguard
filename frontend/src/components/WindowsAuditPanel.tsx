import type { HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type WindowsAuditPanelProps = {
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

export function WindowsAuditPanel({ report, loading, error, onRun }: WindowsAuditPanelProps) {
  return (
    <section className="windows-audit-panel" aria-labelledby="windows-audit-heading">
      <div className="flow-heading">
        <p className="section-kicker">Windows Device Audit</p>
        <h2 id="windows-audit-heading">Read-only local Windows checks</h2>
        <p className="muted">
          This mode asks the local backend for Windows posture findings. No settings are changed,
          no network scan is run, and no data is uploaded.
        </p>
      </div>

      <div className="windows-boundaries" aria-label="Windows check safety boundaries">
        <span>Read-only local checks</span>
        <span>No settings changed</span>
        <span>No network scan</span>
        <span>No data uploaded</span>
      </div>

      <button className="primary-button" type="button" disabled={loading} onClick={onRun}>
        {loading ? "Running Read-Only Check" : "Run Windows Local Check"}
      </button>

      {error ? (
        <div className="loading-panel loading-panel--error">
          <h3>Windows report unavailable</h3>
          <p>{error}</p>
        </div>
      ) : null}

      {report ? (
        <section className="results-panel" aria-labelledby="windows-results-heading">
          {isUnsupportedPlatformReport(report) ? (
            <div className="unsupported-message">
              <strong>Windows checks are unavailable here</strong>
              <p>
                Windows checks can only run when AI HomeGuard is running on a Windows computer. You
                are seeing a safe unsupported-platform result.
              </p>
            </div>
          ) : null}

          <div className="dashboard-summary">
            <div>
              <p className="section-kicker">Windows report</p>
              <h2 id="windows-results-heading">Local Audit Result</h2>
              <p className="muted">{report.disclaimer}</p>
            </div>
            <div className="overall-status">
              <span>Overall status</span>
              <strong>{formatStatus(report.summary.overall_status)}</strong>
              {report.summary.overall_score ? <p>{report.summary.overall_score}/100 local score</p> : null}
            </div>
          </div>

          {report.summary.top_actions.length ? (
            <section className="action-plan" aria-labelledby="windows-actions-heading">
              <h2 id="windows-actions-heading">Suggested Next Steps</h2>
              <ol>
                {report.summary.top_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ol>
            </section>
          ) : null}

          <section className="safety-notes" aria-labelledby="windows-safety-heading">
            <h2 id="windows-safety-heading">Safety Notes</h2>
            <ul>
              {report.safety_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </section>

          <section className="findings-section" aria-labelledby="windows-findings-heading">
            <h2 id="windows-findings-heading">Windows Findings</h2>
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
