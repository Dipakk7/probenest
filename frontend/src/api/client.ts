import { HealthResponse } from '../types/health';

/**
 * Fetch health status from Probenest FastAPI backend.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch('/health', {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Backend health check failed with status ${response.status}`);
  }

  const data: HealthResponse = await response.json();
  return data;
}
