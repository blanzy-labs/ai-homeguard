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
  type NetworkDiscoveryRequest,
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
  | "guided-setup"
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

type NavigationTarget =
  | "welcome"
  | "run-check"
  | "full-report"
  | "advanced"
  | "review"
  | "demo"
  | "local"
  | "questionnaire"
  | "network"
  | "inventory"
  | "guidance";

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
  "AI HomeGuard appears to be running inside a container. Local checks may reflect the container environment rather than the host computer.";

const nativeMacInstruction = "For host-level macOS checks, run the backend natively with uv.";

const safetyAcknowledgementVersion = "0.1.0";
const safetyAcknowledgementStorageKey = "ai-homeguard-safety-ack-v0.1.0";
const advancedOptionsStorageKey = "ai-homeguard-advanced-options-open-v0.1.0";
const networkAwarenessStatementVersion = "v0.1.0-network-awareness";
const networkDiscoveryStatementVersion = "v0.1.0-slice-14";
const demoReportUnavailableMessage =
  "Could not load the demo report. Confirm the backend is running on port 8000.";

function createEmptyDeviceInventorySubmission(): DeviceInventorySubmission {
  return {
    mode: "manual",
    acknowledged_manual: true,
    devices: [],
    user_notes: "",
  };
}

function readSafetyAcknowledgement() {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    const stored = window.sessionStorage.getItem(safetyAcknowledgementStorageKey);
    if (!stored) {
      return false;
    }
    const parsed = JSON.parse(stored) as { acknowledged?: boolean; version?: string };
    return parsed.acknowledged === true && parsed.version === safetyAcknowledgementVersion;
  } catch {
    return false;
  }
}

function writeSafetyAcknowledgement(acknowledged: boolean) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    if (acknowledged) {
      window.sessionStorage.setItem(
        safetyAcknowledgementStorageKey,
        JSON.stringify({ acknowledged: true, version: safetyAcknowledgementVersion }),
      );
    } else {
      window.sessionStorage.removeItem(safetyAcknowledgementStorageKey);
    }
  } catch {
    // Storage can be unavailable in private or locked-down browser sessions.
  }
}

function readAdvancedOptionsExpanded() {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    return window.sessionStorage.getItem(advancedOptionsStorageKey) === "true";
  } catch {
    return false;
  }
}

function writeAdvancedOptionsExpanded(expanded: boolean) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.sessionStorage.setItem(advancedOptionsStorageKey, String(expanded));
  } catch {
    // Storage can be unavailable in private or locked-down browser sessions.
  }
}

type NavigatorWithUserAgentData = Navigator & {
  userAgentData?: {
    platform?: string;
  };
};

function getBrowserPlatformHint() {
  if (typeof navigator === "undefined") {
    return null;
  }
  const browserNavigator = navigator as NavigatorWithUserAgentData;
  const platform = browserNavigator.userAgentData?.platform ?? browserNavigator.platform ?? "";
  const normalized = platform.toLowerCase();
  if (normalized.includes("mac")) {
    return "macOS";
  }
  if (normalized.includes("win")) {
    return "Windows";
  }
  if (normalized.includes("linux")) {
    return "Linux";
  }
  if (normalized.includes("iphone") || normalized.includes("ipad") || normalized.includes("ios")) {
    return "iOS";
  }
  if (normalized.includes("android")) {
    return "Android";
  }
  return platform || null;
}

