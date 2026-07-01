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

test("mode navigation keeps recommended, secondary, and advanced paths visible", () => {
  const app = read("src/App.tsx");
  const css = read("src/styles/app.css");

  [
    "Full HomeGuard Report",
    "Demo Mode",
    "Local Device Audit",
    "Home Security Questionnaire",
    "Device Inventory Helper",
    "Local Network Awareness",
    "Windows Device Audit",
    "macOS Device Audit",
    "Linux Device Audit",
  ].forEach((label) => assert.match(app, new RegExp(label)));

  assert.match(app, /status="Recommended"/);
  assert.match(app, /mode-group--recommended/);
  assert.match(app, /mode-group--advanced/);
  assert.match(app, /variant="advanced"/);
  assert.match(css, /\.mode-card--advanced/);
  assert.match(css, /border-style: dashed/);
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
  assert.match(findingCard, /Technical details and evidence/);
  assert.match(guidance, /D3FEND-informed guidance is educational and does not guarantee protection\./);

  [
    "Questionnaire",
    "Local Device Check",
    "Demo Data",
    "Unsupported Platform",
    "Runtime Context",
    "Manual Device Inventory",
    "Demo Device Inventory",
    "Passive Network Awareness",
  ].forEach((label) => assert.match(labels, new RegExp(label)));
});

test("required safety and privacy copy remains visible", () => {
  const source = readAllSource();

  [
    "Read-only local checks.",
    "No settings are changed.",
    "No network scan is run.",
    "No data is uploaded.",
    "No router login is performed.",
    "Do not enter router passwords.",
    "Review exports before sharing.",
    "Backend unavailable",
    "unsupported-platform result",
  ].forEach((phrase) => assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));
});

test("forbidden overclaiming and remediation language is absent from frontend source", () => {
  const source = readAllSource().toLowerCase();

  ["auto fix", "auto-fix", "hacked", "certified secure", "guaranteed", "pen test", "deep scan"].forEach(
    (phrase) => assert.equal(source.includes(phrase), false, `${phrase} should not appear`),
  );
});
