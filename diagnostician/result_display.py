"""
Module: result_display.py
SRS References: 3.2.4.2, 3.5.1.19, 3.5.1.21, 3.5.1.22, 3.3.1.6.
# ASSUMPTION (A-034): Window modality via transient() and grab_set(), consistent with A-019.
# ASSUMPTION (A-035): "Fix" field displayed as "Not available in prototype" for SRS 3.5.1.21 compliance.
# ASSUMPTION (A-036): Colors: green for OK, orange for skipped, red for fault (SRS 3.5.1.28).
"""

import tkinter as tk
from tkinter import ttk
from diagnostic_engine import DiagnosticResult


def format_result(result: DiagnosticResult) -> dict:
    """Formats DiagnosticResult into structured dictionary for display. SRS 3.2.4.2, 3.5.1.21 (A-035)"""
    if result.status == "skipped_missing_input":
        return {"status": "skipped", "reason": result.reason or "Missing required input data"}
    if result.fault_description is not None:
        return {
            "status": "fault",
            "description": result.fault_description,
            "causes": result.potential_causes,
            "location": result.location or "Unknown Location",
            "absolute_time": result.absolute_time or "Unknown Time",
            "fix": "Not available in prototype"  # ASSUMPTION (A-035): Fix placeholder
        }
    return {"status": "no_fault", "message": "No fault detected."}


class DiagnosticInformationWindow(tk.Toplevel):
    """Diagnostic information window for detailed result view. SRS 3.5.1.19, 3.5.1.21, 3.5.1.22, 3.3.1.6"""

    def __init__(self, parent: tk.Widget, result: DiagnosticResult, on_close=None) -> None:
        """Initializes modal diagnostic information window. SRS Reference: SRS 3.3.1.6 (A-034)"""
        super().__init__(parent)
        self.parent, self.result, self.on_close_cb = parent, result, on_close
        loc_str = result.location or "Diagnostic Detail"
        self.title(f"Diagnostician Detail - {loc_str}")
        self.geometry("480x360")
        self.transient(parent)  # ASSUMPTION (A-034): Modality
        self.grab_set()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def open(self) -> None:
        """Displays and focuses the information window. SRS Reference: SRS 3.5.1.19"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _build_ui(self) -> None:
        """Builds UI elements based on formatted result. SRS Reference: SRS 3.5.1.21 (A-036)"""
        fmt = format_result(self.result)
        status = fmt["status"]
        frame = tk.Frame(self, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        if status == "no_fault":
            # ASSUMPTION (A-036): Green for OK
            tk.Label(frame, text=fmt["message"], font=("Arial", 12, "bold"), fg="green").pack(pady=20)
        elif status == "skipped":
            # ASSUMPTION (A-036): Orange for skipped
            tk.Label(frame, text=fmt["reason"], font=("Arial", 11, "bold"), fg="dark orange", wraplength=440).pack(pady=20)
        else:
            # ASSUMPTION (A-036): Red for fault
            tk.Label(frame, text=f"Possible Problem: {fmt['description']}", font=("Arial", 11, "bold"), fg="red", wraplength=440).pack(anchor="w", pady=4)
            tk.Label(frame, text=f"Location: {fmt['location']}", font=("Arial", 9)).pack(anchor="w", pady=1)
            tk.Label(frame, text=f"Time: {fmt['absolute_time']}", font=("Arial", 9)).pack(anchor="w", pady=1)
            tk.Label(frame, text="Potential Causes:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(6, 1))
            causes = fmt["causes"] if fmt["causes"] else ["None specified"]
            for cause in causes:
                tk.Label(frame, text=f"  • {cause}", font=("Arial", 9)).pack(anchor="w")
            tk.Label(frame, text=f"Recommended Fix: {fmt['fix']}", font=("Arial", 9, "italic"), fg="gray").pack(anchor="w", pady=(6, 1))

        # SRS 3.5.1.22: Close button
        tk.Button(self, text="Close", width=10, command=self.on_close).pack(pady=8)

    def on_close(self) -> None:
        """Closes window and invokes callback. SRS Reference: SRS 3.5.1.22"""
        if self.on_close_cb:
            self.on_close_cb(self)
        self.destroy()


def run_self_tests() -> None:
    """Runs non-GUI self-tests on format_result logic. SRS 3.2.4.2, 3.5.1.21"""
    print("--- Running result_display.py self-tests ---")
    # Test 1: Completed result with no fault -> {"status": "no_fault"}
    r1 = DiagnosticResult(status="completed", fault_description=None)
    f1 = format_result(r1)
    assert f1["status"] == "no_fault" and f1["message"] == "No fault detected."
    print("[PASS] Test 1: Completed result without fault returns status='no_fault'")

    # Test 2: Skipped missing input result -> status="skipped" with reason
    r2 = DiagnosticResult(status="skipped_missing_input", reason="Missing input(s): Ambient Temperature")
    f2 = format_result(r2)
    assert f2["status"] == "skipped" and "Ambient Temperature" in f2["reason"]
    print("[PASS] Test 2: Skipped missing input result returns status='skipped' with reason")

    # Test 3: Fabricated fault result -> dict with description, causes, location, time
    r3 = DiagnosticResult(
        status="completed", fault_description="Low Chiller Efficiency",
        potential_causes=["Fouled Condenser Tubes", "Refrigerant Leak"],
        location="Building 1, Chiller 1", absolute_time="09/13/26 14:30"
    )
    f3 = format_result(r3)
    assert f3["status"] == "fault" and f3["description"] == "Low Chiller Efficiency"
    assert len(f3["causes"]) == 2 and f3["location"] == "Building 1, Chiller 1"
    assert f3["absolute_time"] == "09/13/26 14:30" and f3["fix"] == "Not available in prototype"
    print("[PASS] Test 3: Fault result returns dict with description, causes, location, time, and fix")
    print("All result_display.py self-tests passed successfully!")


if __name__ == "__main__":
    run_self_tests()
