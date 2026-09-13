# AI Assumptions Log

Every design decision the SRS does not explicitly state is recorded here.

Categories:
- A = Supported by SRS (explicit)
- B = Explicit Design Decision (SRS silent, we chose it)
- C = Unsupported (must be removed or justified)

## Section 1 — Assumption Registry

| ID    | Module          | SRS Ref          | Assumption                                                        | Category | Justification                                                          |
|-------|-----------------|------------------|-------------------------------------------------------------------|----------|------------------------------------------------------------------------|
| A-001 | auth.py         | 3.2.1.1          | Role names are "administrator" and "general_user"                 | B        | SRS uses these names but does not define constants.                    |
| A-002 | auth.py         | 3.6              | Credentials stored in users.json in project root                  | B        | SRS does not specify storage. Chose file-based for prototype.          |
| A-003 | auth.py         | 3.6              | SHA-256 hashing, no salt                                          | B        | SRS silent. Acceptable for prototype. bcrypt with salt in production.  |
| A-004 | auth.py         | 3.6              | load_users() raises FileNotFoundError when users.json missing      | B        | Prevents silent credential reset. Requires explicit init_users_file(). |
| A-005 | auth.py         | 3.1.5.2.7 s5     | Three authentication attempts before dismissal                    | A        | Explicitly stated in SRS.                                              |
| A-006 | auth.py         | 3.1.1.2.1 s11    | 15-minute inactivity downgrades admin to general user             | A        | Explicitly stated in SRS.                                              |
| A-007 | auth.py         | 3.1.1.2.1 s11    | Timeout retains username; only role is downgraded                 | A        | SRS says privileges revert, not session ends.                          |
| A-008 | auth.py         | 3.1.5.2.7 s5     | failed_attempts reset on logout                                   | B        | SRS step 5 implies fresh window = fresh attempts.                      |
| A-009 | file_parser.py  | 3.2.2.2          | Sensor names row appears ABOVE Building Identifier row            | A        | Explicitly shown in SRS Table 3 example.                               |
| A-010 | file_parser.py  | 3.2.2.2          | Timestamps must be strictly ascending (no duplicates)             | B        | SRS says "ascending" — ambiguous. Chose strict.                        |
| A-011 | file_parser.py  | 3.2.2.2, 3.2.2.6 | Unparseable numeric values become None                            | B        | SRS 3.2.2.6 allows placeholders for missing data.                      |
| A-013 | data_validator.py | 3.2.2.8        | Configuration stored in validator_config.json                     | B        | SRS silent on storage format for Table 4/5 ranges and thresholds.      |
| A-014 | data_validator.py | 3.2.2.8        | Compressor Current upper bound is None (no limit)                 | B        | SRS Table 5 lists Compressor Current upper bound as NA (chiller dependent). |
| A-015 | data_validator.py | 3.2.2.9        | set_range / set_threshold check requesting_role == ROLE_ADMIN     | B        | Enforces administrator privilege requirement per SRS 3.2.2.9.          |
| A-016 | data_validator.py | 3.2.2.8        | Inclusive range comparison (min <= val <= max)                    | B        | Aligns with Table 5 boundary conventions and boundary-value analysis.  |
| A-017 | data_validator.py | 3.2.2.3, 3.2.2.8 | Unknown sensor types return "in_doubt_range"                    | B        | Without a configured range, accuracy cannot be confirmed.              |
| A-018 | main.py         | 2.4, 3.5.1.1     | Tkinter chosen as cross-platform GUI framework                    | B        | SRS 2.4 specifies Windows compatibility; Tkinter built into standard library. |
| A-019 | main.py         | 3.3.1.6, 3.5.1.11| Modal windows implemented via transient() and grab_set()          | B        | Guarantees window hierarchy and modality constraints across windows.   |
| A-020 | main.py         | 3.5.1.4-3.5.1.10 | Menu item enable/disable states stored in dictionary              | B        | Enables programmatic testability of menu item state transitions.       |
| A-021 | main.py         | 3.5.1.3, Table 3 | Time display uses MM/DD/YY HH:MM format                           | B        | Matches time format conventions in SRS Table 3.                        |
| A-022 | main.py         | 3.1.1.2.1 s11    | check_timeout() is invoked on menu actions to enforce timeout     | A        | Explicitly stated in SRS.                                              |
| A-023 | config_manager.py | 3.7            | Audit log written to data/audit.log as plain text                 | B        | SRS 3.7 specifies audit logging; plain text log file chosen for prototype simplicity. |
| A-024 | config_manager.py | 3.5.1.14, 3.5.1.16 | Save/Recall dialogs use filedialog with .json extension          | B        | JSON selected as standard export/import format for configuration.      |
| A-025 | config_manager.py | 3.5.1.12       | Parameters (a-g) stubbed as out-of-scope for prototype            | B        | Prototype implements 7 FRs; parameter (h) implemented via FR5 / SRS 3.2.2.9. |
| A-026 | config_manager.py | 3.5.1.11, 3.3.1.6 | Config window uses transient() and grab_set() for modality        | B        | Consistent with modal window hierarchy across application.             |
| A-027 | main.py           | 3.5.1.11, 3.3.1.6 | ConfigurationWindow integrated directly into main.py open_configuration_window | B | Connects MainWindow to ConfigurationWindow passing shared auth session state. |
| A-028 | diagnostic_engine.py | 3.2.3.4, 3.2.4.2 | Engine returns completed with no fault; Table 7 algorithms out of scope | B | Prototype focuses on 7 FRs; Table 7 fault rules stubbed for prototype. |
| A-029 | diagnostic_engine.py | 3.2.4.2, Table 3 | absolute_time uses MM/DD/YY HH:MM format                         | B        | Aligns with timestamp format conventions across application.           |
| A-030 | diagnostic_engine.py | 3.2.3.4          | Only None values trigger skipped_missing_input status            | A        | SRS 3.2.3.4 explicitly rules missing data skips processing; out-of-range is in-doubt. |
| A-031 | error_logger.py      | 3.4.1, 3.4.1.1   | data/errors.log plain text file format                            | B        | SRS specifies error logging; plain text log file chosen for prototype. |
| A-032 | error_logger.py      | 3.4.1            | Significant error determination delegated to caller               | B        | Caller decides whether an operational exception warrants logging.      |
| A-033 | error_logger.py      | 3.4.1            | report_to_user uses user_callback parameter                      | B        | Decouples error logger utility from GUI components.                    |
| A-034 | result_display.py    | 3.5.1.19, 3.3.1.6 | Window modality implemented via transient() and grab_set()       | B        | Consistent with modal window hierarchy across application (A-019).    |
| A-035 | result_display.py    | 3.5.1.21         | Fix field displayed as "Not available in prototype"               | B        | DiagnosticResult models fault data; fixes stubbed for prototype.       |
| A-036 | result_display.py    | 3.5.1.28, 3.5.1.21| Color conventions: green=OK, orange=skipped, red=fault           | B        | Matches color conventions defined in SRS 3.5.1.28.                     |
| A-037 | main.py, auth.py, file_parser.py | 3.4.1    | error_logger invoked across core modules for significant operational errors | B | Integrates operational exception logging per SRS 3.4.1 (A-032).        |


