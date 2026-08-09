# Probenest Architecture Documentation

## Overview

Probenest is an Adversarial AI Evaluation & Reliability Platform designed to assess AI applications for quality (accuracy, relevance, faithfulness, hallucination, tool usage) and security (prompt injection, jailbreaks, instruction overrides, data leakage, tool abuse).

---

## Phase 5 Architecture (Adversarial Red-Team Engine)

Phase 5 implements the Adversarial Red-Team Engine evaluating target applications against controlled attack cases across 5 attack categories:

```text
                        Target Application (Mock / DemoRAG)
                                       ↓
                                RedTeamRunner
                                       ↓
                         Adversarial Attack Cases
               ┌───────────────┼───────────────┬───────────────┬───────────────┐
               ↓               ↓               ↓               ↓               ↓
        PromptInjection    Jailbreak     InstructionOverride  DataLeakage    ToolAbuse
               │               │               │               │               │
               └───────────────┼───────────────┴───────────────┴───────────────┘
                               ↓
                 RedTeamEvaluator (PASS = Resisted, FAIL = Succumbed)
                               ↓
                    RedTeamResult & Severity (LOW / MEDIUM / HIGH / CRITICAL)
                               ↓
                       SQLite DB Persistence
```

### Core Architecture Components

1. **Red-Team Domain Models (`backend/app/domain/redteam.py`)**:
   - `AttackCategory`: Controlled attack enum (`prompt_injection`, `jailbreak`, `instruction_override`, `data_leakage`, `tool_abuse`).
   - `Severity`: Impact severity enum (`low`, `medium`, `high`, `critical`).
   - `RedTeamCase`: Represents an adversarial prompt test case.
   - `RedTeamResult`: Standardized evaluation result preserving pass/fail defense state, evidence, actual target output, and expected safe behavior.
   - `RedTeamRun`: Container tracking total cases, defended cases, failed cases, and high-risk failures count.

2. **Red-Team Evaluators (`backend/app/redteam/evaluators/`)**:
   - `PromptInjectionEvaluator`: Checks for refusal, system prompt leakage, or instruction compliance.
   - `JailbreakEvaluator`: Checks if safety boundaries and persona restrictions were bypassed.
   - `InstructionOverrideEvaluator`: Checks if user attack text overrode core system rules.
   - `DataLeakageEvaluator`: Checks for disclosure of synthetic protected secret tokens (`PROBENEST-DEMO-SECRET-001`).
   - `ToolAbuseEvaluator`: Inspects `TargetResponse.tool_calls` for unauthorized execution of protected synthetic actions (`protected_action`, `delete_account`).

3. **Attack Datasets (`datasets/redteam/`)**:
   - Structured JSON attack datasets for prompt injection, jailbreak, data leakage, and tool abuse.

4. **Persistence Layer (`backend/app/repositories/redteam_repository.py`)**:
   - Stores red-team runs and detailed result records in SQLite ORM (`redteam_runs` and `redteam_results`).

---

## Planned Architecture (Future Phases)

In upcoming phases, Probenest will incorporate security scores, regression detection, and dashboard analytics:

```text
Target AI Application (DemoRAG)
           ↓
    EvaluationRunner
    ┌──────┴──────┐
    ↓             ↓
Quality Engine  Red-Team Engine (Phase 5)
    └──────┬──────┘
           ↓
     Score Engine & Analytics (Phase 6+)
           ↓
     React Dashboard
```
