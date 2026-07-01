import type { HomeGuardReport } from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

type DemoDashboardProps = {
  report: HomeGuardReport;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onBackToModes?: () => void;
  onClearReport?: () => void;
};

export function DemoDashboard({
  report,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onBackToModes,
  onClearReport,
}: DemoDashboardProps) {
  return (
    <ReportReviewPanel
      report={report}
      kicker="Demo dashboard"
      heading="Sample HomeGuard Report"
      scoreLabel="sample score"
      findingsHeading="Sample Findings"
      exportStatus={exportStatus}
      onExportMarkdown={onExportMarkdown}
      onExportJson={onExportJson}
      onBackToModes={onBackToModes}
      onClearReport={onClearReport}
    />
  );
}
