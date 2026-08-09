import {
  EvaluationRun,
  HealthResponse,
  RedTeamRun,
  RegressionResult,
  RunReport,
  RunScore,
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // Ignore JSON parse failure
    }
    throw new Error(errorDetail);
  }

  return response.json() as Promise<T>;
}

export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

export async function fetchEvaluations(): Promise<EvaluationRun[]> {
  return request<EvaluationRun[]>('/api/v1/evaluations');
}

export async function fetchEvaluationRun(runId: string): Promise<EvaluationRun> {
  return request<EvaluationRun>(`/api/v1/evaluations/${runId}`);
}

export async function triggerEvaluation(target: string = 'mock'): Promise<EvaluationRun> {
  return request<EvaluationRun>('/api/v1/evaluations', {
    method: 'POST',
    body: JSON.stringify({ target }),
  });
}

export async function fetchRedTeamRuns(): Promise<RedTeamRun[]> {
  return request<RedTeamRun[]>('/api/v1/redteam');
}

export async function fetchRedTeamRun(runId: string): Promise<RedTeamRun> {
  return request<RedTeamRun>(`/api/v1/redteam/${runId}`);
}

export async function triggerRedTeam(target: string = 'demorrag'): Promise<RedTeamRun> {
  return request<RedTeamRun>('/api/v1/redteam', {
    method: 'POST',
    body: JSON.stringify({ target }),
  });
}

export async function fetchRunScore(runId: string): Promise<RunScore> {
  return request<RunScore>(`/api/v1/evaluations/${runId}/score`);
}

export async function fetchRunComparison(baselineId: string, candidateId: string): Promise<RegressionResult> {
  return request<RegressionResult>(`/api/v1/evaluations/compare/${baselineId}/${candidateId}`);
}

export async function fetchRunReport(runId: string): Promise<RunReport> {
  // Construct report client-side from available run/score endpoints if report route is direct
  try {
    const score = await fetchRunScore(runId);
    let evalRun: EvaluationRun | null = null;
    let rtRun: RedTeamRun | null = null;

    try {
      evalRun = await fetchEvaluationRun(runId);
    } catch {
      // Ignore
    }

    try {
      rtRun = await fetchRedTeamRun(runId);
    } catch {
      // Ignore
    }

    return {
      schema_version: '1.0',
      run: {
        run_id: runId,
        target: score.target,
        dataset: evalRun ? 'example.json' : (rtRun ? 'redteam' : 'default'),
        status: evalRun ? evalRun.status : (rtRun ? rtRun.status : 'completed'),
        created_at: score.created_at,
      },
      quality: {
        available: Boolean(evalRun),
        quality_score: evalRun ? score.quality_score.score : null,
        evaluator_scores: score.quality_score.evaluator_scores || {},
        total_cases: evalRun?.total_cases || 0,
        passed_cases: evalRun?.passed_cases || 0,
        failed_cases: evalRun?.failed_cases || 0,
      },
      security: {
        available: Boolean(rtRun),
        security_score: rtRun ? score.security_score.score : null,
        weighted_defense_rate: score.security_score.weighted_defense_rate,
        total_cases: rtRun?.total_cases || 0,
        defended_cases: rtRun?.passed_cases || 0,
        failed_cases: rtRun?.failed_cases || 0,
        high_critical_failures: score.security_score.high_critical_failures || 0,
      },
      overall: {
        reliability_score: score.overall_score.score,
        quality_weight: score.overall_score.quality_weight,
        security_weight: score.overall_score.security_weight,
      },
      failures: [
        ...(evalRun?.results.filter((r) => !r.passed).map((r) => ({
          test_id: r.test_id,
          type: 'quality' as const,
          category_or_evaluator: r.evaluator,
          severity: r.severity,
          input_or_attack: r.test_id,
          actual_output: r.reason,
          expected_or_reason: r.reason,
        })) || []),
        ...(rtRun?.results.filter((r) => !r.passed).map((r) => ({
          test_id: r.test_id,
          type: 'redteam' as const,
          category_or_evaluator: r.category,
          severity: r.severity,
          input_or_attack: r.attack,
          actual_output: r.actual_output,
          expected_or_reason: r.reason,
        })) || []),
      ],
    };
  } catch (err) {
    throw new Error(`Failed to load report for run '${runId}': ${err instanceof Error ? err.message : String(err)}`);
  }
}
