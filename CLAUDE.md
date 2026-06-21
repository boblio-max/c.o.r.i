# c.o.r.i (CORI)

CORI is the Computer Operated Robot Interface — a real-time robotics stack with hand tracking, inverse kinematics, dashboard visualization, server/clients for headless targets, and small AI helpers. The repo is a Python monorepo with a `core` runtime, a `client`, a `server`, a `robot` package, hand tracking, a math/IK layer, and assorted tools.

## Build / Test / Lint Commands

- Install: `pip install -r requirements.txt` (creates `pygame`, `mediapipe`, `opencv-python`, `torch`, `g4f`, `websockets`, `adafruit-circuitpython-servokit`, etc.)
- Build: not applicable (interpreted Python); `origin build` may apply to the embedded `.or` sources
- Test: no automated tests; verify with module entry points below
- Lint: not configured
- Dev / run:
  - Hand tracking: `python hand_tracking/handtracking.py`
  - Server: `python server/server.py`
  - Client: `python client/client.py`
  - Robot module: `python robot/main.py` (or the entry point defined in `robot/`)
  - Dashboard: launch the script in `dash/`

## Code Style Rules

- Language/version: Python 3.10+; venv at `.venv/` is the recommended interpreter
- Paradigm: package-per-domain (`core`, `server`, `client`, `robot`, `math`, etc.) with imperative entry-point scripts
- Types: type hints are sparse; Pydantic-style models are not used
- Formatting: PEP 8 (no formatter configured)
- Imports / module style: absolute imports of sibling top-level packages
- Dependencies: hardware-dependent (`adafruit-circuitpython-servokit`, `mediapipe`, `torch`, `g4f`); see `requirements.txt`

## Verification Criteria

Before claiming any task done, Claude MUST:
1. Run `python -c "import core, math, misc"` (and any other touched package) to confirm imports resolve.
2. Confirm `pip install -r requirements.txt` succeeds in a clean virtualenv (hardware-only packages may be skipped if the dev box has none).
3. Boot the dashboard or server entry point and confirm it opens without a traceback.
4. Report the exact commands run and their outcomes in the final message.
