import os
import sys
import subprocess
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT_DIR / ".venv"
DESKTOP_APP = ROOT_DIR / "desktop_app" / "main.py"
DESKTOP_REQUIREMENTS = ROOT_DIR / "desktop_app" / "requirements.txt"


def banner() -> None:
    print("=" * 68)


def command_version(command: str) -> str | None:
    try:
        result = subprocess.check_output(
            [command, "--version"],
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=(0 if os.name != "nt" else subprocess.CREATE_NO_WINDOW),
        )
        return result.strip()
    except Exception:
        return None
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


def ensure_python_toolchain(python_exe: Path) -> None:
    print("[PHASE 1] Checking Python toolchain...")
    python_version = command_version(str(python_exe))
    if python_version is None:
        raise RuntimeError("Python interpreter unavailable in the target environment.")

    print(f"[OK] Python ready: {python_version}")

def ensure_python_dependencies(python_exe: Path) -> None:
    print("[PHASE 2] Checking Python dependencies...")
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


def discover_js_workspaces() -> list[Path]:
    workspaces: list[Path] = []
    for package_json in ROOT_DIR.rglob("package.json"):
        if "node_modules" in package_json.parts:
            continue
        workspaces.append(package_json.parent)
    return sorted(set(workspaces))


def ensure_js_dependencies() -> None:
    workspaces = discover_js_workspaces()
    if not workspaces:
        print("[PHASE 3] No JavaScript workspace detected. Skipping JS setup.")
        return

    node_version = command_version("node")
    npm_version = command_version("npm")
    if node_version is None or npm_version is None:
        raise RuntimeError("Node.js/npm are required because a JavaScript workspace was detected.")

    print(f"[OK] Node ready: {node_version}")
    print(f"[OK] npm ready: {npm_version}")

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    for workspace in workspaces:
        node_modules = workspace / "node_modules"
        package_json = workspace / "package.json"
        if node_modules.exists():
            print(f"[OK] JavaScript dependencies already present: {workspace}")
            continue

        print(f"[PHASE 3] Installing JavaScript dependencies in {workspace}...")
        subprocess.check_call([npm_cmd, "install"], cwd=str(workspace), shell=True)
        print(f"[OK] JavaScript dependencies installed in {workspace}.")


def start_desktop_app(python_exe: Path) -> subprocess.Popen:
    print("[PHASE 4] Launching Solena desktop MVP...")
    return subprocess.Popen([str(python_exe), str(DESKTOP_APP)], cwd=str(ROOT_DIR))


def main() -> None:
    banner()

    if not DESKTOP_APP.exists():
        print(f"[ERROR] Desktop app not found: {DESKTOP_APP}")
        sys.exit(1)

    try:
        python_exe = ensure_virtualenv()
        ensure_python_toolchain(python_exe)
        ensure_python_dependencies(python_exe)
        ensure_js_dependencies()
    except Exception as exc:
        print(f"[ERROR] Startup validation failed: {exc}")
        input("Press Enter to exit...")
        sys.exit(1)

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
