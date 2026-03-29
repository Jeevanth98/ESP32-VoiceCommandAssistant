# ESP32 Voice Command Assistant

A desktop voice command assistant built in Python, designed as the PC-side companion for an ESP32 microcontroller. Currently in **Phase 2 (Text Mode)** — it accepts natural-language commands via terminal input and processes them through a **custom supervised-ML NLU pipeline** (TF-IDF + LinearSVC) that classifies intent, extracts entities, and dispatches to command handlers that automate desktop tasks.

> **Future:** Serial integration with ESP32 + Whisper speech-to-text is planned for Phase 3.

---

## Features

| Command | Example | Description |
|---|---|---|
| **Open App** | *"Open WhatsApp"* | Launches from a 100+ app registry (desktop, UWP, web) |
| **Close App** | *"Close Chrome"* | Terminates a running process by friendly name |
| **Web Search** | *"Search what is a lion"* | Opens a Google search in the default browser |
| **File Search** | *"Open my physics PDF"* | Fuzzy-matches filenames in configured directories |
| **Content Search** | *"Search for quantum in my notes"* | Full-text keyword search inside PDF/DOCX/TXT documents |
| **Summarize** | *"Summarize my physics notes"* | Finds a document and generates an abstractive summary (BART-CNN) |
| **Active Typing** | *"Write this down: Meeting at 3"* | Opens Notepad and pastes text via clipboard |
| **Screenshot** | *"Take a screenshot"* | Captures the screen and saves a timestamped PNG |
| **GUI Control** | *"Scroll down / Play / Volume up"* | Simulates keyboard media & navigation keys |
| **System Info** | *"What's my CPU usage?"* | Reports CPU, RAM, battery, disk, and network info |
| **Timer** | *"Set a 10 minute timer"* | Background countdown with an audible beep notification |

---

## NLU Pipeline (Supervised ML)

The intent classifier follows a classic supervised NLP lifecycle:

```
Raw text  →  Preprocessing (NLTK)  →  TF-IDF Vectorization  →  LinearSVC  →  Intent label + confidence
```

| Stage | Detail |
|---|---|
| **Data generation** | `generate_data.py` creates ~2 000 synthetic labelled utterances via template expansion |
| **Preprocessing** | Stop-word removal + WordNet lemmatization (`nlu/preprocessor.py`) |
| **Vectorization** | `TfidfVectorizer` with unigrams + bigrams, sublinear TF, 5 000 max features |
| **Classification** | `CalibratedClassifierCV(LinearSVC)` — calibrated for probability estimates |
| **Evaluation** | 5-fold cross-validation accuracy: **99.59%** |

### How It Works

1. **Text input** — User types a command in the terminal
2. **Keyword override** — Regex fast-path for unambiguous commands (bypasses model inference)
3. **Preprocessing** — NLTK stop-word removal + WordNet lemmatization
4. **Intent classification** — TF-IDF + LinearSVC supervised classifier
5. **Entity extraction** — Regex/heuristic extraction of operands (file name, keyword, duration, etc.)
6. **Command dispatch** — Maps the classified intent to the appropriate handler

---

## Project Structure

```
main.py                  # Entry point — interactive loop + NLU pipeline + dispatcher
config.py                # Central configuration (paths, thresholds, model names)
generate_data.py         # Synthetic training-data generator (template expansion)
requirements.txt         # Python dependencies

data/
  training_data.csv      # Generated labelled dataset (~2 000 rows)

models/
  intent_model.joblib    # Trained TF-IDF + LinearSVC pipeline (binary)

nlu/                     # Natural Language Understanding pipeline
  preprocessor.py        # Stop-word removal & lemmatization (NLTK)
  intent_classifier.py   # TF-IDF + LinearSVC supervised classifier
  entity_extractor.py    # Regex-based entity extraction per intent

commands/                # Command handler modules (one per intent)
  open_app.py            # Launch apps from registry
  close_app.py           # Terminate running processes
  web_search.py          # Google search in browser
  file_search.py         # Fuzzy file search + open
  content_mining.py      # Full-text keyword search in documents
  summarize.py           # AI abstractive summarization (BART-CNN)
  active_typing.py       # Open Notepad + paste text
  screenshot.py          # Screen capture
  gui_control.py         # Scroll, media, volume keypresses
  system_info.py         # CPU/RAM/battery/disk/network info
  timer.py               # Background countdown timer

utils/
  text_extraction.py     # Read text from PDF, DOCX, TXT

captures/                # Screenshot output directory (auto-created)
```

---

## Installation

### Prerequisites

- Python 3.10+
- Windows OS (uses `winsound`, `os.startfile()`, UWP app URIs)

### Setup

```bash
# Clone the repository
git clone https://github.com/Jeevanth98/ESP32-VoiceCommandAssistant.git
cd ESP32-VoiceCommandAssistant

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1    # PowerShell
# or
.venv\Scripts\activate.bat    # CMD

# Install dependencies
pip install -r requirements.txt
```

### Train the Intent Classifier

```bash
# 1. Generate synthetic training data
python generate_data.py

# 2. Train the TF-IDF + LinearSVC model
python -m nlu.intent_classifier train
```

The trained model is saved to `models/intent_model.joblib` and loaded automatically at runtime.

---

## Usage

```bash
python main.py
```

Type natural-language commands at the prompt. The classifier loads instantly (no GPU or large model download required).

**Examples:**

```
> open chrome
> search how to learn python
> take a screenshot
> scroll down
> what's my battery level
> set a 5 minute timer
> summarize my physics notes
> close notepad
```

Type `exit` or `quit` to stop.

---

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---|---|---|
| Scan directories | `D:\Sem-06` | Folders indexed for file/content search |
| Fuzzy threshold | 60 | Minimum score (0–100) for file matches |
| Confidence threshold | 0.30 | Minimum confidence for intent classification |
| Summarization model | `facebook/bart-large-cnn` | Abstractive summarizer model |
| Serial port | `COM3 @ 115200` | Placeholder for ESP32 hardware integration |

---

## Dependencies

| Library | Purpose |
|---|---|
| [scikit-learn](https://scikit-learn.org/) | TF-IDF vectorization + LinearSVC classification |
| [joblib](https://joblib.readthedocs.io/) | Model serialization / persistence |
| [pandas](https://pandas.pydata.org/) | Training data loading & manipulation |
| [nltk](https://www.nltk.org/) | Tokenization, stop-words, lemmatization |
| [transformers](https://huggingface.co/docs/transformers) | Abstractive summarization (BART-CNN) |
| [torch](https://pytorch.org/) | PyTorch backend for summarizer |
| [thefuzz](https://github.com/seatgeek/thefuzz) | Fuzzy string matching for file search |
| [PyPDF2](https://pypdf2.readthedocs.io/) | PDF text extraction |
| [python-docx](https://python-docx.readthedocs.io/) | DOCX text extraction |
| [pyautogui](https://pyautogui.readthedocs.io/) | GUI automation (screenshots, keypresses) |
| [psutil](https://psutil.readthedocs.io/) | System monitoring |
| [pyserial](https://pyserial.readthedocs.io/) | Serial communication (future ESP32 link) |

---

## Roadmap

- **Phase 1** ✅ Command modules & NLU pipeline
- **Phase 2** ✅ Text-mode interactive assistant with supervised ML classifier (current)
- **Phase 3** 🔜 ESP32 serial integration with Whisper speech-to-text

---

## License

This project is for personal/educational use.
