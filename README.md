# RECOGNIZER — File Extension Pattern System

RECOGNIZER demonstrates a formal-language recognizer for filename extensions. It also provides a Tkinter simulator where a user can enter one or many strings and see symbol-by-symbol DFA transitions. The file picker reports file metadata and runs the same recognizer on the selected file's final suffix.

## Requirements

- Python 3.9 or newer
- Tkinter (usually included with the standard Python installation)
- `tkinterdnd2` for optional drag-and-drop support; the file picker and extension-string simulator work without it

## Installation guide

1. Download or clone the project, then open a terminal in the `file-extension-recognizer` folder:

   ```powershell
   cd file-extension-recognizer
   ```

2. Optionally create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

   Activate it in Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install the dependency listed in `requirements.txt` to enable drag and drop:

   ```powershell
   python -m pip install -r requirements.txt
   ```

   Skip this step if you only need the file picker and extension-string simulator.

4. Verify that Tkinter is available:

   ```powershell
   python -m tkinter
   ```

   This should open a small test window. If Tkinter is missing, install Python's Tcl/Tk component on Windows or the Tkinter package provided by your Linux distribution. On systems where Python is invoked as `python3`, use `python3` in these commands.

## Run

From the `file-extension-recognizer` folder, run:

```powershell
python main.py
```

Choose a file, drag and drop files when the optional dependency is installed, or select **Test extensions** to enter extension strings. Use **Show technical steps (DFA)** to inspect the state transitions and final state.

## Problem definition and scope

The system decides whether a filename extension belongs to a fixed supported set. Users include people checking whether a file uses one of the application's supported extension labels. Input to the automaton is a string; a valid input is exactly one supported lowercase extension including its initial dot. Missing dots, uppercase letters, incomplete extensions, extra characters, and unsupported extensions are rejected. This is a finite automata problem because membership depends on a finite set of prefixes and exact endings; the machine needs no unbounded memory.

The file picker checks only the filename suffix. It does not inspect file bytes, and its MIME type is a guess based on the extension. RECOGNIZER is the group's file-extension pattern-recognition project: recognizing file names is useful because uploading, storing, and working with digital files depends on identifying their formats and intended uses.

## 3. Scope and Limitations

### Scope

RECOGNIZER checks whether a filename extension belongs to the project's accepted language. It supports the following eight extensions:

- `.pdf`
- `.docx`
- `.txt`
- `.jpg`
- `.png`
- `.mp3`
- `.mp4`
- `.zip`

Users can select files, drag and drop files when drag-and-drop support is installed, or enter extension strings directly. The program checks each extension using a DFA and displays ACCEPTED or REJECTED. It supports multiple test cases and can show processing steps and the final state. For selected files, it also displays basic file metadata.

### Limitations

- Recognition is limited to the eight extensions defined in the project; other extensions are rejected.
- Inputs must match exactly, including the leading dot and lowercase letters. Uppercase extensions, spaces, incomplete extensions, and extra characters are rejected.
- For selected files, only the final filename suffix is checked. For example, `report.pdf.exe` is checked as `.exe`.
- The system does not inspect file contents or verify that a file's actual format matches its extension. Renaming a file can therefore change its recognition result.
- The displayed file type is an extension-based guess, not a verified identification of the file's contents.
- The system does not perform security checks, malware detection, or file-integrity validation. ACCEPTED means only that the extension matches the supported language.
- Drag and drop requires the optional `tkinterdnd2` dependency; file selection and extension-string testing remain available without it.

## Formal language

Let the alphabet be `Σ = { ., p, d, f, o, c, x, t, j, g, n, m, 3, 4, z, i }`.
Strings are finite sequences over `Σ` (`Σ*`). The language is:

`L = { .pdf, .docx, .txt, .jpg, .png, .mp3, .mp4, .zip }`.

Accepted examples (8): `.pdf`, `.docx`, `.txt`, `.jpg`, `.png`, `.mp3`, `.mp4`, `.zip`.

Rejected examples (10): `pdf` (missing dot), `.doc` (incomplete), `.exe` (unsupported), `.pdfx` (extra character), `.mp5` (unsupported digit), `.txt.txt` (extra suffix), `.` (incomplete), `.mp` (incomplete), `..pdf` (bad prefix), `.DOCX` (uppercase).

## Regular expression

```regex
^\.(pdf|docx|txt|jpg|png|mp3|mp4|zip)$
```

`^` and `$` require the entire string to match; `\.` is a literal dot; parentheses group the allowed endings; `|` means “or”. For example, `.pdf` follows the literal dot and `pdf` alternative to a complete match. `.pdfx` fails because the end anchor disallows trailing symbols, and `.exe` matches none of the alternatives.

## NFA

An NFA for this language is the prefix trie: branch from the state after `.` into the supported extension paths, with one accepting leaf for each complete word. Each state has at most one outgoing edge per symbol, so this NFA is also deterministic. Its state set is the 16 prefix states shown below plus eight distinct accepting leaves: `Q = {q0, q1, q_p, q_pd, q_pn, q_d, q_do, q_doc, q_t, q_tx, q_j, q_jp, q_m, q_mp, q_z, q_zi, q_pdf, q_png, q_docx, q_txt, q_jpg, q_mp3, q_mp4, q_zip}`. The start state is `q0`; `F = {q_pdf, q_png, q_docx, q_txt, q_jpg, q_mp3, q_mp4, q_zip}`. A missing NFA transition has value `∅`.

Formal machine: `M_N = (Q, Σ, δ, q0, F)`. `δ` follows the character paths shown below. The NFA transition table is sparse: every transition not listed has value `∅`.

