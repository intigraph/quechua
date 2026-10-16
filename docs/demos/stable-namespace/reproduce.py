"""Source-only demonstration: candidate publication and refusal controls."""

import os
import subprocess

BASE = "1c48fe1fc135fd2200b99919e0390fffa0b43654"


def present(path):
    return subprocess.run(
        ["git", "cat-file", "-e", f"{BASE}:{path}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


assert present("ns.ttl"), "base legacy catalog control missing"
assert not present("ns-stable.ttl"), "base already has candidate artifact"
print(f"BASE {BASE}: legacy catalog present; candidate catalog absent", flush=True)
print("CANDIDATE: exact mapped graph and one-to-one legacy identity links", flush=True)
command = [
    os.environ.get("UV_BIN", "uv"), "run", "--locked", "--script",
    "scripts/publish_stable_namespace.py", "--selftest",
]
print("$ uv run --locked --script scripts/publish_stable_namespace.py --selftest", flush=True)
subprocess.run(command, check=True)
