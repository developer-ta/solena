# Solena Plan

This file records the current planning for Solena so the project remains clear after a pause.

## Current state

- public vitrine is live on GitHub
- private core is separated and documented
- GPS and pipeline guide exist
- dialogue import UI exists
- PyQt6 desktop MVP exists
- Windows packaging flow exists
- launcher exists with environment checks

## What remains to do

### Immediate technical gaps

- test the desktop MVP interactively
- test the launcher end to end
- build a real Windows `.exe`
- validate the packaging output on a clean machine
- prepare the first Linux path later

### Product gaps

- connect the desktop MVP to a real refinement engine
- produce a real structured analysis from imported dialogues
- add clearer results for summary, risk register, and next step
- improve the user onboarding flow

### Quality gaps

- test the import flow with real project folders
- test error messages for missing dependencies
- verify the launcher on a machine without Python setup
- keep the public/private split clean

## Tomorrow

1. launch the desktop MVP
2. test folder import
3. test the private core GPS loading
4. test the pipeline preview
5. check that the launcher can prepare the environment correctly

## After tomorrow

1. build the Windows executable
2. test the `.exe` on Windows
3. write the first installer packaging plan
4. start the Linux packaging strategy
5. begin wiring real dialogue refinement output

## Final direction

Solena is moving toward a multi-stage AI-assisted development framework:

- import dialogues
- read the project GPS
- read the pipeline guide
- refine the dialogue into a structured version
- validate critical risks first
- move to lab modules
- initialize the project only after proof
- archive everything important

Long term, the project should become:

- a desktop app for local use
- a packaged installer for non-technical users
- a reproducible framework for AI-assisted project construction
- a tool that works on Windows first, then Linux and other systems later

## Principle

If a step is risky, validate it before moving on.
If a step is old, archive it.
If a step is public, keep the private core separate.
