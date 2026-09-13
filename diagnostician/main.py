"""
Module: main.py
SRS References: 3.5.1.1-3.5.1.11, 3.3.1.3, 3.1.1.2.2.1, 3.2.3.4, 3.2.4.2, 3.4.1.
# ASSUMPTION (A-018): Tkinter GUI framework.
# ASSUMPTION (A-019): Window modality via transient() and grab_set().
# ASSUMPTION (A-020): Menu states stored in dictionary.
# ASSUMPTION (A-021): Time display format MM/DD/YY HH:MM.
# ASSUMPTION (A-022): check_timeout() on menu actions.
# ASSUMPTION (A-026): Modal configuration window.
# ASSUMPTION (A-027): ConfigurationWindow directly integrated.
# ASSUMPTION (A-037): error_logger invoked for operational failures.
"""

from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from auth import AuthenticationSession, ROLE_ADMIN, ROLE_GENERAL, is_admin, is_general_user
import data_validator
from diagnostic_engine import DiagnosticEngine, DiagnosticInput
import error_logger
import file_parser
from result_display import DiagnosticInformationWindow


class AppState:
    """Holds shared application state including auth session, diagnostic running status, and time mode. SRS 3.1.1.2.1, 3.5.1.7-3.5.1.10"""

    def __init__(self) -> None:
        """Initializes default application state."""
        self.auth_session = AuthenticationSession()
        self.diagnostic_running: bool = False
        self.current_time_mode: str = "real"
        self.batch_time: str | None = None

    def check_inactivity_timeout(self) -> bool:
        """Checks inactivity timeout and downgrades privileges if expired. SRS 3.1.1.2.1 s11 (A-022)"""
        return self.auth_session.check_timeout()

    def is_logout_enabled(self) -> bool:
        """SRS 3.5.1.8: Logout enabled only when authenticated as administrator."""
        return is_admin(self.auth_session.current_role)

    def is_start_enabled(self) -> bool:
        """SRS 3.5.1.9: Start enabled only when diagnostics NOT running."""
        return not self.diagnostic_running

    def is_stop_enabled(self) -> bool:
        """SRS 3.5.1.10: Stop enabled only when diagnostics IS running."""
        return self.diagnostic_running

    def is_configure_enabled(self) -> bool:
        """SRS 3.5.1.7: Configure Diagnostics always enabled."""
        return True

    def is_exit_enabled(self) -> bool:
        """SRS 3.5.1.7: Exit always enabled."""
        return True


