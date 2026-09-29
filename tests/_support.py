"""Shared helpers for offline tests. No test may touch the network, Git, a DB, or GSC."""

from __future__ import annotations

import importlib.util
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_script(name: str):
    """Import scripts/<name>.py as a module without running its main()."""
    spec = importlib.util.spec_from_file_location(f"dbc_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SideEffectBlocked(AssertionError):
    pass


def _blocked(*_args, **_kwargs):
    raise SideEffectBlocked("network/subprocess side effect attempted during tests")


def block_side_effects() -> None:
    """Fail loudly if code under test tries to open sockets or spawn git."""
    socket.socket.connect = _blocked  # type: ignore[assignment]
    socket.create_connection = _blocked  # type: ignore[assignment]
    subprocess.run = _blocked  # type: ignore[assignment]
    subprocess.Popen = _blocked  # type: ignore[assignment]


block_side_effects()
