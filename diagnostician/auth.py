"""
Module: auth.py
SRS References:
  - SRS 3.1.5.2.7: Authenticate User (login attempt, success/failure indication, 3 attempt lock).
  - SRS 3.1.1.2.1 (Step 10): Logout returns privileges to general user.
  - SRS 3.1.1.2.1 (Step 11): 15-minute inactivity timeout reverts privileges to general user.
  - SRS 3.2.1.1: General user vs administrator privilege levels.
  - SRS 3.6: User type determination via identifier and password.

Design Decisions & Category B Assumptions (Traceability to AI_ASSUMPTIONS.md):
  # ASSUMPTION (A-001): Role names are defined as constants 'administrator' and 'general_user' (SRS 3.2.1.1).
  # ASSUMPTION (A-002): Credentials stored in users.json in project root (SRS 3.6).
  # ASSUMPTION (A-003): Password hashing uses unsalted SHA-256 for prototype (SRS 3.6).
  # ASSUMPTION (A-004): load_users() raises FileNotFoundError when users.json missing to prevent backdoor credential reset (SRS 3.6).
  # ASSUMPTION (A-005): Three authentication attempts permitted before window dismissal (SRS 3.1.5.2.7 s5).
  # ASSUMPTION (A-006): 15-minute inactivity timeout downgrades admin role to general user (SRS 3.1.1.2.1 s11).
  # ASSUMPTION (A-007): Timeout retains current_username; only role is downgraded (SRS 3.1.1.2.1 s11).
  # ASSUMPTION (A-008): failed_attempts counter is reset on logout/reset_attempts to grant 3 fresh attempts (SRS 3.1.5.2.7 s5).
"""

import hashlib
import json
import os
import time

import error_logger


MAX_ATTEMPTS = 3
SESSION_TIMEOUT_SECONDS = 15 * 60
ROLE_ADMIN = "administrator"
ROLE_GENERAL = "general_user"

