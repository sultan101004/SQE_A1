# Viva Preparation — Diagnostician Prototype

Complete question bank from all sessions with comprehensive answers for viva defense.

---

## Section 1 — Requirements Concepts

| # | Question | Status | Answer |
|---|---|---|---|
| 1.1 | What is a Functional Requirement? Give an example from your SRS. | ✅ | A Functional Requirement (FR) specifies a capability or behavior the software must perform. For example, **FR1 (SRS 3.2.1.1)** requires the system to authenticate user credentials and assign either an administrator or general user role. |
| 1.2 | What is a Non-Functional Requirement? Give an example from your SRS. | ✅ | A Non-Functional Requirement (NFR) specifies quality attributes, constraints, or operational standards. For example, **NFR1 (SRS 3.4.1.1)** requires all operational errors to be logged with four structural fields (timestamp, module, function, description). |
| 1.3 | What is an assumption? What are the three categories (A/B/C)? | ✅ | An assumption is a design decision or clarification made when the SRS is silent or ambiguous. Category A represents explicit SRS backing, Category B represents explicit engineering design decisions, and Category C represents unsupported choices that must be justified or removed. |
| 1.4 | What is a test condition vs a test case? | ✅ | A test condition is a high-level item or event to verify (e.g., "Admin login grants admin role"), whereas a test case is a formal set of inputs, execution steps, and exact expected outcomes used to verify that condition. |
| 1.5 | What is boundary testing? Give an example from your tests. | ✅ | Boundary testing evaluates system behavior at the exact minimum and maximum limits of valid input ranges. For example, TC-10 tests Ambient Temperature at lower boundary `-40.0`°F (accepted), while TC-12 tests `-40.1`°F (rejected as in-doubt). |
| 1.6 | What is invalid/error testing? Give an example from your tests. | ✅ | Invalid testing verifies that the application correctly rejects malformed or unauthorized inputs with proper error handling. For example, TC-07 tests parsing a file containing non-ASCII `°C` characters, verifying it returns `(False, "non-ASCII")`. |
| 1.7 | What is system-level testing? Give an example from your tests. | ✅ | System-level testing evaluates the integrated application end-to-end against all system requirements. For example, TC-19 loads `valid_value.txt` into `main.py`, testing file parsing, data validation, engine processing, and UI result modal visualization together. |
| 1.8 | What is traceability and why does it matter? | ✅ | Traceability links each test case and code module directly back to a specific SRS requirement ID. It ensures complete requirement coverage and proves every feature fulfills a documented business need. |
| 1.9 | What is the difference between the SRS and a design decision? | ✅ | The SRS is the authoritative specification defining system requirements, while a design decision is an architectural choice made by the developer to implement those requirements (e.g., choosing JSON file storage for user credentials under A-002). |
| 1.10 | What is the difference between authentication and authorization? | ✅ | Authentication verifies *who* the user is (credentials check), while authorization determines *what* privileges an authenticated user has (role permissions). In our app, login is authentication (SRS 3.2.1.1) and restricting config edits to admins is authorization (SRS 3.2.2.9). |

---

## Section 2 — Authentication & Authorization (auth.py)

