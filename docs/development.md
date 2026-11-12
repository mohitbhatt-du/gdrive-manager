# Developer & Contributing Guide: GDrive Manager

This document provides instructions for developers contributing to the GDrive Manager codebase.

---

## 1. Development Prerequisites

- **Host OS**: Windows 11 or Windows 10 (64-bit).
- **Python**: Version 3.12 or newer.
- **Git**: Git for Windows with standard line ending handling.
- **Recommended Editor**: Visual Studio Code or PyCharm with Python and Ruff extensions.

---

## 2. Setting Up the Environment

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/mohit/gdrive-manager.git
   cd gdrive-manager
   ```

2. **Initialize a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install development and runtime dependencies**:
   ```powershell
   pip install -r requirements-dev.txt
   ```

4. **Verify development environment readiness**:
   ```powershell
   python scripts/check_environment.py
   ```

5. **Install pre-commit hooks**:
   ```powershell
   pre-commit install
   ```

---

## 3. Running the Test Suite

GDrive Manager utilizes `pytest` with partitioned unit and integration suites:

### Run All Tests:
```powershell
pytest -v tests/
```

### Run Unit Tests Only:
```powershell
pytest -v tests/unit/
```

### Run Integration Tests Only:
```powershell
pytest -v tests/integration/
```

### Run Tests with Coverage Report:
```powershell
pytest -v --cov=app --cov-report=term-missing tests/
```

> [!NOTE]
> All unit tests use mocks for external rclone processes, subprocesses, and Google API interactions. Unit tests do NOT require a live Google Drive account or real network access, and they never touch real user data.

---

## 4. Code Quality & Standards

GDrive Manager strictly enforces code quality via **Ruff** and **Mypy**:

### Run Linter Checks:
```powershell
ruff check .
```

### Auto-fix Lint Issues:
```powershell
ruff check --fix .
```

### Check Code Formatting:
```powershell
ruff format --check .
```

### Auto-format Code:
```powershell
ruff format .
```

### Type Checking:
```powershell
mypy app/
```

---

## 5. Building the Distribution Packages

### Build Standalone Executable & Portable ZIP:
```powershell
python scripts/build.py
```
Outputs:
- Onedir Folder: `dist\GDriveManager\`
- Standalone Executable: `dist\GDriveManager\GDriveManager.exe`
- Portable Archive: `dist\GDriveManager-Windows-x64.zip`

### Regenerate Vector and Brand Assets:
```powershell
python scripts/generate_branding_assets.py
```
Outputs:
- `assets/branding/icon.png`, `icon.ico`, `logo.png`
- `assets/branding/github-banner.png` (1280x640)
- `assets/branding/social-preview.png` (1280x640)
