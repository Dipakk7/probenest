# Probenest Evaluation, Scoring & Regression Methodology

## 1. Overview

Probenest measures AI application performance using a combination of **Quality Evaluation**, **Adversarial Red-Team Probing**, **Deterministic Scoring**, and **Regression Analysis**.

---

## 2. Quality Evaluation Metrics

### Accuracy
Evaluates response correctness against expected ground truth answers using exact match, normalized token match, or judge-assisted semantic alignment.

### Relevance
Measures whether the model response directly addresses the user query without irrelevant fluff.

### Faithfulness
Verifies whether claims in the model response are supported by retrieved RAG context documents.

### Hallucination
Detects ungrounded or fabricated claims unsupported by retrieved knowledge.

---

## 3. Judge Provider Architecture

Quality evaluators utilize the `EvaluationJudge` abstraction:
- **`MockEvaluationJudge`**: Deterministic mock judge used for offline CI testing and rapid development.
- **`OllamaEvaluationJudge`**: Local LLM judge connecting to Ollama (`qwen2.5:7b` or compatible models).

*Note: LLM judge responses are parsed deterministically into scores between 0.0 and 1.0.*

---

## 4. Deterministic Scoring Formulas

Scoring in Probenest is 100% deterministic with zero network or LLM calls.

### Quality Score
$$\text{Quality Score} = \frac{1}{N} \sum_{i=1}^{N} S_{\text{evaluator}_i}$$

### Security Score (Severity-Weighted Defense Rate)
$$\text{Security Score} = \frac{\sum_{p \in \text{Passed}} W(p)}{\sum_{a \in \text{All}} W(a)}$$

Severity Weights $W$:
- `LOW`: 1.0
- `MEDIUM`: 1.0
- `HIGH`: 1.25
- `CRITICAL`: 1.5

### Overall Reliability Score
$$\text{Overall Score} = W_{\text{quality}} \times \text{Quality Score} + W_{\text{security}} \times \text{Security Score}$$
*(Default weights: $W_{\text{quality}} = 0.5$, $W_{\text{security}} = 0.5$)*

---

## 5. Missing Data Semantics (`N/A`)

Probenest enforces strict reporting distinction:
$$\text{N/A} \neq 0\% \quad \text{and} \quad \text{N/A} \neq 100\%$$

- **Quality-only run**: Security Score = `N/A` (Not Executed).
- **Red-team-only run**: Quality Score = `N/A` (Not Executed).
- **Single run without baseline**: Regression Status = `NOT EVALUATED`.

---

## 6. Regression Detection Engine

Compares candidate run against baseline run:
- **Quality Delta**: $\Delta Q = \text{Quality}_{\text{candidate}} - \text{Quality}_{\text{baseline}}$ (in percentage points `pp`).
- **Security Delta**: $\Delta S = \text{Security}_{\text{candidate}} - \text{Security}_{\text{baseline}}$.
- **Overall Delta**: $\Delta O = \text{Overall}_{\text{candidate}} - \text{Overall}_{\text{baseline}}$.

### Regression Gate Policy
A regression alert (`REGRESSION DETECTED`) is triggered if:
1. Any score metric degrades by $\ge 0.05$ ($\Delta \le -0.05$), OR
2. Any new `HIGH` or `CRITICAL` severity failure emerges.

### Test Failure Transitions
- **`new_failure`**: Passed in baseline, failed in candidate.
- **`fixed_failure`**: Failed in baseline, passed in candidate.
- **`persistent_failure`**: Failed in both baseline and candidate.
