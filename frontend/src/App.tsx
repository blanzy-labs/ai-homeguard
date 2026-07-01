import { useEffect, useState } from "react";
import {
  exportJsonReport,
  exportMarkdownReport,
  getDemoReport,
  getDemoDeviceInventory,
  getDeviceInventoryReport,
  getCombinedReport,
  getD3FENDGuidanceCatalog,
  getLocalDeviceReport,
  getLinuxLocalReport,
  getMacOSLocalReport,
  getNetworkAwarenessReport,
  getQuestionnaire,
  getQuestionnaireReport,
  getRouterGuidance,
  getRuntimeContext,
  getWindowsLocalReport,
  type DeviceInventorySubmission,
  type HomeGuardReport,
  type CombinedReportResponse,
  type D3FENDCatalogResponse,
  type QuestionnaireSection,
  type QuestionnaireSubmission,
  type RouterGuidanceResponse,
  type RuntimeContext,
} from "./api/client";
import { CombinedReportPanel } from "./components/CombinedReportPanel";
import { DemoDashboard } from "./components/DemoDashboard";
import { DeviceInventoryPanel } from "./components/DeviceInventoryPanel";
import { GuidanceCatalogPanel } from "./components/GuidanceCatalogPanel";
import { LocalAuditPanel } from "./components/LocalAuditPanel";
import { ModeCard } from "./components/ModeCard";
import { NetworkAwarenessPanel } from "./components/NetworkAwarenessPanel";
import { QuestionnaireResults } from "./components/QuestionnaireResults";
import { QuestionnaireScreen } from "./components/QuestionnaireScreen";
import { ErrorState, LoadingState } from "./components/ReportReviewPanel";
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
  | "network"
  | "inventory"
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

type RouterGuidanceState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; guidance: RouterGuidanceResponse }
  | { state: "error"; message: string };

const dockerRuntimeNote =
  "If running in Docker, results may reflect the container rather than the host computer.";

