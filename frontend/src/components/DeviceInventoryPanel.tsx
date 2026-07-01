import type {
  DeviceInventoryItem,
  DeviceInventorySubmission,
  DeviceNetworkPlacement,
  DeviceTrustLevel,
  DeviceType,
  DeviceUpdateStatus,
  HomeGuardReport,
  RouterGuidanceResponse,
} from "../api/client";
import { ReportReviewPanel } from "./ReportReviewPanel";

type DeviceInventoryPanelProps = {
  submission: DeviceInventorySubmission;
  routerGuidance: RouterGuidanceResponse | null;
  guidanceLoading: boolean;
  guidanceError: string | null;
  report: HomeGuardReport | null;
  loading: boolean;
  error: string | null;
  onSubmissionChange: (submission: DeviceInventorySubmission) => void;
  onLoadDemo: () => void;
  onRun: () => void;
  onBackToModes: () => void;
  exportStatus?: string | null;
  onExportMarkdown?: (report: HomeGuardReport) => void;
  onExportJson?: (report: HomeGuardReport) => void;
  onClearReport?: () => void;
};

const deviceTypeOptions: Array<{ value: DeviceType; label: string }> = [
  { value: "computer", label: "Computer" },
  { value: "phone", label: "Phone" },
  { value: "tablet", label: "Tablet" },
  { value: "router", label: "Router" },
  { value: "printer", label: "Printer" },
  { value: "smart_tv", label: "Smart TV" },
  { value: "camera", label: "Camera" },
  { value: "doorbell", label: "Doorbell" },
  { value: "speaker", label: "Speaker" },
  { value: "game_console", label: "Game Console" },
  { value: "nas_storage", label: "NAS Storage" },
  { value: "iot_device", label: "IoT Device" },
  { value: "guest_device", label: "Guest Device" },
  { value: "unknown", label: "Unknown" },
  { value: "other", label: "Other" },
];

const trustOptions: Array<{ value: DeviceTrustLevel; label: string }> = [
  { value: "trusted", label: "Trusted" },
  { value: "limited_trust", label: "Limited Trust" },
  { value: "guest", label: "Guest" },
  { value: "unknown", label: "Unknown" },
];

const placementOptions: Array<{ value: DeviceNetworkPlacement; label: string }> = [
  { value: "main_network", label: "Main Network" },
  { value: "guest_network", label: "Guest Network" },
  { value: "isolated_network", label: "Isolated Network" },
  { value: "wired", label: "Wired" },
  { value: "unknown", label: "Unknown" },
];

const updateOptions: Array<{ value: DeviceUpdateStatus; label: string }> = [
  { value: "up_to_date", label: "Up to Date" },
  { value: "needs_review", label: "Needs Review" },
  { value: "unsupported_or_old", label: "Unsupported or Old" },
  { value: "unknown", label: "Unknown" },
  { value: "not_applicable", label: "Not Applicable" },
];

const usedByOptions = ["", "me", "family", "guest", "unknown"];

