import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import assert from "node:assert/strict";

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = join(frontendRoot, "src");

function read(relativePath) {
  return readFileSync(join(frontendRoot, relativePath), "utf8");
}

function walkFiles(directory) {
  return readdirSync(directory).flatMap((entry) => {
    const absolute = join(directory, entry);
    if (statSync(absolute).isDirectory()) {
      return walkFiles(absolute);
    }
    return absolute;
  });
}

function readAllSource() {
  return walkFiles(sourceRoot)
    .filter((file) => /\.(css|ts|tsx)$/.test(file))
    .map((file) => readFileSync(file, "utf8"))
    .join("\n");
}

test("home page presents a dashboard-first guided path and de-emphasized advanced options", () => {
  const app = read("src/App.tsx");
  const dashboard = read("src/components/HomeGuardDashboard.tsx");
  const source = app + dashboard;
  const css = read("src/styles/app.css");

  [
    "Start with one guided check",
    "Run HomeGuard Check",
    "Try Demo",
    "View Last Result in This Session",
    "Advanced Options",
    "What HomeGuard checked",
    "Network Devices",
    "Find devices on my home network",
    "Start Device Discovery",
    "Device checks",
    "Questionnaire answers",
    "Passive network awareness",
    "Device inventory",
    "Router guidance",
    "Not available on this platform",
    "Dashboard / Export",
    "Demo Mode",
    "Local Device Audit",
    "Questionnaire Only",
    "Device Inventory Helper",
    "Local Network Awareness",
    "Windows Device Audit",
    "macOS Device Audit",
    "Linux Device Audit",
    "Advanced Checks",
  ].forEach((label) => assert.match(source, new RegExp(label)));

  assert.match(app, /status="Recommended"/);
  assert.match(app, /mode-group--recommended/);
  assert.match(app, /mode-group--advanced/);
  assert.match(app, /variant="advanced"/);
  assert.match(app, /advancedOptionsStorageKey/);
  assert.match(app, /guided-setup/);
  assert.match(app, /networkDiscoveryStatementVersion/);
  assert.match(app, /include_network_discovery/);
  assert.match(app, /user_understands_private_network_only/);
  assert.match(app, /No public targets/);
  assert.match(app, /No ports checked/);
  assert.match(app, /No router login/);
  assert.match(app, /PrimaryNavigation/);
  assert.match(app, /openNavigationTarget/);
  assert.match(css, /\.home-cta-panel/);
  assert.match(css, /\.advanced-options-drawer/);
  assert.match(css, /\.guided-setup-panel/);
  assert.match(css, /\.guided-discovery-panel/);
  assert.match(css, /\.network-devices-tile/);
  assert.match(css, /\.safety-chip-list/);
  assert.match(css, /\.mode-card--advanced/);
  assert.match(css, /\.primary-nav/);
  assert.match(css, /\.nav-button--active/);
  assert.match(css, /border-style: dashed/);
});

