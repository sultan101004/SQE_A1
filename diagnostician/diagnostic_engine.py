"""
Module: diagnostic_engine.py
SRS References:
  - SRS 3.2.3.4: Diagnostic algorithm shall not process if any input data is missing.
  - SRS 3.2.2.4, 3.2.2.6: Data not acquired is represented as None (missing data placeholder).
  - SRS 3.2.4.2: Fault result attributes (description, potential causes, location, time).
  - SRS 3.2.3.7: Diagnostic result identifies algorithm name.

Design Decisions & Category B Assumptions:
  # ASSUMPTION (A-028): Engine returns "completed" with no fault; full Table 7 algorithms out of scope for prototype.
  # ASSUMPTION (A-029): absolute_time uses MM/DD/YY HH:MM format (consistent with A-021).
  # ASSUMPTION (A-030): Only None values trigger skipped_missing_input status; out-of-range values are in-doubt.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiagnosticInput:
    """Represents a single input parameter for diagnostic processing. SRS Reference: SRS 3.2.3.4"""
    name: str
    value: float | None
    unit: str = ""


@dataclass
class DiagnosticResult:
    """Represents the output result of a diagnostic run. SRS Reference: SRS 3.2.4.2, SRS 3.2.3.7"""
    status: str  # "completed" or "skipped_missing_input"
    algorithm_name: str | None = None
    fault_description: str | None = None
    potential_causes: list[str] = field(default_factory=list)
    location: str | None = None
    absolute_time: str | None = None
    reason: str | None = None


def has_missing_inputs(inputs: list[DiagnosticInput]) -> bool:
    """Checks if any input has value is None. SRS Reference: SRS 3.2.3.4"""
    return any(inp.value is None for inp in inputs)


def get_missing_input_names(inputs: list[DiagnosticInput]) -> list[str]:
    """Returns names of inputs that have value is None. SRS Reference: SRS 3.2.3.4"""
    return [inp.name for inp in inputs if inp.value is None]


class DiagnosticEngine:
    """
    Executes diagnostic evaluation on provided inputs following SRS 3.2.3.4 missing data rules.
    SRS Reference: SRS 3.2.3.4, SRS 3.2.4.2
    """

    def __init__(self, location: str = "Building 1, Chiller 1") -> None:
        """Initializes DiagnosticEngine with target location. SRS Reference: SRS 3.2.4.2"""
        self.location = location

    def run(self, algorithm_name: str, inputs: list[DiagnosticInput]) -> DiagnosticResult:
        """
        Runs diagnostic evaluation. Skips execution if any input data is missing.
        SRS Reference: SRS 3.2.3.4, SRS 3.2.4.2, SRS 3.2.3.7 (A-028, A-029, A-030)
        """
        missing = get_missing_input_names(inputs)  # ASSUMPTION (A-030): None values treated as missing
        if missing:
            reason_str = f"Missing input(s): {', '.join(missing)}"
            return DiagnosticResult(
                status="skipped_missing_input",
                algorithm_name=algorithm_name,
                reason=reason_str,
                fault_description=None,
                potential_causes=[],
                location=self.location,
                absolute_time=None
            )

        # ASSUMPTION (A-028): Table 7 algorithms stubbed; returns completed with no fault
        # ASSUMPTION (A-029): absolute_time formatted as MM/DD/YY HH:MM
        current_time = datetime.now().strftime("%m/%d/%y %H:%M")
        return DiagnosticResult(
            status="completed",
            algorithm_name=algorithm_name,
            fault_description=None,
            potential_causes=[],
            location=self.location,
            absolute_time=current_time,
            reason=None
        )


def run_self_tests() -> None:
    """Runs 6 non-GUI self-tests validating DiagnosticEngine logic. SRS Reference: SRS 3.2.3.4"""
    print("--- Running diagnostic_engine.py self-tests ---")
    engine = DiagnosticEngine(location="Building 1, Chiller 1")

    # Test 1: All inputs present -> status="completed"
    inputs_all = [
        DiagnosticInput("Ambient Temperature", 75.0, "F"),
        DiagnosticInput("Compressor Current", 12.5, "A")
    ]
    res1 = engine.run("Chiller Diagnosis", inputs_all)
    assert res1.status == "completed" and res1.reason is None and res1.absolute_time is not None
    assert res1.algorithm_name == "Chiller Diagnosis"
    print("[PASS] Test 1: All inputs present returns status='completed' with algorithm_name")

    # Test 2: One input None -> status="skipped_missing_input"
    inputs_one_none = [
        DiagnosticInput("Ambient Temperature", None, "F"),
        DiagnosticInput("Compressor Current", 12.5, "A")
    ]
    res2 = engine.run("Chiller Diagnosis", inputs_one_none)
    assert res2.status == "skipped_missing_input"
    assert res2.reason == "Missing input(s): Ambient Temperature"
    assert res2.algorithm_name == "Chiller Diagnosis"
    print("[PASS] Test 2: One missing input returns status='skipped_missing_input'")

    # Test 3: Two inputs None -> reason lists both names
    inputs_two_none = [
        DiagnosticInput("Ambient Temperature", None, "F"),
        DiagnosticInput("Compressor Current", None, "A")
    ]
    res3 = engine.run("Chiller Diagnosis", inputs_two_none)
    assert res3.status == "skipped_missing_input"
    assert "Ambient Temperature" in res3.reason and "Compressor Current" in res3.reason
    print("[PASS] Test 3: Two missing inputs lists both names in skip reason")

    # Test 4: Empty input list -> status="completed" (no inputs to miss)
    res4 = engine.run("Chiller Diagnosis", [])
    assert res4.status == "completed" and res4.reason is None
    print("[PASS] Test 4: Empty input list returns status='completed'")

    # Test 5: has_missing_inputs helper
    assert has_missing_inputs(inputs_all) is False
    assert has_missing_inputs(inputs_one_none) is True
    print("[PASS] Test 5: has_missing_inputs helper functions correctly")

    # Test 6: get_missing_input_names helper
    missing_names = get_missing_input_names(inputs_two_none)
    assert missing_names == ["Ambient Temperature", "Compressor Current"]
    print("[PASS] Test 6: get_missing_input_names returns exact missing input list")

    print("All diagnostic_engine.py self-tests passed successfully!")


if __name__ == "__main__":
    run_self_tests()
