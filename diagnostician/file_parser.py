"""
Module: file_parser.py
SRS Reference: SRS 3.2.2.2 — Electronic File Input (Batch Mode)

Design Decisions & Category B Assumptions (Traceability to AI_ASSUMPTIONS.md):
  # ASSUMPTION (A-009): Sensor names row appears ABOVE Building Identifier row per SRS Table 3 example layout.
  # ASSUMPTION (A-010): Timestamps are required to be strictly ascending (no duplicates). The SRS text says 'ascending order' which we interpret as strictly increasing. If non-decreasing was intended, this is a defect.
  # ASSUMPTION (A-011): Unparseable or blank numeric values become None (missing data placeholder) per SRS 3.2.2.6.
"""

import csv
from datetime import datetime
import error_logger


TIMESTAMP_FORMATS = (
    "%m/%d/%y %H:%M",
    "%m/%d/%Y %H:%M",
    "%m/%d/%y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M"
)


class ParseError(Exception):
    """Custom exception raised for file format and validation errors. SRS Reference: SRS 3.2.2.2"""
    pass


def parse_timestamp(timestamp_string: str) -> datetime:
    """Parses timestamp string against supported datetime formats. SRS Reference: SRS 3.2.2.2 (A-010)"""
    cleaned_timestamp = timestamp_string.strip()
    for datetime_format in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(cleaned_timestamp, datetime_format)
        except ValueError:
            continue
    raise ParseError(f"Invalid timestamp format: '{timestamp_string}'.")


def parse_file(file_path: str) -> tuple[bool, dict | str]:
    """Parses and validates an electronic sensed-data file from disk. SRS Reference: SRS 3.2.2.2"""
    try:
        with open(file_path, "r", encoding="ascii") as file_handle:
            content = file_handle.read()
        return parse_file_content(content)
    except UnicodeDecodeError:
        return False, "File contains non-ASCII characters."
    except Exception as error:
        return False, str(error)


def parse_file_content(content: str) -> tuple[bool, dict | str]:
    """Parses and validates sensed-data file content string. SRS Reference: SRS 3.2.2.2"""
    try:
        return True, _internal_parse(content)
    except ParseError as error:
        error_logger.log_error("file_parser.py", "parse_file_content", str(error))
        return False, str(error)



