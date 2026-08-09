# Probenest Demonstration Sequence Script (60–90 Seconds)

This document provides a step-by-step reproducible script for demonstrating Probenest via CLI and Web Dashboard.

---

## Demonstration Sequence

### Step 1: Quality Evaluation (0–15 Seconds)
Run quality evaluation against mock target application:
```bash
probenest evaluate --target mock --evaluators quality
```
*Expected Output*: Displays Accuracy, Relevance, Faithfulness, and Hallucination metric scores (e.g. 80.0% score, 4/5 cases passed).

### Step 2: Adversarial Red-Team Audit (15–30 Seconds)
Execute automated red-team security probes:
```bash
probenest redteam --target mock
```
*Expected Output*: Displays defense counts across Prompt Injection, Jailbreak, Instruction Override, Data Leakage, and Tool Abuse, listing failed attack payloads and severity.

### Step 3: Reliability Score Summary (30–40 Seconds)
Calculate and display run score for generated run ID:
```bash
probenest score RUN_ID
```
*Expected Output*: Displays Quality Score, Security Score, and Overall Reliability Score.

### Step 4: Report Generation (40–55 Seconds)
Generate JSON (schema v1.0) and Markdown report artifacts:
```bash
probenest report RUN_ID
```
*Expected Output*: Creates `reports/RUN_ID/report.json` and `reports/RUN_ID/report.md`.

### Step 5: Run-to-Run Regression Comparison (55–70 Seconds)
Compare baseline vs candidate runs:
```bash
probenest compare BASELINE_RUN_ID CANDIDATE_RUN_ID
```
*Expected Output*: Displays percentage point (`pp`) deltas, regression alert status (`REGRESSION DETECTED` or `NO REGRESSION`), new failures, fixed failures, and persistent failures.

### Step 6: Web Dashboard Walkthrough (70–90 Seconds)
Start backend and frontend:
```bash
# Terminal 1: cd backend && uvicorn app.main:app --port 8000
# Terminal 2: cd frontend && npm run dev
```
Navigate to `http://localhost:5173`:
1. **Overview Page (`/`)**: Point out Overall Reliability, Quality Score, Security Score, and active Regression Alert banner.
2. **Red Team Page (`/redteam`)**: Highlight category defense rates and failure details table.
3. **Compare Page (`/compare`)**: Show baseline vs candidate run selection and metric deltas.
4. **Reports Page (`/reports`)**: Show JSON (schema v1.0) and Markdown report preview/download.
