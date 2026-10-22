"""Single-instance guard. Two bots on one state file and one account would both
act on the same signal and overwrite each other's state, so the second one to
start must refuse. The OS releases the lock when the process exits, even on a
crash, so there is never a stale lock to clean up."""
from __future__ import annotations

import os


def acquire(state_file: str):
    """Lock <state_file>.lock or exit. Keep the returned handle open for the
    life of the process."""
    path = state_file + ".lock"
    f = open(path, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        raise SystemExit(f"Another copy of this bot is already running ({path} is locked). "
                         "Stop it first (Ctrl-C in its window) -- two copies would double-trade.")
    return f


def is_held(state_file: str) -> bool:
    """True if a running bot holds the lock for state_file. Probes by taking
    the lock for an instant and releasing it at once."""
    path = state_file + ".lock"
    if not os.path.exists(path):
        return False
    with open(path, "a+") as f:
        try:
            if os.name == "nt":
                import msvcrt
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
        except OSError:
            return True
    return False
