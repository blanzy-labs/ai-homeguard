import type { HomeGuardReport } from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

type NetworkAwarenessPanelProps = {
  acknowledged: boolean;
  onAcknowledgeChange: (acknowledged: boolean) => void;
  report: HomeGuardReport | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  onBackToModes: () => void;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onClearReport?: () => void;
};

export function NetworkAwarenessPanel({
  acknowledged,
  onAcknowledgeChange,
  report,
  loading,
  error,
  onRun,
  onBackToModes,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onClearReport,
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
        <ReportReviewPanel
          report={report}
          kicker="Network awareness report"
          heading="Network Awareness Foundation"
          scoreLabel="awareness score"
          findingsHeading="Network Awareness Findings"
          exportStatus={exportStatus}
          onExportMarkdown={onExportMarkdown}
          onExportJson={onExportJson}
          onBackToModes={onBackToModes}
          onClearReport={onClearReport}
        />
      ) : null}
    </section>
  );
}
