#!/usr/bin/env python3
"""Offline package fixtures exercise the real standalone installer."""
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from urllib.request import urlopen as real_urlopen
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {'kind': 'data', 'assets': ['quechua-ns-{tag}.ttl', 'quechua-action-governance-shapes-{tag}.ttl', 'quechua-alignments-{tag}.ttl', 'quechua-camayoc-shapes-{tag}.ttl', 'quechua-data-catalog-shapes-{tag}.ttl', 'quechua-observation-governance-shapes-{tag}.ttl', 'quechua-ontology-shapes-{tag}.ttl', 'quechua-work-item-shapes-{tag}.ttl'], 'checksum': 'SHA256SUMS.txt', 'repo': 'quechua'}
TAG = 'v1.2.3'
VERSION = '1.2.3'


class PackageInstall(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='package-install-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.release = self.root / 'release'
        self.release.mkdir()
        self.prefix = self.root / 'prefix'
        (self.prefix / 'bin').mkdir(parents=True)
        self.previous = self.prefix / 'bin' / CONFIG.get('commands', ['prior'])[0]
        self.previous.write_text('previous bytes')
        self.env = dict(os.environ, HOME=str(self.root / 'home'), STACK_VERSION=TAG,
                        STACK_INSTALL_ROOT=str(self.prefix), STACK_RELEASE_BASE_URL=self.release.as_uri())
        self.names = [name.format(tag=TAG, version=VERSION) for name in CONFIG['assets']]
        self.fixture()
        self.latest = {"tag_name": TAG, "draft": False, "prerelease": False}

    def fixture(self):
        for name in self.names:
            path = self.release / name
            if CONFIG['kind'] == 'wheel':
                distribution = CONFIG['package'].replace('-', '_')
                metadata = distribution + '-' + VERSION + '.dist-info/'
                with zipfile.ZipFile(path, 'w') as wheel:
                    wheel.writestr('fixture_cli.py', 'def main():\n    print("fixture ' + VERSION + '")\n')
                    wheel.writestr(metadata + 'METADATA', 'Metadata-Version: 2.1\nName: ' + CONFIG['package'] + '\nVersion: ' + VERSION + '\n')
                    wheel.writestr(metadata + 'WHEEL', 'Wheel-Version: 1.0\nGenerator: fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n')
                    wheel.writestr(metadata + 'entry_points.txt', '[console_scripts]\n' + '\n'.join(command + ' = fixture_cli:main' for command in CONFIG['commands']))
                    wheel.writestr(metadata + 'RECORD', '')
            elif CONFIG['kind'] == 'source':
                data = json.dumps({'name': 'camayoc', 'version': VERSION}).encode()
                with tarfile.open(path, 'w:gz') as bundle:
                    member = tarfile.TarInfo('camayoc-' + TAG + '/.claude-plugin/plugin.json')
                    member.size, member.mode = len(data), 0o644
                    bundle.addfile(member, io.BytesIO(data))
            else:
                path.write_text('@prefix example: <https://example.org/> .\nexample:Thing a example:Class .\n')
        manifest = ''.join(hashlib.sha256((self.release / name).read_bytes()).hexdigest() + '  ' + name + '\n' for name in self.names)
        (self.release / CONFIG['checksum']).write_text(manifest)

    def open_release(self, request, **kwargs):
        if request.full_url.startswith('https://api.github.com/repos/scbrown/'):
            return io.BytesIO(json.dumps(self.latest).encode())
        return real_urlopen(request, **kwargs)

    def run_installer(self, system='Linux'):
        script = (ROOT / 'install.sh').read_text().split("<<'PYINSTALL'\n", 1)[1].rsplit('PYINSTALL', 1)[0]
        stdout, stderr = io.StringIO(), io.StringIO()
        status = 0
        with patch.dict(os.environ, self.env, clear=True), patch('sys.argv', ['install.sh']), patch('urllib.request.urlopen', side_effect=self.open_release), \
             patch('platform.system', return_value=system), redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exec(compile(script, str(ROOT / 'install.sh'), 'exec'), {'__name__': '__main__'})
            except SystemExit as error:
                status = error.code
        return status, stdout.getvalue(), stderr.getvalue()

    def assert_preserved(self, result):
        self.assertNotEqual(result[0], 0, result)
        self.assertEqual(self.previous.read_text(), 'previous bytes')
        self.assertFalse(self.previous.is_symlink())
        self.assertNotIn('Installed verified', result[1])

    def add_prime_asset(self, version=VERSION):
        import runpy
        builder = runpy.run_path(str(ROOT / 'scripts/build-prime.py'))
        source = self.root / 'cli-source'
        (source / 'scripts').mkdir(parents=True)
        (source / 'docs').mkdir()
        (source / 'version.txt').write_text(version)
        (source / 'docs/agent-primer.md').write_text((ROOT / 'docs/agent-primer.md').read_text())
        (source / 'scripts/prime.py').write_text((ROOT / 'scripts/prime.py').read_text())
        name = 'quechua-cli-' + TAG + '.py'
        (self.release / name).write_text(builder['render_cli'](source))
        self.names.append(name)
        (self.release / CONFIG['checksum']).write_text(''.join(
            hashlib.sha256((self.release / n).read_bytes()).hexdigest() + '  ' + n + '\n' for n in self.names))
        return name

    def test_prime_asset_installs_and_runs_without_package_writes(self):
        name = self.add_prime_asset()
        result = self.run_installer()
        self.assertEqual(result[0], 0, result)
        entry = self.prefix / 'bin/quechua'
        self.assertTrue(entry.is_symlink())
        self.assertEqual(entry.resolve(), self.prefix / 'share/quechua' / TAG / name)
        destination = entry.resolve().parent
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in destination.iterdir()}
        result = subprocess.run([str(entry), 'prime', '--json'], capture_output=True, text=True, env=self.env, timeout=2)
        self.assertEqual(result.returncode, 0, result.stderr)
        obj = json.loads(result.stdout)
        self.assertEqual(obj['version'], VERSION)
        self.assertEqual(obj['live']['status'], 'ok')
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in destination.iterdir()})
        self.assertEqual(self.run_installer()[0], 0)

    def test_bad_cli_digest_preserves_existing_entry(self):
        name = self.add_prime_asset()
        old = self.prefix / 'bin/quechua'
        old.write_text('prior CLI')
        (self.release / name).write_text('corrupted')
        self.assertNotEqual(self.run_installer()[0], 0)
        self.assertEqual(old.read_text(), 'prior CLI')
        self.assertFalse(old.is_symlink())

    def test_cli_smoke_version_refusal_preserves_existing_entry(self):
        self.add_prime_asset(version='9.9.9')
        old = self.prefix / 'bin/quechua'
        old.write_text('prior CLI')
        self.assertNotEqual(self.run_installer()[0], 0)
        self.assertEqual(old.read_text(), 'prior CLI')
        self.assertFalse((self.prefix / 'share/quechua' / TAG).exists())

    def test_legacy_data_only_release_keeps_prior_cli(self):
        old = self.prefix / 'bin/quechua'
        old.write_text('prior CLI')
        result = self.run_installer()
        self.assertEqual(result[0], 0, result)
        self.assertIn('has no prime CLI', result[1])
        self.assertEqual(old.read_text(), 'prior CLI')

    def test_actual_installer_installs_verified_package(self):
        result = self.run_installer()
        self.assertEqual(result[0], 0, result)
        destination = self.prefix / 'share' / CONFIG['repo'] / TAG
        self.assertEqual(json.loads((destination / '.release.json').read_text())['tag'], TAG)
        if CONFIG['kind'] == 'wheel':
            for command in CONFIG['commands']:
                self.assertIn(VERSION, subprocess.check_output([str(self.prefix / 'bin' / command)], text=True))
        else:
            self.assertEqual(self.previous.read_text(), 'previous bytes')

    def test_latest_release_selection_installs_the_resolved_tag(self):
        self.env.pop('STACK_VERSION')
        result = self.run_installer()
        self.assertEqual(result[0], 0, result)
        self.assertIn(TAG, result[1])

    def test_prerelease_cannot_become_latest_stable_install(self):
        self.env.pop('STACK_VERSION')
        self.latest['prerelease'] = True
        self.assert_preserved(self.run_installer())

    def test_reinstall_of_intact_release_succeeds(self):
        self.assertEqual(self.run_installer()[0], 0)
        result = self.run_installer()
        self.assertEqual(result[0], 0, result)

    def test_tampered_existing_install_cannot_claim_verified_success(self):
        self.assertEqual(self.run_installer()[0], 0)
        destination = self.prefix / 'share' / CONFIG['repo'] / TAG
        if CONFIG['kind'] == 'wheel':
            target = self.previous.resolve()
        elif CONFIG['kind'] == 'source':
            target = destination / '.claude-plugin/plugin.json'
        else:
            target = destination / self.names[0]
        target.write_text('tampered installed bytes')
        result = self.run_installer()
        self.assertNotEqual(result[0], 0, result)
        self.assertNotIn('Installed verified', result[1])
        self.assertEqual(target.read_text(), 'tampered installed bytes')

    def test_corrupt_checksum_preserves_previous(self):
        path = self.release / self.names[0]
        path.write_bytes(path.read_bytes() + b'corrupt')
        self.assert_preserved(self.run_installer())

    def test_missing_asset_preserves_previous(self):
        (self.release / self.names[0]).unlink()
        self.assert_preserved(self.run_installer())

    def test_unsupported_platform_preserves_previous(self):
        self.assert_preserved(self.run_installer(system='UnsupportedOS'))

    def test_missing_checksum_entry_preserves_previous(self):
        (self.release / CONFIG['checksum']).write_text('')
        self.assert_preserved(self.run_installer())


if __name__ == '__main__':
    unittest.main(verbosity=2)
