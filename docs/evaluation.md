# Probenest Evaluation & Reliability Philosophy

## Overview

Probenest evaluates AI applications across two primary pillars:

1. **Quality Metrics**: Measuring functional behavior, semantic truthfulness, and domain accuracy.
2. **Adversarial & Security Probes**: Testing resilience against prompt injections, security bypasses, and system boundary violations.

---

## Phase 2 Core Engine Architecture

Phase 2 introduces the foundational evaluation abstractions and pipeline workflow:

```text
EvaluationCase
      ↓
TargetAdapter (MockTargetAdapter)
      ↓
TargetResponse
      ↓
Evaluator (ExactMatchEvaluator)
      ↓
EvaluationResult
      ↓
EvaluationRun (Persisted to SQLite)
```

### Core Abstractions

- **`EvaluationCase`**: Encapsulates prompt inputs, expected ground truth outputs, categories, tags, and expected context snippets.
- **`TargetAdapter`**: Protocol interface decoupling evaluation logic from target AI application implementations.
- **`ExactMatchEvaluator`**: Demonstration evaluator asserting exact text match between target output and expected output.
- **`EvaluationRunner`**: Generic runner orchestrating case execution, evaluator invocation, and pass/fail metric collection.

---

## Planned Evaluation Categories (Future Phases)

> [!NOTE]
> Advanced evaluators (RAG faithfulness, LLM-as-a-judge, prompt injection probes, red-teaming) will be implemented in upcoming phases.

### Quality Engine (Phase 3+)

- **Accuracy**: Verifies whether model output aligns with expected ground truth in golden dataset benchmarks.
- **Relevance**: Measures context adherence and query relevance to prevent off-topic generation.
- **Faithfulness**: Validates whether retrieved context supports the model output in RAG pipelines.
- **Hallucination Detection**: Flags unsupported claims or ungrounded assertions.
- **Tool-Call Correctness**: Validates JSON arguments, function schemas, and execution responses.

### Red-Team Engine (Phase 4+)

- **Prompt Injection**: Injects instructions into user inputs or context streams to test model boundary integrity.
- **Jailbreak Resistance**: Tests resilience against persona switches, prefix injection, and safety filter evasions.
- **Instruction Override**: Evaluates system prompt retention under adversarial manipulation.
- **Data Leakage**: Assesses prevention of internal system prompt disclosure or sensitive training data exposure.
- **Tool Abuse**: Checks for unauthorized parameters or unauthorized actions executed via tool bindings.
