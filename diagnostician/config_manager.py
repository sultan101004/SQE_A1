"""
Module: config_manager.py
SRS References: 3.1.4, 3.5.1.11, 3.5.1.12, 3.5.1.14, 3.5.1.15, 3.5.1.16, 3.2.2.9, 3.7.
# ASSUMPTION (A-023): Audit log written to data/audit.log as plain text.
# ASSUMPTION (A-024): Save/Recall dialogs use filedialog with .json extension.
# ASSUMPTION (A-025): Parameters (a-g) stubbed out of scope for prototype.
# ASSUMPTION (A-026): Config window uses transient() and grab_set() for modality.
"""

from datetime import datetime
import json, os, tkinter as tk
from tkinter import filedialog, messagebox, ttk
import auth, data_validator, error_logger

AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "audit.log")


class ConfigEditor:
    """Handles range modifications, unsaved tracking, and audit logging. SRS 3.1.4, 3.2.2.9, 3.7"""

    def __init__(self) -> None:
        """Initializes ConfigEditor state. SRS Reference: SRS 3.1.4"""
        self._unsaved_changes: bool = False

    def load_ranges(self) -> dict:
        """Loads ranges dictionary from data_validator. SRS Reference: SRS 3.2.2.8, 3.5.1.12"""
        return data_validator.load_config().get("ranges", {})

    def update_range(self, sensor_type: str, min_val: float, max_val: float | None, requesting_role: str, requesting_username: str = "admin") -> tuple[bool, str]:
        """Updates range if admin, logs change to audit trail, and marks unsaved. SRS Reference: SRS 3.2.2.9, 3.7 (A-023)"""
        old_val = self.load_ranges().get(sensor_type, (None, None))
        old_tuple = (old_val[0], old_val[1]) if isinstance(old_val, (list, tuple)) else (None, None)
        success, message = data_validator.set_range(sensor_type, min_val, max_val, requesting_role)
        if not success:
            return False, message
        self._unsaved_changes = True
        self._write_audit_log(sensor_type, old_tuple, (min_val, max_val), requesting_username)
        return True, "ok"

    def _write_audit_log(self, sensor_type: str, old_range: tuple, new_range: tuple, username: str) -> None:
        """Appends audit log entry to data/audit.log. SRS Reference: SRS 3.7 (A-023)"""
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | sensor={sensor_type} | old={old_range} | new={new_range} | user={username}\n"
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(log_line)

    def has_unsaved_changes(self) -> bool:
        """Returns True if range changes occurred since save/recall. SRS Reference: SRS 3.5.1.15"""
        return self._unsaved_changes

    def reset_unsaved_changes(self) -> None:
        """Resets unsaved changes flag. SRS Reference: SRS 3.5.1.14"""
        self._unsaved_changes = False


