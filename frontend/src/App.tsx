import { useEffect, useState } from "react";
import {
  getDemoReport,
  getQuestionnaire,
  getQuestionnaireReport,
  type HomeGuardReport,
  type QuestionnaireSection,
  type QuestionnaireSubmission,
} from "./api/client";
import { DemoDashboard } from "./components/DemoDashboard";
import { ModeCard } from "./components/ModeCard";
import { QuestionnaireResults } from "./components/QuestionnaireResults";
import { QuestionnaireScreen } from "./components/QuestionnaireScreen";
import { StatusPanel } from "./components/StatusPanel";

type FlowStep = "welcome" | "safety" | "mode" | "questionnaire" | "results" | "demo";

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
          A defensive home cyber hygiene helper. Slice 3 guides you through safety notes and a
          questionnaire before any real device or network checks exist.
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
              to demo data and questionnaire answers.
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
            <li>Does not exploit, attack, brute-force, or packet-sniff.</li>
            <li>Does not scan public targets.</li>
            <li>Slice 3 still does not run real device or network checks.</li>
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
              Available options are safe demo and questionnaire flows. Real local checks are still
              intentionally locked for later slices.
            </p>
          </div>
          <div className="mode-grid">
            <ModeCard
              title="Demo Mode"
              status="Available"
              description="Review static sample findings from Slice 2."
              onSelect={() => setFlowStep("demo")}
            />
            <ModeCard
              title="Home Security Questionnaire"
              status="Available"
              description="Answer friendly checklist questions and see questionnaire-only findings."
              onSelect={openQuestionnaire}
            />
            <ModeCard
              title="Device-only Audit"
              status="Coming soon"
              description="Future local device checks with clear boundaries and consent."
              disabled
            />
            <ModeCard
              title="Device + Home Network Audit"
              status="Coming soon"
              description="Future authorized home network awareness flow."
              disabled
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

      <StatusPanel />
    </main>
  );
}
