"DFA for the supported file extensions."

ALPHABET = {".", "p", "d", "f", "o", "c", "x", "t", "j", "g", "n", "m", "3", "4", "z", "i"}
START_STATE = "q0"
TRAP_STATE = "q_trap"
ACCEPTING_STATES = {"q_accept"}

# Each state maps an input character to the next state; missing paths reject.
DFA = {
    "q0": {".": "q1"},
    "q1": {"p": "q_p", "d": "q_d", "t": "q_t", "j": "q_j", "m": "q_m", "z": "q_z"},
    "q_p": {"d": "q_pd", "n": "q_pn"},
    "q_pd": {"f": "q_accept"},
    "q_pn": {"g": "q_accept"},
    "q_d": {"o": "q_do"},
    "q_do": {"c": "q_doc"},
    "q_doc": {"x": "q_accept"},
    "q_t": {"x": "q_tx"},
    "q_tx": {"t": "q_accept"},
    "q_j": {"p": "q_jp"},
    "q_jp": {"g": "q_accept"},
    "q_m": {"p": "q_mp"},
    "q_mp": {"3": "q_accept", "4": "q_accept"},
    "q_z": {"i": "q_zi"},
    "q_zi": {"p": "q_accept"},
}


def process_string(value: str) -> tuple[bool, list[str], str]:
    """Read characters and return the result, steps, and final state."""
    state = START_STATE
    trace = [f"Start at {state}"]
    for index, char in enumerate(value, start=1):
        next_state = DFA.get(state, {}).get(char, TRAP_STATE)
        if char not in ALPHABET:
            trace.append(f"Step {index}: '{char}' is outside the alphabet; {state} -> {TRAP_STATE}")
        else:
            trace.append(f"Step {index}: read '{char}'; {state} -> {next_state}")
        state = next_state
        if state == TRAP_STATE:
            trace.append("Entered the trap state.")
            break
    accepted = state in ACCEPTING_STATES
    trace.extend([f"Final state: {state}", f"Result: {'ACCEPTED' if accepted else 'REJECTED'}"])
    return accepted, trace, state


def process_extension(extension: str) -> tuple[bool, list[str], str]:
    """Check an extension exactly as written, including its dot and letter case."""
    return process_string(extension)
