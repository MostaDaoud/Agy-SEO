#!/usr/bin/env python3
"""Plan Gate: Lane B preconditions. Read-only, exits 1 if Codex cannot be gated safely."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

def say(k: str, v: str) -> None:
    print(f"{k:<22} {v}")

def main() -> int:
    home = Path.home()
    codex_script = home / ".claude" / "plugins" / "marketplaces" / "openai-codex" / "plugins" / "codex" / "scripts" / "codex-companion.mjs"
    fail = 0

    if os.path.exists("/.flatpak-info"):
        say("sandbox:", "FLATPAK  <- Codex bubblewrap cannot nest here")
        say("", "Use 'flatpak-spawn --host' or move the task to Lane A.")
        fail = 1
    else:
        say("sandbox:", "host (ok)")

    if sys.platform.startswith("win"):
        say("bubblewrap:", "n/a (Windows environment)")
    elif shutil.which("bwrap"):
        say("bubblewrap:", shutil.which("bwrap") or "found")
    else:
        say("bubblewrap:", "MISSING  <- Codex sandbox cannot start")
        fail = 1

    for binary in ("node", "codex"):
        loc = shutil.which(binary)
        if loc:
            say(f"{binary}:", loc)
        else:
            say(f"{binary}:", "MISSING")
            fail = 1

    if codex_script.is_file():
        say("companion:", "found")
    else:
        say("companion:", f"MISSING at {codex_script}")
        fail = 1

    config_toml = home / ".codex" / "config.toml"
    if config_toml.is_file():
        try:
            for line in config_toml.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("model"):
                    say("codex model:", line.strip())
                    break
        except OSError:
            pass

    print()
    if fail == 0:
        print("Lane B ready. Plan pass runs read-only (no --write).")
    else:
        print("Lane B NOT safe. Fix the above, or use Lane A.")

    return fail

if __name__ == "__main__":
    sys.exit(main())