Note: A-012 is intentionally skipped. It was assigned to a design decision ("dual layout support") that was subsequently removed from file_parser.py. Skipping avoids renumbering stable IDs.

## Section 2 — Viva Defense Scripts

### A-001
"SRS 3.2.1.1 refers to 'general user' and 'administrator' but does not define constants for them. I chose those exact names as module constants so the rest of the code reads like the SRS."

### A-002
"SRS 3.6 requires identifier/password lookup but does not specify storage. I chose a JSON file in the project root for prototype simplicity. A production system would use a database."

### A-003
"SRS is silent on hashing algorithm. I chose SHA-256 without salt for the prototype. This is a known limitation — SonarQube may flag it, and I would use bcrypt with a per-user salt in production."

### A-004
"If users.json is deleted at runtime, load_users() raises FileNotFoundError instead of silently recreating default credentials. Silent recreation would be a backdoor — anyone who knows the defaults could log in as admin. Re-initialization requires an explicit init_users_file() call."

### A-005
"SRS 3.1.5.2.7 step 5 explicitly allows three authentication attempts before dismissing the window."

### A-006
"SRS 3.1.1.2.1 step 11 explicitly says 15-minute inactivity downgrades admin to general user."

### A-007
"SRS says privileges revert — not that the session ends. My check_timeout() downgrades the role but retains the username. The user stays in the tool as a general user."

### A-008
"SRS step 5 implies a fresh authentication window means fresh attempts. logout() resets failed_attempts so the next window grants three new attempts."

### A-009
"SRS 3.2.2.2 prose says Building Identifier and Input Identifier must appear in that order. Table 3 additionally shows a sensor-names row above both. I match Table 3 exactly."

### A-010
"SRS says 'ascending order'. I interpret this as strictly increasing to reject duplicate timestamps, which would cause ambiguous diagnostics at identical ticks. If the SRS author intended non-decreasing, that is a specification ambiguity."

### A-011
"SRS 3.2.2.6 allows missing-data placeholders. I convert blank or malformed numeric values to None as a placeholder, preserving row alignment for downstream validation."

### A-013
"SRS is silent on where Table 4 thresholds and Table 5 ranges are stored. I chose validator_config.json for prototype simplicity."

### A-014
"SRS Table 5 lists Compressor Current upper bound as 'NA, Chiller dependent'. I model this as None and treat it as no upper limit while still enforcing the lower bound of 0."

### A-015
"SRS 3.2.2.9 says the administrator can modify expected ranges. set_range and set_threshold enforce requesting_role == ROLE_ADMIN and return (False, 'unauthorized') for anyone else."

