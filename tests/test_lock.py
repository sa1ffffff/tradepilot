import subprocess
import sys


from bot.lock import acquire


def test_second_instance_is_refused(tmp_path):
    state = str(tmp_path / "state.json")
    held = acquire(state)
    try:
        # a separate process, as a second bot would be
        code = f"from bot.lock import acquire; acquire({state!r})"
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert r.returncode != 0 and "already running" in r.stderr
    finally:
        held.close()


def test_lock_is_released_when_holder_closes(tmp_path):
    state = str(tmp_path / "state.json")
    acquire(state).close()
    acquire(state).close()  # would raise SystemExit if the lock were stale
