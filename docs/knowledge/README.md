# Repository pendant source

The repository-owned release job exports code and document **pointers**, plus
reviewed summaries of ideas, interfaces, decisions, freshness and starting points.
It does not export source chunk text or line spans. Source witnesses bind each
summary to its defining tracked file. The native index must resolve every
curated pointer before the build can proceed. Stored queries and validating
shapes travel with the share.

`alignments.ttl` is currently a valid empty SSSOM/RDF carrier. Its accompanying
status file explicitly records zero approved mappings and seals those bytes.
This is not evidence of global absence. Missing, changed or malformed input
refuses; an explicit empty carrier does not. Dependencies and glossary references
are not identity alignments. Code/commit deduplication and unrelated exactMatch
records are not cross-repository mapping approval.

Candidate mappings must go through Quipu's existing `align propose` and
`align decide` curation path. Keep their source graphs and source witnesses;
do not fill an approval author from a lexical score. Only the reviewed mapping
record may produce derived identity through the engine's existing apply path.
The current source profile deliberately does not import arbitrary nonempty
mapping data until an actual curated artifact and its transport are reviewed.

The copied release workflow records `NOT_ADMITTED` without asset lookups when
`TRUSTED_REPOSITORY_SHARE_ENABLED` is absent or `false`. Set that repository
variable to `true` only after the existing trusted producer has actually admitted
this repository; the flag does not configure or start a producer. Other values
refuse. An admitted release verifies all three assets after the ordinary release
finishes; missing or invalid assets still fail the bounded readback.
The managed trusted host runs this repository's own
publisher, keeps its publication policy private, pins both native engine
executables and the indexer, and refuses retained uncertain upload outcomes.
Default configuration still publishes only the existing Quipu corpus. Enabling
another repository requires its actual trusted host configuration and a clean
release containing this job; committing this source does not publish an asset.

An engine advertising native alignment transport may include `alignments.ttl`.
Packaging and public readback require its manifest path and SHA-256 to match the
exact reviewed repository carrier. An absent optional member remains valid for
older engines; a declared-but-missing, corrupt, unbound or foreign carrier
refuses. Transporting the empty carrier does not apply or approve a mapping.

The publisher requires the engine's model/digest/dimension manifest recipe.
Loading and vector rebuilding belong to the native engine. No hosted job gets
private publication policy or a new credential route. These source controls do
not establish public asset availability, live loading or service acceptance.
