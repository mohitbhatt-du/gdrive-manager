"""Utility to extract release notes from CHANGELOG.md for GitHub Releases."""

import re
import sys
from pathlib import Path


def extract_notes_for_version(version: str) -> str:
    # Normalize version: strip leading 'v'
    v_clean = version.lstrip("v").strip()

    changelog_path = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    if not changelog_path.exists():
        return f"Release {version}"

    content = changelog_path.read_text(encoding="utf-8")

    # Match header like ## [1.0.0] - 2026-11-12
    pattern = rf"##\s*\[{re.escape(v_clean)}\][^\n]*\n(.*?)(?=\n##\s*\[|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        notes = match.group(1).strip()
        header = f"# GDrive Manager v{v_clean}\n\n"
        footer = (
            "\n\n---\n"
            "### Downloads & Verification\n"
            "- **Windows Installer (Recommended)**: `GDriveManager-Setup-x64.exe`\n"
            "- **Portable Zip**: `GDriveManager-Windows-x64.zip`\n"
            "- **Checksums**: Verify your download against `SHA256SUMS.txt`\n\n"
            "### Prerequisites\n"
            "- Windows 10 / Windows 11 (64-bit)\n"
            "- [WinFsp](https://winfsp.dev/) (Required for virtual drive streaming: `winget install WinFsp.WinFsp`)\n"
        )
        return header + notes + footer

    return f"# GDrive Manager v{v_clean}\n\nRelease notes for version {v_clean}."


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
    out_file = sys.argv[2] if len(sys.argv) > 2 else None

    notes = extract_notes_for_version(version)
    if out_file:
        Path(out_file).write_text(notes, encoding="utf-8")
        print(f"[✓] Release notes written to {out_file}")
    else:
        print(notes)


if __name__ == "__main__":
    main()
