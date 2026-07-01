import type { HomeGuardReport } from "../api/client";
import { HomeGuardDashboard } from "./HomeGuardDashboard";

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
    <HomeGuardDashboard
      report={report}
      kicker="Demo dashboard"
      heading="Sample HomeGuard Dashboard"
      description="Demo data shows how the dashboard works. No checks were run."
      demoMode
      exportStatus={exportStatus}
      onExportMarkdown={onExportMarkdown}
      onExportJson={onExportJson}
      onBackToModes={onBackToModes}
      onClearReport={onClearReport}
    />
  );
}
