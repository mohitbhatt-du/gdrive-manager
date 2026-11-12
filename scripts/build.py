"""Standalone Distribution Build & Packaging Script for GDrive Manager."""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

def get_project_dir() -> Path:
    return Path(__file__).resolve().parent.parent

def build_executable():
    project_dir = get_project_dir()
    os.chdir(str(project_dir))

    print("=" * 65)
    print(" GDrive Manager - Windows Packaging & Distribution Build")
    print("=" * 65)

    # 1. Check bundled rclone
    rclone_exe = project_dir / "bin" / "rclone" / "rclone.exe"
    if not rclone_exe.exists():
        print("[-] Bundled rclone executable not found at:", rclone_exe)
        print("[!] Attempting to download bundled rclone...")
        sys.path.insert(0, str(project_dir))
        from app.services.rclone_service import RcloneService
        svc = RcloneService()
        if not svc.download_bundled_rclone():
            print("[x] Failed to obtain rclone executable. Aborting build.")
            sys.exit(1)
    print(f"[+] Verified rclone binary: {rclone_exe}")

    # 2. Check application icon
    ico_file = project_dir / "assets" / "branding" / "icon.ico"
    if not ico_file.exists():
        ico_file = project_dir / "assets" / "icons" / "app_icon.ico"
    if not ico_file.exists():
        print("[-] Application icon not found. Running generate_branding_assets.py...")
        subprocess.run([sys.executable, str(project_dir / "scripts" / "generate_branding_assets.py")], check=True)
    print(f"[+] Verified application icon: {ico_file}")

    # 3. Clean prior build artifacts
    for d in ["build", "dist"]:
        target = project_dir / d
        if target.exists():
            print(f"[*] Cleaning previous {d} directory...")
            try:
                shutil.rmtree(str(target))
            except Exception as e:
                print(f"[!] Warning cleaning {d}: {e}")

    # 4. Invoke PyInstaller
    spec_file = project_dir / "gdrive_manager.spec"
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

    # 5. Verify output executable
    dist_dir = project_dir / "dist" / "GDriveManager"
    dist_exe = dist_dir / "GDriveManager.exe"
    if not dist_exe.exists():
        print("[x] Expected executable not found at:", dist_exe)
        sys.exit(1)

    size_mb = dist_exe.stat().st_size / (1024 * 1024)
    print(f"[✓] Executable built successfully: {dist_exe.resolve()} ({size_mb:.2f} MB)")

    # 6. Create Portable ZIP archive
    zip_name = "GDriveManager-Windows-x64.zip"
    zip_path = project_dir / "dist" / zip_name
    print(f"[*] Compressing portable archive: {zip_path.name}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, _, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zf.write(file_path, arcname)

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[✓] Portable distribution archive created: {zip_path.resolve()} ({zip_size_mb:.2f} MB)")

    print("=" * 65)
    print("[✓] Distribution Build Completed Successfully!")
    print(f"    - Onedir Folder: {dist_dir}")
    print(f"    - Executable:    {dist_exe}")
    print(f"    - Portable ZIP:  {zip_path}")
    print("=" * 65)

def main():
    build_executable()

if __name__ == "__main__":
    main()
