# /// script
# requires-python = ">=3.12"
# dependencies = ["rdflib==7.6.0", "pyshacl==0.30.1"]
# ///
"""Validate the explicit scheduled-job profile and independent failure arms."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, SH, XSD

ROOT = Path(__file__).resolve().parents[1]
Q = Namespace("https://scbrown.github.io/quechua/ns#")
S = Namespace("https://schema.org/")
EX = Namespace("https://example.org/jobs/")
PROFILE = ROOT / "profiles/scheduled-jobs/shapes.ttl"
EXAMPLE = ROOT / "profiles/scheduled-jobs/example.ttl"


def check():
    shapes = Graph().parse(PROFILE)
    pinned = set((ROOT / "vocab/schemaorg-30.1.terms").read_text().splitlines())
    public_terms = {str(term) for triple in shapes for term in triple
                    if str(term).startswith(str(S))}
    assert public_terms <= pinned, sorted(public_terms - pinned)
    base = Graph().parse(EXAMPLE)
    cases = [("valid declaration", base, True, None)]

    def variant(name, subject, predicate, value=None, add=False, expected_path=None):
        graph = Graph()
        for triple in base:
            graph.add(triple)
        if not add:
            graph.remove((subject, predicate, None))
        if value is not None:
            graph.add((subject, predicate, value))
        cases.append((name, graph, False, expected_path or predicate))

    for predicate in (S.name, S.identifier, Q.sourceKind, Q.owner, Q.enabled, S.location, S.target):
        variant("missing " + str(predicate), EX.review, predicate)
    variant("conflicting revision", EX.review, S.identifier, Literal("other"), add=True)
    variant("untyped action", EX.review, RDF.type, expected_path=S.potentialAction)
    variant("untyped schedule", EX['review-schedule'], RDF.type, expected_path=S.eventSchedule)
    variant("string host cannot resolve scope", EX.review, S.location, Literal("host"))
    variant("string command is not a manifest target", EX.review, S.target, Literal("echo unsafe"))
    variant("inferred is not an enabled declaration", EX.review, Q.sourceKind, Literal("inferred"))
    variant("ambiguous enablement", EX.review, Q.enabled, Literal("maybe"))
    for value in ("PT0S", "-PT1M", "P1M"):
        variant("invalid fixed interval " + value, EX['review-schedule'], S.repeatFrequency,
                Literal(value, datatype=XSD.duration))
    variant("missing timezone", EX['review-schedule'], S.scheduleTimezone)
    variant("missing anchor", EX['review-schedule'], S.startDate)
    variant("naive anchor", EX['review-schedule'], S.startDate,
            Literal("2026-01-01T00:00:00", datatype=XSD.dateTime))
    variant("occurrence bounds cannot override schedule", EX['review-occurrences'], S.startDate,
            Literal("2026-01-02T00:00:00Z", datatype=XSD.dateTime), add=True)
    for predicate, value in ((S.byMonth, Literal(1)),
                             (S.exceptDate, Literal("2026-01-01", datatype=XSD.date))):
        variant("unsupported calendar qualifier " + str(predicate), EX['review-schedule'],
                predicate, value, add=True)
    # The marker is explicit and carries constraints outside Event traversal.
    unmarked = Graph().parse(EXAMPLE)
    unmarked.remove((EX.review, RDF.type, Q.ScheduledJob))
    cases.append(("legacy unmarked declaration remains compatible", unmarked, True, None))
    marked_only = Graph()
    marked_only.add((EX.job, RDF.type, Q.ScheduledJob))
    marked_only.add((EX.job, RDF.type, S.Action))
    cases.append(("bare job marker cannot bypass required fields", marked_only, False, None))
    unlinked = Graph().parse(EXAMPLE)
    unlinked.remove((EX['review-occurrences'], S.potentialAction, None))
    unlinked.remove((EX.review, S.name, None))
    cases.append(("marked unlinked job still requires fields", unlinked, False, S.name))
    disabled = Graph().parse(EXAMPLE)
    disabled.set((EX.review, Q.enabled, Literal(False)))
    cases.append(("disabled remains a queryable declaration", disabled, True, None))
    unrelated = Graph()
    unrelated.add((EX.other, RDF.type, S.Action))
    unrelated.add((EX.other_event, RDF.type, S.Event))
    cases.append(("unrelated action/event not targeted as jobs", unrelated, True, None))
    weekly = Graph().parse(ROOT / 'profiles/scheduled-jobs/weekly-example.ttl')
    cases.append(('weekly local-time declaration', weekly, True, None))
    partial = Graph()
    for triple in base:
        partial.add(triple)
    partial.add((EX['review-schedule'], S.byDay, S.Monday))
    cases.append(('calendar qualifier cannot be silently ignored', partial, False, None))
    for name, predicate, value in (
        ('missing weekday', S.byDay, None),
        ('missing local time', S.startTime, None),
        ('literal weekday', S.byDay, Literal('Monday')),
        ('unknown weekday', S.byDay, EX.Funday),
        ('nonweekly cadence', S.repeatFrequency, Literal('P1D', datatype=XSD.duration)),
        ('time with seconds', S.startTime, Literal('09:17:01', datatype=XSD.time)),
        ('zoned local time', S.startTime, Literal('09:17:00Z', datatype=XSD.time)),
        ('string local time', S.startTime, Literal('09:17:00')),
    ):
        graph = Graph()
        for triple in weekly:
            graph.add(triple)
        graph.remove((EX['review-schedule'], predicate, None))
        if value is not None:
            graph.add((EX['review-schedule'], predicate, value))
        cases.append((name, graph, False, None))
    multiple = Graph()
    for triple in weekly:
        multiple.add(triple)
    multiple.add((EX['review-schedule'], S.byDay, S.Tuesday))
    cases.append(('multiple weekdays require another supported contract', multiple, False, None))
    for name, graph, expected, path in cases:
        conforms, report, _ = validate(graph, shacl_graph=Graph().parse(PROFILE))
        assert bool(conforms) == expected, name
        if path is not None:
            # Nested action/schedule node failures may appear under the linking
            # path too; require the specific violated field somewhere in report.
            assert path in set(report.objects(None, SH.resultPath)), name
        print(name + ": " + ("conforms" if conforms else "refused"))
    print(f"{len(cases)} profile controls passed; no runtime activation")


if __name__ == "__main__":
    check()
