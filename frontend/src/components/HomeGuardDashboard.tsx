import type { Finding, HomeGuardReport } from "../api/client";
import { FindingCard } from "./FindingCard";
import {
  EmptyState,
  ExportPanel,
  LimitationsPanel,
  SafetyNotesPanel,
  StatusCounts,
} from "./ReportReviewPanel";
import { evidenceSourceLabel, overallStatusLabels } from "./reportLabels";

type CoverageStatus =
  | "Checked"
  | "Not checked"
  | "Needs your input"
  | "Limited by Docker/runtime"
  | "Not available on this platform";

type CoverageItem = {
  label: string;
  status: CoverageStatus;
  note: string;
};

type GroupedFindings = {
  label: string;
  findings: Finding[];
};

type HomeGuardDashboardProps = {
  report: HomeGuardReport;
  kicker: string;
  heading: string;
  description?: string;
  limitations?: string[];
  demoMode?: boolean;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onBackToModes?: () => void;
  onClearReport?: () => void;
};

export function HomeGuardDashboard({
  report,
  kicker,
  heading,
  description,
  limitations = [],
  demoMode = false,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onBackToModes,
  onClearReport,
}: HomeGuardDashboardProps) {
  const coverage = coverageItems(report, limitations, demoMode);
  const groups = groupedFindings(report.findings);
  const allLimitations = uniqueValues([...(report.runtime_context?.limitations ?? []), ...limitations]);
  const [doFirst, doNext, later] = actionGroups(report.summary.top_actions);

  return (
    <section className="homeguard-dashboard" aria-labelledby="homeguard-dashboard-heading">
      <div className="dashboard-hero">
        <div>
          <p className="section-kicker">{kicker}</p>
          <h2 id="homeguard-dashboard-heading">{heading}</h2>
          <p className="muted">{description ?? report.disclaimer}</p>
          {demoMode ? <p className="demo-data-note">Demo data - no checks were run.</p> : null}
        </div>
        <div className="dashboard-status">
          <span>Overall status</span>
          <strong>{overallStatusLabels[report.summary.overall_status]}</strong>
          {report.summary.overall_score !== null && report.summary.overall_score !== undefined ? (
            <p>{report.summary.overall_score}/100 HomeGuard score</p>
          ) : null}
        </div>
      </div>

      <section className="action-plan action-plan--primary" aria-labelledby="things-to-do-first-heading">
        <div>
          <p className="section-kicker">Next steps</p>
          <h2 id="things-to-do-first-heading">Things to Do First</h2>
        </div>
        {report.summary.top_actions.length ? (
          <ol>
            {report.summary.top_actions.slice(0, 3).map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ol>
        ) : (
          <EmptyState
            title="No urgent actions"
            message="HomeGuard did not find priority actions from the selected checks."
          />
        )}
      </section>

      <StatusCounts report={report} />

      <section className="coverage-panel" aria-labelledby="coverage-heading">
        <div>
          <p className="section-kicker">Coverage</p>
          <h2 id="coverage-heading">What HomeGuard checked</h2>
        </div>
        <div className="coverage-grid">
          {coverage.map((item) => (
            <article className={`coverage-card coverage-card--${coverageClass(item.status)}`} key={item.label}>
              <span>{item.status}</span>
              <strong>{item.label}</strong>
              <p>{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="dashboard-action-groups" aria-labelledby="action-plan-heading">
        <div>
          <p className="section-kicker">Action plan</p>
          <h2 id="action-plan-heading">Simple action plan</h2>
        </div>
        <ActionGroup title="Do first" actions={doFirst} fallback="Start with the highest-priority items above." />
        <ActionGroup title="Do next" actions={doNext} fallback="No second-step actions were generated." />
        <ActionGroup title="Review when you have time" actions={later} fallback="No extra review items were generated." />
      </section>

      <section className="findings-section" aria-labelledby="grouped-findings-heading">
        <div>
          <p className="section-kicker">Findings</p>
          <h2 id="grouped-findings-heading">Findings by area</h2>
        </div>
        {groups.length ? (
          <div className="grouped-findings">
            {groups.map((group) => (
              <section className="finding-group" key={group.label} aria-labelledby={`${slugify(group.label)}-heading`}>
                <h3 id={`${slugify(group.label)}-heading`}>{group.label}</h3>
                <div className="findings-list">
                  {group.findings.map((finding) => (
                    <FindingCard key={`${group.label}-${finding.id}`} finding={finding} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        ) : (
          <EmptyState title="No findings" message="No findings were generated from the selected checks." />
        )}
      </section>

      <details className="dashboard-detail-drawer">
        <summary>More Detail</summary>
        <div className="detail-stack">
          <LimitationsPanel limitations={allLimitations} />
          <SafetyNotesPanel notes={report.safety_notes} />
        </div>
      </details>

      <ExportPanel
        report={report}
        exportStatus={exportStatus}
        onExportMarkdown={onExportMarkdown}
        onExportJson={onExportJson}
      />

      <div className="flow-actions">
        {onBackToModes ? (
          <button className="secondary-button" type="button" onClick={onBackToModes}>
            Advanced Options
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

function ActionGroup({ title, actions, fallback }: { title: string; actions: string[]; fallback: string }) {
  return (
    <section className="action-group" aria-label={title}>
      <h3>{title}</h3>
      {actions.length ? (
        <ol>
          {actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ol>
      ) : (
        <p className="muted">{fallback}</p>
      )}
    </section>
  );
}

function actionGroups(actions: string[]) {
  return [actions.slice(0, 3), actions.slice(3, 5), actions.slice(5)] as const;
}

function coverageItems(report: HomeGuardReport, limitations: string[], demoMode: boolean): CoverageItem[] {
  const sources = report.findings.map(evidenceSourceLabel);
  const hasDevice = sources.some((source) => source === "Local Device Check" || source === "Runtime Context");
  const hasQuestions = sources.includes("Questionnaire");
  const hasNetwork = sources.includes("Passive Network Awareness");
  const hasInventory = sources.some((source) => source.includes("Device Inventory"));
  const hasCouldNotCheck = sources.includes("Could Not Check");
  const hasRouterGuidance = report.findings.some((finding) => {
    const tags = finding.tags.map((tag) => tag.toLowerCase());
    return tags.includes("router") || finding.category.toLowerCase().includes("router");
  });
  const dockerLimited =
    report.runtime_context?.runtime_environment === "docker" ||
    limitations.some((limitation) => limitation.toLowerCase().includes("container"));

  if (demoMode) {
    return [
      { label: "Device checks", status: "Not checked", note: "Demo data only; no local checks were run." },
      { label: "Questionnaire answers", status: "Checked", note: "Sample questionnaire findings are included." },
      { label: "Passive network awareness", status: "Not checked", note: "No real network context was requested." },
      { label: "Device inventory", status: "Checked", note: "Sample home device findings are included." },
      { label: "Router guidance", status: "Checked", note: "Sample router and Wi-Fi findings are included." },
    ];
  }

  return [
    {
      label: "Device checks",
      status: dockerLimited
        ? "Limited by Docker/runtime"
        : hasDevice
          ? "Checked"
          : hasCouldNotCheck
            ? "Not available on this platform"
            : "Not checked",
      note: dockerLimited
        ? "The backend appears to be in a container. For host-level Mac checks, run the backend natively."
        : hasDevice
          ? "Read-only local checks were included when available."
          : hasCouldNotCheck
            ? "This runtime cannot safely run the requested local check."
          : "Device checks were not included in this run.",
    },
    {
      label: "Questionnaire answers",
      status: hasQuestions ? "Checked" : "Needs your input",
      note: hasQuestions
        ? "Your quick answers helped fill account, backup, router, and Wi-Fi basics."
        : "Answer quick questions to include account, backup, router, and Wi-Fi basics.",
    },
    {
      label: "Passive network awareness",
      status: hasNetwork ? "Checked" : "Not checked",
      note: hasNetwork
        ? "Passive local network context was included with authorization."
        : "Passive network awareness is optional and requires separate authorization.",
    },
    {
      label: "Device inventory",
      status: hasInventory ? "Checked" : "Needs your input",
      note: hasInventory ? "Device inventory findings were included." : "Add manual/router list entries to include this area.",
    },
    {
      label: "Router guidance",
      status: hasRouterGuidance || hasQuestions || hasInventory ? "Checked" : "Needs your input",
      note:
        hasRouterGuidance || hasQuestions || hasInventory
          ? "Router and Wi-Fi guidance was included from the selected inputs."
          : "Use quick questions or device inventory to include router guidance.",
    },
  ];
}

function groupedFindings(findings: Finding[]): GroupedFindings[] {
  const groups = new Map<string, Finding[]>();
  findings.forEach((finding) => {
    const group = findingGroup(finding);
    groups.set(group, [...(groups.get(group) ?? []), finding]);
  });
  return Array.from(groups.entries()).map(([label, groupFindings]) => ({ label, findings: groupFindings }));
}

function findingGroup(finding: Finding) {
  const tags = finding.tags.map((tag) => tag.toLowerCase());
  const category = finding.category.toLowerCase();
  const source = evidenceSourceLabel(finding);

  if (source === "Passive Network Awareness" || tags.includes("network-awareness")) {
    return "Network Awareness";
  }
  if (tags.includes("router") || category.includes("router")) {
    return "Router & Wi-Fi";
  }
  if (tags.includes("accounts") || tags.includes("passwords") || tags.includes("mfa")) {
    return "Accounts";
  }
  if (tags.includes("backup")) {
    return "Backups";
  }
  if (tags.includes("device-inventory") || tags.includes("iot") || source.includes("Device Inventory")) {
    return "Smart Devices";
  }
  if (finding.platform === "windows" || finding.platform === "macos" || finding.platform === "linux") {
    return "This Device";
  }
  return "Other";
}

function coverageClass(status: CoverageStatus) {
  return status.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-$/, "");
}

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function uniqueValues(values: string[]) {
  return values.filter((value, index) => values.indexOf(value) === index);
}
