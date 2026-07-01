import type { HomeGuardReport, RuntimeContext } from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

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
  runtimeContext?: RuntimeContext | null;
  runtimeLoading?: boolean;
  runtimeError?: string | null;
  dockerNote?: string;
  report: HomeGuardReport | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  onBackToModes?: () => void;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onClearReport?: () => void;
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

function formatRuntime(context: RuntimeContext) {
  return `${formatStatus(context.detected_platform)} ${context.runtime_environment}`;
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
  runtimeContext,
  runtimeLoading = false,
  runtimeError = null,
  dockerNote,
  report,
  loading,
  error,
  onRun,
  onBackToModes,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onClearReport,
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

      {runtimeLoading ? <p className="runtime-note">Checking runtime context</p> : null}
      {runtimeError ? <p className="runtime-note runtime-note--error">{runtimeError}</p> : null}
      {runtimeContext ? (
        <div className="runtime-summary" aria-label="Detected runtime context">
          <span>Detected runtime</span>
          <strong>{formatRuntime(runtimeContext)}</strong>
          {runtimeContext.runtime_environment === "docker" && dockerNote ? <p>{dockerNote}</p> : null}
        </div>
      ) : null}

      <div className="flow-actions">
        {onBackToModes ? (
          <button className="secondary-button" type="button" onClick={onBackToModes}>
            Back to Modes
          </button>
        ) : null}
        <button className="primary-button" type="button" disabled={loading} onClick={onRun}>
          {loading ? loadingLabel : runLabel}
        </button>
      </div>

      {error ? (
        <div className="loading-panel loading-panel--error">
          <h3>{platformName} report unavailable</h3>
          <p>{error}</p>
        </div>
      ) : null}

      {report ? (
        <div className="results-panel">
          {report.runtime_context && !runtimeContext ? (
            <div className="runtime-summary" aria-label="Report runtime context">
              <span>Detected runtime</span>
              <strong>{formatRuntime(report.runtime_context)}</strong>
              {report.runtime_context.runtime_environment === "docker" && dockerNote ? <p>{dockerNote}</p> : null}
            </div>
          ) : null}

          {isUnsupportedPlatformReport(report) ? (
            <div className="unsupported-message">
              <strong>{unsupportedTitle}</strong>
              <p>{unsupportedBody}</p>
            </div>
          ) : null}

          <ReportReviewPanel
            report={report}
            kicker={`${platformName} report`}
            heading="Local Audit Result"
            scoreLabel="local score"
            findingsHeading={findingsHeading}
            exportStatus={exportStatus}
            onExportMarkdown={onExportMarkdown}
            onExportJson={onExportJson}
            onBackToModes={onBackToModes}
            onClearReport={onClearReport}
          />
        </div>
      ) : null}
    </section>
  );
}
