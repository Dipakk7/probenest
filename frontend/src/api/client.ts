import { EvaluationRunData, HealthResponse } from '../types/health';

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

/**
 * Trigger an example evaluation run.
 */
export async function triggerEvaluation(): Promise<EvaluationRunData> {
  const response = await fetch('/api/v1/evaluations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error(`Evaluation trigger failed with status ${response.status}`);
  }

  const data: EvaluationRunData = await response.json();
  return data;
}