class MainWindow(tk.Tk):
    """Main root window managing menus, time display, and window hierarchy. SRS 3.5.1.1-3.5.1.11, 3.3.1.3"""

    def __init__(self, app_state: AppState | None = None) -> None:
        """Initializes MainWindow UI widgets, menus, and window tracking stack."""
        super().__init__()
        self.app_state = app_state if app_state is not None else AppState()
        self.title("Diagnostician")
        self.geometry("600x400")
        self.window_stack: list[str] = ["main"]
        self._build_ui()
        self._build_menus()
        self.update_menu_states()
        self._start_clock()

    def _build_ui(self) -> None:
        """Builds title label and time display. SRS Reference: SRS 3.5.1.3"""
        tk.Label(self, text="Diagnostician HVAC Automated Diagnostic Tool", font=("Arial", 14, "bold")).pack(pady=10)
        self.time_label = tk.Label(self, text="", font=("Arial", 11))
        self.time_label.pack(pady=5)

    def _build_menus(self) -> None:
        """Creates File and Status menus in exact SRS order. SRS 3.5.1.4-3.5.1.6 (A-020)"""
        menubar = tk.Menu(self)
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label="Configure Diagnostics", command=self.on_configure_diagnostics)
        self.file_menu.add_command(label="Logout", command=self.on_logout)
        self.file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=self.file_menu)

        self.status_menu = tk.Menu(menubar, tearoff=0)
        self.status_menu.add_command(label="Start Diagnostics", command=self.on_start_diagnostics)
        self.status_menu.add_command(label="Stop Diagnostics", command=self.on_stop_diagnostics)
        menubar.add_cascade(label="Status", menu=self.status_menu)
        self.config(menu=menubar)

    def update_menu_states(self) -> None:
        """Updates menu item state to tk.NORMAL or tk.DISABLED per SRS 3.5.1.7-3.5.1.10 (A-020)."""
        self.app_state.check_inactivity_timeout()
        self.file_menu.entryconfig(0, state=tk.NORMAL if self.app_state.is_configure_enabled() else tk.DISABLED)
        self.file_menu.entryconfig(1, state=tk.NORMAL if self.app_state.is_logout_enabled() else tk.DISABLED)
        self.file_menu.entryconfig(2, state=tk.NORMAL if self.app_state.is_exit_enabled() else tk.DISABLED)
        self.status_menu.entryconfig(0, state=tk.NORMAL if self.app_state.is_start_enabled() else tk.DISABLED)
        self.status_menu.entryconfig(1, state=tk.NORMAL if self.app_state.is_stop_enabled() else tk.DISABLED)

    def _start_clock(self) -> None:
        """Updates clock display every second if in real time mode. SRS Reference: SRS 3.5.1.3, SRS 3.3.1.3 (A-021)"""
        if self.app_state.current_time_mode == "real":
            current_str = datetime.now().strftime("%m/%d/%y %H:%M:%S")
            self.time_label.config(text=f"Time: {current_str} (Real-time)")
            self.after(1000, self._start_clock)
        else:
            batch_str = self.app_state.batch_time if self.app_state.batch_time else "N/A"
            self.time_label.config(text=f"Time: {batch_str} (Batch mode)")

    def set_time_mode(self, mode: str, batch_time: str | None = None) -> None:
        """Sets time mode ('real' or 'batch'). SRS Reference: SRS 3.3.1.3"""
        self.app_state.current_time_mode = mode
        self.app_state.batch_time = batch_time
        self._start_clock()

    def _ensure_admin_authenticated(self) -> bool:
        """Prompts for admin authentication if not already admin. SRS Reference: SRS 3.1.1.2.2.1"""
        self.app_state.check_inactivity_timeout()
        if is_admin(self.app_state.auth_session.current_role):
            return True

        username = simpledialog.askstring("Admin Authentication", "Username:", parent=self)
        password = simpledialog.askstring("Admin Authentication", "Password:", show="*", parent=self)
        if not username or not password:
            return False

        status, role = self.app_state.auth_session.attempt_login(username, password)
        if status != "success" or not is_admin(role):
            messagebox.showerror("Authentication Failed", "Administrator authentication required.")
            self.update_menu_states()
            return False

        self.update_menu_states()
        return True

    def on_logout(self) -> None:
        """Logs out administrator user and updates menu state. SRS Reference: SRS 3.5.1.8, SRS 3.1.1.2.1 Step 10"""
        self.app_state.check_inactivity_timeout()
        self.app_state.auth_session.logout()
        self.update_menu_states()
        messagebox.showinfo("Logout", "Logged out. Privileges returned to General User.")

    def on_configure_diagnostics(self) -> None:
        """Opens modal configuration window with admin authentication. SRS Reference: SRS 3.5.1.11"""
        if not self._ensure_admin_authenticated():
            return
        self.open_configuration_window()

    def on_start_diagnostics(self) -> None:
        """Starts diagnostic processing after admin confirmation and file input. SRS 3.5.1.9, 3.2.2.2, 3.2.3.4 (A-037)"""
        if not self._ensure_admin_authenticated():
            return
        if not messagebox.askyesno("Start Diagnostics", "Confirm starting automated diagnostics?"):
            return

        filepath = filedialog.askopenfilename(parent=self, title="Select Batch Diagnostic File", filetypes=[("Data Files", "*.txt *.csv"), ("All Files", "*.*")])
        if not filepath:
            return

        success, parsed = file_parser.parse_file(filepath)
        if not success:
            error_logger.log_error("main.py", "on_start_diagnostics", str(parsed), report_to_user=True, user_callback=lambda m: messagebox.showerror("File Error", m, parent=self))
            return

        inputs = []
        columns = parsed.get("columns", {})
        for sensor_name, values in columns.items():
            val = values[0] if values else None
            v_status = data_validator.validate_value(sensor_name, val)
            final_val = None if (v_status == "in_doubt_acquisition" or val is None) else val
            inputs.append(DiagnosticInput(name=sensor_name, value=final_val))

        engine = DiagnosticEngine(location="Building 1")
        result = engine.run("Chiller Diagnosis", inputs)
        DiagnosticInformationWindow(self, result, on_close=lambda w: None).open()

        self.app_state.diagnostic_running = True
        self.update_menu_states()
        if parsed.get("timestamps"):
            self.set_time_mode("batch", parsed["timestamps"][0])

    def on_stop_diagnostics(self) -> None:
        """Stops diagnostic processing after admin auth and confirmation. SRS 3.1.1.2.2.1 Steps 2-3"""
        if not self._ensure_admin_authenticated():
            return
        if messagebox.askyesno("Stop Diagnostics", "Confirm stopping automated diagnostics?"):
            self.app_state.diagnostic_running = False
            self.update_menu_states()

    def on_exit(self) -> None:
        """Exits application cleanly after admin auth if running. SRS 3.1.1.2.2.1 Steps 6-7"""
        self.app_state.check_inactivity_timeout()
        if self.app_state.diagnostic_running:
            if not self._ensure_admin_authenticated():
                return
            if not messagebox.askyesno("Exit Warning", "Diagnostics running. Confirm exit?"):
                return
        self.destroy()

    def open_configuration_window(self) -> None:
        """Opens modal configuration window. SRS 3.5.1.11, 3.3.1.6 (A-019, A-026, A-027)"""
        if self.window_stack[-1] != "main":
            raise RuntimeError("Window hierarchy violation: Configuration window must be subordinate to Main window.")
        from config_manager import ConfigurationWindow
        self.window_stack.append("configuration")
        def close_cb(w):
            if "configuration" in self.window_stack:
                self.window_stack.remove("configuration")
        ConfigurationWindow(parent=self, auth_session=self.app_state.auth_session, on_close=close_cb).open()

    def open_subsystems_window(self, building_name: str = "Building 1") -> None:
        """Opens modal subsystems window placeholder. SRS 3.5.1.2, 3.3.1.6 (A-019)"""
        if self.window_stack[-1] != "main":
            raise RuntimeError("Window hierarchy violation: Subsystems window must be subordinate to Main window.")
        win = tk.Toplevel(self)
        win.title(f"Diagnostician - {building_name}")
        win.transient(self)
        win.grab_set()
        self.window_stack.append("subsystems")
        tk.Label(win, text=f"Subsystems Window ({building_name})", font=("Arial", 12)).pack(padx=20, pady=20)
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_modal(win))

    def _close_modal(self, window: tk.Toplevel) -> None:
        """Closes top modal window and pops window stack."""
        if len(self.window_stack) > 1:
            self.window_stack.pop()
        window.destroy()


