# Python Setup Commands

## Step 1: Install pyserial

```bash
pip install pyserial
```

## Step 2: Install all requirements

```bash
pip install -r requirements.txt
```

## Step 3: Install Whisper

```bash
pip install openai-whisper
```

## Step 4: Run the serial listener

```bash
python serial_listener.py
```

---

## Quick One-Line Installation

Run all at once:

```bash
pip install pyserial && pip install -r requirements.txt && pip install openai-whisper
```

---

## Testing Commands

### Test if pyserial is installed:

```bash
python -c "import serial; print('pyserial OK')"
```

### Test if all modules work:

```bash
python -c "import serial; import nltk; import sklearn; print('All OK')"
```

---

## Troubleshooting

### If you get "No module named 'serial'":

```bash
pip install pyserial
```

### If pip doesn't work, try pip3:

```bash
pip3 install pyserial
pip3 install -r requirements.txt
pip3 install openai-whisper
```

### Check Python version:

```bash
python --version
```

Should be Python 3.10 or higher.

---

## Full Setup Sequence

Copy and paste these commands **one by one** in VS Code terminal (Ctrl + `):

1. `pip install pyserial`
2. `pip install -r requirements.txt`
3. `pip install openai-whisper`
4. `python serial_listener.py`

---

## Expected Output After Running serial_listener.py:

```
[SERIAL] Opening COM6 at 115200 baud …
[SERIAL] Listening on COM6 …
[SERIAL] Wake word: "hey assistant"
[SERIAL] Audio format: 16000 Hz, 16-bit, mono
[SERIAL] Press Ctrl+C to stop.
```

Then speak into the microphone to test!