| # | Question | Status | Answer |
|---|---|---|---|
| 2.1 | Which SRS requirement does auth.py implement? | ✅ | `auth.py` implements **SRS 3.2.1.1 (FR1)** for user authentication and session management. |
| 2.2 | Why is SRS 3.2.1.1 an FR and not an NFR? | ✅ | It specifies functional user interactions, role assignments, and login lockout behaviors rather than general quality or performance attributes. |
| 2.3 | Why SHA-256 and not plaintext? | ✅ | Hashing prevents plaintext credential exposure if `users.json` is inspected or compromised (A-003). |
| 2.4 | Why no salt? Is that a defect? | ✅ | Unsalted SHA-256 was an explicit design decision for prototype simplicity (A-003). It is a security limitation to be upgraded to `bcrypt` in production, but not a functional defect against the SRS. |
| 2.5 | What happens after 3 failed login attempts? | ✅ | On the 3rd failed attempt, `attempt_login()` returns `("locked_out", None)` and logs an operational security error to `data/errors.log`. |
| 2.6 | What does `check_timeout()` do if the current user is already a general user? | ✅ | It updates `last_activity_time` to the current timestamp and returns `False` without changing `current_role`, as a general user cannot be demoted further. |
| 2.7 | If users.json is deleted while the app is running, what does the next `authenticate()` call do? | ✅ | `load_users()` raises `FileNotFoundError` (A-004), causing `attempt_login()` to catch it, log an error to `data/errors.log`, and return `("error", "User database missing")`. |
| 2.8 | After 3 failed attempts and a subsequent `logout()`, can the user try again? Why? | ✅ | Yes. Calling `logout()` executes `session.reset()`, which explicitly resets `failed_attempts` to 0 and clears the lockout state. |
| 2.9 | Why a JSON file and not SQLite for user storage? | ✅ | JSON was chosen under design decision A-002 as a zero-dependency, lightweight file storage mechanism suited for prototype evaluation. |
| 2.10 | What happens if the admin walks away for 20 minutes? | ✅ | `check_inactivity_timeout()` calculates elapsed time (1200s > 900s limit), automatically demotes `current_role` to `"general_user"`, and retains the username for audit context. |
| 2.11 | If I open `users.json`, can I log in by editing the hash? | ✅ | Yes, if you replace the stored SHA-256 hex string with the hash of your new known password, `attempt_login()` will match the hash and grant access. |
| 2.12 | Why does `load_users()` raise `FileNotFoundError` instead of recreating defaults? | ✅ | Raising `FileNotFoundError` prevents silent credential resets and forces explicit user initialization (A-004). |

---

## Section 3 — File Parser (file_parser.py)

| # | Question | Status | Answer |
|---|---|---|---|
| 3.1 | Which SRS requirement does file_parser.py implement? | ✅ | `file_parser.py` implements **SRS 3.2.2.2 (FR2)** for batch sensed-data file parsing. |
| 3.2 | What is the required file format? (delimiter, header order, comment rows) | ✅ | Must be ASCII-encoded, consistently tab or comma delimited, contain comment rows starting with `#`, and have 3 mandatory headers (Sensor names, Building Identifier on row 2, Input Identifier on row 3) followed by ascending ISO timestamps. |
| 3.3 | Where in the SRS is the sensor-names row located relative to Building Identifier? | ✅ | Sensor names are on row 1, directly preceding `"Building Identifier"` on row 2 and `"Input Identifier"` on row 3 (SRS 3.2.2.2 Table 3). |
| 3.4 | Does your parser accept two rows with the same timestamp? Why? | ✅ | No. The parser enforces strictly ascending order (`t[i] > t[i-1]`), rejecting duplicate timestamps to maintain time-series integrity. |
| 3.5 | What happens if a numeric value is unparseable, like "abc"? | ✅ | Float conversion fails, raising a `ParseError` that aborts file parsing and logs the syntax error. |
| 3.6 | What happens if the file has a comment row below the data? | ✅ | The parser filters out all comment lines starting with `#` regardless of location before parsing rows. |
| 3.7 | What happens if a line has trailing whitespace after a value? | ✅ | Cell strings are stripped of whitespace via `.strip()`, preventing whitespace from corrupting string matching or float parsing. |
| 3.8 | Why does the parser reject non-ASCII content? | ✅ | SRS Section 3.2.2.2 explicitly restricts batch file encoding to standard ASCII characters. |
| 3.9 | What is "batch mode"? How is it indicated? | ✅ | Batch mode processes offline time-series data files rather than real-time sensor streams; it is indicated by displaying the timestamp from the file data row on the main GUI display. |
| 3.10 | What is the difference between "missing data" and "in-doubt data"? | ✅ | "In-doubt data" is data that was acquired but falls outside valid range boundaries, whereas "missing data" represents data that was never acquired or exceeded consecutive failure thresholds (`None` values or 3+ failures). |

---

## Section 4 — Data Validator (data_validator.py)

