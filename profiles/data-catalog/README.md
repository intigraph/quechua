# Data-map catalog profile

Quipu holds the map: existing datasets, their distributions and services, and
named query recipes. Qhapaq is the proposed read-only DuckDB executor; Chaski
keeps transport, outbox, delivery and deduplication. This profile is a design
artifact, not an engine, connector, access grant or store activation.

## Standard types and explicit participation

Use [DCAT3](https://www.w3.org/TR/vocab-dcat-3/) Dataset, Distribution,
DataService, Catalog and DatasetSeries; use
[Schema.org SoftwareSourceCode](https://schema.org/SoftwareSourceCode) for a
recipe. Do not create a second Dataset vocabulary. General public metadata has
no query-text, distribution or operational-owner requirement from this profile.
Catalog and Series subclass relationships do not make them executable sources.

Strict participation is explicit: assert `dct:conformsTo` with one of these
shape IRIs under `https://scbrown.github.io/quechua/ns#`:

| Role | Marker | Required profile metadata |
| --- | --- | --- |
| Dataset | DataCatalogDatasetShape | public type, title, ownedBy, rights, IRI distributions |
| Distribution | DataCatalogDistributionShape | public type, IRI access URL and media type, schema reference, captured modification time, rights |
| Service | DataCatalogServiceShape | public type, IRI endpoint, served datasets, rights |
| Query | DataCatalogQueryShape | public type, language, text, revision, SHA256, exact source distributions, rights |

The marker identifies a validation contract, not an enable bit. `ownedBy` is
the operational owner; `dct:publisher` can name a different publishing entity.
Titles may be multilingual. Media types are IRIs; the example uses the IANA
`application/json` identifier. Imported standard metadata is not rewritten to
string media types. Distribution `conformsTo` contains both the profile marker
and its schema IRI; the admission plan must bind the intended schema exactly.

[SHACL subjects-of targets](https://www.w3.org/TR/shacl/#targetSubjectsOf) also
select untyped marked nodes. Each role's conditional constraint applies only
when its exact marker occurs. Unrelated standards and profiles remain valid.
Removing or misspelling a marker can put data outside SHACL scope. Therefore
**SHACL conformance alone is never catalog admission**.

## Exact batch admission

The [example](example.ttl) and [admission manifest](admission.json) demonstrate
an explicit batch, not data fetched from the example URLs. The offline
reference checker requires each expected IRI to carry its public type and exact
marker. All required distributions/datasets must belong to that batch; every
query binds its revision, SHA256 of the literal UTF-8 text, and exact source
IRIs. Duplicate or extra marked entries, absent query contracts and identity/digest mismatches
refuse. Removing any role marker refuses admission even when SHACL accepts the
remaining general metadata. Content hashes identify bytes, not trusted authors.

```sh
uv run --locked --script scripts/check_shapes.py --selftest
uv run --locked --script scripts/check_data_catalog.py
# Additionally compare every SHACL case with a pinned native Quipu CLI:
uv run --locked --script scripts/check_data_catalog.py --native /path/to/quipu
```

This checker never imports a graph, opens a mapped URL, reads a source database
or executes SQL. Its example manifest is not an execution-policy format. A
consumer must compose this profile with its loaded shapes, supply its own
reviewed expected batch, and check graph scope. Loading only the permissive vocabulary shapes cannot satisfy admission.

## Separate execution plan

A future approved execution tuple must bind query IRI, revision and content
hash, policy digest, parameter schema/digest, exact source and schema IRIs,
adapter/normalization revisions, engine and extension versions, source capture
identities, consistency/coverage, rights/capability references and output scope.
Catalog rights metadata never provides credentials or execution permission.
Secrets remain outside the graph, SQL and result; references identify local
capabilities. Recipe SQL is inert until that separate policy admits the tuple.

The adapter obtains bounded, coherent projections. It handles API pagination,
rate limits, source identities and owner-approved SQLite snapshots including
WAL consistency. A worker cannot attach an arbitrary production file or URL.
For instance, a reviewed JSON projection can become a DuckDB relation through
`read_json_auto`; metadata for a remote SQLite source is not proof it is a local
attachable file. Unknown schema/rights, stale inputs, partial pagination,
unsupported adapters or failed reads produce UNKNOWN, not an empty result.

The SQL worker receives only prepared read-only inputs and a private bounded
result directory, with hard OS memory/CPU/wall/scratch limits and restricted
network/credentials. DuckDB buffer limits and read-only connections alone are
not the isolation boundary. Extensions are pinned and preloaded; runtime
installation and configuration changes are refused. See the
[DuckDB security guidance](https://duckdb.org/docs/stable/operations_manual/securing_duckdb/overview).
No claim about that future containment follows from metadata validation.

Results carry query/policy/engine identities, input locator/version/hash and
capture times, schema/normalization/coverage, output count/hash, outcome and
measured resources. Different capture times are disclosed rather than called
a global snapshot. [PROV](https://www.w3.org/TR/prov-o/) activities link the
query and input entities to the result; [CSVW](https://www.w3.org/TR/tabular-metadata/)
can describe projection columns. Disposable caches never become authoritative
sources. Optional observation writes require a separately admitted destination.

## Chaski and design-stage acceptance

Chaski supplies bounded immutable event batches and a durable watermark. Qhapaq
can evaluate a named selection/window/join, but watermark advancement follows
Chaski's durable acceptance of a deterministic result/outbox key. Failure holds
the batch visibly. Replay uses the same query revision, event identities and
window boundary. Late events, corrections and recipe changes need explicit
policies; DuckDB batch SQL does not establish continuous-stream completeness.
Results may propose Chaski events; transport and delivery receipts remain there.
Gmail and Telegram account access, retention and personal-graph admission stay
separate from this metadata profile.

The design-stage item requires ten inspected locations admitted into a governed
Quipu catalog, with recipes, and a real cross-source answer with reproducible
input/SQL hashes and lineage. A prior bounded Stop-event/crew-card join is such
demo evidence, not fleet-wide completeness or product/runtime acceptance.
Publication of these shapes is followed by independent semantic review,
composed native validation, explicit loading, and controlled catalog read-back.
Original proposal30's global-target rejection remains the historical baseline;
this source corrects it and does not accept or overwrite that pending proposal.

## Recorded comparison

[Output](demo-output.log) and [timing](demo-timing.log) form a util-linux terminal
recording; download both, then run:

```sh
scriptreplay --log-out demo-output.log --log-timing demo-timing.log
```

Playback was checked. This is a terminal recording, with a readable output log,
not an inline video. It compares the exact **withheld proposal30 fixture**, SHA256
`639f9b7a35766a310472846201aa201aeada78778d523ab64bdb314a7671ab80`, with
the corrected source profile. Proposal30 was never an installed/released profile.
The same ordinary code and Catalog inputs change from rejected to conforming;
the strict complete control passes and an untyped, marked incomplete query
refuses. The recording prints source hashes for the demonstrated candidate.
Reproduce locally with pinned dependencies:

```sh
uv run --with rdflib==7.1.4 --with pyshacl==0.30.1 python profiles/data-catalog/demo.py
```

The small recording and fixture are retained with this profile for reviewers.
The baseline fixture under tests is intentionally invalid for global adoption;
load only the reviewed candidate shape, never test fixtures.
