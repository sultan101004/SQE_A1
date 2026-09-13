# Jira Defect Records — Diagnostician Prototype v1.0

**Project**: Diagnostician Automated Prototype (SE3002 Assignment 1)  
**Baseline**: Commit `3c7a91a` on `main`, Tag `v1.0-frozen`  
**Jira Environment**: Jira Free Workspace (`https://se3002-diagnostician.atlassian.net`)  
**Total Defect Records**: 2 Confirmed Scope Blockers (`BUG-01`, `BUG-02`)

---

## Defect Record 1: BUG-01

- **Issue Key**: `BUG-01`
- **Title**: SRS 3.2.3.1 Table 7 Fault Detection Algorithms Unimplemented (Stubbed Execution)
- **Affected Environment / Build**: Windows 11 x64, Python 3.14, Diagnostician v1.0-frozen (Commit `3c7a91a`)
- **Related Test Case ID**: `TC-24` (Condition `COND-24`)
- **Workflow Status**: `OPEN` / `DEFERRED`
- **Severity**: `High`
- **Priority**: `Medium` (Out of Prototype Scope per Assumption **A-028**)
- **Reproducibility**: `100% Reproducible`

### Preconditions
1. User logs into Diagnostician application as administrator.
2. Sensed-data file containing valid thermodynamic input measurements (e.g., `valid_value.txt`) is parsed successfully.

### Steps to Reproduce
1. Launch `python main.py`.
2. Authenticate as `admin` / `admin123`.
3. Click **Start Diagnostics** and select `valid_value.txt`.
4. Observe the diagnostic engine execution result window.

### Expected Result
The system evaluates complex thermodynamic fault rules specified in SRS 3.2.3.1 Table 7 (e.g., Refrigerant Charge, Condenser Fouling, Compressor Failure) and displays specific diagnostic fault findings, root causes, and recommended fixes in `DiagnosticInformationWindow`.

### Actual Result
`DiagnosticEngine` skips Table 7 algorithmic evaluation and returns a generic stubbed status `completed` with `"No fault detected."` (Reason: `None`). SRS Table 7 rules are not implemented in the v1.0-frozen codebase.

### Evidence & Impact
- **Code Reference**: [diagnostic_engine.py](file:///c:/Users/Sultan/Desktop/SQE_A1/diagnostician/diagnostic_engine.py#L60-L88)
- **Scope Assumption**: Recorded in `AI_ASSUMPTIONS.md` under **A-028** (7 FR prototype scope constraint).
- **Test Status**: `TC-24` marked **BLOCKED**.

---

## Defect Record 2: BUG-02

- **Issue Key**: `BUG-02`
- **Title**: SRS 3.5.1.12 Configuration Parameters a–g Unimplemented in Configuration GUI
- **Affected Environment / Build**: Windows 11 x64, Python 3.14, Diagnostician v1.0-frozen (Commit `3c7a91a`)
- **Related Test Case ID**: `TC-25` (Condition `COND-25`)
- **Workflow Status**: `OPEN` / `DEFERRED`
- **Severity**: `Medium`
- **Priority**: `Low` (Out of Prototype Scope per Assumption **A-025**)
- **Reproducibility**: `100% Reproducible`

### Preconditions
1. User logs into Diagnostician application as administrator.
2. User opens the Configuration Window (`File` → `Configure Diagnostics`).

### Steps to Reproduce
1. Launch `python main.py`.
2. Authenticate as `admin` / `admin123`.
3. Navigate to `File` → `Configure Diagnostics`.
4. Attempt to view or edit configuration parameters **a–g** (e.g., Admin Password, Screen Saver Delay, Topmost Window Toggle).

### Expected Result
`ConfigurationWindow` displays editable UI input controls (text inputs, checkboxes, spinboxes) allowing the administrator to modify parameters a–g per SRS 3.5.1.12.

### Actual Result
Parameters a–g are not editable. The UI renders a disabled notice text label: `"Parameters a-g (Admin Password, Screen Saver, Topmost, etc.) out of prototype scope (FR5 range configuration only)."`

### Evidence & Impact
- **Code Reference**: [config_manager.py](file:///c:/Users/Sultan/Desktop/SQE_A1/diagnostician/config_manager.py#L115-L125)
- **Scope Assumption**: Recorded in `AI_ASSUMPTIONS.md` under **A-025** (FR5 scope prioritization).
- **Test Status**: `TC-25` marked **BLOCKED**.
