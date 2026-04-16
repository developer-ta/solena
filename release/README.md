# Solena Windows Packaging

This folder contains the MVP packaging flow for Windows.

## Goal

Produce a distributable `.exe` for the Solena desktop MVP.

## What the packaged app should do

- open without requiring the user to install Python
- load the desktop MVP
- keep the launcher logic simple for the developer

## Build flow

1. create the project virtual environment if needed
2. install build dependencies
3. run PyInstaller on `desktop_app/main.py`
4. collect the executable in `release/dist/`

## Developer note

This is the MVP packaging path.
It is intentionally simple and can later evolve into a proper installer (`.exe` setup, MSI, or another distribution format).

