#!/usr/bin/env python3
"""Generate a standalone release CLI or synchronize primer documentation."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render_cli(root=ROOT):
    primer = (root / "docs/agent-primer.md").read_text()
    version = (root / "version.txt").read_text().strip()
    template = (root / "scripts/prime.py").read_text()
    return template.replace("PRIMER = None", "PRIMER = " + repr(primer), 1).replace("VERSION = None", "VERSION = " + repr(version), 1)


def skill_text(root=ROOT):
    return ("---\nname: quechua\ndescription: Find vocabulary terms and orient agents with Quechua prime.\n---\n\n"
            "<!-- BEGIN quechua prime -->\n" + (root / "docs/agent-primer.md").read_text() + "<!-- END quechua prime -->\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write standalone CLI release asset")
    parser.add_argument("--sync", action="store_true", help="generate skill and reference primer copies")
    parser.add_argument("--expect-version", help="refuse a CLI asset with a mismatched release tag")
    args = parser.parse_args()
    if args.expect_version and args.expect_version != "v" + (ROOT / "version.txt").read_text().strip():
        parser.error("release tag differs from version.txt")
    if args.output:
        args.output.write_text(render_cli())
        args.output.chmod(0o755)
    if args.sync:
        skill = ROOT / "skills/quechua/SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(skill_text())
        (ROOT / "docs/prime.md").write_text((ROOT / "docs/agent-primer.md").read_text())
    if not args.output and not args.sync:
        parser.error("choose --output or --sync")


if __name__ == "__main__":
    main()
