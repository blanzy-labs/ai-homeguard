import type { HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type NetworkAwarenessPanelProps = {
  acknowledged: boolean;
  onAcknowledgeChange: (acknowledged: boolean) => void;
  report: HomeGuardReport | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  onBackToModes: () => void;
};

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function NetworkAwarenessPanel({
  acknowledged,
  onAcknowledgeChange,
  report,
  loading,
  error,
  onRun,
  onBackToModes,
}: NetworkAwarenessPanelProps) {
  return (
    <section className="local-audit-panel" aria-labelledby="network-awareness-heading">
      <div className="flow-heading">
        <p className="section-kicker">Local Network Awareness</p>
        <h2 id="network-awareness-heading">Passive local network context</h2>
        <p className="muted">
          Review passive local network context and safety guidance. No active discovery, port
          scanning, packet capture, router login, or public target scanning is run.
        </p>
      </div>

      <div className="network-boundaries" aria-label="Network awareness safety boundaries">
        <span>Authorization required</span>
        <span>Passive context only</span>
        <span>No active scan</span>
        <span>No port scan</span>
        <span>No data uploaded</span>
      </div>

      <ul className="safety-boundary-list">
        <li>No active scan was run.</li>
        <li>No ports were scanned.</li>
        <li>No data was uploaded.</li>
        <li>Results may be limited if running in Docker.</li>
        <li>For connected devices, your router app/admin page may be more complete than passive cache data.</li>
      </ul>

      <label className="acknowledgement">
        <input
          type="checkbox"
          checked={acknowledged}
          onChange={(event) => onAcknowledgeChange(event.target.checked)}
        />
        <span>
          I confirm this is my own home network or a network I am authorized to assess. I understand
          this slice uses passive local network context only. No active scanning, port scanning,
          packet capture, router login, or public target scanning will be performed.
        </span>
      </label>

      <div className="flow-actions">
        <button className="secondary-button" type="button" onClick={onBackToModes}>
          Back to Modes
        </button>
        <button className="primary-button" type="button" disabled={!acknowledged || loading} onClick={onRun}>
          {loading ? "Running Local Network Awareness" : "Run Local Network Awareness"}
        </button>
      </div>

      {error ? (
        <div className="loading-panel loading-panel--error">
          <h3>Network awareness unavailable</h3>
          <p>{error}</p>
        </div>
      ) : null}

      {report ? (
        <section className="results-panel" aria-labelledby="network-results-heading">
          <div className="dashboard-summary">
            <div>
              <p className="section-kicker">Network awareness report</p>
              <h2 id="network-results-heading">Network Awareness Foundation</h2>
              <p className="muted">{report.disclaimer}</p>
            </div>
            <div className="overall-status">
              <span>Overall status</span>
              <strong>{formatStatus(report.summary.overall_status)}</strong>
              {report.summary.overall_score !== null && report.summary.overall_score !== undefined ? (
                <p>{report.summary.overall_score}/100 awareness score</p>
              ) : null}
            </div>
          </div>

          {report.summary.top_actions.length ? (
            <section className="action-plan" aria-labelledby="network-actions-heading">
              <h2 id="network-actions-heading">Suggested Next Steps</h2>
              <ol>
                {report.summary.top_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ol>
            </section>
          ) : null}

          <section className="safety-notes" aria-labelledby="network-safety-heading">
            <h2 id="network-safety-heading">Safety Notes and Limitations</h2>
            <ul>
              {report.safety_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </section>

          <section className="findings-section" aria-labelledby="network-findings-heading">
            <h2 id="network-findings-heading">Network Awareness Findings</h2>
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
