#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

PYTHON=
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        PYTHON=$candidate
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3.10 or newer was not found. Please install Python and try again." >&2
    exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    if ! "$PYTHON" -m venv .venv; then
        echo "Virtual environment creation failed. Ensure the Python venv module is installed." >&2
        exit 1
    fi
fi

if ! cmp -s requirements.txt .venv/requirements.installed; then
    echo "Installing dependencies..."
    if ! .venv/bin/python -m pip install --upgrade pip; then
        echo "pip upgrade failed." >&2
        exit 1
    fi
    if ! .venv/bin/python -m pip install -r requirements.txt; then
        echo "Dependency installation failed." >&2
        exit 1
    fi
    cp requirements.txt .venv/requirements.installed
fi

exec .venv/bin/python src/gui.py