| State | Transitions |
| --- | --- |
| q0 | `.` → q1 |
| q1 | `p` → q_p; `d` → q_d; `t` → q_t; `j` → q_j; `m` → q_m; `z` → q_z; `c` → q_c; `g` → q_g |
| q_p | `d` → q_pd; `n` → q_pn |
| q_pd | `f` → q_pdf |
| q_pn | `g` → q_png |
| q_d → q_do → q_doc → q_docx | Each arrow reads `o`, then `c`, then `x` |
| q_t → q_tx → q_txt | Arrows read `x`, then `t` |
| q_j → q_jp → q_jpg | Arrows read `p`, then `g` |
| q_m → q_mp | `p` |
| q_mp | `3` → q_mp3; `4` → q_mp4 |
| q_z → q_zi → q_zip | Arrows read `i`, then `p` |
| q_c → q_cs → q_csv | Arrows read `s`, then `v` |
| q_g → q_gi → q_gif | Arrows read `i`, then `f` |

## NFA-to-DFA subset construction

The NFA above is deterministic (each state has zero or one transition for a symbol), so subset construction yields singleton subsets plus the empty subset. Start subset is `{q0}`. The reachable singleton subsets are `{q0}`, `{q1}`, `{q_p}`, `{q_pd}`, `{q_pn}`, `{q_d}`, `{q_do}`, `{q_doc}`, `{q_t}`, `{q_tx}`, `{q_j}`, `{q_jp}`, `{q_m}`, `{q_mp}`, `{q_z}`, `{q_zi}`, `{q_pdf}`, `{q_png}`, `{q_docx}`, `{q_txt}`, `{q_jpg}`, `{q_mp3}`, `{q_mp4}`, `{q_zip}`. The empty subset is also reachable when a symbol has no NFA transition; it becomes the complete DFA trap state `q_trap`, which loops on every alphabet symbol. For every reachable subset `S` and symbol `a`, compute `δ_D(S,a) = ⋃ δ_N(q,a)` for `q ∈ S`. A subset is accepting exactly when it contains an NFA accepting state. The complete DFA therefore has 25 reachable states: the 24 singleton subsets and the empty subset.

## DFA minimization

The eight-extension trie has 24 live states (16 prefix states and eight accepting leaves), plus the trap state: 25 total. All states are reachable. Initially partition the states into accepting and nonaccepting groups.

The eight accepting leaves have identical behavior and merge into `q_accept`. The current implementation uses this 18-state DFA. One further merge is possible: `q_pn` and `q_jp` both accept only the remaining suffix `g`. The fully minimized DFA therefore has 17 states; this additional merge is not yet implemented.

The implemented transition table follows the NFA prefix transitions above, with every accepting leaf replaced by `q_accept`. All missing transitions, including every transition from `q_accept`, go to `q_trap`. Only `q_trap` loops to itself for every alphabet symbol. The start state is `q0` and the only accepting state is `q_accept`.

## Working simulator

Run `python main.py` from this directory. Choose a file or select **Test extensions** and enter one raw extension per line. The simulator validates alphabet symbols, processes each line independently, shows every transition, reports the final state, and displays ACCEPTED or REJECTED. The file picker supports single- and multiple-file drag and drop when `tkinterdnd2` is installed.

Requirements: Python 3.9+ and Tkinter. Install the drag-and-drop dependency with `python -m pip install -r requirements.txt`. Tkinter is included with most standard Python installations; on some Linux distributions it must be installed separately through the system package manager.

## Course project requirements and submission checklist

The project is developed by a Formal Language and Automata team. Its practical problem is deciding whether a filename extension is in the supported extension language. Users can inspect a file through the file picker or drag-and-drop, and can test raw extension strings in the simulator. The fixed finite set of accepted strings makes finite automata suitable: each state records only the prefix needed to decide whether the remaining symbols can complete a supported extension.

The project must demonstrate the equivalence of the regular expression, NFA, subset-constructed DFA, and minimized DFA. The sections above define the alphabet, strings, language, accepted and rejected examples, regular expression and components, NFA, subset construction, and minimization. For the report and defense, include the transition tables and state diagrams for the NFA, DFA, and minimized DFA. Show the reachable subsets during conversion, identify accepting subsets, show unreachable states if any, partition final and non-final states, justify equivalent-state merges, and compare the original and minimized DFA state counts.

The simulator implements the DFA described above. It accepts one or more input strings, rejects symbols outside the alphabet, processes symbols in sequence, displays transitions and the final state, and reports ACCEPTED or REJECTED. Test cases should include the eight accepted and ten rejected strings listed above, plus representative invalid-symbol and multiple-case tests. Record results and include screenshots of the working system.

Project objectives are to analyze a practical formal-language problem; construct finite automata for its language; apply regular expressions, NFA, DFA, subset construction, and DFA minimization; demonstrate equivalence between those representations; and implement a program that simulates the designed automaton.


## Project folder structure

```text
file-extension-recognizer/
|-- assets/
|   `-- logo/
|       `-- LOGO.png             # Application logo
|-- automata.py                 # DFA states, transitions, and simulation
|-- extension_recognizer.py     # Connects extension extraction to the DFA
|-- file_reader.py              # Reads filenames and filesystem metadata
|-- main.py                     # Application entry point
|-- requirements.txt            # Optional drag-and-drop dependency
|-- ui.py                       # Tkinter window and multi-case simulator
`-- README.md                   # Setup, usage, and project documentation
```
