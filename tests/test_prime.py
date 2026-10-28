"""Prime conformance: offline, bounded, read-only and packaged from one source.

Unreachable-server conformance is inapplicable: Quechua has no server read.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BUILD = runpy.run_path(str(ROOT / "scripts/build-prime.py"))
RUNTIME = runpy.run_path(str(ROOT / "scripts/prime.py"))


def load_tests(loader, tests, pattern):
    # Existing CI unittest discovery also owns the real standalone installer controls.
    tests.addTests(loader.loadTestsFromTestCase(runpy.run_path(str(ROOT / "scripts/test-install-release.py"))["PackageInstall"]))
    return tests


def snapshot(root):
    result = {}
    for path in [root] + list(root.rglob("*")):
        info = path.stat()
        result[str(path.relative_to(root))] = (info.st_mode, info.st_size, info.st_mtime_ns,
                                               path.read_bytes() if path.is_file() else None)
    return result


class Prime(unittest.TestCase):
    def test_primer_copies_and_required_sections(self):
        self.assertEqual((ROOT / "skills/quechua/SKILL.md").read_text(), BUILD["skill_text"](),
                         "stale skill: run python3 scripts/build-prime.py --sync")
        self.assertEqual((ROOT / "docs/prime.md").read_text(), (ROOT / "docs/agent-primer.md").read_text(),
                         "stale docs: run python3 scripts/build-prime.py --sync")
        _, sections = RUNTIME["select_section"]((ROOT / "docs/agent-primer.md").read_text(), None)
        self.assertEqual(sections[:4], ["What quechua is", "Agent workflow", "Core commands", "MCP tools"])
        self.assertEqual(sections[-1], "Next steps")

    def run_cli(self, script, *args, home):
        env = dict(os.environ, HOME=str(home), PYTHONDONTWRITEBYTECODE="1")
        started = time.monotonic()
        result = subprocess.run([sys.executable, str(script), "prime", *args], env=env,
                                cwd=home.parent, capture_output=True, text=True, timeout=2)
        self.assertLess(time.monotonic() - started, 1)
        return result

    def test_release_cli_contract_missing_state_and_no_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cli = root / "quechua.py"
            cli.write_text(BUILD["render_cli"]())
            home = root / "empty-home"
            home.mkdir()
            before = snapshot(root)
            for args in [("--json",), ("--static", "--json"), ("--brief", "--json"),
                         ("--brief",), ("--brief", "--static"), (), ("--static",)]:
                with self.subTest(args=args):
                    result = self.run_cli(cli, *args, home=home)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if "--json" in args:
                        obj = json.loads(result.stdout)
                        self.assertTrue({"schema", "tool", "version", "primer", "live", "status"}.issubset(obj))
                        self.assertEqual(obj["schema"], "stack-prime/1")
                        self.assertEqual(obj["tool"], "quechua")
                        self.assertEqual(obj["version"], (ROOT / "version.txt").read_text().strip())
                        self.assertTrue(obj["primer"]["sections"])
                        self.assertEqual("text" in obj["primer"], "--brief" not in args)
                        self.assertTrue({"status", "elapsed_ms", "summary"}.issubset(obj["live"]))
                        self.assertEqual(obj["live"]["status"], "skipped" if "--static" in args else "absent")
                        self.assertEqual(obj["status"], "ok" if "--static" in args else "degraded")
                    elif "--brief" in args:
                        lines = result.stdout.strip().splitlines()
                        self.assertGreaterEqual(len(lines), 5)
                        self.assertLessEqual(len(lines), 10)
                        self.assertTrue(lines[0].startswith("quechua " + (ROOT / "version.txt").read_text().strip() + ": "))
                        self.assertEqual(lines[-1], "Run `quechua prime` for the full primer.")
                    else:
                        self.assertIn("# Quechua agent primer", result.stdout)
                        self.assertIn("## Next steps", result.stdout)
                        self.assertEqual("## Live state" in result.stdout, "--static" not in args)
                        if "--static" not in args:
                            self.assertIn("State: absent", result.stdout)
                            self.assertIn(str(root / ".release.json"), result.stdout)
                            self.assertIn("Next: curl -fsSL", result.stdout)
                    self.assertEqual(before, snapshot(root))
            result = self.run_cli(ROOT / "scripts/prime.py", "--json", home=home)
            self.assertEqual(json.loads(result.stdout)["live"]["summary"]["mode"], "source")
            self.assertEqual(before, snapshot(root))

    def test_section_selection_and_real_usage_exit_two(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cli = root / "quechua.py"
            cli.write_text(BUILD["render_cli"]())
            result = self.run_cli(cli, "--section", "cOrE", "--static", home=root / "home")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.startswith("## Core commands"))
            self.assertNotIn("## MCP tools", result.stdout)
            for args in [("--section", "unknown"), ("--not-a-flag",), ("--section", ""),
                         ("--brief", "--section", "core")]:
                result = self.run_cli(cli, *args, home=root / "home")
                self.assertEqual(result.returncode, 2, result.stderr)
                if "unknown" in args:
                    self.assertIn("What quechua is, Agent workflow, Core commands, MCP tools", result.stderr)

    def test_identity_bounds_and_metadata_are_read_only(self):
        version = (ROOT / "version.txt").read_text().strip()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cli = root / "quechua.py"
            cli.write_text(BUILD["render_cli"]())
            ns = "quechua-ns-v" + version + ".ttl"
            asset = "quechua-cli-v" + version + ".py"
            identity = {"tag": "v" + version, "assets": {ns: "a" * 64, asset: "b" * 64}}
            (root / ns).write_text("non-vocabulary fixture")
            marker = root / ".release.json"
            marker.write_text(json.dumps(identity))
            before = snapshot(root)
            result = self.run_cli(cli, "--json", "--data-dir", str(root), home=root / "absent")
            self.assertEqual(result.returncode, 0, result.stderr)
            obj = json.loads(result.stdout)
            self.assertEqual(obj["status"], "ok")
            self.assertEqual(obj["live"]["summary"]["verification"], "identity_only")
            self.assertEqual(before, snapshot(root))
            for bad in [[], {}, {"tag": "v999.0.0", "assets": {}}, {"tag": "v" + version, "assets": {ns: "bad"}}]:
                marker.write_text(json.dumps(bad))
                self.assertEqual(RUNTIME["package_state"](root, version, True)["status"], "unreadable", bad)
            marker.write_text("x" * (65536 + 1))
            self.assertEqual(RUNTIME["package_state"](root, version, True)["status"], "unreadable")
            marker.write_bytes(b"\xff")
            self.assertEqual(RUNTIME["package_state"](root, version, True)["status"], "unreadable")
            marker.unlink()
            marker.mkdir()
            self.assertEqual(RUNTIME["package_state"](root, version, True)["status"], "unreadable")

    def test_time_budget_reports_partial_and_elapsed(self):
        done = threading.Event()
        release = threading.Event()
        def slow(*args):
            release.wait(timeout=2)
            done.set()
            return {"status": "ok", "summary": {}}
        fn = RUNTIME["bounded_state"]
        started = time.monotonic()
        try:
            with patch.dict(fn.__globals__, package_state=slow):
                state = fn(Path("unused"), "1.2.3", True)
            self.assertEqual(state["status"], "partial")
            self.assertEqual(state["summary"]["reason"], "deadline")
            self.assertGreaterEqual(state["elapsed_ms"], 0)
            self.assertLess(state["elapsed_ms"], 1000)
            self.assertLess(time.monotonic() - started, 1)
        finally:
            release.set()
            self.assertTrue(done.wait(timeout=1))

    def test_builder_refuses_wrong_tag_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "cli.py"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/build-prime.py"),
                                     "--expect-version", "v999.0.0", "--output", str(target)],
                                    capture_output=True, text=True, timeout=2)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())

    def test_source_identity_missing_and_version_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(RUNTIME["package_state"](root, "1.2.3", False)["status"], "absent")
            (root / "version.txt").write_text("different")
            self.assertEqual(RUNTIME["package_state"](root, "1.2.3", False)["status"], "unreadable")


if __name__ == "__main__":
    unittest.main()