| # | Question | Status | Answer |
|---|---|---|---|
| 4.1 | Which SRS requirements does data_validator.py implement? | ✅ | Implements **SRS 3.2.2.4 (FR3)** for missing data thresholds, **SRS 3.2.2.8 (FR4)** for range validation, and **SRS 3.2.2.9 (FR5)** for range administration. |
| 4.2 | Why does an unknown sensor type return `in_doubt_range`? | ✅ | Fallback safety (A-012): unconfigured sensor types cannot be validated, so values default to `in_doubt_range` to prevent unvalidated processing. |
| 4.3 | What is the exact boundary for Ambient Temperature? | ✅ | Inclusive range `[-40.0, 130.0]` °F per SRS Table 5. |
| 4.4 | Why is Compressor Current's upper bound `None`? | ✅ | Compressor Current has an open-ended upper range (`[0.0, infinity)`), so upper boundary checking is disabled. |
| 4.5 | Why are boundaries inclusive (`<=` and `>=`)? | ✅ | Standard engineering range definition where boundary endpoint values (e.g., -40.0 and 130.0) are valid operating values. |
| 4.6 | What is the missing-data threshold for Temperature? Why? | ✅ | Exactly 3 consecutive failures, as configured in `DEFAULT_THRESHOLDS` per SRS 3.2.2.4. |
| 4.7 | Why does a general user fail to change ranges? | ✅ | SRS 3.2.2.9 explicitly restricts range configuration modifications exclusively to users authenticated as administrators. |
| 4.8 | Explain the difference between `check_missing_threshold` and `validate_value`. | ✅ | `validate_value` checks if a single numeric value falls within min/max bounds, whereas `check_missing_threshold` checks if consecutive acquisition failure counts have reached or exceeded the missing threshold. |

---

## Section 5 — GUI & Window Management (main.py, config_manager.py)

| # | Question | Status | Answer |
|---|---|---|---|
| 5.1 | Show me SRS 3.5.1.8 working. | ✅ | Select File → Start Diagnostics in `main.py`, log in as admin, select data file, and view diagnostic result window. |
| 5.2 | How do you enforce modality? | ✅ | By executing `self.transient(parent)` and `self.grab_set()` on Toplevel child windows (NFR2 / A-019). |
| 5.3 | What is the time shown when in batch mode? | ✅ | The timestamp extracted from the current data row being evaluated in the batch file (SRS 3.2.2.2). |
| 5.4 | Can Subsystems open Configuration? Why not? | ✅ | No. Configuration requires administrator authorization (SRS 3.2.2.9). |
| 5.5 | Show me SRS 3.1.1.2.2.1 step 2 working. | ✅ | Open File menu → Configure Diagnostics → enter incorrect password → error dialog displays. |
| 5.6 | What happens if the admin walks away for 20 minutes and clicks Start? | ✅ | `check_timeout()` fires prior to execution, revokes admin privileges, and prompts for admin re-authentication. |
| 5.7 | Can a general user exit while diagnostics are running? | ✅ | Yes, exiting is permitted, but stopping active diagnostics requires admin authentication (SRS 3.5.1.9). |
| 5.8 | Why did you stub SRS 3.5.1.12 parameters a–g? | ✅ | Parameters a–g were deferred under design decision A-025 as out of scope for the 7 FR prototype. |
| 5.9 | Show me SRS 3.5.1.14's Save flow. | ✅ | Admin edits sensor ranges in `ConfigurationWindow` and clicks Save; changes persist to `validator_config.json` and append an entry to `data/audit.log`. |
| 5.10 | Show me the audit log. | ✅ | Open `data/audit.log` to view lines formatted with timestamp, sensor name, old range, new range, and admin username (NFR3). |
| 5.11 | What happens if I close the config window without saving? | ✅ | `has_unsaved_changes` state triggers an `askyesno` dialog prompting the user to save or discard edits (SRS 3.5.1.15). |
| 5.12 | Why does the config window use `transient()` and `grab_set()`? | ✅ | `transient()` binds the window to its parent, and `grab_set()` intercepts all hardware mouse/keyboard events to enforce modal dialog behavior (SRS 3.3.1.6). |

---

## Section 6 — Diagnostic Engine & Result Display

