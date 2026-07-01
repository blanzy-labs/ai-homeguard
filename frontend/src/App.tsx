import { useEffect, useState } from "react";
import {
  exportJsonReport,
  exportMarkdownReport,
  getDemoReport,
  getCombinedReport,
  getD3FENDGuidanceCatalog,
  getLocalDeviceReport,
  getLinuxLocalReport,
  getMacOSLocalReport,
  getQuestionnaire,
  getQuestionnaireReport,
  getRuntimeContext,
  getWindowsLocalReport,
  type HomeGuardReport,
  type CombinedReportResponse,
  type D3FENDCatalogResponse,
  type QuestionnaireSection,
  type QuestionnaireSubmission,
  type RuntimeContext,
} from "./api/client";
import { CombinedReportPanel } from "./components/CombinedReportPanel";
import { DemoDashboard } from "./components/DemoDashboard";
import { GuidanceCatalogPanel } from "./components/GuidanceCatalogPanel";
import { LocalAuditPanel } from "./components/LocalAuditPanel";
import { ModeCard } from "./components/ModeCard";
import { QuestionnaireResults } from "./components/QuestionnaireResults";
import { QuestionnaireScreen } from "./components/QuestionnaireScreen";
import { StatusPanel } from "./components/StatusPanel";

type FlowStep =
  | "welcome"
  | "safety"
  | "mode"
  | "questionnaire"
  | "results"
  | "full-questionnaire"
  | "full-options"
  | "combined-results"
  | "guidance"
  | "demo"
  | "local"
  | "windows"
  | "macos"
  | "linux";

type ReportState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; report: HomeGuardReport }
  | { state: "error"; message: string };

type CombinedReportState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; response: CombinedReportResponse }
  | { state: "error"; message: string };

type QuestionnaireState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; sections: QuestionnaireSection[] }
  | { state: "error"; message: string };

type RuntimeState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; context: RuntimeContext }
  | { state: "error"; message: string };

type GuidanceCatalogState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; catalog: D3FENDCatalogResponse }
  | { state: "error"; message: string };

const dockerRuntimeNote =
  "If running in Docker, results may reflect the container rather than the host computer.";

