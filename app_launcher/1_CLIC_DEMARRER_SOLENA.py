import os
import sys
import subprocess
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT_DIR / ".venv"
DESKTOP_APP = ROOT_DIR / "desktop_app" / "main.py"
DESKTOP_REQUIREMENTS = ROOT_DIR / "desktop_app" / "requirements.txt"
PACKAGE_JSON = ROOT_DIR / "package.json"


def banner() -> None:
    print("=" * 68)
    print("      SOLENA APP LAUNCHER - 1 CLIC DEMARRER")
    print("      Guided startup for the Solena desktop MVP")
    print("=" * 68)


def venv_python_path() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_virtualenv() -> Path:
    python_exe = Path(sys.executable)
    target_python = venv_python_path()

    if target_python.exists():
        print(f"[OK] Virtual environment found: {target_python}")
        return target_python

    print("[PHASE 0] Creating virtual environment...")
    subprocess.check_call([str(python_exe), "-m", "venv", str(VENV_DIR)])
    print(f"[OK] Virtual environment created: {target_python}")
    return target_python


def ensure_python_dependencies(python_exe: Path) -> None:
    print("[PHASE 1] Checking Python dependencies...")
    try:
        subprocess.check_call(
            [str(python_exe), "-c", "import PyQt6"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[OK] PyQt6 already available in the target environment.")
        return
    except Exception:
        pass

    print("[INFO] Installing desktop dependencies...")
    subprocess.check_call([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(python_exe), "-m", "pip", "install", "-r", str(DESKTOP_REQUIREMENTS)])
    print("[OK] Python dependencies installed.")


def ensure_js_dependencies() -> None:
    if not PACKAGE_JSON.exists():
        print("[PHASE 2] No JavaScript project detected. Skipping JS setup.")
        return

    node_modules = ROOT_DIR / "node_modules"
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    if node_modules.exists():
        print("[OK] JavaScript dependencies already present.")
        return

    print("[PHASE 2] Installing JavaScript dependencies...")
    subprocess.check_call([npm_cmd, "install"], cwd=str(ROOT_DIR), shell=True)
    print("[OK] JavaScript dependencies installed.")


def start_desktop_app(python_exe: Path) -> subprocess.Popen:
    print("[PHASE 3] Launching Solena desktop MVP...")
    return subprocess.Popen([str(python_exe), str(DESKTOP_APP)], cwd=str(ROOT_DIR))


def main() -> None:
    banner()

    if not DESKTOP_APP.exists():
        print(f"[ERROR] Desktop app not found: {DESKTOP_APP}")
        sys.exit(1)

    python_exe = ensure_virtualenv()
    ensure_python_dependencies(python_exe)
    ensure_js_dependencies()

    process = start_desktop_app(python_exe)
    print("[READY] Solena is running. Leave this window open.")

    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Launcher interrupted by user.")
        process.terminate()


if __name__ == "__main__":
    main()
