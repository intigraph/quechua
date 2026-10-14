# /// script
# requires-python = ">=3.12"
# dependencies = ["rdflib==7.6.0", "pyshacl==0.30.1"]
# ///
"""Validate the explicit governance profile and its boundary examples."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, RDFS, SH, XSD

ROOT = Path(__file__).resolve().parents[1]
Q = Namespace("https://scbrown.github.io/quechua/ns#")
EX = Namespace("https://example.org/governance/")
CLASSES = ("Directive", "Policy", "TextRule", "InternalIdentifierPattern",
           "OperatingPoint", "Reaction", "AdmissionPolicy", "Decision", "DecisionRecord")


def main():
    catalog = Graph().parse(ROOT / "ns.ttl")
    profile = ROOT / "profiles/governance/shapes.ttl"
    shapes = Graph().parse(profile)
    for name in CLASSES:
        assert (Q[name], RDF.type, RDFS.Class) in catalog, name
        assert list(shapes.subjects(SH.targetClass, Q[name])), name
    policy = Graph()
    for triple in ((EX.policy, RDF.type, Q.AdmissionPolicy),
                   (EX.policy, Q.claim, Literal("example import requirement")),
                   (EX.policy, Q.targets, Literal("example/**")),
                   (EX.policy, Q.status, Literal("proposed"))):
        policy.add(triple)
    cases = [("proposed policy", policy, True, None)]
    for field in ("claim", "targets", "status"):
        invalid = Graph()
        for triple in policy:
            invalid.add(triple)
        invalid.remove((EX.policy, Q[field], None))
        cases.append(("missing " + field, invalid, False, Q[field]))
    active = Graph()
    for triple in policy:
        active.add(triple)
    active.set((EX.policy, Q.status, Literal("active")))
    cases.append(("activation is not a resource example", active, False, Q.status))
    kind_property = next(p for p in shapes.objects(Q.OperatingPointShape, SH.property)
                         if shapes.value(p, SH.path) == Q.kind)
    kind = next(shapes.items(shapes.value(kind_property, SH["in"])))
    for field in ("falsePositiveTolerance", "falseNegativeTolerance"):
        for value, conforms in (("0.0", True), ("1.0", True),
                                ("-0.01", False), ("1.01", False)):
            point = Graph()
            point.add((EX.point, RDF.type, Q.OperatingPoint))
            point.add((EX.point, Q.kind, kind))
            point.add((EX.point, Q[field], Literal(value, datatype=XSD.decimal)))
            cases.append((field + " " + value, point, conforms,
                          None if conforms else Q[field]))
    for name, data, expected, path in cases:
        # Each validation receives a new profile graph: validator expansion
        # cannot mutate the next control or the resource being published.
        conforms, report, _ = validate(data, shacl_graph=Graph().parse(profile))
        assert bool(conforms) == expected, name
        if path is not None:
            assert path in set(report.objects(None, SH.resultPath)), name
        print(name + ": " + ("conforms" if conforms else "refused"))
    print(f"9/9 declarations and direct shapes; {len(cases)} boundary controls passed")


if __name__ == "__main__":
    main()