test("demo mode uses the sample report route and cannot stay in the old infinite loading state", () => {
  const app = read("src/App.tsx");
  const client = read("src/api/client.ts");

  assert.match(client, /getDemoReport\(\): Promise<HomeGuardReport>/);
  assert.match(client, /"\/demo\/report"/);
  assert.match(
    app,
    /Could not load the demo report\. Confirm the backend is running on port 8000\./,
  );
  assert.match(app, /setDemoReport\(\{ state: "loading" \}\)/);
  assert.match(app, /setDemoReport\(\{ state: "ready", report \}\)/);
  assert.match(app, /setDemoReport\(\{\s*state: "error",\s*message: demoReportUnavailableMessage,/s);
  assert.doesNotMatch(app, /\[demoReport\.state,\s*flowStep\]/);
});

test("safety acknowledgement is versioned session-only state and does not persist answers or reports", () => {
  const app = read("src/App.tsx");

  assert.match(app, /ai-homeguard-safety-ack-v0\.1\.0/);
  assert.match(app, /window\.sessionStorage\.setItem/);
  assert.match(app, /JSON\.stringify\(\{ acknowledged: true, version: safetyAcknowledgementVersion \}\)/);
  assert.match(app, /setPendingNavigation\(null\)/);
  assert.doesNotMatch(app, /localStorage/);
  assert.doesNotMatch(app, /sessionStorage\.setItem\([^)]*questionnaire/i);
  assert.doesNotMatch(app, /sessionStorage\.setItem\([^)]*report/i);
  assert.doesNotMatch(app, /sessionStorage\.setItem\([^)]*inventory/i);
});

test("runtime clarity separates browser hint, backend runtime, and container audit target", () => {
  const localAuditPanel = read("src/components/LocalAuditPanel.tsx");
  const app = read("src/App.tsx");
  const css = read("src/styles/app.css");

  [
    "Browser/device hint",
    "Backend runtime",
    "Audit target",
    "Container Runtime Detected",
    "Your browser appears to be on macOS, but the backend is running in a Linux container.",
    "For host-level macOS checks, run the backend natively with uv.",
  ].forEach((label) => assert.match(localAuditPanel + app, new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));

  assert.match(css, /\.runtime-detail-grid/);
  assert.match(css, /\.runtime-warning/);
});

test("shared report review components cover summary, filters, empty, export, loading, and error states", () => {
  const review = read("src/components/ReportReviewPanel.tsx");

  [
    "Overall posture",
    "Top Recommended Actions",
    "Filter findings",
    "Evidence source",
    "Show good findings",
    "No matching findings",
    "Export Markdown",
    "Export JSON",
    "Review exports before sharing.",
    "Clear Current Report",
    "ErrorState",
    "LoadingState",
    "EmptyState",
  ].forEach((label) => assert.match(review, new RegExp(label)));

  assert.match(review, /statusFilter/);
  assert.match(review, /platformFilter/);
  assert.match(review, /sourceFilter/);
  assert.match(review, /sortMode/);
});

test("finding cards show source badges, guidance labels, and collapsed technical details", () => {
  const findingCard = read("src/components/FindingCard.tsx");
  const labels = read("src/components/reportLabels.ts");
  const guidance = read("src/components/DefensiveGuidancePanel.tsx");

  assert.match(findingCard, /EvidenceSourceBadge/);
  assert.match(findingCard, /More Detail/);
  assert.match(findingCard, /Detailed title/);
  assert.match(guidance, /D3FEND-informed guidance is educational and does not guarantee protection\./);

  [
    "Questionnaire",
    "Local Device Check",
    "Demo Data",
    "Could Not Check",
    "Runtime Context",
    "Manual Device Inventory",
    "Demo Device Inventory",
    "Passive Network Awareness",
    "Network Discovery",
  ].forEach((label) => assert.match(labels, new RegExp(label)));
});

test("network discovery client and dashboard stay private-only and dashboard-first", () => {
  const client = read("src/api/client.ts");
  const dashboard = read("src/components/HomeGuardDashboard.tsx");
  const app = read("src/App.tsx");

  [
    "NetworkDiscoveryRequest",
    "getNetworkDiscoveryPolicy",
    "getNetworkDiscoveryReport",
    "/network/discovery-policy",
    "/reports/network-discovery",
    "include_network_discovery",
    "network_discovery_request",
  ].forEach((label) => assert.match(client, new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));

  [
    "Devices on your home network",
    "No public targets were scanned",
    "No ports were scanned",
    "No router login was attempted",
    "Limited by Docker",
    "Could not check",
    "network-discovery-device",
  ].forEach((label) => assert.match(dashboard, new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));

  assert.doesNotMatch(app + dashboard, /type="password"/i);
  assert.doesNotMatch(app + dashboard, /name=.*router.*password/i);
  assert.doesNotMatch(app + client, /target[_-]?input/i);
  assert.doesNotMatch(app + client, /public target field/i);
});

test("required safety and privacy copy remains visible", () => {
  const source = readAllSource();

  [
    "Read-only checks only.",
    "No settings are changed.",
    "No public scanning, router login, packet capture, or automatic changes.",
    "No data upload, telemetry, database, or AI provider call.",
    "Do not enter router passwords.",
    "Review exports before sharing.",
    "Backend connected",
    "Confirm the backend is running on port 8000.",
    "unsupported-platform result",
  ].forEach((phrase) => assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));
});

test("main user-facing safety copy does not use development slice terminology", () => {
  const app = read("src/App.tsx");
  const network = read("src/components/NetworkAwarenessPanel.tsx");

  assert.doesNotMatch(app, /what this slice/i);
  assert.doesNotMatch(app, /keeps this slice/i);
  assert.doesNotMatch(network, /this slice uses/i);
  assert.match(app, /What this version does and does not do/);
  assert.match(network, /this version uses passive local network context only/);
});

test("forbidden overclaiming and remediation language is absent from frontend source", () => {
  const source = readAllSource().toLowerCase();

  ["auto fix", "auto-fix", "hacked", "certified secure", "guaranteed", "pen test", "deep scan"].forEach(
    (phrase) => assert.equal(source.includes(phrase), false, `${phrase} should not appear`),
  );
});
