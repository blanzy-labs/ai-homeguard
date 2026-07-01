import { useEffect, useState } from "react";
import {
  getDemoReport,
  getLinuxLocalReport,
  getMacOSLocalReport,
  getQuestionnaire,
  getQuestionnaireReport,
  getWindowsLocalReport,
  type HomeGuardReport,
  type QuestionnaireSection,
  type QuestionnaireSubmission,
} from "./api/client";
import { DemoDashboard } from "./components/DemoDashboard";
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
  | "demo"
  | "windows"
  | "macos"
  | "linux";

type ReportState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; report: HomeGuardReport }
  | { state: "error"; message: string };

type QuestionnaireState =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "ready"; sections: QuestionnaireSection[] }
  | { state: "error"; message: string };

export default function App() {
  const [flowStep, setFlowStep] = useState<FlowStep>("welcome");
  const [acknowledged, setAcknowledged] = useState(false);
  const [demoReport, setDemoReport] = useState<ReportState>({ state: "idle" });
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireState>({ state: "idle" });
  const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<string, string>>({});
  const [questionnaireReport, setQuestionnaireReport] = useState<ReportState>({ state: "idle" });
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
          A defensive home cyber hygiene helper. Slice 5 adds read-only Windows, macOS, and Linux
          local checks with friendly unsupported-platform reports.
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
              to local read-only checks, demo data, and questionnaire answers.
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
            <li>Uses read-only device checks for Windows, macOS, and Linux.</li>
            <li>Returns an unsupported-platform report when a check cannot run here.</li>
            <li>Does not request sudo, administrator escalation, or passwords.</li>
            <li>Does not exploit, attack, brute-force, or packet-sniff.</li>
            <li>Does not scan networks or public targets.</li>
            <li>Does not upload data or call an AI provider.</li>
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
              title="Windows Device Audit"
              status="Available"
              description="Run read-only Windows posture checks, or see a safe unsupported-platform result here."
              onSelect={() => setFlowStep("windows")}
            />
            <ModeCard
              title="macOS Device Audit"
              status="Available"
              description="Run read-only macOS posture checks when the backend is running on a Mac."
              onSelect={() => setFlowStep("macos")}
            />
            <ModeCard
              title="Linux Device Audit"
              status="Available"
              description="Run read-only Linux posture checks, or see unsupported status on other platforms."
              onSelect={() => setFlowStep("linux")}
            />
            <ModeCard
              title="Home Security Questionnaire"
              status="Available"
              description="Answer friendly checklist questions and see questionnaire-only findings."
              onSelect={openQuestionnaire}
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
