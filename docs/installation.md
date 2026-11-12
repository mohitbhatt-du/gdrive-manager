# Installation Guide: GDrive Manager

This guide covers installing and setting up GDrive Manager on Windows 10 and Windows 11 (64-bit).

---

## 1. System Requirements

- **Operating System**: Windows 11 or Windows 10 (Build 1809+, 64-bit).
- **Architecture**: x86_64 (64-bit).
- **RAM**: Minimum 512 MB available memory (2 GB recommended).
- **Disk Space**: ~150 MB for application files plus configurable VFS cache space (default 10 GB).
- **Network**: Broadband internet connection for Google Drive synchronization.

---

## 2. Core Dependencies

### 2.1 WinFsp (Windows File System Proxy)
> [!IMPORTANT]
> WinFsp is required for **Streaming Mode** (mounting Google Drives as native Windows drive letters like `G:`, `H:`, etc.). If you only use **Offline Mode** (folder synchronization), WinFsp is optional.

To install WinFsp:

#### Option A: Via Windows Package Manager (winget) — Recommended
Open Windows Terminal or PowerShell and run:
```powershell
winget install WinFsp.WinFsp --accept-package-agreements --accept-source-agreements
```

#### Option B: Direct Installer Download
1. Visit the official WinFsp release page: [https://winfsp.dev/rel/](https://winfsp.dev/rel/)
2. Download the latest `.msi` installer.
3. Run the installer with default settings.
4. No system reboot is required.

### 2.2 Rclone Engine
- GDrive Manager bundles standalone `rclone v1.76.0` inside `bin/rclone/rclone.exe`.
- **No separate manual rclone installation is required.**
- If you have an existing system-wide rclone installed via winget or Chocolatey, GDrive Manager automatically discovers it on `PATH` as a secondary fallback.

---

## 3. Installation Options

### Option 1: Windows Setup Installer (`GDriveManager-Setup-x64.exe`)
1. Download `GDriveManager-Setup-x64.exe` from the [Latest GitHub Release](https://github.com/mohit/gdrive-manager/releases).
2. Double-click the installer executable.
3. Choose your desired destination folder (default: `C:\Program Files\GDriveManager` or `%LOCALAPPDATA%\Programs\GDriveManager`).
4. Select optional shortcuts (Desktop shortcut, Start Menu shortcut).
5. Complete installation and launch GDrive Manager.

### Option 2: Portable Archive (`GDriveManager-Windows-x64.zip`)
1. Download `GDriveManager-Windows-x64.zip` from the GitHub Release page.
2. Extract the ZIP archive to your preferred directory (e.g. `C:\Tools\GDriveManager` or `D:\Apps\GDriveManager`).
3. Double-click `GDriveManager.exe` inside the extracted folder to run immediately.
4. All user configuration, cached chunks, and logs are automatically kept in `%LOCALAPPDATA%\GDriveManager`, making updates as simple as extracting a newer version.

### Option 3: Running from Source Code (Developers)
If you wish to run or develop GDrive Manager directly from the Python repository:

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/mohit/gdrive-manager.git
   cd gdrive-manager
   ```

2. **Create and activate a Python 3.12 virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Verify environment readiness**:
   ```powershell
   python scripts/check_environment.py
   ```

5. **Launch the application**:
   ```powershell
   python main.py
   ```

---

## 4. First-Launch Setup Wizard

On first launch, GDrive Manager opens the **First-Launch Onboarding Wizard**:
1. **Pre-flight Checks**: Confirms that rclone and WinFsp are detected and active.
2. **One-Click Driver Setup**: If WinFsp is missing, click **Install (winget)** directly within the wizard.
3. **Connect Account**: Click **Connect First Account** to immediately authorize your first Google Drive account via browser sign-in.
