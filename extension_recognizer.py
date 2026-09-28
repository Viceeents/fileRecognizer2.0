"""Connect filename extension extraction to the DFA."""

from automata import process_extension
from file_reader import get_extension, get_file_metadata, get_file_name


def recognize_file(file_path: str) -> dict:
    name = get_file_name(file_path)
    extension = get_extension(file_path)
    metadata = get_file_metadata(file_path)
    accepted, trace, final_state = process_extension(extension)
    return {
        "name": name,
        "extension": extension or "(none)",
        "accepted": accepted,
        "trace": trace,
        "final_state": final_state,
        "metadata": metadata,
    }
