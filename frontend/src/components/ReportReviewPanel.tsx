import { useMemo, useState } from "react";
import type { Finding, FindingStatus, HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";
import { evidenceSourceLabel, formatValue, overallStatusLabels, statusLabels, statusPriority } from "./reportLabels";

type ReportReviewPanelProps = {
  report: HomeGuardReport;
  kicker: string;
  heading: string;
  description?: string;
  scoreLabel?: string;
  findingsHeading?: string;
  limitations?: string[];
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onBackToModes?: () => void;
  onClearReport?: () => void;
};

type SortMode = "priority" | "status" | "source" | "title";

const statusOptions: Array<{ value: "all" | FindingStatus; label: string }> = [
  { value: "all", label: "All statuses" },
  { value: "good", label: "Good" },
  { value: "review", label: "Review" },
  { value: "fix_soon", label: "Fix Soon" },
  { value: "needs_attention", label: "Needs Attention" },
  { value: "unable_to_check", label: "Unable to Check" },
];

export function ReportSummaryCard({ report, kicker, heading, description, scoreLabel }: ReportReviewPanelProps) {
  return (
    <div className="dashboard-summary">
      <div>
        <p className="section-kicker">{kicker}</p>
        <h2 id="report-review-heading">{heading}</h2>
        <p className="muted">{description ?? report.disclaimer}</p>
        {description ? <p className="muted">{report.disclaimer}</p> : null}
      </div>
      <div className="overall-status">
        <span>Overall posture</span>
        <strong>{overallStatusLabels[report.summary.overall_status]}</strong>
        {report.summary.overall_score !== null && report.summary.overall_score !== undefined ? (
          <p>{report.summary.overall_score}/100 {scoreLabel ?? "review score"}</p>
        ) : null}
      </div>
    </div>
  );
}

export function StatusCounts({ report }: { report: HomeGuardReport }) {
  const counts = [
    { label: "Good", value: report.summary.good_count },
    { label: "Review", value: report.summary.review_count },
    { label: "Fix Soon", value: report.summary.fix_soon_count },
    { label: "Needs Attention", value: report.summary.needs_attention_count },
    { label: "Unable to Check", value: report.summary.unable_to_check_count },
  ];

  return (
    <div className="count-grid" aria-label="Finding status counts">
      {counts.map((count) => (
        <div key={count.label}>
          <span>{count.label}</span>
          <strong>{count.value}</strong>
        </div>
      ))}
    </div>
  );
}

export function TopActionsList({ actions }: { actions: string[] }) {
  return (
    <section className="action-plan" aria-labelledby="top-actions-heading">
      <h2 id="top-actions-heading">Top Recommended Actions</h2>
      {actions.length ? (
        <ol>
          {actions.slice(0, 5).map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ol>
      ) : (
        <EmptyState
          title="No priority actions"
          message="No priority actions were generated from the selected report sources."
        />
      )}
    </section>
  );
}

export function FindingFilters({
  statusFilter,
  platformFilter,
  sourceFilter,
  sortMode,
  showGood,
  platforms,
  sources,
  onStatusChange,
  onPlatformChange,
  onSourceChange,
  onSortChange,
  onShowGoodChange,
}: {
  statusFilter: "all" | FindingStatus;
  platformFilter: string;
  sourceFilter: string;
  sortMode: SortMode;
  showGood: boolean;
  platforms: string[];
  sources: string[];
  onStatusChange: (value: "all" | FindingStatus) => void;
  onPlatformChange: (value: string) => void;
  onSourceChange: (value: string) => void;
  onSortChange: (value: SortMode) => void;
  onShowGoodChange: (value: boolean) => void;
}) {
  return (
    <section className="finding-filters" aria-labelledby="finding-filters-heading">
      <div>
        <p className="section-kicker">Review controls</p>
        <h2 id="finding-filters-heading">Filter findings</h2>
      </div>
      <div className="filter-grid">
        <label className="form-field">
          <span>Status</span>
          <select value={statusFilter} onChange={(event) => onStatusChange(event.target.value as "all" | FindingStatus)}>
            {statusOptions.map((option) => (
              <option value={option.value} key={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span>Platform</span>
          <select value={platformFilter} onChange={(event) => onPlatformChange(event.target.value)}>
            <option value="all">All platforms</option>
            {platforms.map((platform) => (
              <option value={platform} key={platform}>
                {formatValue(platform)}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span>Evidence source</span>
          <select value={sourceFilter} onChange={(event) => onSourceChange(event.target.value)}>
            <option value="all">All sources</option>
            {sources.map((source) => (
              <option value={source} key={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span>Sort</span>
          <select value={sortMode} onChange={(event) => onSortChange(event.target.value as SortMode)}>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="source">Evidence source</option>
            <option value="title">Title</option>
          </select>
        </label>
      </div>
      <label className="filter-checkbox">
        <input type="checkbox" checked={showGood} onChange={(event) => onShowGoodChange(event.target.checked)} />
        <span>Show good findings</span>
      </label>
    </section>
  );
}

export function LimitationsPanel({ limitations }: { limitations: string[] }) {
  if (!limitations.length) {
    return null;
  }
  return (
    <section className="safety-notes" aria-labelledby="limitations-heading">
      <h2 id="limitations-heading">Limitations</h2>
      <ul>
        {limitations.map((limitation) => (
          <li key={limitation}>{limitation}</li>
        ))}
      </ul>
    </section>
  );
}

export function SafetyNotesPanel({ notes }: { notes: string[] }) {
  return (
    <section className="safety-notes" aria-labelledby="safety-notes-heading">
      <h2 id="safety-notes-heading">Safety Notes</h2>
      {notes.length ? (
        <ul>
          {notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      ) : (
        <EmptyState title="No safety notes" message="This report did not include extra safety notes." />
      )}
    </section>
  );
}

export function ExportPanel({
  report,
  exportStatus,
  onExportMarkdown,
  onExportJson,
}: {
  report: HomeGuardReport;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
}) {
  if (!onExportMarkdown && !onExportJson) {
    return null;
  }
  return (
    <section className="export-panel" aria-labelledby="export-heading">
      <div>
        <h2 id="export-heading">Export and Review</h2>
        <p className="muted">
          Export Markdown or JSON only when you click. Nothing is saved automatically or uploaded.
          Review exports before sharing.
        </p>
      </div>
      <div className="export-actions">
        {onExportMarkdown ? (
          <button className="secondary-button" type="button" onClick={() => onExportMarkdown(report)}>
            Export Markdown
          </button>
        ) : null}
        {onExportJson ? (
          <button className="secondary-button" type="button" onClick={() => onExportJson(report)}>
            Export JSON
          </button>
        ) : null}
      </div>
      {exportStatus ? <p className="runtime-note" role="status">{exportStatus}</p> : null}
    </section>
  );
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  );
}

export function ErrorState({
  kicker,
  title,
  message,
  onBackToModes,
}: {
  kicker: string;
  title: string;
  message: string;
  onBackToModes?: () => void;
}) {
  return (
    <section className="loading-panel loading-panel--error">
      <p className="section-kicker">{kicker}</p>
      <h2>{title}</h2>
      <p>{message}</p>
      {onBackToModes ? (
        <button className="secondary-button" type="button" onClick={onBackToModes}>
          Back to Modes
        </button>
      ) : null}
    </section>
  );
}

export function LoadingState({ kicker, title, message }: { kicker: string; title: string; message: string }) {
  return (
    <section className="loading-panel" aria-live="polite">
      <p className="section-kicker">{kicker}</p>
      <h2>{title}</h2>
      <p className="muted">{message}</p>
    </section>
  );
}

export function ReportReviewPanel({
  report,
  kicker,
  heading,
  description,
  scoreLabel,
  findingsHeading = "Findings",
  limitations = [],
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onBackToModes,
  onClearReport,
}: ReportReviewPanelProps) {
  const [statusFilter, setStatusFilter] = useState<"all" | FindingStatus>("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [sortMode, setSortMode] = useState<SortMode>("priority");
  const [showGood, setShowGood] = useState(true);

  const platforms = useMemo(() => _unique(report.findings.map((finding) => finding.platform)), [report.findings]);
  const sources = useMemo(() => _unique(report.findings.map(evidenceSourceLabel)), [report.findings]);

  const filteredFindings = useMemo(() => {
    return report.findings
      .filter((finding) => statusFilter === "all" || finding.status === statusFilter)
      .filter((finding) => platformFilter === "all" || finding.platform === platformFilter)
      .filter((finding) => sourceFilter === "all" || evidenceSourceLabel(finding) === sourceFilter)
      .filter((finding) => showGood || finding.status !== "good")
      .sort((left, right) => compareFindings(left, right, sortMode));
  }, [platformFilter, report.findings, showGood, sortMode, sourceFilter, statusFilter]);

  return (
    <section className="results-panel report-review" aria-labelledby="report-review-heading">
      <ReportSummaryCard
        report={report}
        kicker={kicker}
        heading={heading}
        description={description}
        scoreLabel={scoreLabel}
      />
      <StatusCounts report={report} />
      <TopActionsList actions={report.summary.top_actions} />
      <FindingFilters
        statusFilter={statusFilter}
        platformFilter={platformFilter}
        sourceFilter={sourceFilter}
        sortMode={sortMode}
        showGood={showGood}
        platforms={platforms}
        sources={sources}
        onStatusChange={setStatusFilter}
        onPlatformChange={setPlatformFilter}
        onSourceChange={setSourceFilter}
        onSortChange={setSortMode}
        onShowGoodChange={setShowGood}
      />
      <section className="findings-section" aria-labelledby="report-findings-heading">
        <h2 id="report-findings-heading">{findingsHeading}</h2>
        {filteredFindings.length ? (
          <div className="findings-list">
            {filteredFindings.map((finding) => (
              <FindingCard key={`${finding.id}-${finding.evidence[0]?.source ?? "source"}`} finding={finding} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No matching findings"
            message="Adjust the filters or turn on good findings to review more of the report."
          />
        )}
      </section>
      <LimitationsPanel limitations={limitations} />
      <SafetyNotesPanel notes={report.safety_notes} />
      <ExportPanel
        report={report}
        exportStatus={exportStatus}
        onExportMarkdown={onExportMarkdown}
        onExportJson={onExportJson}
      />
      <div className="flow-actions">
        {onBackToModes ? (
          <button className="secondary-button" type="button" onClick={onBackToModes}>
            Back to Modes
          </button>
        ) : null}
        {onClearReport ? (
          <button className="secondary-button" type="button" onClick={onClearReport}>
            Clear Current Report
          </button>
        ) : null}
      </div>
    </section>
  );
}

function compareFindings(left: Finding, right: Finding, sortMode: SortMode) {
  if (sortMode === "status" || sortMode === "priority") {
    const statusCompare = statusPriority[left.status] - statusPriority[right.status];
    if (statusCompare !== 0) {
      return statusCompare;
    }
  }
  if (sortMode === "source") {
    const sourceCompare = evidenceSourceLabel(left).localeCompare(evidenceSourceLabel(right));
    if (sourceCompare !== 0) {
      return sourceCompare;
    }
  }
  return left.home_title.localeCompare(right.home_title);
}

function _unique(values: string[]) {
  return values.filter((value, index) => values.indexOf(value) === index);
}
