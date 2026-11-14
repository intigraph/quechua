"""Compare real base/candidate SHACL admission on the same private RDF inputs."""
import hashlib
import subprocess
from pathlib import Path
from pyshacl import validate
from rdflib import Graph

BASE = 'c356c5b80f798c19df0201328f975577dd8c168d'
path = 'shapes/ontology.shapes.ttl'
before = subprocess.check_output(['git', 'show', BASE+':'+path], text=True)
after = Path(path).read_text()
prefix = '''@prefix q: <https://scbrown.github.io/quechua/ns#> .
@prefix stable: <https://w3id.org/intigraph/quechua/ns#> .
@prefix ex: <https://example.org/directives/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:rule a q:Directive ; rdfs:label "Retain a decision" '''
fixtures = [
    ('typed deadline only', '; stable:traceabilityDueAt "2030-11-28T08:00:00Z"^^xsd:dateTime .', False, True),
    ('neither links nor date', '.', False, False),
    ('untyped deadline', '; stable:traceabilityDueAt "2030-11-28T08:00:00Z" .', False, False),
    ('typed links', '; q:trackedBy ex:task ; q:governedBy ex:policy . ex:task a q:WorkItem ; rdfs:label "Evaluate" . ex:policy a q:Policy ; rdfs:label "Policy" .', True, True),
]
print('Private schema demonstration; no running store or write.')
print('Base revision:', BASE)
print('Candidate shape SHA256:', hashlib.sha256(after.encode()).hexdigest())
for name, suffix, old_expected, new_expected in fixtures:
    results = []
    for shape in (before, after):
        conforms, _, _ = validate(Graph().parse(data=prefix+suffix, format='turtle'), shacl_graph=Graph().parse(data=shape, format='turtle'))
        results.append(bool(conforms))
    assert results == [old_expected, new_expected], (name, results)
    print(f'{name}: base={results[0]} candidate={results[1]} PASS')