### A-016
"SRS Table 5 ranges use wording like '-40 to 130'. I treat boundaries as inclusive. So -40 and 130 are accepted; -40.1 and 130.1 are rejected."

### A-017
"If a sensor type has no configured range, I return 'in_doubt_range' rather than 'accurately_acquired'. Without a known range, accuracy cannot be confirmed — so the value is in doubt, not accepted."

### A-018
"SRS 2.4 specifies Windows compatibility. I chose Tkinter because it is built into the Python standard library, requires no external dependencies, and satisfies SRS 2.4 GUI requirements. This is A-018, Category B."

### A-019
"SRS 3.3.1.6 and 3.5.1.11 require window hierarchy modality. I implement modal windows using Toplevel.transient(parent) and grab_set() to restrict user interaction to the top modal window. This is A-019, Category B."

### A-020
"SRS 3.5.1.7 through 3.5.1.10 specify strict menu enable and disable rules. I track menu states in a dictionary and compute states via AppState methods so menu state transitions can be verified in automated self-tests without requiring a display. This is A-020, Category B."

### A-021
"SRS 3.5.1.3 requires current time display. I format timestamps as MM/DD/YY HH:MM matching SRS Table 3 conventions. In real-time mode, it updates live; in batch mode, it displays the fixed batch timestamp. This is A-021, Category B."

### A-022
"SRS 3.1.1.2.1 step 11 requires that if 15 minutes elapse without user activity, privileges revert to general user. I invoke check_timeout() at the start of every menu action handler and menu state update to immediately enforce privilege downgrade if 15 minutes have passed. This is A-022, Category A."

### A-023
"SRS 3.7 requires an audit trail of fixed data changes. I log old and new values, sensor name, timestamp, and username to data/audit.log in plain text format. This is A-023, Category B."

### A-024
"SRS 3.5.1.14 and 3.5.1.16 describe Save and Recall configuration actions. I implement these with standard filedialog prompts with .json extension for seamless export and import. This is A-024, Category B."

### A-025
"SRS 3.5.1.12 lists 8 configurable parameters (a–g and h). Our prototype scope implements parameter (h) expected ranges via FR5 / SRS 3.2.2.9. Parameters (a–g) are stubbed with a visible disabled label in the UI. This is A-025, Category B."

### A-026
"SRS 3.5.1.11 requires the Configuration Window to be modal to the main window. I use transient(parent) and grab_set() for modal window control, consistent with A-019. This is A-026, Category B."

### A-027
"SRS 3.5.1.11 requires the Configuration Window to open from the Main Window. I integrate ConfigurationWindow directly into main.py's open_configuration_window(), passing the active AuthenticationSession to enforce role permissions seamlessly across windows. This is A-027, Category B."

### A-028
"SRS 3.2.3.4 defines missing data rules. My DiagnosticEngine returns status 'completed' with no fault when all inputs are present, as full Table 7 fault detection rules are out of scope for this prototype. This is A-028, Category B."

### A-029
"SRS 3.2.4.2 specifies fault result attributes including absolute time. I format absolute_time as MM/DD/YY HH:MM, matching SRS Table 3 conventions and A-021. This is A-029, Category B."

### A-030
"SRS 3.2.3.4 explicitly states that processing shall not occur if any input data is missing. I treat None values as missing data triggering 'skipped_missing_input' status, while out-of-range values are evaluated as in-doubt data. This is A-030, Category A."

### A-031
"SRS 3.4.1 requires logging significant errors in software operation to permanent storage with absolute time, module, function, and description (SRS 3.4.1.1). I implement log_error() writing to data/errors.log in plain text format. This is A-031, Category B."

### A-032
"SRS 3.4.1 specifies logging of 'significant errors'. The determination of whether an operational event constitutes a significant error is delegated to the calling module. This is A-032, Category B."

### A-033
"SRS 3.4.1 states selected errors shall be reported to the user. I implement report_to_user via a callback parameter to decouple error logging from specific GUI widgets. This is A-033, Category B."

### A-034
"SRS 3.5.1.19 and 3.3.1.6 require the Diagnostic Information window to be modal to the condition/subsystem window. I implement modal behavior via transient(parent) and grab_set(), consistent with A-019. This is A-034, Category B."

### A-035
"SRS 3.5.1.21 requires displaying possible problems, potential causes, and fixes. Since DiagnosticResult models fault conditions, recommended fixes are displayed as 'Not available in prototype'. This is A-035, Category B."

### A-036
"SRS 3.5.1.28 defines color conventions (green=OK, yellow/orange=caution/skipped, red=not OK). I apply green for no fault, orange for skipped missing inputs, and red for fault conditions in the result display window. This is A-036, Category B."

### A-037
"SRS 3.4.1 requires significant errors to be logged. I chose to invoke error_logger.log_error from auth.py (lockout), file_parser.py (parse errors), data_validator.py (unauthorized attempts), config_manager.py (save failures), and main.py (file load errors) so that operational failures across the entire app are logged with the four required fields from SRS 3.4.1.1. This is A-037, Category B."