# Infrastructure alignment profile

Implementation status: optional crosswalk under review. It defines producer
choices, not automatic OWL inference, vocabulary loading or a namespace rewrite.
Use these mappings only when the stated source evidence establishes their
meaning. No class/property equivalence is asserted.

<!-- markdownlint-disable MD013 -->

| Source concept | Output term | Required evidence and boundary |
| --- | --- | --- |
| Physical host or VM | `crtv:ComputerSystem` | A computer resource; declared configuration remains a declaration, not a fresh runtime observation. |
| Hypervisor | `core:ProxmoxNode` plus `crtv:ComputerSystem` | The specific role is retained; no identity merge follows from classification. |
| LXC guest | `core:LXCContainer` | Sharing a kernel is not evidence of an independent OS or physical computer. |
| Running software instance | `crtv:SoftwareServer` | An observed application-hosting instance; a repository or systemd declaration is insufficient. |
| OS process | `crtv:Process` | Observed PID with host, boot and capture-time scope; never inferred from a unit file. |
| IP address | `crtv:IPAddress`, `crtv:address`, `crtv:contextAddressSpace` | Parsed canonical address plus network scope; a shared IP does not establish host identity. |
| Software-server placement | `crtv:runsOn` | SoftwareServer subject and ComputerSystem target; never a global replacement for guest placement. |
| Guest placement | `core:runs_on` | Typed guest and hypervisor with resolved scoped identity. |
| HTTP route | `infra:ReverseProxyRoute`, `core:routes_to` | Host/path matching and a typed service target; an endpoint is not its server. |
| Deployment | `prov:Activity`, existing `delivery:DeploymentEvent` where applicable | A completed activity with outcome evidence; a declaration does not prove installation. |
| Source snapshot | `prov:Entity` | Exact locator, revision and byte digest; no secret values. |
| Extraction | `prov:Activity`, `prov:used` | Activity uses source Entity; its output record Entity wasGeneratedBy the activity. |
| Output record lineage | `prov:wasDerivedFrom` | Record revision derives from the source; do not assert that parsing created the physical host. |
| Ansible group/role | `core:AnsibleGroup`, `core:AnsibleRole` | Declaration layer with source revision; no observed process claim. |
| Terraform address | `infra:TerraformResource` | Provider/workspace-scoped declaration, separate from its observed resource. |

<!-- markdownlint-enable MD013 -->

Prefixes: `crtv:` = `http://open-services.net/ns/crtv#`, `prov:` =
`http://www.w3.org/ns/prov#`, `core:` =
`https://w3id.org/intigraph/camayoc/core/ns#`, `infra:` =
`https://w3id.org/intigraph/camayoc/homelab-infra/ns#`, `delivery:` =
`https://w3id.org/intigraph/camayoc/delivery/ns#`.

The existing canonical terms retain their published pack ownership. No new
infrastructure class or predicate is needed for these rows. Persistent w3id
redirects identify terms; they do not confer standards endorsement or choose a
deployment's instance namespace. Instance keys must be separately scoped and
adjudicated. Do not derive an instance base from an ontology namespace.

## Standards assessment

The [OSLC CRTV vocabulary](https://archive.open-services.net/wiki/reconciliation/Common-IT-Resource-Type-Vocabulary-Version-2.0/)
fits computer systems, processes, application-hosting instances and addresses;
its precise domains prevent a blanket local predicate substitution.
[PROV-O](https://www.w3.org/TR/prov-o/) supplies source and activity lineage.
[DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) describes datasets and data access
services; it does not make every daemon a DataService.
[DOAP](https://github.com/ewilderj/doap) describes software projects and releases,
which are distinct from deployed instances.
[SOSA/SSN](https://www.w3.org/TR/vocab-ssn/) describes sensor hosting, not generic
guest placement. [TOSCA 1.3](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/os/TOSCA-Simple-Profile-YAML-v1.3-os.html)
provides deployment topology concepts, but its YAML types are not RDF IRIs to
construct by string concatenation. Schema.org supplies descriptive record
relations such as `about`, while the precise IT resource model comes from CRTV.

Reusable semantic choices live here; producer constraints live in Camayoc's
optional infrastructure-output profile. Keep alignment separate from default
reasoning and shape loading. A non-author semantic review and actual ingress
compatibility proofs are required before connector activation. This document
alone is not acceptance of the complete connector workstream.
