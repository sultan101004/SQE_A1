# SonarQube Findings — Diagnostician Prototype v1.0

**Baseline**: commit `3c7a91a` on `main`, tag `v1.0-frozen`  
**SonarQube Server**: Community Build v26.9.0.129388 (local)  
**Analyzed Scope**: 8 Python files (`sonar.inclusions=**/*.py`)  
**Total Findings**: 11 (all Maintainability, 10 High, 1 Low)  
No Bugs, no Vulnerabilities, no Security Hotspots.

---

## SONAR-01 — Cognitive Complexity in file_parser.py

- **Rule:** `python:S3776`
- **File:** `file_parser.py`, line 64 (`_internal_parse`)
- **Severity:** High
- **Category:** Maintainability
- **Issue:** "Refactor this function to reduce its Cognitive Complexity from 42 to the 15 allowed."

### Code Context
```python
# file_parser.py: line 64
def _internal_parse(content: str) -> dict:
    """Internal parser enforcing strict SRS Table 3 header format, ASCII, and row alignment. SRS Reference: SRS 3.2.2.2 (A-009, A-010, A-011)"""
    if not content or not content.isascii():
        raise ParseError("File contains non-ASCII characters or is empty.")
    ...
```

### Interpretation
The function carries 42 decision points (branch + loop nesting). The industry-recommended ceiling is 15. At 42, the function is difficult to review, hard to test in isolation, and easy to break when modified. Any future change — e.g., supporting an additional delimiter — risks introducing a regression that unit tests may not catch because the function does too much at once.

### Action Supported
Split `_internal_parse` into smaller functions:
- `_detect_delimiter(lines) -> str`
- `_validate_headers(rows) -> (building_row, input_row, sensor_names)`
- `_validate_data_rows(rows, sensor_names) -> (timestamps, columns)`

This would drop complexity below 15 and make each piece independently testable.

### Link to NFR
Supports SRS 3.4 (Supportability) — maintainability of the codebase underlies the ability to maintain the tool after initial installation. Related to NFR1 (3.4.1 error reporting) since the same module handles parse errors that feed into `error_logger`.

### Verdict
Not a functional defect — tests pass. A code-quality issue that would require refactoring before long-term maintenance. Documented, not fixed (frozen baseline).

---

## SONAR-02 — Duplicate string literal in data_validator.py

- **Rule:** `python:S1192`
- **File:** `data_validator.py`, line 28
- **Severity:** High
- **Category:** Maintainability
- **Issue:** "Define a constant instead of duplicating this literal 'Ambient Temperature' 8 times."

### Code Context
```python
# data_validator.py: line 27-28
DEFAULT_RANGES = {
    "Ambient Temperature": [-40.0, 130.0],
    "Ambient wet-bulb": [-40.0, 100.0],
...
```

### Interpretation
Eight copies of the same string. If the key ever changes — e.g., to match a revised SRS Table 5 label — every occurrence must be found and updated by hand. Miss one and the range lookup silently fails.

### Action Supported
Define at module level:
```python
KEY_AMBIENT_TEMPERATURE = "Ambient Temperature"
```
Replace all 8 literals with the constant. Same for other sensor types.

### Link to NFR
Supports SRS 3.4 (Supportability) — reducing duplication reduces future maintenance cost.

### Verdict
Not a defect. Prototype has frozen string keys that match SRS Table 5. Would refactor before a second version.

---

## SONAR-03 — Duplicate string literal in diagnostic_engine.py

- **Rule:** `python:S1192`
- **File:** `diagnostic_engine.py`, line 101
- **Severity:** High
- **Category:** Maintainability
- **Issue:** "Define a constant instead of duplicating this literal 'Chiller Diagnosis' 6 times."

### Code Context
```python
# diagnostic_engine.py: line 101
res1 = engine.run("Chiller Diagnosis", inputs_all)
```

### Interpretation
The diagnostic algorithm name `"Chiller Diagnosis"` is hardcoded 6 times across tests. If the algorithm is renamed or extended (per SRS 3.2.3.3, which permits adding algorithms), every test must be updated.

### Action Supported
```python
ALGORITHM_CHILLER = "Chiller Diagnosis"
```

### Link to NFR
Supports SRS 3.2.3.3 (extensibility of diagnostic algorithms) — a constant makes future algorithm additions cleaner.

### Verdict
Not a defect.

---

## SONAR-04 — Duplicate string literal in config_manager.py

- **Rule:** `python:S1192`
- **File:** `config_manager.py`, line 212
- **Severity:** High
- **Category:** Maintainability
- **Issue:** "Define a constant instead of duplicating this literal 'Ambient Temperature' 3 times."

### Code Context
```python
# config_manager.py: line 212
success, msg = editor.update_range("Ambient Temperature", -45.0, 135.0, auth.ROLE_GENERAL, "user1")
```

### Interpretation
Same as SONAR-02, but in the GUI layer. Inconsistency risk: if the config layer's string key drifts from `data_validator`'s, the range update silently fails because the lookup misses.

### Action Supported
Import the constant from `data_validator` rather than redefine it.

### Link to NFR
Supports SRS 3.4 (Supportability) — cross-module consistency.

### Verdict
Not a defect. Points to a future refactor: sensor name constants should live in one place (`data_validator`) and be imported everywhere.

---

## SONAR-05 — Comprehension vs constructor in file_parser.py

- **Rule:** `python:S7498`
- **File:** `file_parser.py`, line 92
- **Severity:** Low
- **Category:** Maintainability (Consistency)
- **Issue:** "Replace this comprehension with passing the iterable to the collection constructor call."

### Code Context
```python
# file_parser.py: line 92
rows = [row for row in csv.reader(non_comment_lines, delimiter=delimiter)]
```

### Interpretation
Minor style issue. The comprehension and constructor produce the same result; the constructor is more idiomatic. Cost: 5 minutes. Benefit: consistency with surrounding code.

### Action Supported
```python
# Before
rows = [row for row in csv.reader(non_comment_lines, delimiter=delimiter)]
# After
rows = list(csv.reader(non_comment_lines, delimiter=delimiter))
```

### Link to NFR
Supports SRS 3.4 (Supportability) — code consistency aids readability.

### Verdict
Not a defect. Trivial.

---

## Summary Table

| Finding | Rule | File | Severity | Category | Defect? |
|---|---|---|---|---|---|
| **SONAR-01** | S3776 | `file_parser.py:64` | High | Maintainability | No — refactor |
| **SONAR-02** | S1192 | `data_validator.py:28` | High | Maintainability | No — refactor |
| **SONAR-03** | S1192 | `diagnostic_engine.py:101` | High | Maintainability | No — refactor |
| **SONAR-04** | S1192 | `config_manager.py:212` | High | Maintainability | No — refactor |
| **SONAR-05** | S7498 | `file_parser.py:92` | Low | Maintainability | No — trivial |

**Conclusion:** All five findings are code-quality issues, not functional defects. They support SRS 3.4 (Supportability) by identifying places where the code should be refactored before long-term maintenance. None of them violate an FR or cause incorrect behavior. The frozen baseline passes all 66 self-tests.