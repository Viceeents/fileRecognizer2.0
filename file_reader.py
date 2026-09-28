"""Filename handling for dropped or selected files.

This project recognizes the filename extension; it does not inspect file bytes.
"""

from pathlib import Path
from datetime import datetime
import mimetypes
import os


def get_file_name(file_path: str) -> str:
    return Path(file_path).name


def get_extension(file_path: str) -> str:
    """Return the final suffix as written, including its leading dot."""
    return Path(file_path).suffix


def get_file_metadata(file_path: str) -> dict:
    """Read basic filesystem metadata for the selected file."""
    path = Path(file_path)
    stat = path.stat()
    created_timestamp = getattr(stat, "st_birthtime", stat.st_ctime)
    created_label = "Created" if os.name == "nt" or hasattr(stat, "st_birthtime") else "Metadata changed"
    mime_type, _ = mimetypes.guess_type(path.name)
    return {
        "size_bytes": stat.st_size,
        "mime_type": mime_type or "Unknown (extension-based guess)",
        "created_label": created_label,
        "created": datetime.fromtimestamp(created_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }
