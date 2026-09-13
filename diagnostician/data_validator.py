"""
Module: data_validator.py
SRS References:
  - SRS 3.2.2.3: Sensed data in doubt if acquisition fails OR value outside possible range.
  - SRS 3.2.2.4: Missing data threshold tracking for N consecutive acquisition failures (Table 4).
  - SRS 3.2.2.8: Range validation against Table 5 defaults.
  - SRS 3.2.2.9: Administrator modification of expected ranges and thresholds.

Design Decisions & Category B Assumptions (Traceability to AI_ASSUMPTIONS.md):
  # ASSUMPTION (A-013): Configuration stored in validator_config.json in project root.
  # ASSUMPTION (A-014): Compressor Current upper bound is None (no upper limit per Table 5 NA).
  # ASSUMPTION (A-015): set_range / set_threshold check requesting_role == ROLE_ADMIN.
  # ASSUMPTION (A-016): Inclusive range comparison (min_val <= val <= max_val).
  # ASSUMPTION (A-017): Unknown sensor types without configured range return 'in_doubt_range'.
"""

import json
import os
import error_logger


ROLE_ADMIN = "administrator"
ROLE_GENERAL = "general_user"

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validator_config.json")

DEFAULT_RANGES = {
    "Ambient Temperature": [-40.0, 130.0],
    "Ambient wet-bulb": [-40.0, 100.0],
    "Chilled Water Supply Temperature": [30.0, 80.0],
    "CT Sump Temperature": [32.0, 130.0],
    "CT Inlet Temperature": [35.0, 130.0],
    "Compressor Current": [0.0, None],
    "Condenser Pump Current": [0.0, 200.0],
    "Chilled Water Pump Current": [0.0, 200.0],
    "Secondary CHW Pump(s) Current": [0.0, 200.0],
    "CT Fan(s) Current": [0.0, 200.0],
    "Condenser Fan(s) Current": [0.0, 200.0],
    "Supply Fan(s) Current": [0.0, 1000.0]
}

DEFAULT_THRESHOLDS = {
    "Temperature": 3,
    "Current": 3,
    "Switch": 3
}


def init_config(overwrite: bool = False) -> None:
    """
    Initializes validator_config.json with Table 4 and Table 5 defaults.
    SRS Reference: SRS 3.2.2.4, SRS 3.2.2.8 (A-013)
    """
    if os.path.exists(CONFIG_FILE_PATH) and not overwrite:
        return
    config_data = {
        "ranges": DEFAULT_RANGES,
        "thresholds": DEFAULT_THRESHOLDS
    }
    save_config(config_data)


def load_config() -> dict:
    """
    Loads configuration dictionary from validator_config.json.
    Design Decision (A-013): Configuration stored in validator_config.json.
    """
    if not os.path.exists(CONFIG_FILE_PATH):
        init_config()
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_config(config: dict) -> None:
    """
    Saves configuration dictionary to validator_config.json.
    Design Decision (A-013): Configuration stored in validator_config.json.
    """
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file_handle:
        json.dump(config, file_handle, indent=4)


def validate_value(sensor_type: str, value: float | None) -> str:
    """
    Validates a sensed data value against SRS 3.2.2.8 ranges and missing status.
    SRS Reference: SRS 3.2.2.3, SRS 3.2.2.8 (A-014, A-016, A-017)
    """
    if value is None:
        return "in_doubt_acquisition"

    config = load_config()
    ranges = config.get("ranges", {})
    if sensor_type not in ranges:
        return "in_doubt_range"  # ASSUMPTION (A-017): Unknown sensor type returns in_doubt_range

    min_val, max_val = ranges[sensor_type]
    if min_val is not None and value < min_val:
        return "in_doubt_range"
    if max_val is not None and value > max_val:
        return "in_doubt_range"
    return "accurately_acquired"


def check_missing_threshold(sensor_type: str, consecutive_failures: int) -> bool:
    """
    Checks if consecutive acquisition failures reached threshold N for sensor type.
    SRS Reference: SRS 3.2.2.4
    """
    config = load_config()
    thresholds = config.get("thresholds", {})
    threshold = thresholds.get(sensor_type, 3)
    return consecutive_failures >= threshold


def set_range(sensor_type: str, min_val: float, max_val: float | None, requesting_role: str) -> tuple[bool, str]:
    """
    Modifies expected value range for a sensor type if requesting user is administrator.
    SRS Reference: SRS 3.2.2.9 (A-015)
    """
    if requesting_role != ROLE_ADMIN:
        error_logger.log_error("data_validator.py", "set_range", f"Unauthorized attempt by role '{requesting_role}'")
        return False, "unauthorized"

    config = load_config()
    config.setdefault("ranges", {})[sensor_type] = [min_val, max_val]
    save_config(config)
    return True, "ok"


