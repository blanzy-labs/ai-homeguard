import type { Finding, FindingStatus } from "../api/client";

export const statusLabels: Record<FindingStatus, string> = {
  good: "Good",
  review: "Review",
  fix_soon: "Fix Soon",
  needs_attention: "Needs Attention",
  unable_to_check: "Unable to Check",
};

export const overallStatusLabels: Record<FindingStatus, string> = {
  good: "Looks Good",
  review: "Review Recommended",
  fix_soon: "Fix Soon",
  needs_attention: "Needs Attention",
  unable_to_check: "Unable to Check",
};

export const statusPriority: Record<FindingStatus, number> = {
  needs_attention: 0,
  fix_soon: 1,
  review: 2,
  unable_to_check: 3,
  good: 4,
};

export function formatValue(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function evidenceSourceLabel(finding: Finding) {
  const sources = finding.evidence.map((item) => item.source.toLowerCase());
  const tags = finding.tags.map((tag) => tag.toLowerCase());

  if (sources.some((source) => source === "manual_inventory")) {
    return "Manual Device Inventory";
  }
  if (sources.some((source) => source === "demo_inventory")) {
    return "Demo Device Inventory";
  }
  if (tags.includes("device-inventory")) {
    return "Device Inventory Helper";
  }
  if (sources.some((source) => source === "questionnaire" || source.includes("questionnaire"))) {
    return "Questionnaire";
  }
  if (sources.some((source) => source.includes("demo"))) {
    return "Demo Data";
  }
  if (
    tags.includes("network-awareness") ||
    sources.some(
      (source) =>
        source.includes("passive network") ||
        source.includes("network awareness") ||
        source.includes("request authorization"),
    )
  ) {
    return "Passive Network Awareness";
  }
  if (tags.includes("unsupported-platform") || sources.some((source) => source.includes("platform guard"))) {
    return "Could Not Check";
  }
  if (sources.some((source) => source.includes("runtime"))) {
    return "Runtime Context";
  }
  if (sources.some((source) => source.includes("local check"))) {
    return "Local Device Check";
  }
  return "Local Device Check";
}