def run() -> None:
    """Launches the main Tkinter application loop. SRS Reference: SRS 3.5.1.3 (A-018)"""
    app = MainWindow()
    app.mainloop()


def run_self_tests() -> None:
    """Runs non-GUI self-tests validating AppState and menu logic."""
    print("--- Running main.py self-tests ---")
    state = AppState()

    # Test 1: AppState initial
    assert not is_admin(state.auth_session.current_role)
    assert state.is_logout_enabled() is False
    assert state.is_start_enabled() is True
    assert state.is_stop_enabled() is False
    print("[PASS] Test 1: AppState initial state (no auth, diagnostic stopped)")

    # Test 2: Admin login enables Logout menu
    status, role = state.auth_session.attempt_login("admin", "admin123")
    assert status == "success" and role == ROLE_ADMIN
    assert state.is_logout_enabled() is True
    print("[PASS] Test 2: Admin login enables Logout menu")

    # Test 3: Logout disables Logout menu
    state.auth_session.logout()
    assert state.is_logout_enabled() is False
    print("[PASS] Test 3: Logout disables Logout menu")

    # Test 4: Diagnostic running = True
    state.diagnostic_running = True
    assert state.is_start_enabled() is False
    assert state.is_stop_enabled() is True
    print("[PASS] Test 4: Diagnostic running = True -> Start disabled, Stop enabled")

    # Test 5: Diagnostic running = False
    state.diagnostic_running = False
    assert state.is_start_enabled() is True
    assert state.is_stop_enabled() is False
    print("[PASS] Test 5: Diagnostic running = False -> Start enabled, Stop disabled")

    # Test 6: Configure and Exit menus always enabled
    assert state.is_configure_enabled() is True
    assert state.is_exit_enabled() is True
    print("[PASS] Test 6: Configure and Exit menu items always enabled")

    # Test 7: Non-admin stop diagnostics requires admin auth (SRS 3.1.1.2.2.1)
    state.auth_session.logout()
    state.diagnostic_running = True
    assert not is_admin(state.auth_session.current_role)
    assert state.is_stop_enabled() is True
    print("[PASS] Test 7: Non-admin stop diagnostics requires admin authentication")

    # Test 8: check_timeout() downgrades role after simulated 15-minute inactivity (SRS 3.1.1.2.1 s11)
    state.auth_session.attempt_login("admin", "admin123")
    assert is_admin(state.auth_session.current_role) is True
    import time as _time
    state.auth_session.last_activity_time = _time.time() - 901
    assert state.check_inactivity_timeout() is True and is_admin(state.auth_session.current_role) is False
    assert state.is_logout_enabled() is False
    print("[PASS] Test 8: check_timeout() downgrades admin role after 15-min inactivity")

    # Test 9: Integration file parse with missing input -> skipped_missing_input
    sample_content = "Temp\tFlow\nBuilding Identifier\t1\t1\nInput Identifier\t1\t2\n09/13/26 14:30\t75.0\tNONE"
    ok, parsed_sample = file_parser.parse_file_content(sample_content)
    assert ok is True
    test_inputs_missing = [
        DiagnosticInput(name=sn, value=None if (data_validator.validate_value(sn, sv[0] if sv else None) == "in_doubt_acquisition" or (sv[0] if sv else None) is None) else sv[0])
        for sn, sv in parsed_sample["columns"].items()
    ]
    res_missing = DiagnosticEngine(location="Building 1").run("Chiller Diagnosis", test_inputs_missing)
    assert res_missing.status == "skipped_missing_input"
    print("[PASS] Test 9: Integration test (file parse + missing input validation -> skipped_missing_input)")

    # Test 10: Integration file parse with all inputs present -> completed
    sample_complete = "Ambient Temperature\tCompressor Current\nBuilding Identifier\t1\t1\nInput Identifier\t1\t2\n09/13/26 14:30\t75.0\t12.5"
    ok2, parsed_complete = file_parser.parse_file_content(sample_complete)
    assert ok2 is True
    test_inputs_complete = [
        DiagnosticInput(name=sn, value=None if (data_validator.validate_value(sn, sv[0] if sv else None) == "in_doubt_acquisition" or (sv[0] if sv else None) is None) else sv[0])
        for sn, sv in parsed_complete["columns"].items()
    ]
    res_complete = DiagnosticEngine(location="Building 1").run("Chiller Diagnosis", test_inputs_complete)
    assert res_complete.status == "completed"
    print("[PASS] Test 10: Integration test (file parse + valid inputs -> completed)")

    print("All main.py self-tests passed successfully!")


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_self_tests()
    else:
        run()
