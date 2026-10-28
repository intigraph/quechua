#!/usr/bin/env python3
"""Read-only Quechua orientation; release builds embed guidance and version."""

import argparse
import json
import queue
import re
import stat
import threading
import time
from pathlib import Path

# The release builder replaces these assignments with immutable source values.
PRIMER = None
VERSION = None
DEADLINE = 0.650
LIMIT = 64 * 1024


def read_small(path):
    """Read one bounded regular file without creating or modifying it."""
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("not a regular file")
    with path.open("rb") as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("file exceeds bound")
    return data.decode("utf-8")


def package_state(directory, version, installed):
    """Describe a local identity; never imply validation of vocabulary bytes."""
    mode = "installed" if installed else "source"
    path = directory / (".release.json" if installed else "version.txt")
    summary = {"mode": mode, "path": str(path)}
    try:
        if not installed:
            if read_small(path).strip() != version:
                raise ValueError("version mismatch")
        else:
            identity = json.loads(read_small(path))
            if not isinstance(identity, dict) or identity.get("tag") != "v" + version:
                raise ValueError("identity mismatch")
            assets = identity.get("assets")
            if not isinstance(assets, dict) or not assets or len(assets) > 32:
                raise ValueError("invalid assets")
            required = {"quechua-ns-v" + version + ".ttl", "quechua-cli-v" + version + ".py"}
            if not required.issubset(assets):
                raise ValueError("incomplete identity")
            if not all(isinstance(k, str) and isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for k, v in assets.items()):
                raise ValueError("invalid digest")
            summary.update(listed_assets=len(assets), verification="identity_only")
        summary["vocabulary_version"] = version
        return {"status": "ok", "summary": summary}
    except FileNotFoundError:
        summary["reason"] = "identity_absent" if installed else "version_absent"
        status = "absent"
    except (OSError, ValueError, UnicodeError):
        summary["reason"] = "release_identity" if installed else "source_version"
        status = "unreadable"
    summary["next"] = ("curl -fsSL https://raw.githubusercontent.com/scbrown/quechua/main/install.sh"
                       " | STACK_VERSION=v" + version + " sh")
    return {"status": status, "summary": summary}


def bounded_state(directory, version, installed):
    """Keep a slow filesystem read from blocking orientation past the budget."""
    started = time.monotonic()
    result = queue.Queue(maxsize=1)
    worker = threading.Thread(target=lambda: result.put(package_state(directory, version, installed)), daemon=True)
    worker.start()
    try:
        state = result.get(timeout=DEADLINE)
    except queue.Empty:
        state = {"status": "partial", "summary": {
            "path": str(directory / (".release.json" if installed else "version.txt")),
            "reason": "deadline", "next": "quechua prime --static"}}
    state["elapsed_ms"] = int((time.monotonic() - started) * 1000)
    return state


def select_section(primer, name):
    """Select a case-insensitive heading prefix and enumerate available sections."""
    blocks = primer.split("\n## ")[1:]
    sections = [block.split("\n", 1)[0] for block in blocks]
    if name is None:
        return primer, sections
    for heading, block in zip(sections, blocks):
        if name.strip() and heading.casefold().startswith(name.strip().casefold()):
            return "## " + block, sections
    raise ValueError("unknown primer section " + repr(name) + "; sections: " + ", ".join(sections))


def live_lines(state):
    """Condense local state into bounded, single-line fields."""
    summary = state["summary"]
    lines = ["Package identity: " + summary["path"], "State: " + state["status"]]
    if "reason" in summary:
        lines[-1] += " (" + summary["reason"] + ")"
    if "vocabulary_version" in summary:
        lines.append("Vocabulary release version: " + summary["vocabulary_version"])
    if "listed_assets" in summary:
        lines.append("Listed assets: " + str(summary["listed_assets"]) + " (identity only)")
    if "next" in summary:
        lines.append("Next: " + summary["next"])
    lines.append("Read: " + str(state["elapsed_ms"]) + " ms")
    return [line.replace("\n", "\\n").replace("\r", "\\r") for line in lines]


def main(argv=None):
    """Print static orientation followed by optional local state."""
    parser = argparse.ArgumentParser(prog="quechua", description="Quechua vocabulary orientation")
    sub = parser.add_subparsers(dest="command", required=True)
    prime = sub.add_parser("prime", help="read-only agent primer and vocabulary release version")
    prime.add_argument("--brief", action="store_true", help="5 to 10 lines for stack aggregation")
    prime.add_argument("--json", action="store_true", help="structured stack-prime/1 output")
    prime.add_argument("--static", action="store_true", help="skip local package-state reads")
    prime.add_argument("--section", help="one section by case-insensitive heading prefix")
    prime.add_argument("--data-dir", type=Path, help="explicit package directory to inspect")
    args = parser.parse_args(argv)
    if args.brief and args.section is not None:
        parser.error("--brief and --section cannot be combined")
    installed = VERSION is not None
    root = Path(__file__).resolve().parent if installed else Path(__file__).resolve().parents[1]
    try:
        primer = PRIMER if installed else read_small(root / "docs/agent-primer.md")
        version = VERSION if installed else read_small(root / "version.txt").strip()
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
            raise ValueError("invalid version")
    except (OSError, ValueError, UnicodeError):
        parser.exit(2, "Quechua source primer/version unreadable; use a complete checkout or release CLI.\n")
    try:
        text, sections = select_section(primer, args.section)
    except ValueError as error:
        parser.error(str(error))
    state = {"status": "skipped", "elapsed_ms": 0, "summary": {}} if args.static else bounded_state(
        args.data_dir or root, version, installed)
    document = {"sections": sections}
    if not args.brief:
        document["text"] = text
    if args.json:
        print(json.dumps({"schema": "stack-prime/1", "tool": "quechua", "version": version,
                          "primer": document, "live": state,
                          "status": "ok" if state["status"] in ("ok", "skipped") else "degraded"}))
    elif args.brief:
        lines = ["quechua " + version + ": shared vocabulary and opt-in SHACL shapes"]
        if args.static:
            what, _ = select_section(primer, "What quechua is")
            lines.extend(line for line in what.splitlines()[1:] if line.strip())
        else:
            lines.extend(live_lines(state))
        lines.append("Run `quechua prime` for the full primer.")
        print("\n".join(lines))
    else:
        print(text.rstrip())
        if args.section is None:
            print("\nVocabulary release version: " + version)
        if not args.static:
            print("\n## Live state\n\n" + "\n".join(live_lines(state)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