| # | Question | Status | Answer |
|---|---|---|---|
| 6.1 | Which SRS requirement does diagnostic_engine.py implement? | ✅ | Implements **SRS 3.2.3.4 (FR6)** for diagnostic input validation and execution skipping. |
| 6.2 | Show me FR6 working end-to-end. | ✅ | Load `missing_value.txt` via `main.py`; engine detects missing `Compressor Current` and opens orange skipped window naming the missing input. |
| 6.3 | Show me NFR1 working. | ✅ | Trigger an error (e.g. bad file format) and inspect `data/errors.log` to view timestamp, module, function, description. |
| 6.4 | Show me SRS 3.4.1.1 working. | ✅ | `error_logger.py` formats error entries with all 4 required structural fields. |
| 6.5 | Show me SRS 3.2.4.2 working. | ✅ | `DiagnosticInformationWindow` renders result description, potential causes, location, absolute time, and Close button. |
| 6.6 | Why does an empty input list return "completed"? | ✅ | If no inputs are required or missing, the stubbed algorithm has no missing data dependencies and completes execution. |
| 6.7 | What is a "significant error"? Who decides? | ✅ | A significant error is any unhandled operational failure, unauthorized access attempt, or data parsing rejection (A-037). |
| 6.8 | Why is the fix field "Not available in prototype"? | ✅ | Detailed repair instructions are part of Table 7 fault algorithms, which were stubbed per A-028. |

---

## Section 7 — SonarQube Findings

| # | Question | Status | Answer |
|---|---|---|---|
| 7.1 | Explain SONAR-01 (Cognitive Complexity) to me. | ✅ | `_internal_parse` in `file_parser.py` scored 42 vs 15 ceiling due to monolithic nested parsing logic; resolve by splitting into 3 sub-functions. |
| 7.2 | Why is SONAR-01 a Maintainability issue and not a Bug? | ✅ | It measures mental reading friction rather than functional correctness; all parsing tests pass cleanly on the frozen baseline. |
| 7.3 | Explain SONAR-02 (duplicate "Ambient Temperature"). | ✅ | `"Ambient Temperature"` duplicated 8x in `data_validator.py`; replace with module constant `SENSOR_AMBIENT_TEMP`. |
| 7.4 | Why is SONAR-04 (duplicate string in config_manager) more dangerous than SONAR-02? | ✅ | It crosses module boundaries — string mismatches between GUI and validator cause silent range update failures. |
| 7.5 | Why did you select only 5 of 11 findings? | ✅ | Selected 5 findings across 4 core modules to demonstrate representative breadth across complexity, literal duplication, cross-module coupling, and style constructors. |
| 7.6 | Why is a SonarQube code smell not automatically a Jira defect? | ✅ | Code smells measure internal maintainability/style guidelines, not functional spec violations or runtime failures. |
| 7.7 | Why didn't SonarQube flag unsalted SHA-256? | ✅ | Static analysis rules treat `hashlib.sha256()` as a generic utility call and lack domain context to infer user password storage. |
| 7.8 | SonarQube found 0 Security issues. Does that mean your code is secure? | ✅ | No. 0 Security findings in static analysis does not guarantee security. It cannot detect architectural security choices like unsalted hashing (A-003), plaintext file storage (`users.json`), or unencrypted local IPC. |

---

## Section 8 — Testing