USERS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def hash_password(password: str) -> str:
    """
    Computes SHA-256 hex digest of UTF-8 encoded password string.
    SRS Reference: SRS 3.6
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_users_file(overwrite: bool = False) -> None:
    """
    Explicitly initializes users.json with default seed accounts.
    Design Decision (A-002, A-004): Explicit initializer prevents silent password resets.
    """
    if os.path.exists(USERS_FILE_PATH) and not overwrite:
        return

    default_users = {
        "admin": {"password_hash": hash_password("admin123"), "role": ROLE_ADMIN},
        "user1": {"password_hash": hash_password("password1"), "role": ROLE_GENERAL}
    }
    save_users(default_users)


def load_users() -> dict:
    """
    Loads user database from users.json.
    Design Decision (A-002, A-004): Stored in users.json; raises FileNotFoundError if missing.
    """
    if not os.path.exists(USERS_FILE_PATH):
        raise FileNotFoundError(f"User database file not found: {USERS_FILE_PATH}")

    with open(USERS_FILE_PATH, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_users(users: dict) -> None:
    """
    Saves user database dictionary to users.json.
    Design Decision (A-002): Stored in users.json in project root.
    """
    with open(USERS_FILE_PATH, "w", encoding="utf-8") as file_handle:
        json.dump(users, file_handle, indent=4)


def authenticate(username: str, password: str) -> tuple[bool, str | None]:
    """
    Authenticates username and password against stored user credentials.
    SRS Reference: SRS 3.1.5.2.7, SRS 3.6
    """
    users = load_users()
    if username in users:
        if users[username].get("password_hash") == hash_password(password):
            return True, users[username].get("role")
    return False, None


def is_admin(role: str) -> bool:
    """Checks if role corresponds to administrator privileges. SRS Reference: SRS 3.2.1.1 (A-001)"""
    return role == ROLE_ADMIN


def is_general_user(role: str) -> bool:
    """Checks if role corresponds to general user privileges. SRS Reference: SRS 3.2.1.1 (A-001)"""
    return role == ROLE_GENERAL


class AuthenticationSession:
    """
    Manages user session, login attempt count, privilege level, and session timeouts.
    SRS Reference: SRS 3.1.5.2.7, SRS 3.1.1.2.1, SRS 3.2.1.1
    """

    def __init__(self) -> None:
        """Initializes default unauthenticated session with general user privileges (A-001, A-007)."""
        self.current_username: str | None = None
        self.current_role: str = ROLE_GENERAL
        self.failed_attempts: int = 0
        self.last_activity_time: float | None = None

    def attempt_login(self, username: str, password: str) -> tuple[str, str | None]:
        """
        Attempts user authentication and tracks failed attempt counts up to MAX_ATTEMPTS.
        SRS Reference: SRS 3.1.5.2.7 (Steps 1-5) (A-005)
        """
        if self.failed_attempts >= MAX_ATTEMPTS:
            error_logger.log_error("auth.py", "attempt_login", "Authentication locked out after 3 failed attempts")
            return "locked_out", None

        success, role = authenticate(username, password)
        if success and role is not None:
            self.failed_attempts = 0
            self.current_username = username
            self.current_role = role
            self.last_activity_time = time.time()
            return "success", role

        self.failed_attempts += 1
        if self.failed_attempts >= MAX_ATTEMPTS:
            error_logger.log_error("auth.py", "attempt_login", "Authentication locked out after 3 failed attempts")
            return "locked_out", None
        return "failure", None


    def reset_attempts(self) -> None:
        """Resets failed login attempt counter. SRS Reference: SRS 3.1.5.2.7 Step 5 (A-005, A-008)"""
        self.failed_attempts = 0

    def logout(self) -> None:
        """
        Logs out current user, reverts privileges to general user, and resets failed attempts.
        SRS Reference: SRS 3.1.1.2.1 (Step 10), SRS 3.1.5.2.7 (Step 5) (A-008)
        """
        self.current_username = None
        self.current_role = ROLE_GENERAL
        self.failed_attempts = 0
        self.last_activity_time = None

    def touch(self) -> None:
        """Updates last activity timestamp if user is authenticated. SRS Reference: SRS 3.1.1.2.1 (Step 11)"""
        if self.current_username is not None:
            self.last_activity_time = time.time()

    def check_timeout(self) -> bool:
        """
        Reverts privileges to general user if inactivity exceeds timeout. Retains username.
        SRS Reference: SRS 3.1.1.2.1 (Step 11) (A-006, A-007)
        """
        if self.last_activity_time is None or self.current_role == ROLE_GENERAL:
            return False

        if (time.time() - self.last_activity_time) >= SESSION_TIMEOUT_SECONDS:
            self.current_role = ROLE_GENERAL
            return True
        return False


if __name__ == "__main__":
    print("--- Running updated auth.py self-tests ---")

    # Verify missing users.json raises FileNotFoundError (A-004)
    if os.path.exists(USERS_FILE_PATH):
        os.remove(USERS_FILE_PATH)

    try:
        load_users()
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("[PASS] Test 0: Missing users.json raises FileNotFoundError (A-004)")

    init_users_file(overwrite=True)
    session = AuthenticationSession()

    # Test 1: Valid admin login (A-001)
    status, role = session.attempt_login("admin", "admin123")
    assert status == "success" and role == ROLE_ADMIN, f"Test 1 failed: {status}, {role}"
    print("[PASS] Test 1: Valid admin login")

    # Test 2: Valid general user login (A-001)
    session.logout()
    status, role = session.attempt_login("user1", "password1")
    assert status == "success" and role == ROLE_GENERAL, f"Test 2 failed: {status}, {role}"
    print("[PASS] Test 2: Valid general user login")

    # Test 3: Wrong password
    session.logout()
    status, role = session.attempt_login("user1", "wrongpass")
    assert status == "failure" and role is None, f"Test 3 failed: {status}, {role}"
    print("[PASS] Test 3: Wrong password")

    # Test 4: Unknown username
    session.logout()
    status, role = session.attempt_login("unknown_user", "password1")
    assert status == "failure" and role is None, f"Test 4 failed: {status}, {role}"
    print("[PASS] Test 4: Unknown username")

    # Test 5: Three failed attempts -> locked_out (A-005)
    session.reset_attempts()
    session.attempt_login("admin", "bad1")
    session.attempt_login("admin", "bad2")
    status, role = session.attempt_login("admin", "bad3")
    assert status == "locked_out" and role is None, f"Test 5 failed: {status}, {role}"
    print("[PASS] Test 5: Three failed attempts -> locked_out")

    # Test 6: logout() resets failed_attempts state (A-008)
    session.logout()
    assert session.failed_attempts == 0
    status, role = session.attempt_login("admin", "admin123")
    assert status == "success"
    print("[PASS] Test 6: logout() resets failed_attempts state")

    # Test 7: check_timeout() reverts role to ROLE_GENERAL but keeps current_username (A-006, A-007)
    session.last_activity_time = time.time() - (SESSION_TIMEOUT_SECONDS + 1)
    timed_out = session.check_timeout()
    assert timed_out is True
    assert session.current_role == ROLE_GENERAL
    assert session.current_username == "admin"
    print("[PASS] Test 7: check_timeout() downgrades role to general user while keeping username")

    # Test 8: Pre-login timeout check returns False (A-007)
    session.logout()
    assert session.last_activity_time is None
    assert session.check_timeout() is False
    print("[PASS] Test 8: Pre-login session does not timeout")

    # Test 9: is_admin and is_general_user helpers (A-001)
    assert is_admin(ROLE_ADMIN) is True and is_admin(ROLE_GENERAL) is False
    assert is_general_user(ROLE_GENERAL) is True and is_general_user(ROLE_ADMIN) is False
    print("[PASS] Test 9: Role helper functions")

    print("All auth.py self-tests passed successfully!")
