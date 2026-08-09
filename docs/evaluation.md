# Probenest Evaluation & Reliability Philosophy

## Overview

Probenest evaluates AI applications across two primary pillars:

1. **Quality Metrics**: Measuring functional behavior, semantic truthfulness, query relevance, context faithfulness, and hallucination grounding.
2. **Adversarial & Security Probes**: Stress-testing resilience against prompt injections, jailbreaks, data leakage, and tool abuse.

---

## Phase 4 Quality Engine Metrics

Phase 4 implements four normalized quality metrics (scored `0.0` to `1.0`, where `1.0` = excellent/pass):

### 1. Accuracy (`AccuracyEvaluator`)
- **Question**: Is the factual content of the answer semantically correct compared to ground truth?
- **Method**: Layer 1 text normalization, Layer 2 exact/fuzzy matching, Layer 3 LLM judge fallback.

### 2. Relevance (`RelevanceEvaluator`)
- **Question**: Does the output directly address the user's question without off-topic filler?
- **Method**: Evaluates query-response directness, penalizing unhelpful or off-topic responses.

### 3. Faithfulness (`FaithfulnessEvaluator`)
- **Question**: Are the claims in the answer supported by retrieved context snippets?
- **Method**: Evaluates support of output claims strictly against `TargetResponse.context`.

### 4. Hallucination Risk / Grounding (`HallucinationEvaluator`)
- **Question**: Does the output contain unsupported or invented facts?
- **Semantics**: **Score 1.0 = no hallucination / fully grounded**, **Score 0.0 = severe ungrounded hallucination**.

---

## Metric Comparison Table

| Metric | Primary Question | Primary Inputs | Score 1.0 Meaning |
| :--- | :--- | :--- | :--- |
| **Accuracy** | Is the answer factually correct? | Input, Expected Output, Actual Output | Factually accurate answer |
| **Relevance** | Does the answer address the question? | Input, Actual Output | Directly relevant response |
| **Faithfulness** | Are claims supported by context? | Actual Output, Retrieved Context | Claims fully supported by context |
| **Hallucination** | Are there ungrounded claims? | Actual Output, Retrieved Context | Fully grounded (no hallucination) |
