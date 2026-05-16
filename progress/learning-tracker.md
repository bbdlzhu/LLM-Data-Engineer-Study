# LLM Data Engineer — Learning Tracker

**Last Updated**: 2026-05-16
**Start Date**: 2026-05-16
**Target Completion**: 2027-01-16 (8 months)
**Days Elapsed**: 0

This single document tracks ALL your LLM Data Engineer learning progress, including:
- Phase completion status and sub-goal tracking
- Skills mastered with proficiency levels
- Knowledge gaps identified
- Milestone project progress

---

## Quick Stats

📊 **Overall Progress**: 0/25 sub-goals = **0%**
🎯 **Current Phase**: Phase 1 — Python Engineering Foundation
📅 **Days Remaining**: ~245 days
💻 **Sessions Completed**: 0

---

## Phase Progress Summary

| Phase | Timeframe | Sub-goals | Completed | Status | Priority |
|-------|-----------|-----------|-----------|--------|----------|
| **P1: Python Engineering** | Month 1-2 | 0/6 | 0% | ⚪ Not Started | **ACTIVE** |
| **P2: Multimodal Data Engine** | Month 3-4 | 0/5 | 0% | ⚪ Not Started | — |
| **P3: Training Data Construction** | Month 5-6 | 0/5 | 0% | ⚪ Not Started | — |
| **P4: Evaluation-Driven Development** | Month 7-8 | 0/5 | 0% | ⚪ Not Started | — |

---

## Phase 1: Python Engineering Foundation (Months 1-2)

**Goal**: Upgrade Python from "scripting" to "systems programming" quality.
**Milestone**: Rewrite a Spark data processing task in pure Python with type hints, tests, Docker.

### Sub-goal Progress

- [ ] **P1.1 — Advanced Python** (0%)
  - Decorators, generators, context managers, descriptors
  - Reference: *Fluent Python* by Luciano Ramalho

- [ ] **P1.2 — Type Hints (Type Annotations)** (0%)
  - mypy strict mode, Protocol, TypedDict, Generic, overload
  - Goal: 100% type coverage in milestone project

- [ ] **P1.3 — Modern AI Toolchain** (0%)
  - Cursor / GitHub Copilot, prompt-driven programming
  - Claude Code mastery for development workflow

- [ ] **P1.4 — Code Quality & Linting** (0%)
  - ruff (linter + formatter), pre-commit hooks, pyproject.toml
  - Reference: [ruff docs](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/)

- [ ] **P1.5 — Testing with pytest** (0%)
  - Fixtures, parametrize, mocking for data pipelines
  - Goal: ≥ 80% test coverage

- [ ] **P1.6 — Docker** (0%)
  - Multi-stage builds, docker-compose, .dockerignore
  - Goal: Production-ready container for milestone project

### Milestone Project: Spark-to-Python Rewrite

| Requirement | Status | Notes |
|-------------|--------|-------|
| Task selection (medium complexity from prior Spark work) | ⚪ Not started | |
| 100% type annotations (mypy strict) | ⚪ Not started | |
| pre-commit hooks (ruff, mypy, pytest) | ⚪ Not started | |
| Unit tests (≥ 80% coverage) | ⚪ Not started | |
| Docker runtime environment | ⚪ Not started | |
| Performance comparison vs Spark | ⚪ Not started | |

---

## Phase 2: Multimodal Data Computing Engine (Months 3-4)

**Goal**: Transition from Spark batch to Ray distributed AI computing.
**Milestone**: Build complete pretraining data cleaning pipeline on Common Crawl / Wudao subset.

- [ ] **P2.1 — Ray Core** (0%)
  - Tasks, actors, object store, scheduling vs Spark executors

- [ ] **P2.2 — Ray Data** (0%)
  - Datasets, transforms, pipelines, shuffle strategies

- [ ] **P2.3 — Text Processing Operators** (0%)
  - Language detection (fasttext/lingua), PCL filtering, MinHash LSH dedup

- [ ] **P2.4 — Visual/Cross-modal Operators** (0%)
  - CLIP score, feature extraction

- [ ] **P2.5 — Pipeline Performance & Monitoring** (0%)
  - Shuffle monitoring, throughput tracking, Ray Dashboard

### Milestone Project: Pretraining Data Cleaning Pipeline

| Stage | Status | Notes |
|-------|--------|-------|
| Raw data acquisition (Common Crawl / Wudao) | ⚪ Not started | |
| HTML → Text extraction | ⚪ Not started | |
| Language detection & filtering | ⚪ Not started | |
| PCL (toxicity/bias) filtering | ⚪ Not started | |
| MinHash LSH deduplication | ⚪ Not started | |
| Quality scoring & filtering | ⚪ Not started | |
| JSONL formatted output | ⚪ Not started | |
| Shuffle & throughput monitoring | ⚪ Not started | |
| Performance tuning | ⚪ Not started | |

