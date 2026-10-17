# /// script
# requires-python = ">=3.12"
# dependencies = ["rdflib==7.1.4", "pyshacl==0.30.1"]
# ///
"""Offline data-map profile/admission reference checks; never execute a recipe."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from check_shapes import check_terms, load_catalog

ROOT = Path(__file__).resolve().parents[1]
Q = Namespace("https://scbrown.github.io/quechua/ns#")
D = Namespace("http://www.w3.org/ns/dcat#")
T = Namespace("http://purl.org/dc/terms/")
S = Namespace("https://schema.org/")
EX = Namespace("https://example.org/data-map/")
TYPES = {"Dataset": D.Dataset, "Distribution": D.Distribution,
         "Service": D.DataService, "Query": S.SoftwareSourceCode}
PROFILE = ROOT / "shapes/data-catalog.shapes.ttl"
EXAMPLE = ROOT / "profiles/data-catalog/example.ttl"
MANIFEST = ROOT / "profiles/data-catalog/admission.json"


def absolute_iri(value):
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        raise ValueError("expected an absolute IRI")
    # This is an identity check, never URL dereferencing or endpoint permission.
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise ValueError("expected an absolute IRI")
    return URIRef(value)


def admit(data, manifest):
    """Require explicit intent even when removing a marker avoids SHACL targets.

    Only validate a reviewed bounded batch. No graph import, URL fetch, SQL,
    credential use or execution authorization takes place here.
    """
    if set(manifest) != {"version", "entries", "queries"}:
        raise ValueError("unknown or missing manifest fields")
    if manifest.get("version") != 1:
        raise ValueError("unknown admission manifest version")
    entries = manifest.get("entries", [])
    if not 1 <= len(entries) <= 100:
        raise ValueError("expected 1..100 explicit entries")
    roles = {}
    for entry in entries:
        iri, role = absolute_iri(entry["iri"]), entry["role"]
        if role not in TYPES or iri in roles:
            raise ValueError("unknown role or duplicate entry")
        roles[iri] = role
        if (iri, RDF.type, TYPES[role]) not in data:
            raise ValueError("explicit public type missing")
        if (iri, T.conformsTo, Q[f"DataCatalog{role}Shape"]) not in data:
            raise ValueError("exact admission profile marker missing")
    marked = {(node, role) for role in TYPES
              for node in data.subjects(T.conformsTo, Q[f"DataCatalog{role}Shape"])}
    if marked != set(roles.items()):
        raise ValueError("marked catalog entries differ from exact batch")
    for iri, role in roles.items():
        links = {"Dataset": (D.distribution, "Distribution"),
                 "Service": (D.servesDataset, "Dataset"),
                 "Query": (T.requires, "Distribution")}
        if role in links:
            predicate, target_role = links[role]
            targets = set(data.objects(iri, predicate))
            if not targets or any(roles.get(target) != target_role for target in targets):
                raise ValueError("referenced source outside exact admitted batch")
    queries = manifest.get("queries", [])
    bound_queries = set()
    for query in queries:
        iri = absolute_iri(query["iri"])
        if roles.get(iri) != "Query" or iri in bound_queries:
            raise ValueError("unknown or duplicate query contract")
        bound_queries.add(iri)
        texts = list(data.objects(iri, S.text))
        if len(texts) != 1 or not isinstance(texts[0], Literal):
            raise ValueError("one SQL text required")
        digest = hashlib.sha256(str(texts[0]).encode("utf-8")).hexdigest()
        if query["sha256"] != digest or set(data.objects(iri, S.sha256)) != {Literal(digest)}:
            raise ValueError("query content digest mismatch")
        if set(data.objects(iri, S.version)) != {Literal(query["revision"])}:
            raise ValueError("query revision mismatch")
        sources = [absolute_iri(value) for value in query["sources"]]
        if len(sources) != len(set(sources)) or set(sources) != set(data.objects(iri, T.requires)):
            raise ValueError("query source identity mismatch")
    if bound_queries != {iri for iri, role in roles.items() if role == "Query"}:
        raise ValueError("every admitted query needs an exact contract")


def run_cases(native=None):
    shape_text = PROFILE.read_text()
    shapes = Graph().parse(data=shape_text, format="turtle")
    classes, properties = load_catalog(ROOT)
    check_terms(PROFILE, shapes, classes, properties, ROOT)
    base = Graph().parse(EXAMPLE)
    manifest = json.loads(MANIFEST.read_text())
    cases = [("strict complete", base, True)]
    # Every strict field has a positive base and a one-field removal refusal.
    required = {EX.events: [Q.ownedBy, T.title, T.accessRights, D.distribution],
                EX.snapshot: [D.accessURL, D.mediaType, T.modified, T.accessRights],
                EX.service: [D.endpointURL, D.servesDataset, T.accessRights],
                EX.query: [S.programmingLanguage, S.text, S.version, S.sha256, T.requires, T.accessRights]}
    for node, predicates in required.items():
        for predicate in predicates:
            graph = Graph()
            graph += base
            graph.remove((node, predicate, None))
            cases.append(("missing " + str(node).split("/")[-1] + ":" + str(predicate), graph, False))
    for name, node, predicate, value in (
        ("untyped opt-in", EX.query, RDF.type, None),
        ("blank source", EX.query, T.requires, BNode("source")),
        ("literal media type", EX.snapshot, D.mediaType, Literal("application/json")),
        ("bad digest", EX.query, S.sha256, Literal("not-a-sha256")),
        ("literal endpoint", EX.service, D.endpointURL, Literal("https://example.org/")),
    ):
        graph = Graph()
        graph += base
        graph.remove((node, predicate, None))
        if value is not None:
            graph.add((node, predicate, value))
        if name == "blank source":
            graph.add((value, RDF.type, D.Distribution))
        cases.append((name, graph, False))
    outside = '''@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix s: <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<urn:example:code> a s:SoftwareSourceCode; s:codeRepository <https://example.org/git> .
<urn:example:catalog> a dcat:Catalog; dct:title "Catalogue"@fr; dcat:dataset <urn:example:dataset> .
<urn:example:series> a dcat:DatasetSeries; dct:title "Series"@en .
<urn:example:other-profile> dct:conformsTo <urn:example:other-standard> .
dcat:Catalog rdfs:subClassOf dcat:Dataset .
dcat:DatasetSeries rdfs:subClassOf dcat:Dataset .'''
    cases.append(("ordinary code Catalog Series and unrelated profile", Graph().parse(data=outside, format="turtle"), True))
    for name, graph, expected in cases:
        conforms = bool(validate(graph, shacl_graph=Graph().parse(data=shape_text, format="turtle"))[0])
        if conforms != expected:
            raise ValueError(f"{name}: pyshacl conforms={conforms}, expected={expected}")
        if native:
            with tempfile.TemporaryDirectory(prefix="data-map-native-") as tmp:
                data_path = Path(tmp) / "data.ttl"
                data_path.write_text(graph.serialize(format="turtle"))
                result = subprocess.run([native, "validate", "--shapes", str(PROFILE), "--data", str(data_path), "--format", "json"], capture_output=True, text=True, timeout=30)
                report = json.loads(result.stdout)
                if report["conforms"] != expected or result.returncode != (0 if expected else 1):
                    raise ValueError(f"{name}: native result differs (exit={result.returncode})")
        print(name + (": conforms" if expected else ": refused"))
    admit(base, manifest)
    # SHACL does not invent intent: absent/typo marker can be outside the profile.
    # The exact admission contract MUST refuse all such submissions.
    negatives = []
    for role, name in (("Dataset", "events"), ("Distribution", "snapshot"), ("Service", "service"), ("Query", "query")):
        graph = Graph()
        graph += base
        graph.remove((EX[name], T.conformsTo, Q[f"DataCatalog{role}Shape"]))
        negatives.append(("missing opt-in " + role, graph, manifest))
    for field, value in (("revision", "other"), ("sha256", "0" * 64), ("sources", [str(EX.other)])):
        changed = copy.deepcopy(manifest)
        changed["queries"][0][field] = value
        negatives.append(("mismatched " + field, base, changed))
    changed = copy.deepcopy(manifest)
    changed["queries"] = []
    negatives.append(("missing query contract", base, changed))
    graph = Graph()
    graph += base
    graph.add((EX.unexpected, T.conformsTo, Q.DataCatalogQueryShape))
    negatives.append(("extra marked entry", graph, manifest))
    for name, graph, contract in negatives:
        try:
            admit(graph, contract)
        except ValueError:
            print(name + ": admission refused")
        else:
            raise ValueError(name + ": admission incorrectly accepted")
    print(f"{len(cases)} SHACL controls and 1 positive/{len(negatives)} negative admission controls passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", help="optional pinned Quipu CLI to compare every SHACL control")
    args = parser.parse_args()
    run_cases(args.native)
