import type { HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";

type DemoDashboardProps = {
  report: HomeGuardReport;
};

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function DemoDashboard({ report }: DemoDashboardProps) {
  const counts = [
    { label: "Good", value: report.summary.good_count },
    { label: "Review", value: report.summary.review_count },
    { label: "Fix Soon", value: report.summary.fix_soon_count },
    { label: "Needs Attention", value: report.summary.needs_attention_count },
    { label: "Unable to Check", value: report.summary.unable_to_check_count },
  ];

  return (
    <section className="dashboard" aria-labelledby="dashboard-heading">
      <div className="dashboard-summary">
        <div>
          <p className="section-kicker">Demo dashboard</p>
          <h2 id="dashboard-heading">Sample HomeGuard Report</h2>
          <p className="muted">{report.disclaimer}</p>
        </div>
        <div className="overall-status">
          <span>Overall status</span>
          <strong>{formatStatus(report.summary.overall_status)}</strong>
          {report.summary.overall_score ? <p>{report.summary.overall_score}/100 sample score</p> : null}
        </div>
      </div>

      <div className="count-grid" aria-label="Finding counts">
        {counts.map((count) => (
          <div key={count.label}>
            <span>{count.label}</span>
            <strong>{count.value}</strong>
          </div>
        ))}
      </div>

      <section className="action-plan" aria-labelledby="action-plan-heading">
        <h2 id="action-plan-heading">Sample Action Plan</h2>
        <ol>
          {report.summary.top_actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ol>
      </section>

      <section className="safety-notes" aria-labelledby="safety-notes-heading">
        <h2 id="safety-notes-heading">Safety Notes</h2>
        <ul>
          {report.safety_notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="findings-section" aria-labelledby="findings-heading">
        <h2 id="findings-heading">Sample Findings</h2>
        <div className="findings-list">
          {report.findings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} />
          ))}
        </div>
      </section>
    </section>
  );
}