def _internal_parse(content: str) -> dict:
    """Internal parser enforcing strict SRS Table 3 header format, ASCII, and row alignment. SRS Reference: SRS 3.2.2.2 (A-009, A-010, A-011)"""
    if not content or not content.isascii():
        raise ParseError("File contains non-ASCII characters or is empty.")

    lines = content.splitlines()
    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]

    if len(non_comment_lines) < 4:
        raise ParseError("File must contain at least 3 header rows and 1 data row.")

    first_line = non_comment_lines[0]
    has_tab, has_comma = "\t" in first_line, "," in first_line
    if has_tab and has_comma:
        raise ParseError("Mixed delimiters found in file header.")
    elif has_tab:
        delimiter = "\t"
    elif has_comma:
        delimiter = ","
    else:
        raise ParseError("Invalid delimiter; file must be tab or comma delimited.")

    for idx, line in enumerate(non_comment_lines):
        if delimiter == "\t" and "," in line:
            raise ParseError(f"Mixed or inconsistent delimiter ',' on line {idx + 1}.")
        if delimiter == "," and "\t" in line:
            raise ParseError(f"Mixed or inconsistent delimiter '\\t' on line {idx + 1}.")

    rows = [row for row in csv.reader(non_comment_lines, delimiter=delimiter)]
    sensor_names_row, building_row, input_row = rows[0], rows[1], rows[2]

    if not building_row or building_row[0].strip() != "Building Identifier":
        raise ParseError("Missing required header: 'Building Identifier' must be second header row.")
    if not input_row or input_row[0].strip() != "Input Identifier":
        raise ParseError("Missing required header: 'Input Identifier' must be third header row.")

    sensor_names = [col.strip() for col in sensor_names_row]
    num_sensors = len(sensor_names)
    if num_sensors == 0 or any(name == "" for name in sensor_names):
        raise ParseError("Sensor column names missing or empty in header.")

    try:
        buildings = [int(val.strip()) for val in building_row[1:]]
        inputs = [int(val.strip()) for val in input_row[1:]]
    except ValueError:
        raise ParseError("Building and Input identifiers must be valid integers.")

    if len(buildings) != num_sensors or len(inputs) != num_sensors:
        raise ParseError("Header column count mismatch between sensor names, buildings, and inputs.")

    timestamps, columns = [], {name: [] for name in sensor_names}
    previous_datetime = None

    for row_index, row in enumerate(rows[3:], start=4):
        if len(row) != 1 + num_sensors:
            raise ParseError(f"Unequal column length on line {row_index}: expected {1 + num_sensors}, got {len(row)}.")

        raw_ts = row[0].strip()
        current_dt = parse_timestamp(raw_ts)
        if previous_datetime is not None and current_dt <= previous_datetime:
            raise ParseError(f"Timestamps not in ascending order on line {row_index}: '{raw_ts}'.")
        previous_datetime = current_dt
        timestamps.append(raw_ts)

        for c_idx, name in enumerate(sensor_names):
            val_str = row[c_idx + 1].strip()
            if val_str == "" or val_str.upper() in ("NONE", "NULL", "NAN"):
                val_float = None
            else:
                try:
                    val_float = float(val_str)
                except ValueError:
                    val_float = None
            columns[name].append(val_float)

    return {
        "batch_mode": True,
        "buildings": buildings,
        "inputs": inputs,
        "timestamps": timestamps,
        "columns": columns
    }