class ConfigurationWindow(tk.Toplevel):
    """Configuration modal window for sensed data ranges. SRS Reference: SRS 3.5.1.11-3.5.1.16, 3.3.1.6"""

    def __init__(self, parent: tk.Widget, auth_session: auth.AuthenticationSession, on_close=None) -> None:
        """Initializes configuration Toplevel modal window. SRS Reference: SRS 3.5.1.11 (A-026)"""
        super().__init__(parent)
        self.parent, self.auth_session, self.on_close_cb = parent, auth_session, on_close
        self.editor = ConfigEditor()
        self.title("Diagnostician - Configuration")
        self.geometry("680x480")
        self.transient(parent)  # ASSUMPTION (A-026): Modal hierarchy
        self.grab_set()
        self._build_ui()
        self._populate_tree()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def open(self) -> None:
        """Displays and focuses the configuration window. SRS Reference: SRS 3.5.1.11"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _build_ui(self) -> None:
        """Builds treeview, entry controls, out-of-scope note, and buttons. SRS Reference: SRS 3.5.1.12 (A-025)"""
        tk.Label(self, text="Sensed Input Data Expected Ranges (FR5 / SRS 3.2.2.9)", font=("Arial", 10, "bold")).pack(pady=4)
        frame_tree = tk.Frame(self)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.tree = ttk.Treeview(frame_tree, columns=("sensor", "min", "max"), show="headings", height=7)
        for col, head, w in [("sensor", "Sensor Type", 280), ("min", "Min Value", 110), ("max", "Max Value", 110)]:
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w)
        sb = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        frame_edit = tk.Frame(self)
        frame_edit.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(frame_edit, text="Min:").pack(side=tk.LEFT, padx=2)
        self.entry_min = tk.Entry(frame_edit, width=10)
        self.entry_min.pack(side=tk.LEFT, padx=4)
        tk.Label(frame_edit, text="Max:").pack(side=tk.LEFT, padx=2)
        self.entry_max = tk.Entry(frame_edit, width=10)
        self.entry_max.pack(side=tk.LEFT, padx=4)
        tk.Button(frame_edit, text="Apply Change", command=self.on_apply_change).pack(side=tk.LEFT, padx=8)

        # ASSUMPTION (A-025): Stubbed parameters (a-g) displayed as disabled note
        stub_msg = "Other parameters (out of scope for this prototype): Admin Password, Screen Saver, Topmost, Buildings/Subsystems, Conditions Enabled, Sensitivity, Scale Factors"
        tk.Label(self, text=stub_msg, font=("Arial", 8, "italic"), fg="gray", wraplength=640).pack(pady=4)

        frame_btns = tk.Frame(self)
        frame_btns.pack(fill=tk.X, padx=8, pady=8)
        tk.Button(frame_btns, text="Save", width=10, command=self.on_save).pack(side=tk.LEFT, padx=6)
        tk.Button(frame_btns, text="Recall", width=10, command=self.on_recall).pack(side=tk.LEFT, padx=6)
        tk.Button(frame_btns, text="Close", width=10, command=self.on_close).pack(side=tk.RIGHT, padx=6)

    def _populate_tree(self) -> None:
        """Populates Treeview with current ranges. SRS Reference: SRS 3.5.1.12"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for sensor, (min_v, max_v) in self.editor.load_ranges().items():
            max_str = "None" if max_v is None else str(max_v)
            self.tree.insert("", tk.END, values=(sensor, str(min_v), max_str))

    def _on_tree_select(self, event) -> None:
        """Fills entry fields when a row is selected. SRS Reference: SRS 3.5.1.12"""
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            self.entry_min.delete(0, tk.END)
            self.entry_min.insert(0, vals[1])
            self.entry_max.delete(0, tk.END)
            self.entry_max.insert(0, vals[2])

    def on_apply_change(self) -> None:
        """Applies edited min/max values to selected sensor. SRS Reference: SRS 3.2.2.9"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a sensor from the table first.", parent=self)
            return
        sensor_type = self.tree.item(selected[0], "values")[0]
        try:
            min_val = float(self.entry_min.get().strip())
            max_str = self.entry_max.get().strip()
            max_val = None if max_str.lower() in ("none", "null", "") else float(max_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Min and Max must be numeric values (or 'None' for Max).", parent=self)
            return

        username = self.auth_session.current_username or "admin"
        success, msg = self.editor.update_range(sensor_type, min_val, max_val, self.auth_session.current_role, username)
        if success:
            self._populate_tree()
            messagebox.showinfo("Success", f"Updated range for {sensor_type}.", parent=self)
        else:
            messagebox.showerror("Update Failed", f"Failed to update range: {msg}", parent=self)

    def on_save(self) -> None:
        """Saves configuration to JSON file and asks to relay to processing. SRS Reference: SRS 3.5.1.14 (A-024)"""
        if not self.editor.has_unsaved_changes():
            messagebox.showinfo("Save Configuration", "No changes to save.", parent=self)
            return
        filepath = filedialog.asksaveasfilename(parent=self, title="Save Configuration As", defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not filepath:
            return
        config_data = {"ranges": self.editor.load_ranges(), "thresholds": data_validator.load_config().get("thresholds", {})}
        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(config_data, fh, indent=4)
        except Exception as exc:
            error_logger.log_error("config_manager.py", "on_save", str(exc))
            messagebox.showerror("Save Failed", f"Failed to save configuration: {exc}", parent=self)
            return
        self.editor.reset_unsaved_changes()
        messagebox.askyesno("Relay to diagnostics", "Apply changes to diagnostic processing immediately?", parent=self)


    def on_recall(self) -> None:
        """Recalls configuration from JSON file. SRS Reference: SRS 3.5.1.16 (A-024)"""
        filepath = filedialog.askopenfilename(parent=self, title="Recall Configuration File", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not filepath or not os.path.exists(filepath):
            return
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                recalled = json.load(fh)
            data_validator.save_config(recalled)
            self.editor.reset_unsaved_changes()
            self._populate_tree()
            messagebox.showinfo("Recall Complete", "Configuration successfully loaded.", parent=self)
        except Exception as exc:
            messagebox.showerror("Recall Failed", f"Invalid configuration file: {exc}", parent=self)

    def on_close(self) -> None:
        """Closes window with confirmation if unsaved changes exist. SRS Reference: SRS 3.5.1.15"""
        if self.editor.has_unsaved_changes():
            if not messagebox.askyesno("Unsaved Changes", "Discard unsaved changes?", parent=self):
                return
        if self.on_close_cb:
            self.on_close_cb(self)
        self.destroy()


def run_self_tests() -> None:
    """Runs non-GUI self-tests validating ConfigEditor logic and audit logging. SRS Reference: SRS 3.1.4"""
    print("--- Running config_manager.py self-tests ---")
    data_validator.init_config(overwrite=True)
    editor = ConfigEditor()

    # Test 1: ConfigEditor.load_ranges() returns dict with at least 12 sensor types
    ranges = editor.load_ranges()
    assert isinstance(ranges, dict) and len(ranges) >= 12
    print("[PASS] Test 1: ConfigEditor.load_ranges() returns >= 12 sensor ranges")

    # Test 2: update_range as general user returns (False, "unauthorized")
    success, msg = editor.update_range("Ambient Temperature", -45.0, 135.0, auth.ROLE_GENERAL, "user1")
    assert success is False and msg == "unauthorized"
    print("[PASS] Test 2: General user update_range returns (False, 'unauthorized')")

    # Test 3: update_range as admin returns (True, "ok") and persists
    success, msg = editor.update_range("Ambient Temperature", -45.0, 135.0, auth.ROLE_ADMIN, "admin")
    assert success is True and msg == "ok"
    assert data_validator.load_config()["ranges"]["Ambient Temperature"] == [-45.0, 135.0]
    print("[PASS] Test 3: Admin update_range succeeds and persists in data_validator")

    # Test 4: update_range writes audit log entry (SRS 3.7)
    assert os.path.exists(AUDIT_LOG_PATH)
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as fh:
        log_content = fh.read()
    assert "sensor=Ambient Temperature" in log_content
    assert "old=" in log_content and "new=(-45.0, 135.0)" in log_content and "user=admin" in log_content
    print("[PASS] Test 4: update_range writes audit log entry to data/audit.log (SRS 3.7)")

    # Test 5: has_unsaved_changes state tracking
    assert editor.has_unsaved_changes() is True
    editor.reset_unsaved_changes()
    assert editor.has_unsaved_changes() is False
    print("[PASS] Test 5: has_unsaved_changes state tracking and reset")

    print("All config_manager.py self-tests passed successfully!")


if __name__ == "__main__":
    run_self_tests()