---

## Phase 3: LLM Training Data Construction (Months 5-6)

**Goal**: Master SFT and RLHF/DPO data construction logic.
**Milestone**: Synthesize 2,000 high-quality SFT samples in Llama 3 / Qwen 2 format.

- [ ] **P3.1 — Pretraining Data Composition** (0%)
  - Data mixing strategies (code/encyclopedia/web ratios, DoReMi, DRO)

- [ ] **P3.2 — SFT Data Synthesis** (0%)
  - Self-Instruct, Evol-Instruct, LLM API batch generation

- [ ] **P3.3 — Preference Data (DPO/RLHF)** (0%)
  - Chosen/Rejected pair construction, prompt difficulty design

- [ ] **P3.4 — Training Templates** (0%)
  - Llama 3, Qwen 2 chat template, tokenization

- [ ] **P3.5 — API-Driven Data Pipelines** (0%)
  - Rate limiting, retries, cost tracking, async batch calls

### Milestone Project: SFT Data Synthesis

| Requirement | Status | Notes |
|-------------|--------|-------|
| Domain selection (medical / code generation) | ⚪ Not started | |
| Prompt template design | ⚪ Not started | |
| Self-Instruct / Evol-Instruct implementation | ⚪ Not started | |
| LLM API integration (Claude / GPT-4) | ⚪ Not started | |
| 2,000 QA pairs generated | ⚪ Not started | |
| Output format: Llama 3 / Qwen 2 template | ⚪ Not started | |

---

## Phase 4: Evaluation-Driven Development (Months 7-8)

**Goal**: Build the "eval → find gaps → add data → improve → re-eval" closed loop.
**Milestone**: Fine-tune Qwen2-7B, compare benchmarks, produce impact report.

- [ ] **P4.1 — Benchmark Analysis** (0%)
  - MMLU, GSM8K, HumanEval test set study

- [ ] **P4.2 — LLM-as-a-Judge** (0%)
  - Evaluation prompt design, pairwise comparison, rubric scoring

- [ ] **P4.3 — Automated Evaluation Pipeline** (0%)
  - Metrics tracking, regression detection

- [ ] **P4.4 — Fine-tuning Practice** (0%)
  - LLaMA-Factory + Qwen2-7B + Phase 3 data

- [ ] **P4.5 — Data Quality Impact Analysis** (0%)
  - Pre/post fine-tuning benchmark comparison, quantitative report

### Milestone Project: Data Impact Analysis

| Requirement | Status | Notes |
|-------------|--------|-------|
| Qwen2-7B baseline benchmarks | ⚪ Not started | |
| Fine-tuning with LLaMA-Factory | ⚪ Not started | |
| Fine-tuned model benchmarks | ⚪ Not started | |
| Quantitative impact report | ⚪ Not started | |

---

## Knowledge Gaps

### High Priority

*None yet — will be populated from sessions*

### Medium Priority

*None yet*

### Low Priority

*None yet*

### Recently Resolved

*None yet*

---

## Skills Inventory

### Production Python
| Skill | Proficiency | Last Practiced |
|-------|-------------|----------------|
| Type Hints (mypy strict) | Not assessed | — |
| Decorators & Generators | Not assessed | — |
| pytest (fixtures, mock, coverage) | Not assessed | — |
| ruff / pre-commit | Not assessed | — |
| Docker | Not assessed | — |

### Distributed Computing
| Skill | Proficiency | Last Practiced |
|-------|-------------|----------------|
| Spark (batch, SQL, RDD) | Strong (prior) | — |
| Ray Core | Not started | — |
| Ray Data | Not started | — |

### LLM Data Engineering
| Skill | Proficiency | Last Practiced |
|-------|-------------|----------------|
| Text deduplication (MinHash LSH) | Not started | — |
| PCL/toxicity filtering | Not started | — |
| CLIP score computation | Not started | — |
| SFT data synthesis | Not started | — |
| DPO preference data | Not started | — |
| LLM-as-a-Judge | Not started | — |
| Model fine-tuning | Not started | — |

### Tools & APIs
| Skill | Proficiency | Last Practiced |
|-------|-------------|----------------|
| Claude API / GPT-4 API | Not started | — |
| HuggingFace ecosystem | Not started | — |
| LLaMA-Factory | Not started | — |

---

## Study Log

| Date | Phase | Topics | Duration | Notes |
|------|-------|--------|----------|-------|
| — | — | — | — | No sessions yet |

---

*This tracker is updated after every learning session. Last update: 2026-05-16*
