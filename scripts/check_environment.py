"""System and environment verification utility for GDrive Manager developers and CI."""

import platform
import sys
from pathlib import Path


def check_env():
    print("=" * 65)
    print(" GDrive Manager - System & Development Environment Check")
    print("=" * 65)

    base_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base_dir))

    all_ok = True

    # 1. OS & Architecture Check
    os_name = platform.system()
    arch = platform.architecture()[0]
    print(f"[*] Operating System: {os_name} {platform.release()} ({arch})")
    if os_name != "Windows":
        print("[-] WARNING: GDrive Manager is designed exclusively for Microsoft Windows.")
        all_ok = False
    else:
        print("[✓] Supported Windows platform detected.")

    # 2. Python Version Check
    py_ver = sys.version_info
    print(f"[*] Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if (py_ver.major, py_ver.minor) < (3, 12):
        print("[-] WARNING: Python >= 3.12 is recommended.")
        all_ok = False
    else:
        print("[✓] Python version requirement met.")

    # 3. Bundled Rclone Check
    from app.services.rclone_service import RcloneService

    svc = RcloneService()
    exe = svc.rclone_exe
    if exe and Path(exe).exists():
        ver = svc.get_version() or "v1.76.0"
        print(f"[✓] Rclone Engine: Found ({exe}) - Version: {ver}")
    else:
        print("[-] Rclone Engine: NOT FOUND in bundled directory or PATH.")
        all_ok = False

    # 4. WinFsp Virtual Filesystem Driver
    from app.utils.platform_checks import is_winfsp_installed

    if is_winfsp_installed():
        print("[✓] WinFsp Driver: Active and ready for virtual drive mounting.")
    else:
        print("[!] WinFsp Driver: Not installed. Run 'winget install WinFsp.WinFsp' for streaming mode.")

    # 5. App Data Permissions
    from app.utils.paths import get_app_data_dir

    app_data = get_app_data_dir()
    print(f"[*] App Data Directory: {app_data}")
    try:
        test_file = app_data / ".perm_check"
        test_file.touch()
        test_file.unlink()
        print("[✓] User LocalAppData write permissions verified.")
    except Exception as e:
        print(f"[-] AppData write permission failed: {e}")
        all_ok = False

    print("=" * 65)
    if all_ok:
        print("[✓] Environment verification passed successfully!")
    else:
        print("[!] Environment verification completed with warnings/errors.")
    print("=" * 65)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(check_env())
