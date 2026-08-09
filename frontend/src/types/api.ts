export interface HealthResponse {
  status: string;
  app: string;
  env: string;
}

export interface EvaluationResult {
  id?: string;
  run_id?: string;
  test_id: string;
  evaluator: string;
  passed: boolean;
  score: number;
  reason: string;
  severity: 'low' | 'medium' | 'high' | 'critical' | 'info';
  evidence_json?: Record<string, unknown>;
}

export interface EvaluationRun {
  run_id: string;
  target?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  results: EvaluationResult[];
}

export interface RedTeamResult {
  id?: string;
  run_id?: string;
  test_id: string;
  category: string;
  attack: string;
  passed: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
  actual_output: string;
  expected_behavior: string;
  evidence_json?: Record<string, unknown>;
}

export interface RedTeamRun {
  run_id: string;
  target: string;
  status: 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  high_critical_failures: number;
  results: RedTeamResult[];
}

export interface QualityScore {
  score: number;
  evaluator_scores: Record<string, number>;
}

export interface SecurityScore {
  score: number;
  high_critical_failures: number;
  weighted_defense_rate: number;
}

export interface OverallScore {
  score: number;
  quality_weight: number;
  security_weight: number;
}

export interface RunScore {
  run_id: string;
  target: string;
  quality_score: QualityScore;
  security_score: SecurityScore;
  overall_score: OverallScore;
  policy: {
    quality_weight: number;
    security_weight: number;
  };

  created_at: string;
}

export interface MetricDelta {
  metric_name: string;
  baseline_score: number;
  candidate_score: number;
  delta: number;
  is_regression: boolean;
}

export interface TestFailureChange {
  test_id: string;
  category_or_evaluator: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  change_type: 'new_failure' | 'fixed_failure' | 'persistent_failure';
}

export interface RunComparison {
  baseline_run_id: string;
  candidate_run_id: string;
  target: string;
  is_comparable: boolean;
  warning?: string;
  quality_delta: number;
  security_delta: number;
  overall_delta: number;
  metric_deltas: MetricDelta[];
  new_failures: TestFailureChange[];
  fixed_failures: TestFailureChange[];
  persistent_failures: TestFailureChange[];
}

export interface RegressionResult {
  detected: boolean;
  severity: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  reasons: string[];
  comparison: RunComparison;
}

export interface RunMetadataReport {
  run_id: string;
  target: string;
  dataset?: string;
  status: string;
  created_at: string;
}

export interface QualityReportSection {
  available: boolean;
  quality_score: number | null;
  evaluator_scores: Record<string, number>;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
}

export interface SecurityReportSection {
  available: boolean;
  security_score: number | null;
  weighted_defense_rate: number | null;
  total_cases: number;
  defended_cases: number;
  failed_cases: number;
  high_critical_failures: number;
}

export interface OverallReportSection {
  reliability_score: number | null;
  quality_weight: number;
  security_weight: number;
}

export interface FailureDetail {
  test_id: string;
  type: 'quality' | 'redteam';
  category_or_evaluator: string;
  severity: string;
  input_or_attack: string;
  actual_output: string;
  expected_or_reason: string;
  evidence?: Record<string, unknown>;
}

export interface RunReport {
  schema_version: string;
  run: RunMetadataReport;
  quality: QualityReportSection;
  security: SecurityReportSection;
  overall: OverallReportSection;
  regression?: RegressionResult;
  failures: FailureDetail[];
}

export interface UnifiedRunSummary {
  run_id: string;
  target: string;
  type: 'quality' | 'redteam' | 'combined';
  status: string;
  created_at: string;
  quality_score: number | null;
  security_score: number | null;
  overall_score: number | null;
  total_cases: number;
  failed_cases: number;
}