function formatStatus(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function newDevice(): DeviceInventoryItem {
  const id = `manual-device-${Date.now()}`;
  return {
    id,
    label: "New Device",
    device_type: "unknown",
    recognized: false,
    trust_level: "unknown",
    network_placement: "unknown",
    update_status: "unknown",
    used_by: "unknown",
    notes: "",
    sensitive: false,
  };
}

export function DeviceInventoryPanel({
  submission,
  routerGuidance,
  guidanceLoading,
  guidanceError,
  report,
  loading,
  error,
  onSubmissionChange,
  onLoadDemo,
  onRun,
  onBackToModes,
  exportStatus,
  onExportMarkdown,
  onExportJson,
  onClearReport,
}: DeviceInventoryPanelProps) {
  function updateSubmission(update: Partial<DeviceInventorySubmission>) {
    onSubmissionChange({
      ...submission,
      ...update,
      mode: update.mode ?? "manual",
      acknowledged_manual: true,
    });
  }

  function updateDevice(index: number, update: Partial<DeviceInventoryItem>) {
    const devices = submission.devices.map((device, currentIndex) =>
      currentIndex === index ? { ...device, ...update } : device,
    );
    updateSubmission({ devices });
  }

  function removeDevice(index: number) {
    updateSubmission({ devices: submission.devices.filter((_, currentIndex) => currentIndex !== index) });
  }

  function addDevice() {
    updateSubmission({ devices: [...submission.devices, newDevice()] });
  }

  return (
    <section className="local-audit-panel inventory-panel" aria-labelledby="device-inventory-heading">
      <div className="flow-heading">
        <p className="section-kicker">Device Inventory Helper</p>
        <h2 id="device-inventory-heading">Manual router device review</h2>
        <p className="muted">
          Manually review devices from your router app/device list. AI HomeGuard does not scan or
          log in to your router.
        </p>
      </div>

      <div className="network-boundaries" aria-label="Device inventory safety boundaries">
        <span>Manual/demo only</span>
        <span>No scan is run</span>
        <span>No router login</span>
        <span>No router passwords</span>
        <span>No data uploaded</span>
      </div>

      <ul className="safety-boundary-list">
        <li>No scan is run.</li>
        <li>No router login is performed.</li>
        <li>Do not enter router passwords.</li>
        <li>Use your router app/admin page as the source of truth.</li>
        <li>Device inventory is manual in this version.</li>
      </ul>

      <section className="router-guidance-panel" aria-labelledby="router-guidance-heading">
        <div>
          <p className="section-kicker">Router guidance</p>
          <h2 id="router-guidance-heading">What to review in your router app</h2>
        </div>
        {guidanceLoading ? <p className="muted">Loading router guidance.</p> : null}
        {guidanceError ? <p className="runtime-note">{guidanceError}</p> : null}
        {routerGuidance ? (
          <>
            <p className="muted">{routerGuidance.source_note}</p>
            <div className="router-guidance-grid">
              {routerGuidance.topics.map((topic) => (
                <article className="router-guidance-topic" key={topic.id}>
                  <h3>{topic.title}</h3>
                  <p>{topic.summary}</p>
                  <ul>
                    {topic.steps.slice(0, 2).map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </>
        ) : null}
      </section>

      <section className="inventory-editor" aria-labelledby="inventory-editor-heading">
        <div className="inventory-editor__header">
          <div>
            <p className="section-kicker">Inventory</p>
            <h2 id="inventory-editor-heading">Devices to include</h2>
            <p className="muted">
              Current source: {submission.mode === "demo" ? "fake demo inventory" : "manual inventory"}.
            </p>
          </div>
          <div className="flow-actions">
            <button className="secondary-button" type="button" onClick={onLoadDemo}>
              Load Demo Inventory
            </button>
            <button className="secondary-button" type="button" onClick={addDevice}>
              Add Manual Device
            </button>
          </div>
        </div>

        <label className="form-field">
          <span>Inventory notes (optional, keep general)</span>
          <textarea
            value={submission.user_notes ?? ""}
            maxLength={500}
            onChange={(event) => updateSubmission({ user_notes: event.target.value })}
          />
        </label>

        <div className="inventory-device-list">
          {submission.devices.map((device, index) => (
            <article className="inventory-device-editor" key={device.id}>
              <div className="inventory-device-editor__header">
                <h3>{device.label || "Device"}</h3>
                <button className="secondary-button" type="button" onClick={() => removeDevice(index)}>
                  Remove
                </button>
              </div>
              <div className="form-grid">
                <label className="form-field">
                  <span>Label</span>
                  <input
                    value={device.label}
                    maxLength={120}
                    onChange={(event) => updateDevice(index, { label: event.target.value })}
                  />
                </label>
                <label className="form-field">
                  <span>Device type</span>
                  <select
                    value={device.device_type}
                    onChange={(event) => updateDevice(index, { device_type: event.target.value as DeviceType })}
                  >
                    {deviceTypeOptions.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="form-field">
                  <span>Trust level</span>
                  <select
                    value={device.trust_level}
                    onChange={(event) => updateDevice(index, { trust_level: event.target.value as DeviceTrustLevel })}
                  >
                    {trustOptions.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="form-field">
                  <span>Network placement</span>
                  <select
                    value={device.network_placement}
                    onChange={(event) =>
                      updateDevice(index, { network_placement: event.target.value as DeviceNetworkPlacement })
                    }
                  >
                    {placementOptions.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="form-field">
                  <span>Update status</span>
                  <select
                    value={device.update_status}
                    onChange={(event) =>
                      updateDevice(index, { update_status: event.target.value as DeviceUpdateStatus })
                    }
                  >
                    {updateOptions.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="form-field">
                  <span>Used by (optional)</span>
                  <select
                    value={device.used_by ?? ""}
                    onChange={(event) => updateDevice(index, { used_by: event.target.value || null })}
                  >
                    {usedByOptions.map((option) => (
                      <option value={option} key={option || "blank"}>
                        {option ? formatStatus(option) : "Not specified"}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="inventory-toggles">
                <label>
                  <input
                    type="checkbox"
                    checked={device.recognized}
                    onChange={(event) => updateDevice(index, { recognized: event.target.checked })}
                  />
                  <span>Recognized</span>
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={device.sensitive}
                    onChange={(event) => updateDevice(index, { sensitive: event.target.checked })}
                  />
                  <span>Sensitive device</span>
                </label>
              </div>

              <label className="form-field">
                <span>Notes (optional, avoid personal details)</span>
                <textarea
                  value={device.notes ?? ""}
                  maxLength={240}
                  onChange={(event) => updateDevice(index, { notes: event.target.value })}
                />
              </label>
            </article>
          ))}
        </div>
      </section>

      <div className="flow-actions">
        <button className="secondary-button" type="button" onClick={onBackToModes}>
          Back to Modes
        </button>
        <button className="primary-button" type="button" disabled={loading || !submission.devices.length} onClick={onRun}>
          {loading ? "Building Device Inventory Report" : "Build Device Inventory Report"}
        </button>
      </div>

      {error ? (
        <div className="loading-panel loading-panel--error">
          <h3>Device inventory unavailable</h3>
          <p>{error}</p>
        </div>
      ) : null}

      {report ? (
        <ReportReviewPanel
          report={report}
          kicker="Device inventory report"
          heading="Manual Device Inventory"
          scoreLabel="inventory score"
          findingsHeading="Device Inventory Findings"
          exportStatus={exportStatus}
          onExportMarkdown={onExportMarkdown}
          onExportJson={onExportJson}
          onBackToModes={onBackToModes}
          onClearReport={onClearReport}
        />
      ) : null}
    </section>
  );
}
