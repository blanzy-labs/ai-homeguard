import type { CombinedReportResponse, HomeGuardReport } from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

type CombinedReportPanelProps = {
  response: CombinedReportResponse;
  exportStatus: string | null;
  onExportMarkdown: (report: HomeGuardReport) => void;
  onExportJson: (report: HomeGuardReport) => void;
  onBackToModes: () => void;
  onClearReport?: () => void;
};

export function CombinedReportPanel({
  response,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onBackToModes,
  onClearReport,
}: CombinedReportPanelProps) {
  const report = response.report;

  return (
    <ReportReviewPanel
      report={report}
      kicker="Full HomeGuard Report"
      heading="Combined HomeGuard Report"
      scoreLabel="review score"
      limitations={response.limitations}
      exportStatus={exportStatus}
      onExportMarkdown={onExportMarkdown}
      onExportJson={onExportJson}
      onBackToModes={onBackToModes}
      onClearReport={onClearReport}
    />
  );
}
