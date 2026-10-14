# Governance resources

This optional module implements the retained governance specification as a new
source proposal. It makes no claim to recover a lost source tree, original
implementation, commit history or certification. The specification is the
reviewed 0.7.0 catalogue and single combined SHACL profile. Their content identity
is `sha256:e3952ce1919300af934e0a2846836e559d3d900652ecbbf7cbbd9889ba056e17`.

The catalogue contains 449 direct class/property declarations (1,418 triples).
The profile contains 2,133 triples and directly targets Directive, Policy,
TextRule, InternalIdentifierPattern, OperatingPoint, Reaction, AdmissionPolicy,
Decision and DecisionRecord. AdmissionPolicy examples remain proposed policies;
validation does not activate enforcement or resolve instruction conflicts.

The manifest describes specification data. Its historical source graph is not a
default destination or permission to load ROOT. Optional alignments are separate:
AdmissionPolicy specializes ODRL Policy, `refines` specializes PROV revision only
for substantial revisions preserving or narrowing obligations, and `contradicts`
has no external equivalence. These are newly adjudicated meanings, not inferred
from the artifact or proof of ODRL conformance.

Use this complete profile explicitly when building a governance resource.
The ordinary partitioned shapes remain unchanged. A fresh consumer must select
its destination and verify the native catalogue/profile readback; the profile
is not an automatic bootstrap or alignment import.

Source review, certification, release publication and native consumer adoption
are separate steps. A resource declaration does not provide execution authority,
policy precedence, exemption approval, an enforcement promotion or a load window.
