# NexusAI Autonomous PC Assistant

An autonomous, standalone AI Assistant with deep operating system and browser automation capabilities.

## ✨ Features Implemented

- **🌐 Autonomous Browser Control**: Direct automation of Chromium via Playwright (search, navigation, element interaction, extraction, and screenshotting).
- **🖥️ System & App Automation**: OS-level app launching (Notepad, Chrome, VS Code, Calculator, Explorer, etc.), process management, typing, clicking, and hotkeys.
- **⚡ Multi-Language Code Runner**: Real-time execution of code snippets in Python, JavaScript/Node.js, PowerShell, Bash, and CMD.
- **🔊 Voice Interface**: Multi-threaded text-to-speech output (`pyttsx3`) and Web Speech API audio transcription.
- **📊 Real-Time Hardware Metrics**: Dynamic polling and live display of CPU usage, RAM utilization, and Disk capacity.
- **🎨 Modern Dark Dashboard**: Responsive web desktop GUI styled with dark mode gradients, interactive execution console, and quick-action triggers.

## 🚀 How to Launch

Double click `start_assistant.bat` or run:

```bash
.\venv\Scripts\python.exe main.py
```

Then open your browser to `http://127.0.0.1:8765`.

## 🧪 Running Tests

```bash
.\venv\Scripts\python.exe test_suite.py
```