export default function App() {
  const [flowStep, setFlowStep] = useState<FlowStep>("welcome");
  const [acknowledged, setAcknowledged] = useState(false);
  const [demoReport, setDemoReport] = useState<ReportState>({ state: "idle" });
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireState>({ state: "idle" });
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<string, string>>({});
  const [fullReportAnswers, setFullReportAnswers] = useState<Record<string, string>>({});
  const [questionnaireReport, setQuestionnaireReport] = useState<ReportState>({ state: "idle" });
  const [combinedReport, setCombinedReport] = useState<CombinedReportState>({ state: "idle" });
  const [combinedSubmission, setCombinedSubmission] = useState<QuestionnaireSubmission | null>(null);
  const [includeLocalInCombined, setIncludeLocalInCombined] = useState(false);
  const [combinedLocalAcknowledged, setCombinedLocalAcknowledged] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const [guidanceCatalog, setGuidanceCatalog] = useState<GuidanceCatalogState>({ state: "idle" });
  const [localReport, setLocalReport] = useState<ReportState>({ state: "idle" });
  const [runtimeContext, setRuntimeContext] = useState<RuntimeState>({ state: "idle" });
  const [windowsReport, setWindowsReport] = useState<ReportState>({ state: "idle" });
  const [macosReport, setMacosReport] = useState<ReportState>({ state: "idle" });
  const [linuxReport, setLinuxReport] = useState<ReportState>({ state: "idle" });
  const [isSubmittingQuestionnaire, setIsSubmittingQuestionnaire] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadDemoReport() {
      if (flowStep !== "demo" || demoReport.state !== "idle") {
        return;
      }
      setDemoReport({ state: "loading" });
      try {
        const report = await getDemoReport();
        if (isMounted) {
          setDemoReport({ state: "ready", report });
        }
      } catch (error) {
        if (isMounted) {
          setDemoReport({
            state: "error",
            message: error instanceof Error ? error.message : "Demo report unavailable",
          });
        }
      }
    }

    void loadDemoReport();

    return () => {
      isMounted = false;
    };
  }, [demoReport.state, flowStep]);

  async function openQuestionnaire() {
    setFlowStep("questionnaire");
    if (questionnaire.state === "ready" || questionnaire.state === "loading") {
      return;
    }
    setQuestionnaire({ state: "loading" });
    try {
      const sections = await getQuestionnaire();
      setQuestionnaire({ state: "ready", sections });
    } catch (error) {
      setQuestionnaire({
        state: "error",
        message: error instanceof Error ? error.message : "Questionnaire unavailable",
      });
    }
  }

  async function ensureQuestionnaireLoaded() {
    if (questionnaire.state === "ready" || questionnaire.state === "loading") {
      return;
    }
    setQuestionnaire({ state: "loading" });
    try {
      const sections = await getQuestionnaire();
      setQuestionnaire({ state: "ready", sections });
    } catch (error) {
      setQuestionnaire({
        state: "error",
        message: error instanceof Error ? error.message : "Questionnaire unavailable",
      });
    }
  }

  async function openFullReportFlow() {
    setFlowStep("full-questionnaire");
    await ensureQuestionnaireLoaded();
  }

  async function openLocalAudit() {
    setFlowStep("local");
    if (runtimeContext.state === "ready" || runtimeContext.state === "loading") {
      return;
    }
    setRuntimeContext({ state: "loading" });
    try {
      const context = await getRuntimeContext();
      setRuntimeContext({ state: "ready", context });
    } catch (error) {
      setRuntimeContext({
        state: "error",
        message: error instanceof Error ? error.message : "Runtime context unavailable",
      });
    }
  }

  async function openGuidanceCatalog() {
    setFlowStep("guidance");
    if (guidanceCatalog.state === "ready" || guidanceCatalog.state === "loading") {
      return;
    }
    setGuidanceCatalog({ state: "loading" });
    try {
      const catalog = await getD3FENDGuidanceCatalog();
      setGuidanceCatalog({ state: "ready", catalog });
    } catch (error) {
      setGuidanceCatalog({
        state: "error",
        message: error instanceof Error ? error.message : "Guidance catalog unavailable",
      });
    }
  }

  async function submitQuestionnaire(submission: QuestionnaireSubmission) {
    setIsSubmittingQuestionnaire(true);
    setQuestionnaireReport({ state: "loading" });
    setFlowStep("results");
    try {
      const report = await getQuestionnaireReport(submission);
      setQuestionnaireReport({ state: "ready", report });
    } catch (error) {
      setQuestionnaireReport({
        state: "error",
        message: error instanceof Error ? error.message : "Questionnaire report unavailable",
      });
    } finally {
      setIsSubmittingQuestionnaire(false);
    }
  }

  function submitFullReportQuestionnaire(submission: QuestionnaireSubmission) {
    setCombinedSubmission(submission);
    setFlowStep("full-options");
  }

  async function buildCombinedReport() {
    if (!combinedSubmission) {
      setCombinedReport({ state: "error", message: "Questionnaire answers are required for the full report." });
      setFlowStep("combined-results");
      return;
    }
    if (includeLocalInCombined && !combinedLocalAcknowledged) {
      setCombinedReport({
        state: "error",
        message: "Please acknowledge the read-only local device audit before including local checks.",
      });
      return;
    }
    setCombinedReport({ state: "loading" });
    setExportStatus(null);
    setFlowStep("combined-results");
    try {
      const response = await getCombinedReport({
        include_questionnaire: true,
        include_local_device: includeLocalInCombined,
        questionnaire_submission: combinedSubmission,
        acknowledged_authorization: includeLocalInCombined ? combinedLocalAcknowledged : false,
      });
      setCombinedReport({ state: "ready", response });
    } catch (error) {
      setCombinedReport({
        state: "error",
        message: error instanceof Error ? error.message : "Combined report unavailable",
      });
    }
  }

  async function runWindowsLocalCheck() {
    setWindowsReport({ state: "loading" });
    try {
      const report = await getWindowsLocalReport();
      setWindowsReport({ state: "ready", report });
    } catch (error) {
      setWindowsReport({
        state: "error",
        message: error instanceof Error ? error.message : "Windows local report unavailable",
      });
    }
  }

  async function runLocalDeviceAudit() {
    setLocalReport({ state: "loading" });
    try {
      const report = await getLocalDeviceReport();
      setLocalReport({ state: "ready", report });
      if (report.runtime_context) {
        setRuntimeContext({ state: "ready", context: report.runtime_context });
      }
    } catch (error) {
      setLocalReport({
        state: "error",
        message: error instanceof Error ? error.message : "Local device report unavailable",
      });
    }
  }

  async function runMacOSLocalCheck() {
    setMacosReport({ state: "loading" });
    try {
      const report = await getMacOSLocalReport();
      setMacosReport({ state: "ready", report });
    } catch (error) {
      setMacosReport({
        state: "error",
        message: error instanceof Error ? error.message : "macOS local report unavailable",
      });
    }
  }

  async function runLinuxLocalCheck() {
    setLinuxReport({ state: "loading" });
    try {
      const report = await getLinuxLocalReport();
      setLinuxReport({ state: "ready", report });
    } catch (error) {
      setLinuxReport({
        state: "error",
        message: error instanceof Error ? error.message : "Linux local report unavailable",
      });
    }
  }

  async function exportMarkdown(report: HomeGuardReport) {
    try {
      const markdown = await exportMarkdownReport(report);
      downloadText("ai-homeguard-report.md", markdown, "text/markdown");
      setExportStatus("Markdown export created in your browser.");
    } catch (error) {
      setExportStatus(error instanceof Error ? error.message : "Markdown export unavailable");
    }
  }

  async function exportJson(report: HomeGuardReport) {
    try {
      const json = await exportJsonReport(report);
      downloadText("ai-homeguard-report.json", JSON.stringify(json, null, 2), "application/json");
      setExportStatus("JSON export created in your browser.");
    } catch (error) {
      setExportStatus(error instanceof Error ? error.message : "JSON export unavailable");
    }
  }

  function downloadText(filename: string, content: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  return (
    <main className="app-shell">
      <section className={flowStep === "welcome" ? "intro intro--welcome" : "intro intro--compact"}>
        <div className="brand-row">
          <span className="brand-mark" aria-hidden="true">
            HG
          </span>
          <p>Blanzy Labs AI app family</p>
        </div>
        <h1>AI HomeGuard</h1>
        <p className="subtitle">Local Home Security Audit MVP</p>
        <p className="safety-message">
          A defensive home cyber hygiene helper. Slice 8 adds local D3FEND-informed guidance to
          questionnaire, local device, combined, and exportable reports.
        </p>
        <span className="demo-badge">Safety-first local flow</span>
      </section>

      {flowStep === "welcome" && (
        <section className="welcome-panel" aria-labelledby="welcome-heading">
          <div>
            <p className="section-kicker">Welcome</p>
            <h2 id="welcome-heading">A calm checklist for home security basics</h2>
            <p className="muted">
              AI HomeGuard explains defensive steps in plain language and keeps this slice limited
              to local read-only checks, runtime context, demo data, questionnaire answers, and
              user-triggered report exports.
            </p>
          </div>
          <div className="welcome-actions">
            <button className="primary-button" type="button" onClick={() => setFlowStep("safety")}>
              Start Guided Flow
            </button>
            <button className="secondary-button" type="button" onClick={() => setFlowStep("demo")}>
              Open Demo Dashboard
            </button>
          </div>
        </section>
      )}

      {flowStep === "safety" && (
        <section className="safety-flow-panel" aria-labelledby="safety-flow-heading">
          <div className="flow-heading">
            <p className="section-kicker">Safety notes</p>
            <h2 id="safety-flow-heading">What this slice does and does not do</h2>
            <p className="muted">
              The goal is transparency first: you should always know when the app is using sample
              data, questionnaire answers, or future local checks.
            </p>
          </div>

          <ul className="safety-boundary-list">
            <li>Runs locally in your development environment.</li>
            <li>Auto-detects Windows, macOS, Linux, or unsupported runtimes.</li>
            <li>Uses read-only device checks for the detected runtime.</li>
            <li>Returns an unsupported-platform report when a check cannot run here.</li>
            <li>If running in Docker, results may reflect the container rather than the host.</li>
            <li>Does not request sudo, administrator escalation, or passwords.</li>
            <li>Does not exploit, attack, brute-force, or packet-sniff.</li>
            <li>Does not scan networks or public targets.</li>
            <li>Does not upload data or call an AI provider.</li>
            <li>Does not save reports automatically.</li>
            <li>Exports are created only when you click an export button.</li>
            <li>Questionnaire answers stay in this browser session and are not uploaded.</li>
            <li>Future network checks will require explicit authorization.</li>
          </ul>

          <label className="acknowledgement">
            <input
              type="checkbox"
              checked={acknowledged}
              onChange={(event) => setAcknowledged(event.target.checked)}
            />
            <span>
              I understand this is a defensive tool and I should only use it on devices and networks
              I own or am authorized to assess.
            </span>
          </label>

          <div className="flow-actions">
            <button className="secondary-button" type="button" onClick={() => setFlowStep("welcome")}>
              Back
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={!acknowledged}
              onClick={() => setFlowStep("mode")}
            >
              Continue
            </button>
          </div>
        </section>
      )}

      {flowStep === "mode" && (
        <section className="mode-panel" aria-labelledby="mode-heading">
          <div className="flow-heading">
            <p className="section-kicker">Choose mode</p>
            <h2 id="mode-heading">Pick what you want to explore</h2>
            <p className="muted">
              Device audits are read-only and platform-specific. Unsupported checks return a calm
              local report without running commands for the wrong operating system.
            </p>
          </div>
          <div className="mode-grid">
            <ModeCard
              title="Full HomeGuard Report"
              status="Available"
              description="Answer the home security questionnaire and optionally include read-only local device checks."
              onSelect={openFullReportFlow}
            />
            <ModeCard
              title="Local Device Audit"
              status="Available"
              description="AI HomeGuard will choose the right local checks for this runtime."
              onSelect={openLocalAudit}
            />
            <ModeCard
              title="Windows Device Audit"
              status="Advanced/manual"
              description="Manually run Windows posture checks for debugging or platform validation."
              onSelect={() => setFlowStep("windows")}
            />
            <ModeCard
              title="macOS Device Audit"
              status="Advanced/manual"
              description="Manually run macOS posture checks when the backend is running on a Mac."
              onSelect={() => setFlowStep("macos")}
            />
            <ModeCard
              title="Linux Device Audit"
              status="Advanced/manual"
              description="Manually run Linux posture checks, including container visibility in Docker."
              onSelect={() => setFlowStep("linux")}
            />
            <ModeCard
              title="Home Security Questionnaire"
              status="Available"
              description="Answer friendly checklist questions and see questionnaire-only findings."
              onSelect={openQuestionnaire}
            />
            <ModeCard
              title="Defensive Guidance Catalog"
              status="Available"
              description="Review the local D3FEND-informed educational guidance used in reports."
              onSelect={openGuidanceCatalog}
            />
            <ModeCard
              title="Demo Mode"
              status="Available"
              description="Review static sample findings from Slice 2."
              onSelect={() => setFlowStep("demo")}
            />
          </div>
        </section>
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Defensive guidance</p>
          <h2>Loading local catalog</h2>
          <p className="muted">Reading the bundled D3FEND-informed guidance catalog.</p>
        </section>
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Defensive guidance</p>
          <h2>Guidance catalog unavailable</h2>
          <p>{guidanceCatalog.message}</p>
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </section>
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "ready" && (
        <GuidanceCatalogPanel catalog={guidanceCatalog.catalog} onBackToModes={() => setFlowStep("mode")} />
      )}

      {flowStep === "questionnaire" && questionnaire.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Questionnaire</p>
          <h2>Loading checklist</h2>
          <p className="muted">Fetching local questionnaire questions from the backend.</p>
        </section>
      )}

      {flowStep === "questionnaire" && questionnaire.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Questionnaire</p>
          <h2>Checklist unavailable</h2>
          <p>{questionnaire.message}</p>
        </section>
      )}

      {flowStep === "questionnaire" && questionnaire.state === "ready" && (
        <QuestionnaireScreen
          sections={questionnaire.sections}
          answers={questionnaireAnswers}
          isSubmitting={isSubmittingQuestionnaire}
          onAnswerChange={(questionId, value) =>
            setQuestionnaireAnswers((current) => ({ ...current, [questionId]: value }))
          }
          onSubmit={submitQuestionnaire}
        />
      )}

      {flowStep === "full-questionnaire" && questionnaire.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Full report</p>
          <h2>Loading checklist</h2>
          <p className="muted">Fetching local questionnaire questions from the backend.</p>
        </section>
      )}

      {flowStep === "full-questionnaire" && questionnaire.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Full report</p>
          <h2>Checklist unavailable</h2>
          <p>{questionnaire.message}</p>
        </section>
      )}

      {flowStep === "full-questionnaire" && questionnaire.state === "ready" && (
        <QuestionnaireScreen
          sections={questionnaire.sections}
          answers={fullReportAnswers}
          isSubmitting={false}
          kicker="Full HomeGuard Report"
          heading="Start with the home security questionnaire"
          description="These answers create questionnaire findings for the combined report. No passwords, addresses, account names, device identifiers, or Wi-Fi join codes are requested."
          submitLabel="Continue to Local Audit Options"
          onAnswerChange={(questionId, value) =>
            setFullReportAnswers((current) => ({ ...current, [questionId]: value }))
          }
          onSubmit={submitFullReportQuestionnaire}
        />
      )}

      {flowStep === "full-options" && (
        <section className="questionnaire-panel" aria-labelledby="full-options-heading">
          <div className="flow-heading">
            <p className="section-kicker">Full report</p>
            <h2 id="full-options-heading">Choose report sources</h2>
            <p className="muted">
              The questionnaire is included. You can also add read-only local device checks. No
              network scan is run, no settings are changed, and no data is uploaded.
            </p>
          </div>

          <label className="acknowledgement">
            <input
              type="checkbox"
              checked={includeLocalInCombined}
              onChange={(event) => {
                setIncludeLocalInCombined(event.target.checked);
                if (!event.target.checked) {
                  setCombinedLocalAcknowledged(false);
                }
              }}
            />
            <span>Include read-only local device audit findings in the combined report.</span>
          </label>

          {includeLocalInCombined ? (
            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={combinedLocalAcknowledged}
                onChange={(event) => setCombinedLocalAcknowledged(event.target.checked)}
              />
              <span>
                I understand AI HomeGuard will run read-only local checks on this device. It will
                not change settings, scan the network, upload data, or attempt remediation.
              </span>
            </label>
          ) : null}

          <div className="flow-actions">
            <button className="secondary-button" type="button" onClick={() => setFlowStep("full-questionnaire")}>
              Back
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={includeLocalInCombined && !combinedLocalAcknowledged}
              onClick={buildCombinedReport}
            >
              Build Combined Report
            </button>
          </div>
        </section>
      )}

      {flowStep === "combined-results" && combinedReport.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Full report</p>
          <h2>Building combined report</h2>
          <p className="muted">Combining selected findings in memory.</p>
        </section>
      )}

      {flowStep === "combined-results" && combinedReport.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Full report</p>
          <h2>Combined report unavailable</h2>
          <p>{combinedReport.message}</p>
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </section>
      )}

      {flowStep === "combined-results" && combinedReport.state === "ready" && (
        <CombinedReportPanel
          response={combinedReport.response}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "results" && questionnaireReport.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Results</p>
          <h2>Building questionnaire report</h2>
          <p className="muted">Creating local questionnaire-derived findings.</p>
        </section>
      )}

      {flowStep === "results" && questionnaireReport.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Results</p>
          <h2>Questionnaire report unavailable</h2>
          <p>{questionnaireReport.message}</p>
        </section>
      )}

      {flowStep === "results" && questionnaireReport.state === "ready" && (
        <QuestionnaireResults
          report={questionnaireReport.report}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "demo" && demoReport.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Demo dashboard</p>
          <h2>Loading sample report</h2>
          <p className="muted">Fetching static demo findings from the local backend.</p>
        </section>
      )}

      {flowStep === "demo" && demoReport.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Demo dashboard</p>
          <h2>Sample report unavailable</h2>
          <p>{demoReport.message}</p>
        </section>
      )}

      {flowStep === "demo" && demoReport.state === "ready" && (
        <>
          <DemoDashboard report={demoReport.report} />
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </>
      )}

      {flowStep === "local" && (
        <>
          <LocalAuditPanel
            platformName="Local Device"
            panelKicker="Local Device Audit"
            heading="Auto-detected local device checks"
            description="AI HomeGuard will choose the right local checks for this runtime. Read-only checks only; no settings are changed, no network scan is run, and no data is uploaded."
            runLabel="Run Local Device Audit"
            loadingLabel="Running Local Device Audit"
            findingsHeading="Local Device Findings"
            unsupportedTitle="Local device checks are unavailable here"
            unsupportedBody="AI HomeGuard could not match this runtime to a supported local platform. You are seeing a safe limited-visibility result."
            runtimeContext={runtimeContext.state === "ready" ? runtimeContext.context : null}
            runtimeLoading={runtimeContext.state === "loading"}
            runtimeError={runtimeContext.state === "error" ? runtimeContext.message : null}
            dockerNote={dockerRuntimeNote}
            report={localReport.state === "ready" ? localReport.report : null}
            loading={localReport.state === "loading"}
            error={localReport.state === "error" ? localReport.message : null}
            onRun={runLocalDeviceAudit}
          />
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </>
      )}

      {flowStep === "windows" && (
        <>
          <LocalAuditPanel
            platformName="Windows"
            panelKicker="Windows Device Audit"
            heading="Read-only local Windows checks"
            description="This mode asks the local backend for Windows posture findings. No settings are changed, no network scan is run, and no data is uploaded."
            runLabel="Run Windows Local Check"
            loadingLabel="Running Read-Only Check"
            findingsHeading="Windows Findings"
            unsupportedTitle="Windows checks are unavailable here"
            unsupportedBody="Windows checks can only run when AI HomeGuard is running on a Windows computer. You are seeing a safe unsupported-platform result."
            dockerNote={dockerRuntimeNote}
            report={windowsReport.state === "ready" ? windowsReport.report : null}
            loading={windowsReport.state === "loading"}
            error={windowsReport.state === "error" ? windowsReport.message : null}
            onRun={runWindowsLocalCheck}
          />
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </>
      )}

      {flowStep === "macos" && (
        <>
          <LocalAuditPanel
            platformName="macOS"
            panelKicker="macOS Device Audit"
            heading="Read-only local macOS checks"
            description="This mode asks the local backend for macOS posture findings. No settings are changed, no network scan is run, and no data is uploaded."
            runLabel="Run macOS Local Check"
            loadingLabel="Running Read-Only Check"
            findingsHeading="macOS Findings"
            unsupportedTitle="macOS checks are unavailable here"
            unsupportedBody="macOS checks can only run when AI HomeGuard is running on a Mac. You are seeing a safe unsupported-platform result."
            dockerNote={dockerRuntimeNote}
            report={macosReport.state === "ready" ? macosReport.report : null}
            loading={macosReport.state === "loading"}
            error={macosReport.state === "error" ? macosReport.message : null}
            onRun={runMacOSLocalCheck}
          />
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </>
      )}

      {flowStep === "linux" && (
        <>
          <LocalAuditPanel
            platformName="Linux"
            panelKicker="Linux Device Audit"
            heading="Read-only local Linux checks"
            description="This mode asks the local backend for Linux posture findings. No settings are changed, no network scan is run, and no data is uploaded."
            runLabel="Run Linux Local Check"
            loadingLabel="Running Read-Only Check"
            findingsHeading="Linux Findings"
            unsupportedTitle="Linux checks are unavailable here"
            unsupportedBody="Linux checks can only run when AI HomeGuard is running on a Linux computer. You are seeing a safe unsupported-platform result."
            dockerNote={dockerRuntimeNote}
            report={linuxReport.state === "ready" ? linuxReport.report : null}
            loading={linuxReport.state === "loading"}
            error={linuxReport.state === "error" ? linuxReport.message : null}
            onRun={runLinuxLocalCheck}
          />
          <button className="secondary-button" type="button" onClick={() => setFlowStep("mode")}>
            Back to Modes
          </button>
        </>
      )}

      <StatusPanel />
    </main>
  );
}
