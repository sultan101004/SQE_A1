"""
Module: error_logger.py
SRS References:
  - SRS 3.4.1: Significant errors logged to permanent storage; selected errors reported to user (NFR1).
  - SRS 3.4.1.1: Logged errors include: (a) time, (b) module name, (c) function name, (d) description.

Design Decisions & Category B Assumptions:
  # ASSUMPTION (A-031): data/errors.log plain text log file format.
  # ASSUMPTION (A-032): "Significant error" determination delegated to caller.
  # ASSUMPTION (A-033): report_to_user delegates to optional user_callback function (no GUI dependency).
"""

from datetime import datetime
import os

ERROR_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "errors.log")


def get_log_path() -> str:
    """Returns absolute path to errors log file. SRS Reference: SRS 3.4.1"""
    return ERROR_LOG_PATH


def init_error_log(overwrite: bool = False) -> None:
    """Ensures error log directory and file exist. SRS Reference: SRS 3.4.1 (A-031)"""
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    if overwrite or not os.path.exists(ERROR_LOG_PATH):
        with open(ERROR_LOG_PATH, "w", encoding="utf-8") as fh:
            fh.write("")


def log_error(module_name: str, function_name: str, description: str, report_to_user: bool = False, user_callback=None) -> None:
    """
    Logs software error with time, module, function, and description (SRS 3.4.1.1).
    SRS Reference: SRS 3.4.1, SRS 3.4.1.1 (A-031, A-032, A-033)
    """
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | module={module_name} | function={function_name} | description={description}\n"
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(log_entry)

    if report_to_user and user_callback is not None:
        user_callback(description)


def run_self_tests() -> None:
    """Runs 4 non-GUI self-tests validating error logging functionality. SRS Reference: SRS 3.4.1.1"""
    print("--- Running error_logger.py self-tests ---")
    init_error_log(overwrite=True)

    # Test 1: log_error creates file if missing
    log_error("auth", "attempt_login", "Failed login attempt")
    assert os.path.exists(ERROR_LOG_PATH)
    print("[PASS] Test 1: log_error creates data/errors.log file")

    # Test 2: Log line contains all 4 required fields (SRS 3.4.1.1 a-d)
    with open(ERROR_LOG_PATH, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    assert len(lines) == 1
    line = lines[0]
    assert "module=auth" in line and "function=attempt_login" in line and "description=Failed login attempt" in line
    assert line[:4].isdigit()  # Timestamp YYYY
    print("[PASS] Test 2: Log line contains all 4 required fields (time, module, function, description)")

    # Test 3: Two calls -> two lines
    log_error("file_parser", "parse_file", "File missing header")
    with open(ERROR_LOG_PATH, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    assert len(lines) == 2
    print("[PASS] Test 3: Two log calls result in two lines in error log")

    # Test 4: report_to_user=True with a mock callback invokes it
    reported_messages = []
    mock_cb = lambda msg: reported_messages.append(msg)
    log_error("main", "on_start_diagnostics", "Hardware disconnect", report_to_user=True, user_callback=mock_cb)
    assert len(reported_messages) == 1 and reported_messages[0] == "Hardware disconnect"
    print("[PASS] Test 4: report_to_user=True correctly invokes user_callback")

    print("All error_logger.py self-tests passed successfully!")


if __name__ == "__main__":
    run_self_tests()
