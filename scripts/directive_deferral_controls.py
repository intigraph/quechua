"""Admission controls for deferred directive traceability (aegis-rdj)."""
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, RDFS, SH, XSD

Q = Namespace('https://scbrown.github.io/quechua/ns#')
STABLE = Namespace('https://w3id.org/intigraph/quechua/ns#')
E = Namespace('https://example.org/directives/')


def check_directive_deferrals(shapes):
    def data(links=False, dates=()):
        g = Graph()
        g.add((E.rule, RDF.type, Q.Directive))
        g.add((E.rule, RDFS.label, Literal('Retain the decision')))
        if links:
            g.add((E.rule, Q.trackedBy, E.task))
            g.add((E.task, RDF.type, Q.WorkItem))
            g.add((E.task, RDFS.label, Literal('Evaluate')))
            g.add((E.rule, Q.governedBy, E.policy))
            g.add((E.policy, RDF.type, Q.Policy))
            g.add((E.policy, RDFS.label, Literal('Policy')))
        for date in dates:
            g.add((E.rule, STABLE.traceabilityDueAt, date))
        return g

    future = Literal('2030-11-28T07:30:00Z', datatype=XSD.dateTime)
    past = Literal('2020-11-28T07:30:00Z', datatype=XSD.dateTime)
    cases = [
        ('linked', data(links=True), True),
        ('deferred-without-links', data(dates=[future]), True),
        # Overdue decisions remain retained; the overdue query surfaces them.
        ('overdue-retained', data(dates=[past]), True),
        ('neither-links-nor-date', data(), False),
        ('invalid-typed-date', data(dates=[Literal('later', datatype=XSD.dateTime)]), False),
        ('timezone-missing', data(dates=[Literal('2030-11-28T07:30:00', datatype=XSD.dateTime)]), False),
        ('untyped-date', data(dates=[Literal(str(future))]), False),
        ('wrong-datatype', data(dates=[Literal('2030-11-28', datatype=XSD.date)]), False),
        ('multiple-dates', data(dates=[future, past]), False),
        ('linked-invalid-date', data(links=True, dates=[Literal('later')]), False),
    ]
    legacy = data(dates=[future])
    legacy.remove((E.rule, STABLE.traceabilityDueAt, future))
    legacy.add((E.rule, Q.traceabilityDueAt, future))
    cases.append(('legacy-date-reader', legacy, True))
    both = data(dates=[future])
    both.add((E.rule, Q.traceabilityDueAt, past))
    cases.append(('conflicting-alias-dates', both, False))
    missing_policy = data(links=True)
    missing_policy.remove((E.rule, Q.governedBy, E.policy))
    cases.append(('one-link-only', missing_policy, False))
    wrong_class = data(links=True)
    wrong_class.remove((E.task, RDF.type, Q.WorkItem))
    cases.append(('untyped-work-item', wrong_class, False))
    for name, graph, expected in cases:
        conforms, report, _ = validate(graph, shacl_graph=shapes, advanced=False)
        if conforms != expected:
            raise ValueError(f'directive {name}: expected conforms={expected}, got {conforms}')
        if not expected and SH.Violation not in set(report.objects(None, SH.resultSeverity)):
            raise ValueError(f'directive {name}: refusal must be a violation, not a warning')
        print(f'Directive control PASS: {name}')
    return len(cases)
