import type { CombinedReportResponse, HomeGuardReport } from "../api/client";
import { HomeGuardDashboard } from "./HomeGuardDashboard";

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
    <HomeGuardDashboard
      report={report}
      kicker="Full HomeGuard Report"
      heading="HomeGuard Dashboard"
      description="Your local HomeGuard check is summarized below with plain-English next steps."
      limitations={response.limitations}
      exportStatus={exportStatus}
      onExportMarkdown={onExportMarkdown}
      onExportJson={onExportJson}
      onBackToModes={onBackToModes}
      onClearReport={onClearReport}
    />
  );
}
