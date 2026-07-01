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
  guidance_id?: string | null;
  category: "harden" | "detect" | "isolate" | "recover" | "educate" | "out_of_scope";
  defensive_concept: string;
  home_action: string;
  technical_action?: string | null;
  rationale: string;
  difficulty: Difficulty;
  estimated_time_minutes?: number | null;
  requires_admin: boolean;
  educational_only: boolean;
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
  mode: "demo" | "local" | "combined";
  platform_scope: string[];
  summary: ReportSummary;
  findings: Finding[];
  disclaimer: string;
  safety_notes: string[];
  runtime_context?: RuntimeContext | null;
};

export type RuntimeContext = {
  detected_platform: string;
  runtime_environment: "native" | "docker" | "unknown";
  architecture?: string | null;
  hostname_present: boolean;
  platform_notes: string[];
  limitations: string[];
};

export type QuestionnaireOption = {
  value: string;
  label: string;
};

export type QuestionnaireQuestion = {
  id: string;
  section: string;
  prompt: string;
  help_text?: string | null;
  answer_type: "yes_no" | "yes_no_unsure" | "single_choice" | "multi_choice" | "text_short";
  options: QuestionnaireOption[];
  required: boolean;
  home_user_label?: string | null;
};

export type QuestionnaireSection = {
  id: string;
  title: string;
  description: string;
  questions: QuestionnaireQuestion[];
};

export type QuestionnaireAnswer = {
  question_id: string;
  value: string | string[] | null;
  skipped?: boolean;
};

export type QuestionnaireSubmission = {
  answers: QuestionnaireAnswer[];
  mode?: "demo" | "questionnaire";
  generated_at?: string | null;
};

export type QuestionnaireResult = {
  answered_count: number;
  skipped_count: number;
  findings: Finding[];
  top_actions: string[];
};

export type CombinedReportRequest = {
  include_local_device?: boolean;
  include_questionnaire?: boolean;
  questionnaire_submission?: QuestionnaireSubmission | null;
  acknowledged_authorization?: boolean;
  export_format?: "none" | "markdown" | "json";
};

export type CombinedReportResponse = {
  report: HomeGuardReport;
  export_markdown?: string | null;
  export_json?: Record<string, unknown> | null;
  warnings: string[];
  limitations: string[];
};

export type D3FENDCatalogEntry = {
  guidance_id: string;
  category: D3FENDGuidance["category"];
  defensive_concept: string;
  home_action: string;
  technical_action?: string | null;
  rationale: string;
  difficulty: Difficulty;
  estimated_time_minutes: number;
  applies_to_categories: string[];
  applies_to_platforms: string[];
  requires_admin: boolean;
  educational_only: boolean;
};

export type D3FENDCatalogResponse = {
  version: string;
  source_note: string;
  disclaimer: string;
  remote_fetch_performed: boolean;
  guidance: D3FENDCatalogEntry[];
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

export async function getQuestionnaire(): Promise<QuestionnaireSection[]> {
  return getJson<QuestionnaireSection[]>("/questionnaire");
}

export async function getD3FENDGuidanceCatalog(): Promise<D3FENDCatalogResponse> {
  return getJson<D3FENDCatalogResponse>("/knowledge/d3fend-guidance");
}

export async function evaluateQuestionnaire(
  submission: QuestionnaireSubmission,
): Promise<QuestionnaireResult> {
  const response = await fetch(`${apiBaseUrl}/questionnaire/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<QuestionnaireResult>;
}

export async function getQuestionnaireReport(
  submission: QuestionnaireSubmission,
): Promise<HomeGuardReport> {
  const response = await fetch(`${apiBaseUrl}/reports/questionnaire`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<HomeGuardReport>;
}

export async function getWindowsLocalReport(): Promise<HomeGuardReport> {
  return getJson<HomeGuardReport>("/reports/windows-local");
}

export async function getMacOSLocalReport(): Promise<HomeGuardReport> {
  return getJson<HomeGuardReport>("/reports/macos-local");
}

export async function getLinuxLocalReport(): Promise<HomeGuardReport> {
  return getJson<HomeGuardReport>("/reports/linux-local");
}

export async function getLocalDeviceReport(): Promise<HomeGuardReport> {
  return getJson<HomeGuardReport>("/reports/local-device");
}

export async function getRuntimeContext(): Promise<RuntimeContext> {
  return getJson<RuntimeContext>("/runtime");
}

export async function getCombinedReport(request: CombinedReportRequest): Promise<CombinedReportResponse> {
  const response = await fetch(`${apiBaseUrl}/reports/combined`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      message = payload.detail ?? message;
    } catch {
      message = await response.text();
    }
    throw new Error(message);
  }
  return response.json() as Promise<CombinedReportResponse>;
}

export async function exportMarkdownReport(report: HomeGuardReport): Promise<string> {
  const response = await fetch(`${apiBaseUrl}/reports/export/markdown`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.text();
}

export async function exportJsonReport(report: HomeGuardReport): Promise<Record<string, unknown>> {
  const response = await fetch(`${apiBaseUrl}/reports/export/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<Record<string, unknown>>;
}
