# Configuration Guide: GDrive Manager

This document provides detailed reference for GDrive Manager's configuration files, storage caches, drive letter assignments, and runtime settings.

---

## 1. Storage Paths & User Data

All persistent user configuration, credentials, and cache folders reside in the standard Windows user profile directory:

```
%LOCALAPPDATA%\GDriveManager\
├── accounts.json              # Account metadata and mount settings
├── rclone.conf                # Remote endpoint configuration
├── vfs_cache\                 # Temporary VFS streaming chunk cache
│   └── vfs\
├── logs\
│   └── app.log                # Rotating execution logs
└── .onboarding_completed      # Onboarding wizard completion marker
```

> [!NOTE]
> Even if GDrive Manager is installed into `C:\Program Files\GDriveManager`, application state is strictly maintained in `%LOCALAPPDATA%`. This prevents permission errors and ensures multi-user isolation on shared Windows PCs.

---

## 2. Account Metadata Schema (`accounts.json`)

Account records are stored in `%LOCALAPPDATA%\GDriveManager\accounts.json`. Updates are written atomically using a `.tmp` file and replaced in place to prevent file corruption.

### Example Schema:
```json
{
  "accounts": [
    {
      "id": "gdrive_personal",
      "email": "user.work@gmail.com",
      "display_name": "Personal Drive",
      "remote_name": "gdrive_personal",
      "drive_letter": "G:",
      "streaming_enabled": true,
      "offline_enabled": false,
      "offline_path": "D:\\GDriveOffline\\Personal",
      "cache_size": "20G",
      "cache_expiry": "24h",
      "read_only": false,
      "auto_mount": false,
      "used_storage_bytes": 161480704,
      "total_storage_bytes": 16106127360,
      "is_mounted": false,
      "mount_pid": null,
      "status": "Connected",
      "status_message": "",
      "is_sample": false
    }
  ]
}
```

### Key Field Descriptions:
- **`id`** *(str)*: Unique account identifier used across settings and Windows Credential Manager lookups.
- **`remote_name`** *(str)*: Corresponding remote entry name inside `rclone.conf`.
- **`drive_letter`** *(str)*: Assigned Windows drive letter (e.g. `G:`, `H:`).
- **`cache_size`** *(str)*: Maximum disk space allocated for VFS chunk cache (e.g. `10G`, `20G`, `50G`).
- **`cache_expiry`** *(str)*: Maximum retention age for cached file chunks (e.g. `24h`, `72h`).
- **`read_only`** *(bool)*: Mounts the virtual drive in read-only mode, preventing accidental cloud modifications.

---

## 3. VFS Streaming Cache Tuning

When a virtual drive letter is mounted, GDrive Manager invokes `rclone mount` with `--vfs-cache-mode full`. This ensures native Windows compatibility, supporting random reads, partial writes, file locking, and background chunk uploading.

### Recommended Cache Settings:

| Workload | Recommended Cache Size | Cache Expiry |
|---|---|---|
| **Office Documents & Spreadsheets** | `5G` | `24h` |
| **General Desktop Use (Standard)** | `10G` to `20G` | `24h` |
| **Media Editing & Large Archives** | `50G` to `100G` | `72h` |

### Cache Directory Customization:
By default, the cache directory is configured at `%LOCALAPPDATA%\GDriveManager\vfs_cache`. You can change this directory in **Settings > VFS Streaming & Cache Policies** to an alternate fast SSD or secondary storage drive.

### Purging Cache:
If disk space is low, open **Drive Settings > Storage Breakdown > Purge VFS Cache**. This deletes local temporary chunks immediately without affecting files stored on Google Drive.

---

## 4. Drive Letter Allocation Rules

Windows supports drive letters from `D:` through `Z:` (`A:` and `B:` are reserved for legacy floppy devices; `C:` is the system drive).

1. GDrive Manager inspects active logical drives via Win32 API `GetLogicalDriveStrings`.
2. When creating an account, GDrive Manager suggests the highest available preferred virtual letters (`G:`, `H:`, `I:`, `J:`, down to `Z:`).
3. If an assigned drive letter is occupied when mounting (e.g., due to an inserted USB flash drive), GDrive Manager notifies the user and blocks the mount to prevent mount collision.

---

## 5. Windows Startup Registry

To enable or disable launch on Windows startup:
- Toggle **Launch GDrive Manager automatically at Windows startup** in the application's **Settings** page.
- Under the hood, this configures:
  `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\GDriveManager`
- Because it operates under `HKEY_CURRENT_USER`, administrator elevation is not required.
