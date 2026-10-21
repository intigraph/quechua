# /// script
# requires-python = ">=3.12"
# dependencies = ["rdflib==7.6.0", "pyshacl==0.30.1"]
# ///
"""Synthetic before/after opt-in profile validation; no store or activation."""
from pathlib import Path
import subprocess

from pyshacl import validate
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'profiles/scheduled-jobs/shapes.ttl'
BASE = '2374dd5f9c37aaeec13f85a326f7d17e39ca0bb8'


def main():
    old = subprocess.check_output(['git', 'show', BASE+':'+PROFILE], cwd=ROOT)
    before = Graph().parse(data=old.decode(), format='turtle')
    after = Graph().parse(ROOT / PROFILE)
    weekly = Graph().parse(ROOT / 'profiles/scheduled-jobs/weekly-example.ttl')
    fixed = Graph().parse(ROOT / 'profiles/scheduled-jobs/example.ttl')
    assert not validate(weekly, shacl_graph=before)[0]
    assert validate(weekly, shacl_graph=after)[0]
    assert validate(fixed, shacl_graph=before)[0] and validate(fixed, shacl_graph=after)[0]
    print('Base', BASE, ': disabled weekly declaration refused')
    print('Candidate: disabled P7D/Monday/09:17:00 declaration conforms')
    print('Fixed interval control: conforms before and after')
    schema = Namespace('https://schema.org/')
    weekly.remove((None, schema.startTime, None))
    assert not validate(weekly, shacl_graph=after)[0]
    print('Partial calendar qualifier: refused, not reinterpreted as elapsed P7D')
    print('SOURCE VALIDATION ONLY: no profile loaded, graph minted, job enabled or runtime firing')


if __name__ == '__main__':
    main()
