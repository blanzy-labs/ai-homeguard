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
