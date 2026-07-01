import type { HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type QuestionnaireResultsProps = {
  report: HomeGuardReport;
  onBackToModes: () => void;
};

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function QuestionnaireResults({ report, onBackToModes }: QuestionnaireResultsProps) {
  return (
    <section className="results-panel" aria-labelledby="results-heading">
      <div className="dashboard-summary">
        <div>
          <p className="section-kicker">Questionnaire results</p>
          <h2 id="results-heading">HomeGuard Questionnaire Report</h2>
          <p className="muted">
            These findings are based on your questionnaire answers only. No device or network checks
            were run.
          </p>
        </div>
        <div className="overall-status">
          <span>Overall status</span>
          <strong>{formatStatus(report.summary.overall_status)}</strong>
          {report.summary.overall_score ? <p>{report.summary.overall_score}/100 questionnaire score</p> : null}
        </div>
      </div>

      <section className="action-plan" aria-labelledby="questionnaire-actions-heading">
        <h2 id="questionnaire-actions-heading">Suggested Next Steps</h2>
        {report.summary.top_actions.length ? (
          <ol>
            {report.summary.top_actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ol>
        ) : (
          <p className="muted">No questionnaire-based action items were created from these answers.</p>
        )}
      </section>

      <section className="safety-notes" aria-labelledby="questionnaire-safety-heading">
        <h2 id="questionnaire-safety-heading">Result Boundaries</h2>
        <ul>
          {report.safety_notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="findings-section" aria-labelledby="questionnaire-findings-heading">
        <h2 id="questionnaire-findings-heading">Questionnaire Findings</h2>
        <div className="findings-list">
          {report.findings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} />
          ))}
        </div>
      </section>

      <button className="secondary-button" type="button" onClick={onBackToModes}>
        Back to Modes
      </button>
    </section>
  );
}
