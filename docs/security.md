# Security Architecture & Policy: GDrive Manager

This document outlines the security architecture, threat model, and vulnerability reporting procedures for GDrive Manager.

---

## 1. Security Architecture

### 1.1 Token Storage & Windows Credential Manager
- **Zero Plaintext Tokens in JSON**: GDrive Manager never writes Google OAuth client secrets, refresh tokens, or bearer access tokens into `accounts.json`.
- **Windows Credential Manager Integration**: All sensitive account credentials and tokens are delegated to Windows Credential Manager via the `keyring` library under target name `GDriveManager`.
- **Cryptographic Protection**: Windows Credential Manager uses Windows Data Protection API (DPAPI) to encrypt secrets using keys tied to the user's Windows login credentials and TPM (Trusted Platform Module).

### 1.2 Subprocess Command Injection Defense
- **Strict Argument Lists**: Subprocesses spawned by `AuthManager`, `MountManager`, and `TransferManager` are strictly invoked using structured argument arrays (e.g. `[exe, "mount", remote, letter, ...]`).
- **Zero Raw Shell Concatenation**: The application avoids `shell=True` and raw string concatenations, eliminating command injection and shell escape vulnerabilities.

### 1.3 Rclone Configuration Security
- **Configuration Isolation**: Rclone configuration is isolated to `%LOCALAPPDATA%\GDriveManager\rclone.conf`.
- **User ACL Protection**: On NTFS volumes, `%LOCALAPPDATA%` is protected by default discretionary access control lists (DACLs) granting access only to the logged-in user and administrators.

---

## 2. Threat Model & Boundaries

| Component | Threat Addressed | Mitigation |
|---|---|---|
| **Account Metadata** | Malicious JSON tampering | Schema validation and atomic `.tmp` file replacement |
| **Streaming Drives** | Drive letter conflict / collision | Logical drive pre-flight checks before mounting |
| **Offline Sync** | Accidental mass file deletion | Destructive confirmation prompts + dry-run verification mode |
| **OAuth Redirects** | Local port eavesdropping | Loopback-only binding (`127.0.0.1:53682`) with 3-minute timeout |

---

## 3. Reporting a Vulnerability

We take the security of GDrive Manager seriously. If you believe you have discovered a security vulnerability:

1. **Do not create a public GitHub issue.**
2. Send a detailed report via email to: `security@gdrivemanager.local` (or file a private GitHub Security Advisory).
3. Include:
   - Type of issue (e.g., credential exposure, privilege escalation, injection).
   - Step-by-step instructions or proof-of-concept to reproduce.
   - Impact assessment.
4. We will acknowledge receipt within 48 hours and work with you on coordinated disclosure.
