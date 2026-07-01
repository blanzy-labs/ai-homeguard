import type { CombinedReportResponse, HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type CombinedReportPanelProps = {
  response: CombinedReportResponse;
  exportStatus: string | null;
  onExportMarkdown: (report: HomeGuardReport) => void;
  onExportJson: (report: HomeGuardReport) => void;
  onBackToModes: () => void;
};

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function sourceLabel(report: HomeGuardReport) {
  const hasQuestionnaire = report.findings.some((finding) => finding.tags.includes("questionnaire"));
  const hasLocal = report.runtime_context !== null && report.runtime_context !== undefined;
  const hasLocalFinding = report.findings.some(
    (finding) =>
      finding.tags.includes("unsupported-platform") ||
      finding.evidence.some((evidence) => {
        const source = evidence.source.toLowerCase();
        return source.includes("local check") || source.includes("platform guard") || source.includes("runtime context");
      }),
  );
  if (hasQuestionnaire && (hasLocal || hasLocalFinding)) {
    return "questionnaire + local device";
  }
  if (hasLocal || hasLocalFinding) {
    return "local device";
  }
  return "questionnaire";
}

export function CombinedReportPanel({
  response,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onBackToModes,
}: CombinedReportPanelProps) {
  const report = response.report;

  return (
    <section className="results-panel" aria-labelledby="combined-results-heading">
      <div className="dashboard-summary">
        <div>
          <p className="section-kicker">Full HomeGuard Report</p>
          <h2 id="combined-results-heading">Combined HomeGuard Report</h2>
          <p className="muted">{report.disclaimer}</p>
          <p className="muted">Evidence source: {sourceLabel(report)}</p>
        </div>
        <div className="overall-status">
          <span>Overall status</span>
          <strong>{formatStatus(report.summary.overall_status)}</strong>
          {report.summary.overall_score !== null && report.summary.overall_score !== undefined ? (
            <p>{report.summary.overall_score}/100 review score</p>
          ) : null}
        </div>
      </div>

      <section className="action-plan" aria-labelledby="combined-actions-heading">
        <h2 id="combined-actions-heading">Top Recommended Actions</h2>
        {report.summary.top_actions.length ? (
          <ol>
            {report.summary.top_actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ol>
        ) : (
          <p className="muted">No priority actions were generated from the selected sources.</p>
        )}
      </section>

      {response.limitations.length ? (
        <section className="safety-notes" aria-labelledby="combined-limitations-heading">
          <h2 id="combined-limitations-heading">Limitations</h2>
          <ul>
            {response.limitations.map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="safety-notes" aria-labelledby="combined-safety-heading">
        <h2 id="combined-safety-heading">Safety Notes</h2>
        <ul>
          {report.safety_notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="export-panel" aria-labelledby="export-heading">
        <div>
          <h2 id="export-heading">Export</h2>
          <p className="muted">
            Exports are created only when you click an export button. Nothing is saved automatically
            or uploaded.
          </p>
        </div>
        <div className="export-actions">
          <button className="secondary-button" type="button" onClick={() => onExportMarkdown(report)}>
            Export Markdown
          </button>
          <button className="secondary-button" type="button" onClick={() => onExportJson(report)}>
            Export JSON
          </button>
        </div>
        {exportStatus ? <p className="runtime-note">{exportStatus}</p> : null}
      </section>

      <section className="findings-section" aria-labelledby="combined-findings-heading">
        <h2 id="combined-findings-heading">Findings</h2>
        <div className="findings-list">
          {report.findings.map((finding) => (
            <FindingCard key={`${finding.id}-${finding.evidence[0]?.source ?? "source"}`} finding={finding} />
          ))}
        </div>
      </section>

      <button className="secondary-button" type="button" onClick={onBackToModes}>
        Back to Modes
      </button>
    </section>
  );
}
