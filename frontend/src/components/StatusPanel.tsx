import { useEffect, useState } from "react";
import { getHealth, getVersion, type HealthResponse, type VersionResponse } from "../api/client";

type BackendStatus =
  | { state: "loading" }
  | { state: "ready"; health: HealthResponse; version: VersionResponse }
  | { state: "error"; message: string };

export function StatusPanel() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ state: "loading" });

  useEffect(() => {
    let isMounted = true;

    async function loadStatus() {
      try {
        const [health, version] = await Promise.all([getHealth(), getVersion()]);
        if (isMounted) {
          setBackendStatus({ state: "ready", health, version });
        }
      } catch (error) {
        if (isMounted) {
          setBackendStatus({
            state: "error",
            message: error instanceof Error ? error.message : "Backend unavailable",
          });
        }
      }
    }

    void loadStatus();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section className="status-panel" aria-labelledby="backend-status-heading">
      <div>
        <p className="section-kicker">Backend status</p>
        <h2 id="backend-status-heading">Local API</h2>
      </div>
      {backendStatus.state === "loading" && <p className="muted">Checking local backend...</p>}
      {backendStatus.state === "error" && (
        <p className="status-error">Backend unavailable: {backendStatus.message}</p>
      )}
      {backendStatus.state === "ready" && (
        <dl className="status-grid">
          <div>
            <dt>Status</dt>
            <dd>{backendStatus.health.status}</dd>
          </div>
          <div>
            <dt>App</dt>
            <dd>{backendStatus.version.app}</dd>
          </div>
          <div>
            <dt>Version</dt>
            <dd>{backendStatus.version.version}</dd>
          </div>
          <div>
            <dt>Family</dt>
            <dd>{backendStatus.version.family}</dd>
          </div>
        </dl>
      )}
    </section>
  );
}
