"""Generate SHA256 checksums for release distribution assets."""

import hashlib
import sys
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    dist_dir = Path(__file__).resolve().parent.parent / "dist"
    if not dist_dir.exists():
        print(f"[-] dist directory not found at: {dist_dir}")
        sys.exit(1)

    target_files = [
        "GDriveManager-Windows-x64.zip",
        "GDriveManager-Setup-x64.exe",
    ]

    checksums = []
    for filename in target_files:
        file_path = dist_dir / filename
        if file_path.exists():
            h = calculate_sha256(file_path)
            checksums.append(f"{h}  {filename}")
            print(f"[✓] {filename}: {h}")
        else:
            print(f"[!] Warning: {filename} not found in dist/")

    if checksums:
        out_file = dist_dir / "SHA256SUMS.txt"
        out_file.write_text("\n".join(checksums) + "\n", encoding="ascii")
        print(f"\n[✓] Checksum manifest written to: {out_file}")
    else:
        print("[-] No release files found to checksum.")
        sys.exit(1)


if __name__ == "__main__":
    main()