def set_threshold(sensor_type: str, new_threshold: int, requesting_role: str) -> tuple[bool, str]:
    """
    Modifies missing data consecutive failure threshold N if requesting user is administrator.
    SRS Reference: SRS 3.2.2.4, SRS 3.2.2.9 (A-015)
    """
    if requesting_role != ROLE_ADMIN:
        error_logger.log_error("data_validator.py", "set_threshold", f"Unauthorized attempt by role '{requesting_role}'")
        return False, "unauthorized"

    config = load_config()
    config.setdefault("thresholds", {})[sensor_type] = new_threshold
    save_config(config)
    return True, "ok"



if __name__ == "__main__":
    print("--- Running data_validator.py self-tests ---")
    init_config(overwrite=True)

    # Test 1: Lower boundary (A-016)
    assert validate_value("Ambient Temperature", -40) == "accurately_acquired"
    print("[PASS] Test 1: Lower boundary (-40)")

    # Test 2: Upper boundary (A-016)
    assert validate_value("Ambient Temperature", 130) == "accurately_acquired"
    print("[PASS] Test 2: Upper boundary (130)")

    # Test 3: Just below lower boundary
    assert validate_value("Ambient Temperature", -40.1) == "in_doubt_range"
    print("[PASS] Test 3: Just outside lower boundary (-40.1)")

    # Test 4: Just above upper boundary
    assert validate_value("Ambient Temperature", 130.1) == "in_doubt_range"
    print("[PASS] Test 4: Just outside upper boundary (130.1)")

    # Test 5: Missing value
    assert validate_value("Ambient Temperature", None) == "in_doubt_acquisition"
    print("[PASS] Test 5: Missing value (None)")

    # Test 6: Condenser Pump Current lower boundary
    assert validate_value("Condenser Pump Current", 0) == "accurately_acquired"
    print("[PASS] Test 6: Condenser Pump Current lower boundary (0)")

    # Test 7: Below threshold
    assert check_missing_threshold("Temperature", 2) is False
    print("[PASS] Test 7: Consecutive failures below threshold (2 < 3)")

    # Test 8: At threshold
    assert check_missing_threshold("Temperature", 3) is True
    print("[PASS] Test 8: Consecutive failures at threshold (3 == 3)")

    # Test 9: Above threshold
    assert check_missing_threshold("Temperature", 4) is True
    print("[PASS] Test 9: Consecutive failures above threshold (4 > 3)")

    # Test 10: Admin sets threshold successfully (A-015)
    status, msg = set_threshold("Temperature", 5, ROLE_ADMIN)
    assert status is True and msg == "ok"
    assert check_missing_threshold("Temperature", 4) is False
    assert check_missing_threshold("Temperature", 5) is True
    print("[PASS] Test 10: Admin sets threshold (5) and persists")

    # Test 11: General user setting threshold rejected (A-015)
    status, msg = set_threshold("Temperature", 6, ROLE_GENERAL)
    assert status is False and msg == "unauthorized"
    print("[PASS] Test 11: General user setting threshold rejected")

    # Test 12: Admin sets range and validates new boundary (A-015)
    status, msg = set_range("Ambient Temperature", -50, 140, ROLE_ADMIN)
    assert status is True and msg == "ok"
    assert validate_value("Ambient Temperature", -45) == "accurately_acquired"
    print("[PASS] Test 12: Admin sets range (-50 to 140) and validates -45")

    # Test 13: Compressor Current has no upper bound (A-014)
    assert validate_value("Compressor Current", 99999) == "accurately_acquired"
    print("[PASS] Test 13: Compressor Current accepts high values")

    # Test 14: Compressor Current lower bound enforced (A-014)
    assert validate_value("Compressor Current", -1) == "in_doubt_range"
    print("[PASS] Test 14: Compressor Current rejects negative values")

    # Test 15: Unknown sensor type in doubt (A-017)
    assert validate_value("Unknown Sensor", 42) == "in_doubt_range"
    print("[PASS] Test 15: Unknown sensor type in_doubt_range")

    # Test 16: Threshold persistence round-trip (A-013)
    set_threshold("Current", 7, ROLE_ADMIN)
    assert load_config()["thresholds"]["Current"] == 7
    print("[PASS] Test 16: Threshold persists")

    # Test 17: Missing None for unknown sensor is in_doubt_acquisition
    assert validate_value("Unknown Sensor", None) == "in_doubt_acquisition"
    print("[PASS] Test 17: Unknown sensor + None = missing")

    print("All data_validator.py self-tests passed successfully!")
