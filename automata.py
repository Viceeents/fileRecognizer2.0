"""DFA for the supported file extensions."""

# These are exactly the symbols used by the accepted extension strings.
ALPHABET = {".", "p", "d", "f", "o", "c", "x", "t", "j", "g", "n", "m", "3", "4", "z", "i"}
START_STATE = "q0"
TRAP_STATE = "q_trap"
ACCEPTING_STATES = {"q_pdf", "q_docx", "q_txt", "q_jpg", "q_png", "q_mp3", "q_mp4", "q_zip"}

# Unlisted transitions go to q_trap. q_trap loops to itself.
DFA = {
    "q0": {".": "q1"},
    "q1": {"p": "q_p", "d": "q_d", "t": "q_t", "j": "q_j", "m": "q_m", "z": "q_z"},
    # .pdf and .png share the .p prefix.
    "q_p": {"d": "q_pd", "n": "q_pn"},
    "q_pd": {"f": "q_pdf"},
    "q_pn": {"g": "q_png"},
    # .docx
    "q_d": {"o": "q_do"},
    "q_do": {"c": "q_doc"},
    "q_doc": {"x": "q_docx"},
    # .txt
    "q_t": {"x": "q_tx"},
    "q_tx": {"t": "q_txt"},
    # .jpg
    "q_j": {"p": "q_jp"},
    "q_jp": {"g": "q_jpg"},
    # .mp3 and .mp4 share the .mp prefix.
    "q_m": {"p": "q_mp"},
    "q_mp": {"3": "q_mp3", "4": "q_mp4"},
    # .zip
    "q_z": {"i": "q_zi"},
    "q_zi": {"p": "q_zip"},
}


def process_extension(extension: str) -> tuple[bool, list[str], str]:
    """Run the DFA and return (accepted, trace, final_state)."""
    state = START_STATE
    trace = [f"Start at {state}"]

    for index, char in enumerate(extension, start=1):
        next_state = DFA.get(state, {}).get(char, TRAP_STATE)
        if char not in ALPHABET:
            trace.append(
                f"Step {index}: '{char}' is outside the alphabet; {state} -> {TRAP_STATE}"
            )
        else:
            trace.append(f"Step {index}: read '{char}'; {state} -> {next_state}")
        state = next_state
        if state == TRAP_STATE:
            trace.append("Entered the trap state.")
            break

    accepted = state in ACCEPTING_STATES
    trace.append(f"Final state: {state}")
    trace.append(f"Verdict: {'ACCEPTED' if accepted else 'REJECTED'}")
    return accepted, trace, state
