




"Connect filename extension extraction to the DFA."

from automata import process_extension
from file_reader import get_extension, get_file_metadata, get_file_name


FULL_FILE_NAMES = {
    ".pdf": "Portable Document Format (PDF)",
    ".docx": "Office Open XML Document (DOCX)",
    ".txt": "Plain Text File (TXT)",
    ".jpg": "Joint Photographic Experts Group Image (JPG)",
    ".png": "Portable Network Graphics (PNG)",
    ".mp3": "MPEG Audio Layer III (MP3)",
    ".mp4": "MPEG-4 Part 14 (MP4)",
    ".zip": "ZIP Archive (ZIP)",
}


def recognize_file(file_path: str) -> dict:
    """Combine file details and extension-check results for the interface."""
    name = get_file_name(file_path)
    extension = get_extension(file_path)
    metadata = get_file_metadata(file_path)
    accepted, trace, final_state = process_extension(extension)
    return {
        "name": name,
        "extension": extension or "(none)",
        "accepted": accepted,
        "full_file_name": FULL_FILE_NAMES.get(extension) if accepted else None,
        "trace": trace,
        "final_state": final_state,
        "metadata": metadata,
    }
