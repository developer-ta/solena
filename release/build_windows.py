import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DESKTOP_MAIN = ROOT_DIR / "desktop_app" / "main.py"
BUILD_DIR = ROOT_DIR / "release" / "build"
DIST_DIR = ROOT_DIR / "release" / "dist"
SPEC_DIR = ROOT_DIR / "release" / "spec"
LAUNCHER_NAME = "SolenaDesktop"


def ensure_desktop_target() -> None:
    if not DESKTOP_MAIN.exists():
        raise FileNotFoundError(f"Desktop entry point missing: {DESKTOP_MAIN}")


def ensure_pyinstaller() -> None:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "PyInstaller", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(ROOT_DIR / "release" / "requirements-build.txt")]
        )


def clean_previous_builds() -> None:
    for folder in [BUILD_DIR, DIST_DIR, SPEC_DIR]:
        if folder.exists():
            shutil.rmtree(folder)


def build_exe() -> None:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        LAUNCHER_NAME,
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(SPEC_DIR),
        str(DESKTOP_MAIN),
    ]
    subprocess.check_call(command, cwd=str(ROOT_DIR))


def main() -> None:
    print("=" * 68)
    print("Solena Windows Packaging")
    print("=" * 68)
    ensure_desktop_target()
    ensure_pyinstaller()
    clean_previous_builds()
    build_exe()
    print(f"[OK] Build complete: {DIST_DIR / (LAUNCHER_NAME + '.exe')}")


if __name__ == "__main__":
    main()