| # | Question | Status | Answer |
|---|---|---|---|
| 8.1 | What is the difference between a FAILED test and a BLOCKED test? | ✅ | A FAILED test executed code that contradicted expected SRS output; a BLOCKED test could not execute because the feature was stubbed out due to scope boundaries. |
| 8.2 | Why is TC-24 BLOCKED and not FAILED? | ✅ | TC-24 requires Table 7 fault algorithms, which were explicitly stubbed per design decision A-028. |
| 8.3 | You have 0 FAILED tests except TC-31. Is that suspicious? | ✅ | No. The code was thoroughly debugged across 66 module self-tests prior to freezing the baseline at tag `v1.0-frozen`. |
| 8.4 | Show me the boundary values you used for FR4. | ✅ | Tested -40.0 (lower bound pass), -40.1 (lower bound fail), 130.0 (upper bound pass), 130.1 (upper bound fail). |
| 8.5 | Show me an invalid test that failed to reject. | ✅ | All invalid test cases (TC-06, TC-07, TC-08, TC-09, TC-16) correctly rejected invalid inputs. |
| 8.6 | Is TC-31 a code defect or a test error? Defend. | ✅ | Code defect in application error handling. A production app should handle missing `users.json` gracefully rather than crashing. |
| 8.7 | Show me a test that would FAIL if I removed `check_timeout()` from main.py. | ✅ | `main.py --test` Test 8 and `auth.py` Test 7 would both FAIL because admin roles would never revert after 15 minutes of inactivity. |
| 8.8 | Why is `<=` used on timestamp comparison? Is it defensible? | ✅ | Yes. SRS 3.2.2.2 requires strictly ascending order (`t[i] > t[i-1]`); `<=` correctly rejects duplicate (`t[i] == t[i-1]`) and out-of-order timestamps. |
| 8.9 | What is the difference between PASS and BLOCKED? | ✅ | PASS means code executed and matched expected results; BLOCKED means test could not run due to un-implemented scope. |
| 8.10 | Why do you need at least 2 FAILED/BLOCKED tests? | ✅ | To prove honest testing rigour and defend explicit requirement scope boundaries rather than fabricating results. |

---

## Section 9 — Jira & Defect Analysis

| # | Question | Status | Answer |
|---|---|---|---|
| 9.1 | What is the difference between a Bug and a Code Smell? | ✅ | A Bug is a functional defect violating system requirements; a Code Smell is a maintainability concern affecting code quality. |
| 9.2 | When does a SonarQube finding become a Jira defect? | ✅ | When a finding violates a mandatory NFR quality gate or causes functional failure in runtime execution. |
| 9.3 | Show me your Jira defect tickets. | ✅ | Documented in `JIRA_DEFECTS.md` (`SCRUM-5` for TC-24 Table 7 rules and `SCRUM-6` for TC-25 config params a–g). |
| 9.4 | Why did you file SCRUM-6 as a Bug and not a Task? | ✅ | Because SRS 3.5.1.12 specifies config parameters a–g; filing as a scope defect formally tracks the unimplemented requirements. |
| 9.5 | What is reproducibility and why does it matter? | ✅ | Reproducibility provides exact steps to reliably recreate a defect, allowing developers to isolate and fix root causes. |
| 9.6 | What is the defect lifecycle? | ✅ | New → Open → In Progress → Resolved → Verified → Closed. |
| 9.7 | You submitted without Jira complete on time. Why should I mark you full marks for defect analysis? | ✅ | Because all scope exclusions and unhandled edge case defects were thoroughly tracked, categorized, and documented with root-cause analysis in `JIRA_DEFECTS.md` and `TEST_RESULTS.md` prior to code freeze. |

---

## Section 10 — Hard Pushback Questions

| # | Question | Status | Answer |
|---|---|---|---|
| 10.1 | Show me FR2 working end-to-end. | ✅ | Execute `python file_parser.py` self-tests or load `valid_value.txt` via `main.py` GUI. |
| 10.2 | Why is this an NFR? (for any NFR you selected) | ✅ | NFR1 specifies error log formatting constraints; NFR2 specifies GUI modality constraints; NFR3 specifies audit trail data tracking. |
| 10.3 | What assumption did AI make here? (for any module) | ✅ | Consult `AI_ASSUMPTIONS.md` (e.g., A-002 JSON user storage, A-003 unsalted SHA-256, A-019 Tkinter modality). |
| 10.4 | If the software violates the requirement, is it a defect? What if the requirement is ambiguous? | ✅ | Yes, violating a clear requirement is a defect. Ambiguous requirements require documenting a Category B design assumption. |
| 10.5 | You only implemented 7 FRs out of the 40+ in the SRS. Justify your scope. | ✅ | Prototype scope was bounded to core baseline capabilities (FR1–FR7, NFR1–NFR3) to establish a baseline before full Table 7 implementation. |
| 10.6 | Why did you choose Python and Tkinter? | ✅ | Standard library cross-platform compatibility, fast prototyping, built-in modal window support (`transient` + `grab_set`). |
| 10.7 | What would you do differently in a second iteration? | ✅ | Upgrade hashing to `bcrypt`, implement SQLite database, refactor `_internal_parse`, and implement Table 7 fault rules. |
| 10.8 | What is the difference between verification and validation? | ✅ | Verification asks "Did we build the system right?" (checking against SRS spec), while Validation asks "Did we build the right system?" (checking user needs). |
| 10.9 | What is the difference between a test plan, test case, and test condition? | ✅ | A Test Plan defines strategy/scope; a Test Condition is an item to test; a Test Case specifies steps and expected outcomes. |
| 10.10 | Explain your frozen baseline and why it matters for evidence. | ✅ | Tag `v1.0-frozen` at commit `3c7a91a` creates an immutable baseline so test evidence matches the exact inspected code. |

