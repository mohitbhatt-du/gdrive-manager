"""Version extraction and Git tag validation utility for CI/CD."""

import re
import sys
import argparse
from pathlib import Path

def get_app_version() -> str:
    base_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base_dir))
    from app.__version__ import __version__
    return __version__

def main():
    parser = argparse.ArgumentParser(description="GDrive Manager Version Utility")
    parser.add_argument("--verify-tag", help="Verify matching Git tag (e.g. v1.0.0)")
    parser.add_argument("--raw", action="store_true", help="Print raw version number only")
    args = parser.parse_args()

    version = get_app_version()

    # Validate semantic version format (e.g. 1.0.0, 1.0.1-rc1)
    semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"
    if not re.match(semver_pattern, version):
        print(f"[-] ERROR: Invalid semantic version format: '{version}'")
        sys.exit(1)

    if args.verify_tag:
        expected_tag = f"v{version}"
        if args.verify_tag != expected_tag:
            print(f"[-] ERROR: Tag mismatch! Git tag is '{args.verify_tag}' but app version is '{version}' (expected '{expected_tag}')")
            sys.exit(1)
        print(f"[✓] Version verification passed: Git tag '{args.verify_tag}' matches app version '{version}'")
        return

    if args.raw:
        print(version, end="")
    else:
        print(f"GDrive Manager Version: {version}")

if __name__ == "__main__":
    main()
