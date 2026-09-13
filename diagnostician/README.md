# Diagnostician — Automated HVAC Diagnostic Tool (v1.0-frozen)

**Course**: SE3002 — Software Quality Engineering  
**Assignment**: Assignment #01 — Quality Evaluation of AI-Generated Software  
**Baseline Release**: Commit `3c7a91a` on `main`, Git Tag `v1.0-frozen`  
**Submission Branch**: `test-results-v1`

---

## Assignment Submission Index & Document Navigation

1. **[SUBMISSION_REPORT.md](SUBMISSION_REPORT.md)**: **Master Assignment Report** (Scope Table, AI Assumptions, Part 2 Baseline, Part 3A SonarQube/NFR Evaluation, Part 3B Test Tables A/B/C, Part 4 Jira Defects & Final Quality Judgment).
2. **[TEST_RESULTS.md](TEST_RESULTS.md)**: **Test Execution Master Table** (30 Executed Test Cases, Actual Results, Status, Screenshot & Output Evidence).
3. **[SONAR_FINDINGS.md](SONAR_FINDINGS.md)**: **SonarQube Analysis Findings** (100% Python Scan, 5 Selected Maintainability Findings interpreted with Code Context Snippets).
4. **[AI_ASSUMPTIONS.md](AI_ASSUMPTIONS.md)**: **AI Assumptions Log** (Registry of 37 explicit design assumptions A-001 through A-037 classified as SRS Supported, Design Decisions, or Unsupported).
5. **[JIRA_DEFECTS.md](JIRA_DEFECTS.md)**: **Jira Defect Records** (Complete defect reports for BLOCKED scope cases `BUG-01` and `BUG-02`).

---

## Scope & Module Overview

Selected Scope: Exactly 10 Requirements (**7 Functional Requirements** + **3 Non-Functional Requirements**).

| Module | SRS Reference | Requirement | Description |
|---|---|---|---|
| `auth.py` | SRS 3.2.1.1 | **FR1** | User authentication, SHA-256 session management, 3x lockout, 15-min timeout downgrade. |
| `file_parser.py` | SRS 3.2.2.2 | **FR2** | Batch data file parsing, ASCII validation, header/delimiter consistency, timestamp ordering. |
| `data_validator.py` | SRS 3.2.2.4, 3.2.2.8, 3.2.2.9 | **FR3, FR4, FR5** | Failure threshold tracking, range envelope validation (Table 5), sensor range administration. |
| `config_manager.py` | SRS 3.2.2.9, 3.7 | **FR5, NFR3** | Modal configuration GUI Treeview editor, unsaved changes prompt, audit logging (`data/audit.log`). |
| `diagnostic_engine.py` | SRS 3.2.3.4 | **FR6** | Pre-execution input missing data gatekeeper and diagnostic result wrapper. |
| `result_display.py` | SRS 3.2.4.2 | **FR7** | Modal diagnostic information window visualizing fault/completed/skipped results. |
| `error_logger.py` | SRS 3.4.1.1 | **NFR1** | Operational error logging with 4 structural fields (`data/errors.log`). |
| `main.py` | SRS 3.5.1.x, 3.3.1.6 | **NFR2** | Main GUI window controller, event pipeline, modal window hierarchy (`transient` + `grab_set`). |

---

## Setup & Running Instructions

```bash
# 1. Execute all 66 non-GUI self-tests across 8 core modules:
python auth.py
python file_parser.py
python data_validator.py
python config_manager.py
python diagnostic_engine.py
python error_logger.py
python result_display.py
python main.py --test

# 2. Launch the interactive GUI application:
python main.py
```

### Pre-configured Prototype Test Credentials
- **Administrator**: Username `admin` / Password `admin123`
- **General User**: Username `user1` / Password `password1`