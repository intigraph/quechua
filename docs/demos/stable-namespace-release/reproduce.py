"""Show the release file-set correction and matching-version controls."""

import json
import os
import subprocess
from pathlib import Path

BASE = "04071d1b4340692d0b33ed5aca856dd3b994efce"
before = json.loads(subprocess.check_output(["git", "show", BASE + ":release-please-config.json"]))
after = json.loads(Path("release-please-config.json").read_text())
paths = lambda config: [entry["path"] for entry in config["packages"]["."]["extra-files"]]
print(f"BASE {BASE}: release catalogs = {paths(before)}", flush=True)
print(f"CANDIDATE: release catalogs = {paths(after)}", flush=True)
print("$ uv run --locked --script scripts/publish_stable_namespace.py --selftest", flush=True)
subprocess.run([
    os.environ.get("UV_BIN", "uv"), "run", "--locked", "--script",
    "scripts/publish_stable_namespace.py", "--selftest",
], check=True)