function createEmptyDeviceInventorySubmission(): DeviceInventorySubmission {
  return {
    mode: "manual",
    acknowledged_manual: true,
    devices: [],
    user_notes: "",
  };
}

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
  const [includeNetworkInCombined, setIncludeNetworkInCombined] = useState(false);
  const [combinedNetworkAcknowledged, setCombinedNetworkAcknowledged] = useState(false);
  const [includeDeviceInventoryInCombined, setIncludeDeviceInventoryInCombined] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);
  const [guidanceCatalog, setGuidanceCatalog] = useState<GuidanceCatalogState>({ state: "idle" });
  const [networkReport, setNetworkReport] = useState<ReportState>({ state: "idle" });
  const [networkAcknowledged, setNetworkAcknowledged] = useState(false);
  const [deviceInventorySubmission, setDeviceInventorySubmission] = useState<DeviceInventorySubmission>(
    createEmptyDeviceInventorySubmission,
  );
  const [deviceInventoryReport, setDeviceInventoryReport] = useState<ReportState>({ state: "idle" });
  const [routerGuidance, setRouterGuidance] = useState<RouterGuidanceState>({ state: "idle" });
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
      setExportStatus(null);
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
    setExportStatus(null);
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
    setExportStatus(null);
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
    setExportStatus(null);
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
    setExportStatus(null);
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

  function openNetworkAwareness() {
    setExportStatus(null);
    setFlowStep("network");
  }

  async function openDeviceInventory() {
    setFlowStep("inventory");
    setExportStatus(null);
    if (routerGuidance.state === "ready" || routerGuidance.state === "loading") {
      return;
    }
    setRouterGuidance({ state: "loading" });
    try {
      const guidance = await getRouterGuidance();
      setRouterGuidance({ state: "ready", guidance });
    } catch (error) {
      setRouterGuidance({
        state: "error",
        message: error instanceof Error ? error.message : "Router guidance unavailable",
      });
    }
  }

  async function submitQuestionnaire(submission: QuestionnaireSubmission) {
    setIsSubmittingQuestionnaire(true);
    setQuestionnaireReport({ state: "loading" });
    setExportStatus(null);
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
    setExportStatus(null);
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
    if (includeNetworkInCombined && !combinedNetworkAcknowledged) {
      setCombinedReport({
        state: "error",
        message: "Please acknowledge passive local network awareness before including network context.",
      });
      return;
    }
    if (includeDeviceInventoryInCombined && deviceInventorySubmission.devices.length === 0) {
      setCombinedReport({
        state: "error",
        message: "Add manual devices or load demo inventory before including Device Inventory Helper findings.",
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
        include_network_awareness: includeNetworkInCombined,
        include_device_inventory: includeDeviceInventoryInCombined,
        questionnaire_submission: combinedSubmission,
        acknowledged_authorization: includeLocalInCombined ? combinedLocalAcknowledged : false,
        network_authorization: includeNetworkInCombined
          ? {
              acknowledged: combinedNetworkAcknowledged,
              scope: "home_network",
              statement_version: "v0.1.0-slice-9",
            }
          : null,
        device_inventory_submission: includeDeviceInventoryInCombined ? deviceInventorySubmission : null,
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
    setExportStatus(null);
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
    setExportStatus(null);
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

  async function runNetworkAwareness() {
    if (!networkAcknowledged) {
      setNetworkReport({
        state: "error",
        message: "Network awareness requires authorization acknowledgement.",
      });
      return;
    }
    setNetworkReport({ state: "loading" });
    setExportStatus(null);
    try {
      const report = await getNetworkAwarenessReport({
        acknowledged: true,
        scope: "home_network",
        statement_version: "v0.1.0-slice-9",
      });
      setNetworkReport({ state: "ready", report });
    } catch (error) {
      setNetworkReport({
        state: "error",
        message: error instanceof Error ? error.message : "Network awareness report unavailable",
      });
    }
  }

  async function loadDemoDeviceInventory() {
    setDeviceInventoryReport({ state: "loading" });
    setExportStatus(null);
    try {
      const demo = await getDemoDeviceInventory();
      setDeviceInventorySubmission(demo.submission);
      setDeviceInventoryReport({ state: "ready", report: demo.report });
    } catch (error) {
      setDeviceInventoryReport({
        state: "error",
        message: error instanceof Error ? error.message : "Demo device inventory unavailable",
      });
    }
  }

  async function runDeviceInventoryReport() {
    if (deviceInventorySubmission.devices.length === 0) {
      setDeviceInventoryReport({
        state: "error",
        message: "Add a manual device or load demo inventory before building the report.",
      });
      return;
    }
    setDeviceInventoryReport({ state: "loading" });
    setExportStatus(null);
    try {
      const report = await getDeviceInventoryReport({
        ...deviceInventorySubmission,
        acknowledged_manual: true,
      });
      setDeviceInventoryReport({ state: "ready", report });
    } catch (error) {
      setDeviceInventoryReport({
        state: "error",
        message: error instanceof Error ? error.message : "Device inventory report unavailable",
      });
    }
  }

  async function runMacOSLocalCheck() {
    setMacosReport({ state: "loading" });
    setExportStatus(null);
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
    setExportStatus(null);
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
    setExportStatus("Creating Markdown export in your browser.");
    try {
      const markdown = await exportMarkdownReport(report);
      downloadText("ai-homeguard-report.md", markdown, "text/markdown");
      setExportStatus("Markdown export created in your browser.");
    } catch (error) {
      setExportStatus(error instanceof Error ? error.message : "Markdown export unavailable");
    }
  }

  async function exportJson(report: HomeGuardReport) {
    setExportStatus("Creating JSON export in your browser.");
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

  function clearCurrentReport() {
    setExportStatus(null);
    let shouldReturnToModes = false;
    if (flowStep === "demo") {
      setDemoReport({ state: "idle" });
      shouldReturnToModes = true;
    }
    if (flowStep === "results") {
      setQuestionnaireReport({ state: "idle" });
      shouldReturnToModes = true;
    }
    if (flowStep === "combined-results") {
      setCombinedReport({ state: "idle" });
      shouldReturnToModes = true;
    }
    if (flowStep === "network") {
      setNetworkReport({ state: "idle" });
    }
    if (flowStep === "inventory") {
      setDeviceInventoryReport({ state: "idle" });
    }
    if (flowStep === "local") {
      setLocalReport({ state: "idle" });
    }
    if (flowStep === "windows") {
      setWindowsReport({ state: "idle" });
    }
    if (flowStep === "macos") {
      setMacosReport({ state: "idle" });
    }
    if (flowStep === "linux") {
      setLinuxReport({ state: "idle" });
    }
    if (shouldReturnToModes) {
      setFlowStep("mode");
    }
  }

  function startOver() {
    setFlowStep("welcome");
    setAcknowledged(false);
    setQuestionnaire({ state: "idle" });
    setQuestionnaireAnswers({});
    setFullReportAnswers({});
    setCombinedSubmission(null);
    setIncludeLocalInCombined(false);
    setCombinedLocalAcknowledged(false);
    setIncludeNetworkInCombined(false);
    setCombinedNetworkAcknowledged(false);
    setIncludeDeviceInventoryInCombined(false);
    setNetworkAcknowledged(false);
    setDeviceInventorySubmission(createEmptyDeviceInventorySubmission());
    setGuidanceCatalog({ state: "idle" });
    setRouterGuidance({ state: "idle" });
    setRuntimeContext({ state: "idle" });
    setIsSubmittingQuestionnaire(false);
    setDemoReport({ state: "idle" });
    setQuestionnaireReport({ state: "idle" });
    setCombinedReport({ state: "idle" });
    setNetworkReport({ state: "idle" });
    setDeviceInventoryReport({ state: "idle" });
    setLocalReport({ state: "idle" });
    setWindowsReport({ state: "idle" });
    setMacosReport({ state: "idle" });
    setLinuxReport({ state: "idle" });
    setExportStatus(null);
  }

  return (
    <main className="app-shell">
      <section className={flowStep === "welcome" ? "intro intro--welcome" : "intro intro--compact"}>
        <div className="brand-row">
          <div className="brand-identity">
            <span className="brand-mark" aria-hidden="true">
              HG
            </span>
            <p>Blanzy Labs AI app family</p>
          </div>
          {flowStep !== "welcome" ? (
            <button className="secondary-button secondary-button--compact" type="button" onClick={startOver}>
              Start Over
            </button>
          ) : null}
        </div>
        <h1>AI HomeGuard</h1>
        <p className="subtitle">Local Home Security Audit MVP</p>
        <p className="safety-message">
          A defensive home cyber hygiene helper. Slice 11 polishes report review, evidence labels,
          export controls, and calm safety copy without adding new checks or persistence.
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
              data, questionnaire answers, manual inventory, passive network context, or read-only
              local checks.
            </p>
          </div>

          <ul className="safety-boundary-list">
            <li>Runs locally in your development environment.</li>
            <li>Auto-detects Windows, macOS, Linux, or unsupported runtimes.</li>
            <li>Read-only local checks.</li>
            <li>No settings are changed.</li>
            <li>Returns an unsupported-platform report when a check cannot run here.</li>
            <li>If running in Docker, results may reflect the container rather than the host.</li>
            <li>Does not request sudo, administrator escalation, or passwords.</li>
            <li>Does not exploit, attack, brute-force, or packet-sniff.</li>
            <li>Does not scan networks or public targets.</li>
            <li>Network awareness uses passive local context only after explicit authorization.</li>
            <li>Network awareness does not run active discovery, port scans, or packet capture.</li>
            <li>Device inventory is manual/demo only and does not discover devices automatically.</li>
            <li>Device inventory does not ask for router credentials, IP addresses, MAC addresses, or hostnames.</li>
            <li>Does not upload data or call an AI provider.</li>
            <li>Does not save reports automatically.</li>
            <li>Exports are created only when you click an export button.</li>
            <li>Questionnaire answers stay in this browser session and are not uploaded.</li>
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
              Full HomeGuard Report is the recommended path. Read-only local checks. No settings are
              changed. No network scan is run. No data is uploaded.
            </p>
          </div>
          <div className="mode-sections">
            <section className="mode-group mode-group--recommended" aria-labelledby="recommended-mode-heading">
              <div className="mode-group__header">
                <p className="section-kicker">Recommended path</p>
                <h3 id="recommended-mode-heading">Start with the full report</h3>
              </div>
              <div className="mode-grid mode-grid--single">
                <ModeCard
                  title="Full HomeGuard Report"
                  status="Recommended"
                  variant="recommended"
                  description="Answer the home security questionnaire, then optionally include read-only local checks, passive network awareness, and manual/demo inventory findings."
                  onSelect={openFullReportFlow}
                />
              </div>
            </section>

            <section className="mode-group" aria-labelledby="secondary-mode-heading">
              <div className="mode-group__header">
                <p className="section-kicker">Secondary paths</p>
                <h3 id="secondary-mode-heading">Explore one source at a time</h3>
              </div>
              <div className="mode-grid">
                <ModeCard
                  title="Demo Mode"
                  status="Available"
                  description="Review static sample findings without entering information."
                  onSelect={() => setFlowStep("demo")}
                />
                <ModeCard
                  title="Local Device Audit"
                  status="Available"
                  description="AI HomeGuard chooses the right read-only local checks for this runtime."
                  onSelect={openLocalAudit}
                />
                <ModeCard
                  title="Home Security Questionnaire"
                  status="Available"
                  description="Answer friendly checklist questions and see questionnaire-only findings."
                  onSelect={openQuestionnaire}
                />
                <ModeCard
                  title="Device Inventory Helper"
                  status="Available"
                  description="Manually review router app/device list entries. No router login is performed. Do not enter router passwords."
                  onSelect={openDeviceInventory}
                />
                <ModeCard
                  title="Local Network Awareness"
                  status="Available"
                  description="Review passive local network context. No active discovery, port scanning, or packet capture is run."
                  onSelect={openNetworkAwareness}
                />
                <ModeCard
                  title="Defensive Guidance Catalog"
                  status="Available"
                  description="Review the local D3FEND-informed educational guidance used in reports."
                  onSelect={openGuidanceCatalog}
                />
              </div>
            </section>

            <section className="mode-group mode-group--advanced" aria-labelledby="advanced-mode-heading">
              <div className="mode-group__header">
                <p className="section-kicker">Advanced/manual paths</p>
                <h3 id="advanced-mode-heading">Platform-specific validation</h3>
              </div>
              <div className="mode-grid mode-grid--compact">
                <ModeCard
                  title="Windows Device Audit"
                  status="Advanced/manual"
                  variant="advanced"
                  description="Manually run Windows posture checks for debugging or platform validation."
                  onSelect={() => setFlowStep("windows")}
                />
                <ModeCard
                  title="macOS Device Audit"
                  status="Advanced/manual"
                  variant="advanced"
                  description="Manually run macOS posture checks when the backend is running on a Mac."
                  onSelect={() => setFlowStep("macos")}
                />
                <ModeCard
                  title="Linux Device Audit"
                  status="Advanced/manual"
                  variant="advanced"
                  description="Manually run Linux posture checks, including container visibility in Docker."
                  onSelect={() => setFlowStep("linux")}
                />
              </div>
            </section>
          </div>
        </section>
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "loading" && (
        <LoadingState
          kicker="Defensive guidance"
          title="Loading local catalog"
          message="Reading the bundled D3FEND-informed guidance catalog."
        />
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "error" && (
        <ErrorState
          kicker="Defensive guidance"
          title="Guidance catalog unavailable"
          message={guidanceCatalog.message}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "guidance" && guidanceCatalog.state === "ready" && (
        <GuidanceCatalogPanel catalog={guidanceCatalog.catalog} onBackToModes={() => setFlowStep("mode")} />
      )}

      {flowStep === "network" && (
        <NetworkAwarenessPanel
          acknowledged={networkAcknowledged}
          onAcknowledgeChange={setNetworkAcknowledged}
          report={networkReport.state === "ready" ? networkReport.report : null}
          loading={networkReport.state === "loading"}
          error={networkReport.state === "error" ? networkReport.message : null}
          onRun={runNetworkAwareness}
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "inventory" && (
        <DeviceInventoryPanel
          submission={deviceInventorySubmission}
          routerGuidance={routerGuidance.state === "ready" ? routerGuidance.guidance : null}
          guidanceLoading={routerGuidance.state === "loading"}
          guidanceError={routerGuidance.state === "error" ? routerGuidance.message : null}
          report={deviceInventoryReport.state === "ready" ? deviceInventoryReport.report : null}
          loading={deviceInventoryReport.state === "loading"}
          error={deviceInventoryReport.state === "error" ? deviceInventoryReport.message : null}
          onSubmissionChange={setDeviceInventorySubmission}
          onLoadDemo={loadDemoDeviceInventory}
          onRun={runDeviceInventoryReport}
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "questionnaire" && questionnaire.state === "loading" && (
        <LoadingState
          kicker="Questionnaire"
          title="Loading checklist"
          message="Fetching local questionnaire questions from the backend."
        />
      )}

      {flowStep === "questionnaire" && questionnaire.state === "error" && (
        <ErrorState
          kicker="Questionnaire"
          title="Checklist unavailable"
          message={questionnaire.message}
          onBackToModes={() => setFlowStep("mode")}
        />
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
        <LoadingState
          kicker="Full report"
          title="Loading checklist"
          message="Fetching local questionnaire questions from the backend."
        />
      )}

      {flowStep === "full-questionnaire" && questionnaire.state === "error" && (
        <ErrorState
          kicker="Full report"
          title="Checklist unavailable"
          message={questionnaire.message}
          onBackToModes={() => setFlowStep("mode")}
        />
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
              The questionnaire is included. You can also add read-only local device checks and
              passive local network awareness, plus manual/demo device inventory findings. No
              active scan is run, no ports are scanned, no router login is performed, no settings
              are changed, and no data is uploaded.
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

          <label className="acknowledgement">
            <input
              type="checkbox"
              checked={includeNetworkInCombined}
              onChange={(event) => {
                setIncludeNetworkInCombined(event.target.checked);
                if (!event.target.checked) {
                  setCombinedNetworkAcknowledged(false);
                }
              }}
            />
            <span>Include Local Network Awareness findings in the combined report.</span>
          </label>

          {includeNetworkInCombined ? (
            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={combinedNetworkAcknowledged}
                onChange={(event) => setCombinedNetworkAcknowledged(event.target.checked)}
              />
              <span>
                I confirm this is my own home network or a network I am authorized to assess. I
                understand this uses passive local context only. No active scanning, port scanning,
                packet capture, router login, or public target scanning will be performed.
              </span>
            </label>
          ) : null}

          <label className="acknowledgement">
            <input
              type="checkbox"
              checked={includeDeviceInventoryInCombined}
              onChange={(event) => setIncludeDeviceInventoryInCombined(event.target.checked)}
            />
            <span>
              Include Device Inventory Helper findings from the current manual/demo inventory. Add
              devices or load demo inventory in the helper before building the combined report.
            </span>
          </label>

          <div className="flow-actions">
            <button className="secondary-button" type="button" onClick={() => setFlowStep("full-questionnaire")}>
              Back
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={
                (includeLocalInCombined && !combinedLocalAcknowledged) ||
                (includeNetworkInCombined && !combinedNetworkAcknowledged) ||
                (includeDeviceInventoryInCombined && deviceInventorySubmission.devices.length === 0)
              }
              onClick={buildCombinedReport}
            >
              Build Combined Report
            </button>
          </div>
        </section>
      )}

      {flowStep === "combined-results" && combinedReport.state === "loading" && (
        <LoadingState
          kicker="Full report"
          title="Building combined report"
          message="Combining selected findings in memory."
        />
      )}

      {flowStep === "combined-results" && combinedReport.state === "error" && (
        <ErrorState
          kicker="Full report"
          title="Combined report unavailable"
          message={combinedReport.message}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "combined-results" && combinedReport.state === "ready" && (
        <CombinedReportPanel
          response={combinedReport.response}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onBackToModes={() => setFlowStep("mode")}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "results" && questionnaireReport.state === "loading" && (
        <LoadingState
          kicker="Results"
          title="Building questionnaire report"
          message="Creating local questionnaire-derived findings."
        />
      )}

      {flowStep === "results" && questionnaireReport.state === "error" && (
        <ErrorState
          kicker="Results"
          title="Questionnaire report unavailable"
          message={questionnaireReport.message}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "results" && questionnaireReport.state === "ready" && (
        <QuestionnaireResults
          report={questionnaireReport.report}
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "demo" && demoReport.state === "loading" && (
        <LoadingState
          kicker="Demo dashboard"
          title="Loading sample report"
          message="Fetching static demo findings from the local backend."
        />
      )}

      {flowStep === "demo" && demoReport.state === "error" && (
        <ErrorState
          kicker="Demo dashboard"
          title="Sample report unavailable"
          message={demoReport.message}
          onBackToModes={() => setFlowStep("mode")}
        />
      )}

      {flowStep === "demo" && demoReport.state === "ready" && (
        <DemoDashboard
          report={demoReport.report}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onBackToModes={() => setFlowStep("mode")}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "local" && (
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
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "windows" && (
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
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "macos" && (
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
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      {flowStep === "linux" && (
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
          onBackToModes={() => setFlowStep("mode")}
          exportStatus={exportStatus}
          onExportMarkdown={exportMarkdown}
          onExportJson={exportJson}
          onClearReport={clearCurrentReport}
        />
      )}

      <StatusPanel />
    </main>
  );
}