if __name__ == "__main__":
    print("--- Running file_parser.py self-tests (Exact SRS Table 3 Match) ---")

    # SRS Table 3 Example Test (Character-for-character match) (A-009)
    srs_table_3 = (
        "#Test Run\n"
        "#Sensor Name\n"
        "Temperature\tFlow\tPressure\n"
        "Building Identifier\t1\t1\t2\n"
        "Input Identifier\t1\t2\t3\n"
        "12/14/01 8:43\t12.4\t35.8\t407.3\n"
        "12/14/01 13:30\t5.4\t955.1\t971.0\n"
        "12/14/01 20:01\t123.5\t576.21\t491.4\n"
    )
    success, result = parse_file_content(srs_table_3)
    assert success is True, f"SRS Table 3 example rejected: {result}"
    assert result["buildings"] == [1, 1, 2], f"Buildings mismatch: {result['buildings']}"
    assert result["inputs"] == [1, 2, 3], f"Inputs mismatch: {result['inputs']}"
    assert result["columns"]["Temperature"] == [12.4, 5.4, 123.5], f"Temperature mismatch: {result['columns']['Temperature']}"
    assert result["columns"]["Flow"] == [35.8, 955.1, 576.21], f"Flow mismatch: {result['columns']['Flow']}"
    assert result["columns"]["Pressure"] == [407.3, 971.0, 491.4], f"Pressure mismatch: {result['columns']['Pressure']}"
    print("[PASS] SRS Table 3 exact character match test")

    # Test 1: Valid tab-delimited file
    tab_data = (
        "Temp\tFlow\tPressure\n"
        "Building Identifier\t1\t1\t2\n"
        "Input Identifier\t1\t2\t3\n"
        "12/14/01 08:43\t12.4\t35.8\t407.3\n"
        "12/14/01 08:44\t12.5\t35.9\t407.4\n"
    )
    success, result = parse_file_content(tab_data)
    assert success is True and result["batch_mode"] is True
    print("[PASS] Test 1: Valid tab-delimited file")

    # Test 2: Valid comma-delimited file
    csv_data = (
        "Temp,Flow,Pressure\n"
        "Building Identifier,1,1,2\n"
        "Input Identifier,1,2,3\n"
        "12/14/01 08:43,12.4,35.8,407.3\n"
        "12/14/01 08:44,12.5,35.9,407.4\n"
    )
    success, result = parse_file_content(csv_data)
    assert success is True and result["columns"]["Temp"] == [12.4, 12.5]
    print("[PASS] Test 2: Valid comma-delimited file")

    # Test 3: Missing header -> rejected
    missing_header = (
        "Building Identifier\t1\t1\t2\n"
        "Input Identifier\t1\t2\t3\n"
        "DummyHeader\tRow\tHere\n"
        "12/14/01 08:43\t12.4\t35.8\t407.3\n"
    )
    success, err = parse_file_content(missing_header)
    assert success is False and "Building Identifier" in err
    print("[PASS] Test 3: Missing header rejected")

    # Test 4: Header in wrong order -> rejected
    wrong_order = (
        "Temp\tFlow\tPressure\n"
        "Input Identifier\t1\t2\t3\n"
        "Building Identifier\t1\t1\t2\n"
        "12/14/01 08:43\t12.4\t35.8\t407.3\n"
    )
    success, err = parse_file_content(wrong_order)
    assert success is False and ("Building Identifier" in err or "Input Identifier" in err)
    print("[PASS] Test 4: Header in wrong order rejected")

    # Test 5: Comment rows ignored
    comment_data = (
        "# Top Comment\n"
        "Temperature\tFlow\n"
        "# Comment 2\n"
        "Building Identifier\t1\t1\n"
        "Input Identifier\t1\t2\n"
        "# Data Comment\n"
        "12/14/01 08:43\t12.4\t35.8\n"
    )
    success, result = parse_file_content(comment_data)
    assert success is True and len(result["timestamps"]) == 1
    print("[PASS] Test 5: Comment rows ignored")

    # Test 6: Timestamps not ascending -> rejected (A-010)
    descending_ts = (
        "Temp\tFlow\n"
        "Building Identifier\t1\t1\n"
        "Input Identifier\t1\t2\n"
        "12/14/01 08:44\t12.4\t35.8\n"
        "12/14/01 08:43\t12.5\t35.9\n"
    )
    success, err = parse_file_content(descending_ts)
    assert success is False and "ascending order" in err
    print("[PASS] Test 6: Non-ascending timestamps rejected")

    # Test 7: Unequal column lengths -> rejected
    unequal_cols = (
        "Temperature\tFlow\tPressure\n"
        "Building Identifier\t1\t1\t2\n"
        "Input Identifier\t1\t2\t3\n"
        "12/14/01 08:43\t12.4\t35.8\n"
    )
    success, err = parse_file_content(unequal_cols)
    assert success is False and "Unequal column length" in err
    print("[PASS] Test 7: Unequal column lengths rejected")

    # Test 8: Empty file -> rejected
    empty_data = "# Only comment lines\n"
    success, err = parse_file_content(empty_data)
    assert success is False and "at least 3 header rows" in err
    print("[PASS] Test 8: Empty file rejected")

    # Test 9: Non-ASCII content -> rejected
    non_ascii = (
        "Temp\tFlow\n"
        "Building Identifier\t1\t1\n"
        "12/14/01 08:43\t12.4°C\t35.8\n"
    )
    success, err = parse_file_content(non_ascii)
    assert success is False and ("non-ASCII" in err or "at least 3 header rows" in err)
    print("[PASS] Test 9: Non-ASCII content rejected")

    # Test 10: Mixed delimiters -> rejected
    mixed_delims = (
        "Temp,Flow\n"
        "Building Identifier\t1,1\n"
        "Input Identifier\t1,2\n"
        "12/14/01 08:43\t12.4,35.8\n"
    )
    success, err = parse_file_content(mixed_delims)
    assert success is False and "Mixed" in err
    print("[PASS] Test 10: Mixed delimiters rejected")

    print("All file_parser.py self-tests passed successfully!")
