# Probenest AI Security Threat Model

## 1. Executive Summary

This document defines the threat model for AI applications evaluated by **Probenest**. It outlines protected assets, threat actors, attack surfaces, threat categories, and security limitations.

---

## 2. Protected Assets

| Asset ID | Asset Name | Description | Sensitivity |
|---|---|---|---|
| `AST-01` | System Instructions | Core system prompts and behavioral guardrails | High |
| `AST-02` | Retrieved Context | Confidential RAG knowledge base documents | High |
| `AST-03` | Synthetic Secrets | Protected credentials (e.g. `PROBENEST-DEMO-SECRET-001`) | Critical |
| `AST-04` | Tool Execution Payload | Authorized API parameters and function invocations | Critical |
| `AST-05` | Application State | Memory, user session, and execution environment | High |

---

## 3. Threat Actors

1. **Malicious External User**: An untrusted user crafting adversarial prompts to bypass guardrails, steal secrets, or manipulate model outputs.
2. **Adversarial Input Data**: Malicious inputs embedded in retrieved RAG context (indirect prompt injection).
3. **Curious User**: An authorized user attempting to discover system prompts or extract hidden instructions.

---

## 4. Attack Surfaces

- **User Input Stream**: Input text submitted to the target AI application.
- **RAG Context Retrieval Pipeline**: Document chunks retrieved from vector indices or databases.
- **System Prompt Boundaries**: System instruction boundaries separating system rules from user input.
- **Tool / Function Calling Interface**: Function execution parameters passed to tools.

---

## 5. Threat Categories

### 1. Prompt Injection (`SEC-INJ`)
- **Direct Injection**: User prompt contains commands instructing the model to ignore system guidelines.
- **Indirect Injection**: Retrieved RAG documents contain hidden adversarial instructions.

### 2. Jailbreaks & Persona Switches (`SEC-JBK`)
- **DAN Persona Switching**: Adversarial framing compelling the model to adopt unrestricted personas.
- **Roleplay & Hypothetical Framing**: Framing forbidden actions inside roleplay games or fictional scenarios.
- **Developer Mode Bypasses**: Claiming system validation or developer override modes.

### 3. Instruction Override (`SEC-OVR`)
- Manipulating system logic to invent unsupported policies or violate context constraints.

### 4. Data Leakage (`SEC-LEAK`)
- Attempting to force verbatim disclosure of protected system prompts or secret tokens (`PROBENEST-DEMO-SECRET-001`).

### 5. Tool Abuse (`SEC-TOOL`)
- Injecting shell commands, SQL injection strings, or arbitrary parameter payloads into tool calls.

---

## 6. Security Limitations & Disclosures

> [!WARNING]
> Probenest's red-team test suites evaluate controlled benchmark attack vectors. Passing red-team benchmarks does NOT constitute proof of absolute application security.

1. **Finite Attack Coverage**: Test suites cover defined attack vectors; novel zero-day prompt techniques can bypass static benchmarks.
2. **Synthetic Secrets**: Synthetic secret tokens evaluate leakage patterns; they do not replace production secret management systems.
3. **Probabilistic Behavior**: LLM behavior is inherently probabilistic. High benchmark scores indicate high statistical defense probability over evaluated test cases.