export default function App() {
  const [flowStep, setFlowStep] = useState<FlowStep>("welcome");
  const [acknowledged, setAcknowledged] = useState(readSafetyAcknowledgement);
  const [pendingNavigation, setPendingNavigation] = useState<NavigationTarget | null>(null);
  const [advancedOptionsExpanded, setAdvancedOptionsExpanded] = useState(readAdvancedOptionsExpanded);
  const [browserPlatformHint] = useState(getBrowserPlatformHint);
  const [demoReport, setDemoReport] = useState<ReportState>({ state: "idle" });
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireState>({ state: "idle" });
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<string, string>>({});
  const [fullReportAnswers, setFullReportAnswers] = useState<Record<string, string>>({});
  const [questionnaireReport, setQuestionnaireReport] = useState<ReportState>({ state: "idle" });
  const [combinedReport, setCombinedReport] = useState<CombinedReportState>({ state: "idle" });
  const [combinedSubmission, setCombinedSubmission] = useState<QuestionnaireSubmission | null>(null);
  const [includeQuestionsInCombined, setIncludeQuestionsInCombined] = useState(true);
  const [includeLocalInCombined, setIncludeLocalInCombined] = useState(false);
  const [combinedLocalAcknowledged, setCombinedLocalAcknowledged] = useState(false);
  const [includeNetworkInCombined, setIncludeNetworkInCombined] = useState(false);
  const [combinedNetworkAcknowledged, setCombinedNetworkAcknowledged] = useState(false);
  const [includeNetworkDiscoveryInCombined, setIncludeNetworkDiscoveryInCombined] = useState(false);
  const [networkDiscoveryAcknowledged, setNetworkDiscoveryAcknowledged] = useState(false);
  const [networkDiscoveryPrivateOnlyAcknowledged, setNetworkDiscoveryPrivateOnlyAcknowledged] = useState(false);
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
    writeSafetyAcknowledgement(acknowledged);
  }, [acknowledged]);

  useEffect(() => {
    writeAdvancedOptionsExpanded(advancedOptionsExpanded);
  }, [advancedOptionsExpanded]);

  useEffect(() => {
    if (flowStep !== "demo" || demoReport.state !== "idle") {
      return;
    }

    let isMounted = true;

    async function loadDemoReport() {
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
            message: demoReportUnavailableMessage,
          });
        }
      }
    }

    void loadDemoReport();

    return () => {
      isMounted = false;
    };
  }, [flowStep]);

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
    setIncludeQuestionsInCombined(true);
    setIncludeLocalInCombined(true);
    setCombinedLocalAcknowledged(true);
    setIncludeNetworkInCombined(false);
    setCombinedNetworkAcknowledged(false);
    setIncludeNetworkDiscoveryInCombined(false);
    setNetworkDiscoveryAcknowledged(false);
    setNetworkDiscoveryPrivateOnlyAcknowledged(false);
    setIncludeDeviceInventoryInCombined(false);
    setCombinedSubmission(null);
    setCombinedReport({ state: "idle" });
    setFlowStep("guided-setup");
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
    void buildCombinedReport(submission, true);
  }

  async function continueGuidedSetup() {
    if (includeQuestionsInCombined) {
      setFlowStep("full-questionnaire");
      await ensureQuestionnaireLoaded();
      return;
    }
    setCombinedSubmission(null);
    await buildCombinedReport(null, false);
  }

  async function skipQuickQuestions() {
    setIncludeQuestionsInCombined(false);
    setCombinedSubmission(null);
    await buildCombinedReport(null, false);
  }

  async function buildCombinedReport(
    questionnaireSubmission: QuestionnaireSubmission | null = combinedSubmission,
    includeQuestions = includeQuestionsInCombined,
  ) {
    if (includeQuestions && !questionnaireSubmission) {
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
    if (
      includeNetworkDiscoveryInCombined &&
      (!networkDiscoveryAcknowledged || !networkDiscoveryPrivateOnlyAcknowledged)
    ) {
      setCombinedReport({
        state: "error",
        message: "Please acknowledge private home network discovery before finding devices.",
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
        include_questionnaire: includeQuestions,
        include_local_device: includeLocalInCombined,
        include_network_awareness: includeNetworkInCombined,
        include_network_discovery: includeNetworkDiscoveryInCombined,
        include_device_inventory: includeDeviceInventoryInCombined,
        questionnaire_submission: includeQuestions ? questionnaireSubmission : null,
        acknowledged_authorization: includeLocalInCombined ? combinedLocalAcknowledged : false,
        network_authorization: includeNetworkInCombined
          ? {
              acknowledged: combinedNetworkAcknowledged,
              scope: "home_network",
              statement_version: networkAwarenessStatementVersion,
            }
          : null,
        network_discovery_request: includeNetworkDiscoveryInCombined ? createNetworkDiscoveryRequest() : null,
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
        statement_version: networkAwarenessStatementVersion,
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
    setDemoReport({ state: "idle" });
    setQuestionnaireReport({ state: "idle" });
    setCombinedReport({ state: "idle" });
    setNetworkReport({ state: "idle" });
    setDeviceInventoryReport({ state: "idle" });
    setLocalReport({ state: "idle" });
    setWindowsReport({ state: "idle" });
    setMacosReport({ state: "idle" });
    setLinuxReport({ state: "idle" });
    if (flowStep !== "welcome" && flowStep !== "safety" && flowStep !== "mode") {
      setFlowStep("mode");
    }
  }

  function startOver() {
    setFlowStep("welcome");
    setPendingNavigation(null);
    setQuestionnaire({ state: "idle" });
    setQuestionnaireAnswers({});
    setFullReportAnswers({});
    setCombinedSubmission(null);
    setIncludeQuestionsInCombined(true);
    setIncludeLocalInCombined(true);
    setCombinedLocalAcknowledged(false);
    setIncludeNetworkInCombined(false);
    setCombinedNetworkAcknowledged(false);
    setIncludeNetworkDiscoveryInCombined(false);
    setNetworkDiscoveryAcknowledged(false);
    setNetworkDiscoveryPrivateOnlyAcknowledged(false);
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

  function createNetworkDiscoveryRequest(): NetworkDiscoveryRequest {
    return {
      authorization: {
        acknowledged: networkDiscoveryAcknowledged,
        scope: "home_network",
        statement_version: networkDiscoveryStatementVersion,
        include_active_discovery: true,
        user_understands_private_network_only: networkDiscoveryPrivateOnlyAcknowledged,
      },
      method: "combined",
      max_hosts: 64,
      timeout_ms: 500,
      include_router_gateway: true,
    };
  }

  function currentReportTarget(): FlowStep | null {
    if (combinedReport.state !== "idle") {
      return "combined-results";
    }
    if (questionnaireReport.state !== "idle") {
      return "results";
    }
    if (demoReport.state !== "idle") {
      return "demo";
    }
    if (localReport.state !== "idle") {
      return "local";
    }
    if (networkReport.state !== "idle") {
      return "network";
    }
    if (deviceInventoryReport.state !== "idle") {
      return "inventory";
    }
    if (windowsReport.state !== "idle") {
      return "windows";
    }
    if (macosReport.state !== "idle") {
      return "macos";
    }
    if (linuxReport.state !== "idle") {
      return "linux";
    }
    return null;
  }

  async function openNavigationTarget(target: NavigationTarget) {
    setExportStatus(null);
    if (target === "welcome") {
      setFlowStep("welcome");
      return;
    }
    if (target === "run-check" || target === "full-report") {
      await openFullReportFlow();
      return;
    }
    if (target === "advanced") {
      setAdvancedOptionsExpanded(true);
      setFlowStep("mode");
      return;
    }
    if (target === "demo") {
      setFlowStep("demo");
      return;
    }
    if (target === "local") {
      await openLocalAudit();
      return;
    }
    if (target === "questionnaire") {
      await openQuestionnaire();
      return;
    }
    if (target === "network") {
      openNetworkAwareness();
      return;
    }
    if (target === "inventory") {
      await openDeviceInventory();
      return;
    }
    if (target === "guidance") {
      await openGuidanceCatalog();
      return;
    }
    const reportTarget = currentReportTarget();
    if (reportTarget) {
      setFlowStep(reportTarget);
    }
  }

  function navigateTo(target: NavigationTarget) {
    if (target === "welcome") {
      setPendingNavigation(null);
      void openNavigationTarget(target);
      return;
    }
    if (!acknowledged) {
      setPendingNavigation(target);
      setFlowStep("safety");
      return;
    }
    void openNavigationTarget(target);
  }

  function continueAfterSafetyAcknowledgement() {
    if (!acknowledged) {
      return;
    }
    const target = pendingNavigation ?? "run-check";
    setPendingNavigation(null);
    void openNavigationTarget(target);
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
        </div>
        <h1>AI HomeGuard</h1>
        <p className="subtitle">A local home cyber hygiene check with plain-English next steps.</p>
        <p className="safety-message">
          AI HomeGuard checks what it can locally, asks a few simple questions, and gives you a
          short action plan without uploading data or changing settings.
        </p>
        <span className="demo-badge">Safety-first local flow</span>
      </section>

      {flowStep !== "welcome" ? (
        <PrimaryNavigation
          activeTarget={activeNavigationTarget(flowStep)}
          reportAvailable={currentReportTarget() !== null}
          onNavigate={navigateTo}
          onStartOver={startOver}
          onClearCurrentReport={clearCurrentReport}
        />
      ) : null}

      {flowStep === "welcome" && (
        <div className="home-stack">
          <section className="home-cta-panel" aria-labelledby="welcome-heading">
            <div>
              <p className="section-kicker">HomeGuard check</p>
              <h2 id="welcome-heading">Start with one guided check</h2>
              <p className="muted">
                Run HomeGuard Check gives you a dashboard, the top things to do first, what was
                checked, what still needs your input, and a report you can export when you choose.
              </p>
            </div>
            <div className="welcome-actions">
              <button className="primary-button primary-button--large" type="button" onClick={() => navigateTo("run-check")}>
                Run HomeGuard Check
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("demo")}>
                Try Demo
              </button>
              {currentReportTarget() ? (
                <button className="secondary-button" type="button" onClick={() => navigateTo("review")}>
                  View Last Result in This Session
                </button>
              ) : null}
              <button className="secondary-button" type="button" onClick={() => navigateTo("advanced")}>
                Advanced Options
              </button>
            </div>
          </section>

          <section className="home-info-panel" aria-labelledby="what-it-checks-heading">
            <div>
              <p className="section-kicker">What it checks</p>
              <h2 id="what-it-checks-heading">Plain-English coverage</h2>
            </div>
            <div className="home-check-grid">
              {[
                "This Device",
                "Network Devices",
                "Accounts & Passwords",
                "Backups",
                "Router & Wi-Fi",
                "Smart Devices",
              ].map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
          </section>

          <section className="home-info-panel" aria-labelledby="trust-heading">
            <div>
              <p className="section-kicker">Trust boundaries</p>
              <h2 id="trust-heading">What it does not do</h2>
            </div>
            <div className="home-trust-grid">
              {["No hacking", "No public scanning", "No router login", "No data upload", "No automatic changes"].map(
                (label) => (
                  <span key={label}>{label}</span>
                ),
              )}
            </div>
          </section>

          <details
            className="advanced-options-drawer"
            open={advancedOptionsExpanded}
            onToggle={(event) => setAdvancedOptionsExpanded(event.currentTarget.open)}
          >
            <summary>Advanced Options</summary>
            <div className="advanced-options-list">
              <button className="secondary-button" type="button" onClick={() => navigateTo("demo")}>
                Demo Mode
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("local")}>
                Local Device Audit
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("questionnaire")}>
                Questionnaire Only
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("network")}>
                Local Network Awareness
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("inventory")}>
                Device Inventory Helper
              </button>
              <button className="secondary-button" type="button" onClick={() => navigateTo("advanced")}>
                Platform-Specific Checks
              </button>
            </div>
          </details>
        </div>
      )}

      {flowStep === "safety" && (
        <section className="safety-flow-panel" aria-labelledby="safety-flow-heading">
          <div className="flow-heading">
            <p className="section-kicker">Safety notes</p>
            <h2 id="safety-flow-heading">What this version does and does not do</h2>
            <p className="muted">
              HomeGuard is a defensive local helper. It explains what it can check, what it cannot
              check, and what you may want to do next.
            </p>
          </div>

          <ul className="safety-boundary-list">
            <li>Read-only checks only.</li>
            <li>No settings are changed.</li>
            <li>No public scanning, router login, packet capture, or automatic changes.</li>
            <li>No data upload, telemetry, database, or AI provider call.</li>
            <li>Exports happen only when you click an export button.</li>
            <li>If Docker limits visibility, the dashboard shows that as a limitation.</li>
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
            <button
              className="secondary-button"
              type="button"
              onClick={() => {
                setPendingNavigation(null);
                setFlowStep("welcome");
              }}
            >
              Back
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={!acknowledged}
              onClick={continueAfterSafetyAcknowledgement}
            >
              Continue
            </button>
          </div>
        </section>
      )}

      {flowStep === "guided-setup" && (
        <section className="questionnaire-panel guided-setup-panel" aria-labelledby="guided-setup-heading">
          <div className="flow-heading">
            <p className="section-kicker">Run HomeGuard Check</p>
            <h2 id="guided-setup-heading">Choose what to include</h2>
            <p className="muted">
              HomeGuard will combine what it can check locally with a few simple answers. You can
              keep the defaults and run a useful check without choosing technical tools.
            </p>
          </div>

          <div className="guided-option-list">
            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={includeLocalInCombined}
                onChange={(event) => {
                  setIncludeLocalInCombined(event.target.checked);
                  setCombinedLocalAcknowledged(event.target.checked);
                }}
              />
              <span>
                <strong>Include This Device</strong>
                <br />
                Read-only checks when available. If Docker limits visibility, the dashboard will
                show that as a limitation.
              </span>
            </label>

            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={includeQuestionsInCombined}
                onChange={(event) => setIncludeQuestionsInCombined(event.target.checked)}
              />
              <span>
                <strong>Include quick home security questions</strong>
                <br />
                A few plain questions fill in areas HomeGuard cannot check automatically.
              </span>
            </label>

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
              <span>
                <strong>Include Router & Wi-Fi awareness</strong>
                <br />
                Optional passive local context only. No active discovery, port scanning, packet
                capture, router login, or public target scanning.
              </span>
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
                  understand HomeGuard uses passive local context only.
                </span>
              </label>
            ) : null}

            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={includeNetworkDiscoveryInCombined}
                onChange={(event) => {
                  setIncludeNetworkDiscoveryInCombined(event.target.checked);
                  if (!event.target.checked) {
                    setNetworkDiscoveryAcknowledged(false);
                    setNetworkDiscoveryPrivateOnlyAcknowledged(false);
                  }
                }}
              />
              <span>
                <strong>Find devices on my home network</strong>
                <br />
                Optional private local device discovery. HomeGuard checks private local addresses
                only. No public targets, ports, router login, passwords, or packet capture.
              </span>
            </label>

            {includeNetworkDiscoveryInCombined ? (
              <div className="guided-discovery-panel">
                <div className="safety-chip-list" aria-label="Device discovery safety boundaries">
                  <span>No public targets</span>
                  <span>No ports checked</span>
                  <span>No router login</span>
                  <span>No passwords</span>
                  <span>No packet capture</span>
                </div>
                <label className="acknowledgement">
                  <input
                    type="checkbox"
                    checked={networkDiscoveryAcknowledged}
                    onChange={(event) => setNetworkDiscoveryAcknowledged(event.target.checked)}
                  />
                  <span>I confirm this is my own home network or I am authorized to check it.</span>
                </label>
                <label className="acknowledgement">
                  <input
                    type="checkbox"
                    checked={networkDiscoveryPrivateOnlyAcknowledged}
                    onChange={(event) => setNetworkDiscoveryPrivateOnlyAcknowledged(event.target.checked)}
                  />
                  <span>I understand HomeGuard will only check private local network addresses.</span>
                </label>
              </div>
            ) : null}

            <label className="acknowledgement">
              <input
                type="checkbox"
                checked={includeDeviceInventoryInCombined}
                onChange={(event) => setIncludeDeviceInventoryInCombined(event.target.checked)}
              />
              <span>
                <strong>Include Smart Devices from manual/router list</strong>
                <br />
                Optional. Use this only after adding devices in Device Inventory Helper.
              </span>
            </label>

            {includeDeviceInventoryInCombined && deviceInventorySubmission.devices.length === 0 ? (
              <div className="guided-warning">
                <strong>Device inventory needs your input</strong>
                <p>Add devices or load demo inventory before including this area.</p>
                <button className="secondary-button" type="button" onClick={() => void openDeviceInventory()}>
                  Open Device Inventory Helper
                </button>
              </div>
            ) : null}
          </div>

          <div className="flow-actions">
            <button className="secondary-button" type="button" onClick={() => setFlowStep("welcome")}>
              Back
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={
                (includeNetworkInCombined && !combinedNetworkAcknowledged) ||
                (includeNetworkDiscoveryInCombined &&
                  (!networkDiscoveryAcknowledged || !networkDiscoveryPrivateOnlyAcknowledged)) ||
                (includeDeviceInventoryInCombined && deviceInventorySubmission.devices.length === 0) ||
                (!includeQuestionsInCombined &&
                  !includeLocalInCombined &&
                  !includeNetworkInCombined &&
                  !includeNetworkDiscoveryInCombined &&
                  !includeDeviceInventoryInCombined)
              }
              onClick={continueGuidedSetup}
            >
              {includeQuestionsInCombined
                ? "Answer Quick Questions"
                : includeNetworkDiscoveryInCombined
                  ? "Start Device Discovery"
                  : "Run Check"}
            </button>
          </div>
        </section>
      )}

      {flowStep === "mode" && (
        <section className="mode-panel" aria-labelledby="mode-heading">
          <div className="flow-heading">
            <p className="section-kicker">Advanced Options</p>
            <h2 id="mode-heading">Tools for deeper review</h2>
            <p className="muted">
              The main path is Run HomeGuard Check. These options remain available when you want to
              review one area at a time or validate platform-specific checks.
            </p>
          </div>
          <div className="mode-sections">
            <section className="mode-group mode-group--recommended" aria-labelledby="recommended-mode-heading">
              <div className="mode-group__header">
                <p className="section-kicker">Recommended</p>
                <h3 id="recommended-mode-heading">Return to the guided check</h3>
              </div>
              <div className="mode-grid mode-grid--single">
                <ModeCard
                  title="Run HomeGuard Check"
                  status="Recommended"
                  variant="recommended"
                  description="Use one guided flow to create a dashboard, top actions, coverage summary, and exportable report."
                  onSelect={openFullReportFlow}
                />
              </div>
            </section>

            <section className="mode-group" aria-labelledby="secondary-mode-heading">
              <div className="mode-group__header">
                <p className="section-kicker">Secondary tools</p>
                <h3 id="secondary-mode-heading">Review one area at a time</h3>
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
          kicker="Run HomeGuard Check"
          heading="Answer a few quick questions"
          description="Answer a few quick questions so HomeGuard can fill in what it cannot check automatically. You can skip this and still run selected local checks."
          submitLabel="Run Check"
          skipLabel="Skip Questions and Run Check"
          onSkip={skipQuickQuestions}
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
              onClick={() => void buildCombinedReport()}
            >
              Build Combined Report
            </button>
          </div>
        </section>
      )}

      {flowStep === "combined-results" && combinedReport.state === "loading" && (
        <LoadingState
          kicker="Full report"
          title={includeNetworkDiscoveryInCombined ? "Finding devices on your home network..." : "Building combined report"}
          message={
            includeNetworkDiscoveryInCombined
              ? "Checking local private network only. No ports are being scanned."
              : "Combining selected findings in memory."
          }
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
          nativeMacInstruction={nativeMacInstruction}
          browserPlatformHint={browserPlatformHint}
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
          nativeMacInstruction={nativeMacInstruction}
          browserPlatformHint={browserPlatformHint}
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
          nativeMacInstruction={nativeMacInstruction}
          browserPlatformHint={browserPlatformHint}
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
          nativeMacInstruction={nativeMacInstruction}
          browserPlatformHint={browserPlatformHint}
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

function activeNavigationTarget(flowStep: FlowStep): NavigationTarget {
  if (flowStep === "combined-results" || flowStep === "demo" || flowStep === "results") {
    return "review";
  }
  if (flowStep === "guided-setup" || flowStep === "full-questionnaire" || flowStep === "full-options") {
    return "run-check";
  }
  if (flowStep === "local") {
    return "advanced";
  }
  if (flowStep === "questionnaire") {
    return "advanced";
  }
  if (flowStep === "network") {
    return "advanced";
  }
  if (flowStep === "inventory") {
    return "advanced";
  }
  if (flowStep === "guidance") {
    return "advanced";
  }
  if (flowStep === "windows" || flowStep === "macos" || flowStep === "linux" || flowStep === "mode") {
    return "advanced";
  }
  return "welcome";
}

function PrimaryNavigation({
  activeTarget,
  reportAvailable,
  onNavigate,
  onStartOver,
  onClearCurrentReport,
}: {
  activeTarget: NavigationTarget;
  reportAvailable: boolean;
  onNavigate: (target: NavigationTarget) => void;
  onStartOver: () => void;
  onClearCurrentReport: () => void;
}) {
  const items: Array<{ target: NavigationTarget; label: string; disabled?: boolean }> = [
    { target: "welcome", label: "Home" },
    { target: "run-check", label: "Run Check" },
    { target: "review", label: "Dashboard / Export", disabled: !reportAvailable },
    { target: "advanced", label: "Advanced Checks" },
  ];

  return (
    <nav className="primary-nav" aria-label="Primary navigation">
      <div className="primary-nav__items">
        {items.map((item) => {
          const isActive = item.target === activeTarget;
          return (
            <button
              className={isActive ? "nav-button nav-button--active" : "nav-button"}
              type="button"
              key={item.target}
              disabled={item.disabled}
              aria-current={isActive ? "page" : undefined}
              onClick={() => onNavigate(item.target)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      <div className="primary-nav__actions">
        <button className="secondary-button secondary-button--compact" type="button" onClick={onStartOver}>
          Start Over
        </button>
        <button
          className="secondary-button secondary-button--compact"
          type="button"
          disabled={!reportAvailable}
          onClick={onClearCurrentReport}
        >
          Clear Current Report
        </button>
      </div>
    </nav>
  );
}
