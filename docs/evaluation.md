# Probenest Evaluation & Reliability Philosophy

## Overview

Probenest evaluates AI applications across two primary pillars:

1. **Quality Metrics**: Measuring functional behavior, semantic truthfulness, and domain accuracy.
2. **Adversarial & Security Probes**: Testing resilience against prompt injections, security bypasses, and system boundary violations.

---

## Planned Evaluation Categories (Future Phases)

> [!NOTE]
> Evaluation features described below are planned for upcoming phases. Phase 1 provides the foundational architecture.

### Quality Engine

- **Accuracy**: Verifies whether model output aligns with expected ground truth in golden dataset benchmarks.
- **Relevance**: Measures context adherence and query relevance to prevent off-topic generation.
- **Faithfulness**: Validates whether retrieved context supports the model output in RAG pipelines.
- **Hallucination Detection**: Flags unsupported claims or ungrounded assertions.
- **Tool-Call Correctness**: Validates JSON arguments, function schemas, and execution responses.

### Red-Team Engine

- **Prompt Injection**: Injects instructions into user inputs or context streams to test model boundary integrity.
- **Jailbreak Resistance**: Tests resilience against persona switches, prefix injection, and safety filter evasions.
- **Instruction Override**: Evaluates system prompt retention under adversarial manipulation.
- **Data Leakage**: Assesses prevention of internal system prompt disclosure or sensitive training data exposure.
- **Tool Abuse**: Checks for unauthorized parameters or unauthorized actions executed via tool bindings.

---

## Evaluation Workflow Concept

```text
Golden / Red-Team Datasets
            ↓
     Evaluation Runner
            ↓
  Probe Execution Engine
            ↓
    Scoring & Metrics
            ↓
   Regression Dashboard
```
