"""Standalone Distribution Build Script for GDrive Manager."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    os.chdir(str(base_dir))

    print("=" * 60)
    print(" GDrive Manager - Windows Packaging & Distribution Build")
    print("=" * 60)

    # 1. Check bundled rclone
    rclone_exe = base_dir / "bin" / "rclone" / "rclone.exe"
    if not rclone_exe.exists():
        print("[-] Bundled rclone executable not found at:", rclone_exe)
        print("[!] Attempting to download bundled rclone...")
        sys.path.insert(0, str(base_dir))
        from app.services.rclone_service import RcloneService
        svc = RcloneService()
        if not svc.download_bundled_rclone():
            print("[x] Failed to obtain rclone executable. Aborting build.")
            sys.exit(1)
    print(f"[+] Verified rclone binary: {rclone_exe}")

    # 2. Check application icon
    ico_file = base_dir / "assets" / "icons" / "app_icon.ico"
    if not ico_file.exists():
        print("[-] Application icon not found at:", ico_file)
    else:
        print(f"[+] Verified application icon: {ico_file}")

    # 3. Clean prior build artifacts
    for d in ["build", "dist"]:
        target = base_dir / d
        if target.exists():
            print(f"[*] Cleaning previous {d} directory...")
            try:
                shutil.rmtree(str(target))
            except Exception as e:
                print(f"[!] Warning cleaning {d}: {e}")

    # 4. Invoke PyInstaller
    spec_file = base_dir / "gdrive_manager.spec"
    print(f"[*] Invoking PyInstaller with spec: {spec_file.name}")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec_file),
        "--noconfirm",
        "--clean"
    ]

    ret = subprocess.run(cmd)
    if ret.returncode != 0:
        print("[x] PyInstaller build failed with exit code:", ret.returncode)
        sys.exit(ret.returncode)

    # 5. Verify output
    dist_exe = base_dir / "dist" / "GDriveManager" / "GDriveManager.exe"
    if dist_exe.exists():
        size_mb = dist_exe.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print("[✓] Build Successful!")
        print(f"[✓] Executable: {dist_exe.resolve()}")
        print(f"[✓] Binary Size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("[x] Expected executable not found at:", dist_exe)
        sys.exit(1)

if __name__ == "__main__":
    main()
