# Changelog

All notable changes to GDrive Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.2] - 2026-11-12

### Fixed
- **Rclone Detection in Windows GUI Subsystem**:
  - Eliminated 5-second subprocess timeouts when probing rclone version by supplying `creationflags=CREATE_NO_WINDOW` and `stdin=subprocess.DEVNULL`, preventing Windows GUI console handle inheritance deadlocks.
  - Cached rclone engine availability status (`is_available`) to prevent redundant subprocess spawns during UI updates and drive mounting.
  - Increased timeout thresholds to 10-15s to tolerate Windows Defender on-demand scanning on first executable launch.
- **Google OAuth Sign-In & Remote Configuration**:
  - `AddAccountDialog` now mandates real Google OAuth authentication and prevents silently generating dummy placeholder accounts (`remote_test`) when rclone is being detected.
  - Passed `config_is_local true` to `rclone config create` to guarantee automatic browser launching for OAuth authorization.
- **Clean Initial Launch State**:
  - Removed sample accounts (`alex.chen.personal@gmail.com`) from fresh installations so newly installed applications open directly to the clean dashboard empty state (`+ Add Google Drive Account`).
  - Cleared default mock transfers from transfer activity queue.
- **Orphaned Mount & Drive Release**:
  - Added detection and automated termination of orphaned `rclone.exe mount` background processes holding drive letters (e.g., `G:\`, `H:\`).
  - Added **"Force Unmount All Virtual Drives"** one-click maintenance tool in Settings.
- **Storage Quota Persistence & Dashboard Refresh**:
  - Persisted background storage quota updates directly to `accounts.json` so storage metric pills accurately reflect used and total Google Drive cloud storage.
  - Removed duplicate card layout calls in Dashboard.

---

## [1.0.1] - 2026-11-12

### Added
- **In-App Cloud File & Directory Explorer (`CloudBrowserDialog`)**:
  - Visit and navigate remote Google Drive folders and subdirectories directly inside the desktop application without requiring WinFsp driver or Windows drive letter mounting.
  - Full support for **"Shared with me"** files (`--drive-shared-with-me`) with instant toggle switch.
  - In-app file downloading to local storage with native Windows Save As dialog.
  - Direct web client deep-linking ("Open in Web").
  - Real-time file name filtering and breadcrumb path traversal.
  - Dedicated "Browse" action buttons on both Dashboard drive cards and Streaming drives table.
- **Dynamic Dashboard Storage & Quota Refresh**:
  - Top metric pills (Total Accounts, Streaming Drives, Cloud Usage) now update dynamically in real time whenever drives are connected, mounted, unmounted, or removed.
  - Automatic asynchronous cloud quota sync (`rclone about`) on startup and upon connecting new accounts.
  - Manual "Refresh Storage" trigger added to Dashboard header.

### Fixed
- **Rclone Discovery in Packaged Release**:
  - Resolved missing rclone engine error by expanding binary discovery across PyInstaller `_internal\bin\rclone\rclone.exe`, user `AppData`, root directory, and system `PATH`.
  - Fixed runtime rclone downloads by saving to user-writable `%LOCALAPPDATA%\GDriveManager\bin\rclone\` rather than restricted `Program Files` directory, preventing UAC permission failures.

---

## [1.0.0] - 2026-11-12

### Added
- **Multi-Account Google Drive Management**: Connect and manage multiple independent Google Drive accounts (Personal, Work, University) with separate credentials and drive assignments.
- **Streaming Mode**: Mount Google Drive as native Windows drive letters (`G:`, `H:`, `I:`) via WinFsp and rclone with full VFS chunk caching (`--vfs-cache-mode full`).
- **Offline Storage & Sync Engine**:
  - Safe Copy (one-way copy without deleting destination files).
  - Mirror Synchronization (source mirroring with destructive deletion safety warnings).
  - Two-Way Bi-Sync with automated conflict resolution.
  - Dry-Run preview mode for all sync operations.
- **Hybrid Storage Mode**: Operate simultaneous virtual streaming drive letters and dedicated offline synchronization folders for the same Google account without conflict.
- **Real-Time Telemetry & Transfer Queue**: Asynchronous transfer queue with live rclone JSON telemetry parsing on stderr (`--use-json-log --stats 1s`) displaying byte counters, speeds, and ETA countdowns.
- **Enterprise Credential Security**: Hardware-encrypted OAuth 2.0 token vaulting using Windows Credential Manager (`keyring`) with zero plaintext secrets on disk.
- **Windows System Integration**:
  - System tray icon with background minimization (`pystray`) and quick mount/unmount context menu.
  - Native Windows balloon notifications for mount, unmount, and transfer events.
  - Optional Windows startup autorun toggle (`HKCU\...\Run`).
  - Explorer integration: one-click drive opening in `explorer.exe`.
- **First-Launch Setup Wizard**: Pre-flight checklist verifying bundled rclone, WinFsp virtual drive driver, and Windows Credential Manager.
- **Diagnostics & In-App Logs Viewer**: Filterable log inspector (`INFO`, `WARNING`, `ERROR`, `DEBUG`) and direct Notepad launcher.
- **Original Geometric Brand Identity**: Custom vector logo and multi-resolution Windows icon (`assets/branding/icon.ico`).
- **Comprehensive Automated Test Suite**: 50 unit and integration tests covering core business logic, models, and dialogs.
- **Standalone Packaging**: PyInstaller build pipeline and portable Windows distribution (`GDriveManager-Windows-x64.zip`).
