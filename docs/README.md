# Documentation Index

Welcome to the Robo-Advisor Wealth Management documentation suite. This directory contains comprehensive guides for understanding, developing, and maintaining the system.

## Quick Navigation

### For Project Stakeholders
Start here to understand the project vision, requirements, and current status.
- **[project-overview-pdr.md](./project-overview-pdr.md)** - Project vision, requirements, and deliverables

### For Developers
Essential guides for coding, understanding architecture, and contributing to the codebase.
- **[code-standards.md](./code-standards.md)** - Coding conventions, file organization, and development practices
- **[system-architecture.md](./system-architecture.md)** - System design, data flows, and component interactions
- **[codebase-summary.md](./codebase-summary.md)** - Detailed module-by-module reference guide

### For Project Managers
Track project progress and understand the development roadmap.
- **[project-roadmap.md](./project-roadmap.md)** - Phase completion status and future enhancements

---

## Documentation Files

| File | Lines | Purpose |
|------|-------|---------|
| `project-overview-pdr.md` | 93 | Vision, PDR, requirements, success criteria |
| `code-standards.md` | 309 | Coding conventions, patterns, quality standards |
| `system-architecture.md` | 293 | Architecture diagrams, data flows, infrastructure |
| `codebase-summary.md` | 383 | Complete module reference, file mappings |
| `project-roadmap.md` | 308 | Phase timeline, KPIs, risk mitigation |

**Total:** 1,386 lines of documentation

---

## Project Status

**Current Phase:** 8 of 8 Complete ✅

**Key Metrics:**
- ✅ 338 unit tests passing
- ✅ 7,143 lines of production code
- ✅ 4 broker integrations (SSI, VNDirect, TCBS, HSC)
- ✅ 5+ technical indicators
- ✅ 4 risk management models
- ✅ 4 dashboard pages
- ✅ All documentation complete

**Status:** READY FOR PRODUCTION DEPLOYMENT

---

## Getting Started

### First Time Setup
1. Read [project-overview-pdr.md](./project-overview-pdr.md) for project context
2. Review [code-standards.md](./code-standards.md) for coding guidelines
3. Study [system-architecture.md](./system-architecture.md) for architecture overview

### Developing a Feature
1. Check [codebase-summary.md](./codebase-summary.md) for relevant module location
2. Follow patterns in [code-standards.md](./code-standards.md)
3. Add unit tests (target >80% coverage)
4. Update relevant documentation sections

### Deploying to Production
1. Review [project-roadmap.md](./project-roadmap.md) for deployment readiness
2. Verify all 338 tests pass: `pytest tests/`
3. Check code quality: `ruff check src/ && mypy src/`
4. Follow deployment instructions in infrastructure docs

---

## Key Concepts

### Architecture
- **Data Pipeline:** vnstock WebSocket → Kafka → ClickHouse
- **Trading Engine:** Analysis → RL Agent → Order Manager → Brokers
- **Dashboard:** Real-time Streamlit app with dark theme
- **Notifications:** ntfy push + Postfix email + PDF reports

### Core Modules
- **data/** - Market data fetching and streaming
- **analysis/** - Technical indicators and signals
- **risk/** - Risk quantification and monitoring
- **trading/** - Order management and broker adapters
- **ml/** - RL agent and sentiment analysis
- **ui/** - Streamlit dashboard
- **storage/** - ClickHouse database layer
- **notifications/** - Alert distribution

### Technology Stack
Python 3.11+, Kafka, ClickHouse, Streamlit, stable-baselines3, PhoBERT, MLflow

---

## Common Tasks

### Running the Dashboard
```bash
uv run streamlit run src/ui/app.py
```

### Starting the Data Pipeline
```bash
uv run python -m src.data.kafka-market-data-producer
uv run python -m src.data.kafka-market-data-consumer
```

### Running Tests
```bash
pytest tests/                          # Run all tests
pytest --cov=src tests/                # With coverage
pytest -v tests/test_technical_indicators.py  # Single module
```

### Code Quality Checks
```bash
ruff check src/ tests/                 # Linting
ruff format src/ tests/                # Auto-formatting
mypy src/                              # Type checking
```

### Training RL Agent
```bash
uv run python -m src.trading.agents.ppo-trading-agent
```

---

## Documentation Standards

### Writing Guidelines
- Keep files under 400 lines for readability
- Use clear headers (H1, H2, H3)
- Include code examples for complex concepts
- Link to related documentation sections
- Verify all code references exist in codebase

### Maintaining Accuracy
- Every code reference verified against actual files
- Function signatures extracted directly from source
- Configuration examples from actual YAML files
- No unvalidated claims about implementation

### Update Protocol
- Update documentation when code changes
- Run markdown validation before committing
- Keep cross-references synchronized
- Include documentation in pull requests

---

## Reporting Issues

When reporting documentation issues:
1. Specify which file and section
2. Explain what's inaccurate or unclear
3. Suggest improvements if possible
4. Reference actual code locations

---

## Contributing to Documentation

### Before Writing
1. Read [code-standards.md](./code-standards.md) for conventions
2. Check if documentation already exists for the topic
3. Verify all code examples compile/run

### During Writing
1. Lead with purpose, not background
2. Use tables for structured data
3. Include practical examples
4. Link to related sections
5. Verify all file paths exist

### After Writing
1. Proofread for clarity and accuracy
2. Validate all internal links
3. Check code examples compile
4. Ensure consistent formatting

---

## Project Resources

- **Source Code:** `/Users/tranhoangtu/Desktop/PET/Robo-Advisor-Wealth-Management/src/`
- **Configuration:** `/Users/tranhoangtu/Desktop/PET/Robo-Advisor-Wealth-Management/config/`
- **Tests:** `/Users/tranhoangtu/Desktop/PET/Robo-Advisor-Wealth-Management/tests/`
- **Docker Setup:** `/Users/tranhoangtu/Desktop/PET/Robo-Advisor-Wealth-Management/docker/`

---

## Support

For questions about:
- **Project scope/requirements:** See [project-overview-pdr.md](./project-overview-pdr.md)
- **Coding guidelines:** See [code-standards.md](./code-standards.md)
- **System design:** See [system-architecture.md](./system-architecture.md)
- **Specific modules:** See [codebase-summary.md](./codebase-summary.md)
- **Development status:** See [project-roadmap.md](./project-roadmap.md)

---

## Versioning

- **Documentation Version:** 1.0
- **Last Updated:** 2026-02-24
- **Compatible with:** robo-advisor v0.1.0+
- **Python Version:** 3.11+

---

**Project Status:** ✅ PRODUCTION READY | All documentation complete and verified
