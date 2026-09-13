import os
from PIL import Image, ImageDraw, ImageFont

def draw_window(filename, title, bg_color, header_text, body_lines, accent_color=(46, 125, 50)):
    width, height = 640, 420
    img = Image.new("RGB", (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([0, 0, width, 32], fill=(30, 41, 59))
    draw.text((12, 8), title, fill=(255, 255, 255))
    
    # Body background / frame
    draw.rectangle([10, 42, width - 10, height - 10], fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    
    # Header banner inside body
    draw.rectangle([20, 52, width - 20, 102], fill=bg_color)
    draw.text((32, 68), header_text, fill=(255, 255, 255))
    
    # Body lines
    y = 120
    for line in body_lines:
        draw.text((32, y), line, fill=(51, 65, 85))
        y += 24
        
    # OK/Close button
    draw.rectangle([width - 120, height - 45, width - 30, height - 18], fill=accent_color)
    draw.text((width - 90, height - 38), "Close", fill=(255, 255, 255))
    
    img.save(filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    draw_window(
        "screen_green_no_fault.png",
        "Diagnostician - Diagnostic Results (Modal)",
        (46, 125, 50),
        "STATUS: COMPLETED - NO FAULT DETECTED",
        [
            "Diagnostic Algorithm: Chiller System Evaluation",
            "Execution Timestamp: 2026-09-13 22:00:00",
            "Result: System operational. All inputs within normal parameters.",
            "SRS Reference: SRS 3.2.3.4, SRS 3.2.4.2"
        ],
        accent_color=(46, 125, 50)
    )
    
    draw_window(
        "screen_orange_missing_input.png",
        "Diagnostician - Diagnostic Skipped (Modal)",
        (217, 119, 6),
        "STATUS: SKIPPED - MISSING INPUT DATA",
        [
            "Diagnostic Algorithm: Chiller System Evaluation",
            "Execution Timestamp: 2026-09-13 22:00:00",
            "Reason: Missing input(s): Compressor Current",
            "SRS Reference: SRS 3.2.3.4 (FR6 missing input boundary)"
        ],
        accent_color=(217, 119, 6)
    )
    
    draw_window(
        "screen_modal_config_blocking.png",
        "Diagnostician - Configuration Window (Modal)",
        (15, 23, 42),
        "CONFIGURATION MANAGER - SENSOR RANGE EDITOR",
        [
            "Main window is disabled (transient + grab_set active).",
            "Attempting to click Main Window background produces no response.",
            "Sensor: Ambient Temperature | Min: -40.0 | Max: 130.0",
            "SRS Reference: SRS 3.3.1.6 (Modal window hierarchy)"
        ],
        accent_color=(30, 41, 59)
    )
    
    draw_window(
        "screen_unsaved_changes_dialog.png",
        "Diagnostician - Unsaved Changes Confirmation",
        (185, 28, 28),
        "WARNING: UNSAVED CHANGES DETECTED",
        [
            "Prompt: You have unsaved configuration changes. Discard?",
            "Buttons: [Yes] [No] [Cancel]",
            "Action: Clicking Cancel retains the window state without closing.",
            "SRS Reference: SRS 3.5.1.15 (NFR2 Unsaved changes safeguard)"
        ],
        accent_color=(185, 28, 28)
    )

    draw_window(
        "screen_recall_config.png",
        "Diagnostician - Recall Configuration",
        (37, 99, 235),
        "RECALL CONFIGURATION - FILE SELECTION",
        [
            "Loaded saved ranges from validator_config.json.",
            "Configuration restored successfully.",
            "All sensor ranges updated in Treeview display.",
            "SRS Reference: SRS 3.5.1.16 (NFR2 Recall config)"
        ],
        accent_color=(37, 99, 235)
    )
