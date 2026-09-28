# RECOGNIZER

RECOGNIZER is a small Python desktop application that recognizes selected file
extensions using a Deterministic Finite Automaton (DFA). It accepts `.pdf`,
`.docx`, `.txt`, `.jpg`, `.png`, `.mp3`, `.mp4`, and `.zip` and rejects other
extensions.

The application checks a file's **filename extension**. It does not inspect or
validate the file's contents, so a file renamed to an accepted extension may
still contain different data.

## Features

- Choose a file with the file picker, or drag and drop a file when the optional
  drag-and-drop package is installed.
- Display the recognition verdict and basic file metadata: name, extension,
  size, creation time, and modification time.
- Show the MIME type guessed from the extension. This is not a content check.
- Expand **Show DFA steps** to see each state transition and the final state for
  the course demonstration.
- Use `assets/logo/LOGO.png` as the application logo.

## Requirements

- Python 3.9 or newer
- Tkinter (usually included with the standard Python installation)
- `tkinterdnd2` for drag-and-drop support (optional; the file picker works
  without it)

Install drag-and-drop support:

```powershell
python -m pip install tkinterdnd2
```

## Run

Open a terminal in the `file-extension-recognizer` folder and run:

```powershell
python main.py
```

## Project files

```text
file-extension-recognizer/
|-- assets/
|   `-- logo/
|       `-- LOGO.png
|-- automata.py                 # DFA states, transitions, and simulation
|-- extension_recognizer.py     # Connects extension extraction to the DFA
|-- file_reader.py              # Reads filename and filesystem metadata
|-- main.py                     # Application entry point
|-- ui.py                       # Tkinter window and user interaction
`-- README.md
```

## DFA language and test examples

The DFA is case-sensitive and recognizes these exact extension strings:

| Input | Result | Reason |
| --- | --- | --- |
| `.pdf` | ACCEPTED | Supported extension |
| `.docx` | ACCEPTED | Supported extension |
| `.txt` | ACCEPTED | Supported extension |
| `.jpg` | ACCEPTED | Supported extension |
| `.png` | ACCEPTED | Supported extension |
| `.mp3` | ACCEPTED | Supported extension |
| `.mp4` | ACCEPTED | Supported extension |
| `.zip` | ACCEPTED | Supported extension |
| `pdf` | REJECTED | Missing leading dot |
| `.doc` | REJECTED | Incomplete extension |
| `.exe` | REJECTED | `e` is outside the alphabet |
| `.pdfx` | REJECTED | Extra character after an accepting state |
| `.mp5` | REJECTED | `5` is outside the alphabet |
| `.txt.txt` | REJECTED | Extra suffix |
| `.` | REJECTED | No complete extension |
| `.mp` | REJECTED | Incomplete extension |
| `..pdf` | REJECTED | Duplicate dot |
| `.DOCX` | REJECTED | Uppercase characters are outside the alphabet |

The alphabet is the set of characters used by the accepted strings:

```text
Sigma = { ., p, d, f, o, c, x, t, j, g, n, m, 3, 4, z, i }
```

The regular expression for the extension language is:

```regex
^\.(pdf|docx|txt|jpg|png|mp3|mp4|zip)$
```

- `^` and `$` require the whole input to match.
- `\.` matches a literal dot.
- Parentheses group the permitted extension endings.
- `|` means “or”.

The accepted examples contain eight distinct strings because `.pdf` and `.png`
were repeated in the supplied list. If the report requires ten **distinct**
accepted strings, add two more extensions to the language, RE, and DFA.

When checking a file, the program extracts its final suffix as written. It does
not convert uppercase letters to lowercase, so `.DOCX` is rejected while
`.docx` is accepted. A filename without a suffix is rejected.

## Course project note

The main result view hides the transition trace to keep the interface simple.
The **Show DFA steps** control makes the symbol-by-symbol transitions and final
state available during the simulator demonstration. The NFA construction,
NFA-to-DFA conversion, DFA minimization, formal language definition, and test
cases should also be documented separately in the course report.
