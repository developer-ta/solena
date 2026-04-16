# Solena

Solena is the public vitrine for an AI-assisted software development workflow.

It presents the project clearly on GitHub while keeping the sensitive working material in a separate private repository.

## What this repo is

- a clean public face for Solena
- a small GUI landing page
- a high-level explanation of the workflow
- a visible, professional project identity

## What this repo is not

- it is not the private working memory
- it is not the raw dialogue archive
- it is not the internal governance layer

## Public features

- a responsive landing page
- a clear project statement
- a visible workflow overview
- a clean structure for GitHub
- a desktop MVP entry point for importing dialogue folders

## Tech stack

- HTML
- CSS
- JavaScript

## Run locally

Open `index.html` in a browser.

## Project structure

- `index.html` main entry point
- `styles.css` visual design
- `app.js` light interaction
- `desktop_app/` PyQt6 desktop MVP
- `SOLENA_REPOSITORIES.md` public/private split map

## Desktop MVP

Solena also ships with a small PyQt6 desktop entry point:

- choose the private core folder
- import a folder of dialogues
- load the GPS and pipeline guide
- preview a structured JSON result

Run it with:

```bash
python desktop_app/main.py
```

## One-click launcher

For a more guided startup, use the launcher in `app_launcher/`.

It checks the Python environment, prepares the desktop dependencies, and starts the desktop MVP automatically.

```bash
python app_launcher/1_CLIC_DEMARRER_SOLENA.py
```

## Windows packaging

To build a distributable Windows executable, use the release scripts in `release/`.

The build flow:

1. create or reuse the Python virtual environment
2. install packaging dependencies
3. build the desktop app with PyInstaller
4. collect the executable in `release/dist/`

See `release/README.md` for the exact build steps.

## Private core

The private core lives in `private-core/` and contains:

- raw dialogues
- internal notes
- governance rules
- versioning material
- lab modules

## Positioning

The public repo shows the project identity and its method at a high level.
The private core keeps the deeper knowledge, drafts, and experimental material separate.

## Repository split

- public repo: visible vitrine, GUI, and high-level explanation
- private repo: sensitive workflow, dialogues, governance, and lab material

See [`SOLENA_REPOSITORIES.md`](SOLENA_REPOSITORIES.md) for the exact split.
