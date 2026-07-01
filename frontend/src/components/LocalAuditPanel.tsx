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
  nativeMacInstruction?: string;
  browserPlatformHint?: string | null;
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
  const names: Record<string, string> = {
    docker: "Docker/container",
    linux: "Linux",
    macos: "macOS",
    native: "Native host",
    unknown: "Unknown",
    windows: "Windows",
  };
  if (names[value]) {
    return names[value];
  }
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function isUnsupportedPlatformReport(report: HomeGuardReport) {
  return report.findings.some((finding) => finding.id.includes("unsupported-platform"));
}

function formatRuntime(context: RuntimeContext) {
  return `${formatStatus(context.detected_platform)} / ${formatStatus(context.runtime_environment)}`;
}

function auditTarget(context: RuntimeContext) {
  if (context.runtime_environment === "docker") {
    return "Container Runtime Detected";
  }
  if (context.runtime_environment === "native") {
    return `${formatStatus(context.detected_platform)} host runtime`;
  }
  return "Runtime visibility unknown";
}

function browserLooksLikeMacOS(browserPlatformHint?: string | null) {
  return browserPlatformHint?.toLowerCase().includes("mac") ?? false;
}

function RuntimeSummary({
  context,
  browserPlatformHint,
  dockerNote,
  nativeMacInstruction,
}: {
  context: RuntimeContext;
  browserPlatformHint?: string | null;
  dockerNote?: string;
  nativeMacInstruction?: string;
}) {
  const macBrowserLinuxContainer =
    browserLooksLikeMacOS(browserPlatformHint) &&
    context.detected_platform === "linux" &&
    context.runtime_environment === "docker";

  return (
    <div className="runtime-summary" aria-label="Detected runtime context">
      <span>Runtime visibility</span>
      <dl className="runtime-detail-grid">
        <div>
          <dt>Browser/device hint</dt>
          <dd>{browserPlatformHint ?? "Not available"}</dd>
        </div>
        <div>
          <dt>Backend runtime</dt>
          <dd>{formatRuntime(context)}</dd>
        </div>
        <div>
          <dt>Audit target</dt>
          <dd>{auditTarget(context)}</dd>
        </div>
      </dl>
      {macBrowserLinuxContainer ? (
        <p className="runtime-warning">
          Your browser appears to be on macOS, but the backend is running in a Linux container. For
          host-level macOS checks, run the backend natively with uv.
        </p>
      ) : null}
      {context.runtime_environment === "docker" && dockerNote ? <p>{dockerNote}</p> : null}
      {context.runtime_environment === "docker" && nativeMacInstruction ? <p>{nativeMacInstruction}</p> : null}
      {context.limitations.map((limitation) => (
        <p key={limitation}>{limitation}</p>
      ))}
    </div>
  );
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
  nativeMacInstruction,
  browserPlatformHint,
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
        <RuntimeSummary
          context={runtimeContext}
          browserPlatformHint={browserPlatformHint}
          dockerNote={dockerNote}
          nativeMacInstruction={nativeMacInstruction}
        />
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
            <RuntimeSummary
              context={report.runtime_context}
              browserPlatformHint={browserPlatformHint}
              dockerNote={dockerNote}
              nativeMacInstruction={nativeMacInstruction}
            />
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
