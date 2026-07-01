import { useEffect, useState } from "react";
import { getDemoReport, type HomeGuardReport } from "./api/client";
import { DemoDashboard } from "./components/DemoDashboard";
import { StatusPanel } from "./components/StatusPanel";

type DemoReportState =
  | { state: "loading" }
  | { state: "ready"; report: HomeGuardReport }
  | { state: "error"; message: string };

export default function App() {
  const [demoReport, setDemoReport] = useState<DemoReportState>({ state: "loading" });

  useEffect(() => {
    let isMounted = true;

    async function loadDemoReport() {
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
  }, []);

  return (
    <main className="app-shell">
      <section className="intro">
        <div className="brand-row">
          <span className="brand-mark" aria-hidden="true">
            HG
          </span>
          <p>Blanzy Labs AI app family</p>
        </div>
        <h1>AI HomeGuard</h1>
        <p className="subtitle">Local Home Security Audit MVP</p>
        <p className="safety-message">
          Demo Mode uses sample findings only. No checks or network scans are run in this slice.
          AI HomeGuard does not exploit, attack, brute-force, packet-sniff, or scan public targets.
        </p>
        <span className="demo-badge">Demo Mode - static sample report</span>
      </section>

      {demoReport.state === "loading" && (
        <section className="loading-panel">
          <p className="section-kicker">Demo dashboard</p>
          <h2>Loading sample report</h2>
          <p className="muted">Fetching static demo findings from the local backend.</p>
        </section>
      )}

      {demoReport.state === "error" && (
        <section className="loading-panel loading-panel--error">
          <p className="section-kicker">Demo dashboard</p>
          <h2>Sample report unavailable</h2>
          <p>{demoReport.message}</p>
        </section>
      )}

      {demoReport.state === "ready" && <DemoDashboard report={demoReport.report} />}

      <StatusPanel />
    </main>
  );
}
