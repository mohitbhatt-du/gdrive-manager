# Troubleshooting Guide: GDrive Manager

This guide covers common issues, error messages, and remediation steps for GDrive Manager.

---

## 1. WinFsp Virtual Drive Issues

### Problem: "WinFsp is not installed or service is not running"
- **Cause**: Windows requires the WinFsp kernel/user-mode file system driver to project Google Drive into Windows File Explorer as a drive letter.
- **Solution**:
  1. Open Windows PowerShell and run:
     ```powershell
     winget install WinFsp.WinFsp
     ```
  2. Verify that the launcher service is active:
     ```powershell
     sc query winfsp-launcher
     ```
  3. Reopen GDrive Manager or click **Re-check** in **Settings > Storage Engine Diagnostics**.

### Problem: "Drive letter G: is already occupied"
- **Cause**: Another physical partition, external USB drive, network share, or virtual drive is already assigned to this letter.
- **Solution**:
  1. In GDrive Manager, open **Settings (Gear Icon)** on the drive card.
  2. Change the **Drive Letter** dropdown to an unassigned letter (e.g. `H:`, `I:`, `M:`, or `Z:`).
  3. Click **Save Changes** and mount the drive again.

---

## 2. Google OAuth 2.0 Sign-In Issues

### Problem: "Google authorization timed out (3 minutes exceeded)"
- **Cause**: The browser sign-in flow took longer than 180 seconds, or the authentication popup was blocked.
- **Solution**:
  1. Check your default web browser for an open sign-in tab.
  2. Ensure loopback port `53682` is not blocked by third-party firewall software.
  3. Click **+ Add Drive** again and complete the sign-in prompt promptly.

### Problem: "Access blocked: GDrive Manager has not completed the Google verification process"
- **Cause**: Standard Google OAuth consent screen for unverified custom desktop client credentials.
- **Solution**:
  1. On the Google authorization screen, click **Advanced** (bottom left).
  2. Click **Go to GDrive Manager (unsafe)** to grant Drive permissions.
  3. Consent to the requested scopes (`drive` / `drive.file`).

---

## 3. Storage & Synchronization Conflicts

### Problem: "Hybrid Mode Violation: The offline directory cannot be placed inside virtual drive G:\"
- **Cause**: You selected a local offline destination path that resides inside the virtual drive letter itself (e.g. `G:\MyOfflineFolder`).
- **Explanation**: This would cause an infinite sync loop, as rclone would attempt to synchronize files from cloud `G:\` into a target that is also on `G:\`.
- **Solution**: Select a physical local disk path on your machine (e.g. `C:\Users\username\GoogleDriveOffline` or `D:\GDriveBackup`).

### Problem: Files disappeared after running "Mirror / Sync"
- **Cause**: "Mirror Sync" strictly mirrors the source to the destination. Any files that exist in the destination but NOT at the source will be deleted to achieve an exact replica.
- **Solution**:
  - Always run with **Dry-Run Preview** checked first to inspect which files will be deleted.
  - If you want to transfer new files without deleting anything in the destination, select **Safe Copy** instead of Mirror Sync.

---

## 4. Disk Space & VFS Cache Management

### Problem: Local SSD is running out of disk space
- **Cause**: Large files accessed through the streaming drive are cached locally in the VFS cache for faster subsequent reads.
- **Solution**:
  1. Open GDrive Manager and navigate to **Drive Settings > Storage Breakdown**.
  2. Click **Purge VFS Cache**.
  3. This immediately frees up local SSD space while leaving your files safe on Google Drive.
  4. Lower the **Max VFS Cache Size** (e.g. to `5G` or `10G`) in Drive Settings.

---

## 5. Inspecting Diagnostic Logs

If an unexpected error occurs:
1. Navigate to the **Logs & Diagnostics** page in the left sidebar.
2. Select your desired filter (e.g. `ERROR` or `WARNING`).
3. Click **Open in Notepad** to inspect the raw log file directly.
4. The log file is located at:
   ```
   %LOCALAPPDATA%\GDriveManager\logs\app.log
   ```
5. When filing a bug report on GitHub, attach relevant excerpt lines from this log file.
