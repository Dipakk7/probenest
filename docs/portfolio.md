# Probenest Portfolio & Resume Documentation

## 1. Resume Bullet Points

- **AI Evaluation & Security Platform**: Architected and built Probenest, an open-source evaluation and adversarial red-teaming platform for assessing LLMs and RAG applications across quality metrics and 5 security failure modes (Prompt Injection, Jailbreak, Instruction Override, Data Leakage, Tool Abuse).
- **Deterministic Reliability Scoring & Regression Engine**: Designed a 100% deterministic score engine calculating severity-weighted security defense rates and run-to-run regression detection with automated CI gating (`0` = Pass, `1` = Regression Gate).
- **Full-Stack Engineering & CLI Tooling**: Developed a FastAPI REST backend, SQLite ORM persistence layer, Typer CLI with JSON (schema v1.0) / Markdown reporting, and a React + TypeScript + Vite engineering dashboard.
- **Reference RAG Application Architecture**: Created DemoRAG, a standalone reference RAG application featuring document chunking, TF-IDF retrieval, synthetic security policy enforcement, and a decoupled adapter boundary (`TargetAdapter`).
- **Reliability & Offline CI Hardening**: Implemented isolated test database session fixtures, 85% backend test coverage with `pytest-cov`, and an offline multi-job GitHub Actions CI workflow executing without external LLM dependencies.

---

## 2. Project Summary Paragraph

> **Probenest** is an open-source adversarial AI evaluation and reliability platform built with Python, FastAPI, SQLite, React, and TypeScript. It enables developers and security engineers to systematically evaluate AI applications for accuracy, faithfulness, hallucination detection, prompt injection resilience, jailbreaks, data leakage, and tool abuse. Probenest features a 100% deterministic reliability scoring engine, run-to-run regression detection, machine-readable JSON/Markdown report generation, engineering CLI workflows, and a web dashboard.

---

## 3. GitHub Repository Tagline

> Adversarial AI evaluation & reliability platform combining quality metrics, red-team security audits, deterministic reliability scoring, regression detection, CLI workflows, and a React dashboard.
