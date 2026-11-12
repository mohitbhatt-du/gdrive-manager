# GDrive Manager

A modern, production-grade Windows desktop application that bridges multiple Google Drive accounts directly into Windows File Explorer through on-demand virtual drive streaming (WinFsp & rclone) and selective local offline synchronization.

---

## Key Features

- **Multi-Account Independence**: Connect multiple personal, business, university, or backup Google accounts simultaneously with separate configurations and independent drive letter assignments.
- **Streaming Mode**: Mount Google Drive as a native Windows drive letter (`G:`, `H:`, `I:`, etc.) with local VFS caching and Windows Explorer integration.
- **Offline Storage & Sync**: Selective local sync (downloads, uploads, one-way mirrors, and bidirectional bi-sync with safety dry-runs).
- **Hybrid Storage**: Combine virtual streaming and dedicated local offline sync folders for the same Google account without conflict.
- **Real-Time Transfer Queue**: Live speed telemetry, byte counters, ETAs, pause, resume, cancel, and retry capabilities.
- **Enterprise-Grade Security**: Google OAuth 2.0 integration with tokens stored securely in Windows Credential Manager.
- **Modern Dark UI**: Deep navy aesthetic (`#0B0F19`) with purple/violet accents (`#7C3AED`), responsive cards, clean typography, and antialiased vector iconography.

---

## Project Structure

```
gdrive-manager/
├── main.py                  # Application entrypoint
├── requirements.txt         # Core dependencies
├── DEVELOPMENT_STATUS.md    # Phased progress and tracking
├── .gitignore               # Environment and credential exclusion rules
├── app/
│   ├── ui/                  # Presentation layer
│   │   ├── main_window.py   # Primary window coordinator
│   │   ├── sidebar.py       # Modern sidebar navigation & status footer
│   │   ├── dashboard.py     # Main dashboard with drive cards & metrics
│   │   ├── drive_card.py    # Reusable modern card component
│   │   ├── streaming_page.py# WinFsp mount & VFS cache manager
│   │   ├── offline_page.py  # Offline sync & local folder manager
│   │   ├── transfers_page.py# Real-time transfer queue & telemetry
│   │   ├── settings_page.py # Startup preferences, cache paths, diagnostics
│   │   ├── assets.py        # Antialiased Pillow vector icon generator
│   │   └── dialogs/         # Modal dialogs
│   │       ├── add_account_dialog.py
│   │       ├── drive_settings_dialog.py
│   │       └── confirmation_dialog.py
│   ├── config/              # Themes, typography, and constants
│   ├── models/              # Account and TransferJob data representations
│   └── utils/               # Platform checks, Windows drive querying, logging, paths
└── tests/                   # Automated unit and UI test suite
```

---

## Getting Started

### Prerequisites
- Windows 10 / 11 (x64)
- Python 3.12+
- *(For Phase 2/3)*: `rclone` and `WinFsp`

### Setup Environment
```powershell
cd gdrive-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running the Application
```powershell
python main.py
```

### Running Tests
```powershell
pytest -v tests/
```
