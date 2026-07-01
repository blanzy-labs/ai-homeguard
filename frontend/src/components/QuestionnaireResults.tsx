import type { HomeGuardReport } from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

type QuestionnaireResultsProps = {
  report: HomeGuardReport;
  onBackToModes: () => void;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onClearReport?: () => void;
};

export function QuestionnaireResults({
  report,
  onBackToModes,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onClearReport,
}: QuestionnaireResultsProps) {
  return (
    <ReportReviewPanel
      report={report}
      kicker="Questionnaire results"
      heading="HomeGuard Questionnaire Report"
      description="These findings are based on your questionnaire answers only. No device or network checks were run."
      scoreLabel="questionnaire score"
      findingsHeading="Questionnaire Findings"
      exportStatus={exportStatus}
      onExportMarkdown={onExportMarkdown}
      onExportJson={onExportJson}
      onBackToModes={onBackToModes}
      onClearReport={onClearReport}
    />
  );
}
