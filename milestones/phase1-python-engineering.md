# Phase 1 Milestone — Python Engineering Foundation

**Timeframe**: Month 1-2
**Status**: ⚪ Not Started

---

## Milestone Project

**Task**: Select a previously Spark-based data processing task of medium complexity and rewrite it in pure Python with production engineering standards.

### Requirements Checklist

#### 1. Task Selection
- [ ] Identify a medium-complexity Spark task previously written in Java/Scala
- [ ] Document the original task's input, processing logic, and output
- [ ] Evaluate suitability for Python rewrite (complexity appropriate for 2-month effort)

#### 2. Code Quality
- [ ] 100% type annotated Python code
- [ ] mypy strict mode passes with zero errors
- [ ] ruff configured as linter and formatter
- [ ] pre-commit hooks: ruff, mypy, pytest
- [ ] pyproject.toml with all tool configurations

#### 3. Testing
- [ ] pytest test suite with fixtures and parametrize
- [ ] Mock tests for external dependencies (DB, file system, APIs)
- [ ] Code coverage ≥ 80%
- [ ] Edge case tests (empty input, large input, malformed data)

#### 4. Docker
- [ ] Multi-stage Dockerfile (build + runtime stages)
- [ ] docker-compose.yml for any dependent services
- [ ] .dockerignore configured
- [ ] Image size optimized

#### 5. Documentation
- [ ] README with setup and run instructions
- [ ] Architecture decision record (ADR) for key design choices

### Completion Criteria

All checklist items marked complete + code review by Claude (acting as senior engineer).

---

## Learning Resources

- **Book**: *Fluent Python* (2nd Ed.) — Luciano Ramalho
- **Docs**: [mypy](https://mypy.readthedocs.io/), [ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/), [pre-commit](https://pre-commit.com/)
- **Reference**: [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

---

*Created: 2026-05-16*
