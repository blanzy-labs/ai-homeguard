export type HealthResponse = {
  status: string;
  app: string;
};

export type VersionResponse = {
  app: string;
  repo: string;
  version: string;
  family: string;
};

export type FindingStatus =
  | "good"
  | "review"
  | "fix_soon"
  | "needs_attention"
  | "unable_to_check";

export type Severity = "info" | "low" | "medium" | "high";
export type Confidence = "high" | "medium" | "low" | "unknown";
export type Difficulty = "easy" | "medium" | "advanced";

export type Evidence = {
  source: string;
  method: string;
  observed_value: string;
  expected_value: string;
  command_hint?: string | null;
  notes?: string | null;
};

export type D3FENDGuidance = {
  category: "harden" | "detect" | "isolate" | "recover" | "educate" | "out_of_scope";
  defensive_concept: string;
  home_action: string;
  technical_action?: string | null;
  rationale: string;
  difficulty: Difficulty;
  estimated_time_minutes?: number | null;
};

export type AttackContext = {
  tactic?: string | null;
  technique_id?: string | null;
  technique_name?: string | null;
  explanation: string;
  confidence: Confidence;
  educational_only: boolean;
};

export type Finding = {
  id: string;
  title: string;
  home_title: string;
  technical_title?: string | null;
  status: FindingStatus;
  severity: Severity;
  confidence: Confidence;
  platform: string;
  category: string;
  summary: string;
  why_it_matters: string;
  evidence: Evidence[];
  d3fend_guidance: D3FENDGuidance[];
  attack_context: AttackContext[];
  recommended_action: string;
  difficulty: Difficulty;
  estimated_time_minutes?: number | null;
  user_can_fix: boolean;
  requires_admin: boolean;
  safe_to_ignore: boolean;
  docs_url?: string | null;
  tags: string[];
};

export type ReportSummary = {
  overall_status: FindingStatus;
  overall_score?: number | null;
  good_count: number;
  review_count: number;
  fix_soon_count: number;
  needs_attention_count: number;
  unable_to_check_count: number;
  top_actions: string[];
};

export type HomeGuardReport = {
  report_id: string;
  app: string;
  version: string;
  generated_at: string;
  mode: "demo" | "local";
  platform_scope: string[];
  summary: ReportSummary;
  findings: Finding[];
  disclaimer: string;
  safety_notes: string[];
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/health");
}

export async function getVersion(): Promise<VersionResponse> {
  return getJson<VersionResponse>("/version");
}

export async function getDemoReport(): Promise<HomeGuardReport> {
  return getJson<HomeGuardReport>("/demo/report");
}
