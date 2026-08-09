export interface HealthResponse {
  status: string;
  service: string;
}

export type ConnectionState = 'idle' | 'loading' | 'success' | 'error';

export interface EvaluationResultData {
  test_id: string;
  evaluator: string;
  passed: boolean;
  score: number;
  reason: string;
  severity?: string | null;
  evidence?: Record<string, unknown>;
}

export interface EvaluationRunData {
  run_id: string;
  started_at: string;
  completed_at?: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed';
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  results: EvaluationResultData[];
}
