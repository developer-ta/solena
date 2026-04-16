# Solena App Launcher

This launcher mirrors the startup philosophy used in your other project:

- verify the Python environment
- create a virtual environment if needed
- install missing Python dependencies
- verify Node.js/npm if a JavaScript workspace is present
- install JavaScript dependencies if needed
- start the Solena desktop MVP automatically

## Main entry point

- `1_CLIC_DEMARRER_SOLENA.py`

## What it launches

- the PyQt6 desktop MVP in `desktop_app/main.py`

## Philosophy

The launcher is meant to remove repetitive terminal steps for the developer.
It is the guided startup layer for Solena.
