"""
utils/helpers.py — Utility functions for Microscope Calculator
"""
import os
import csv
import io
from datetime import datetime


def save_uploaded_image(uploaded_file, upload_dir: str) -> str:
    """Save an uploaded Streamlit file object to disk and return the filename."""
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filename


def records_to_csv(records: list[dict]) -> str:
    """Convert a list of record dicts to a CSV string."""
    if not records:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def validate_username(username: str) -> tuple[bool, str]:
    """Return (is_valid, error_message)."""
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 2:
        return False, "Username must be at least 2 characters."
    if len(username) > 50:
        return False, "Username must be 50 characters or fewer."
    return True, ""


def validate_measured_size(value) -> tuple[bool, str]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, "Measured size must be a number."
    if v <= 0:
        return False, "Measured size must be greater than zero."
    return True, ""