---

## Section 11 — The 15 Mock Viva Questions

| # | Question | Status | Answer |
|---|---|---|---|
| 11.1 | Difference between FR and NFR? Give examples from your assignment. | ✅ | FR specifies system capabilities (FR1 admin login); NFR specifies operational quality standards (NFR1 4-field error logging). |
| 11.2 | Which SRS requirement does file_parser.py implement, and what is the required format? | ✅ | Implements SRS 3.2.2.2 (FR2). ASCII-encoded, tab/comma delimited, 3 header rows, ascending ISO timestamps. |
| 11.3 | Why test -40 (TC-10) and -40.1 (TC-12)? What is this technique called? | ✅ | Verifies boundary envelope acceptance/rejection endpoints using Boundary Value Analysis (BVA). |
| 11.4 | Difference between a FAILED test and a BLOCKED test? Which of your tests falls into each? | ✅ | FAILED executed and produced wrong output; BLOCKED could not run due to deferred scope (TC-24, TC-25). |
| 11.5 | Is TC-31 failing on missing users.json a code defect or a test error? | ✅ | Code defect in error handling; app should catch `FileNotFoundError` gracefully instead of crashing. |
| 11.6 | Explain SONAR-01 (Cognitive Complexity in file_parser.py). | ✅ | `_internal_parse` scored 42 vs 15 ceiling due to monolithic nesting; refactor into 3 helper functions. |
| 11.7 | Why is a SonarQube code smell not automatically a Jira defect? | ✅ | Code smells measure maintainability style, not functional requirement violations or runtime crashes. |
| 11.8 | Difference between authentication and authorization in your prototype? | ✅ | Authentication verifies identity (login in FR1); Authorization enforces role permissions (range edits in FR5). |
| 11.9 | Why didn't SonarQube flag unsalted SHA-256 (A-003)? | ✅ | Static analysis rules treat `hashlib.sha256()` as a general utility call and lack semantic password domain context. |
| 11.10 | Read the SRS text that FR6 implements. | ✅ | SRS 3.2.3.4: "A diagnostic algorithm shall not process if any input data to the algorithm is missing. The user shall be notified..." |
| 11.11 | You submitted without Jira complete on time. Why should I mark you full marks? | ✅ | All scope decisions and edge cases were fully documented with root-cause analysis in `JIRA_DEFECTS.md` before baseline freeze. |
| 11.12 | Show me a test that would FAIL if I removed `check_timeout()` from main.py. | ✅ | `main.py --test` Test 8 and `auth.py` Test 7 would FAIL because admin roles would never revert after 15 minutes of inactivity. |
| 11.13 | Your file_parser uses `<=` on timestamps to reject duplicates. Is it defensible? | ✅ | Yes. SRS 3.2.2.2 requires strictly ascending order (`t[i] > t[i-1]`); `<=` correctly rejects duplicate timestamps. |
| 11.14 | SonarQube found 0 Security issues. Does that mean your code is secure? | ✅ | No. Static analysis cannot detect architectural vulnerabilities like unsalted hashing (A-003) or plaintext local file storage. |
| 11.15 | Why is TC-24 BLOCKED and not FAILED? | ✅ | TC-24 requires Table 7 fault algorithms, which were explicitly stubbed per design decision A-028. |
