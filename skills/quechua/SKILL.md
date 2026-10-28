---
name: quechua
description: Find vocabulary terms and orient agents with Quechua prime.
---

<!-- BEGIN quechua prime -->
# Quechua agent primer

## What quechua is

Quechua supplies shared vocabulary and opt-in SHACL shapes for the Quipu stack.
Quipu stores knowledge and Camayoc prepares governed records.
Quechua gives those records interoperable names and constraints.
Installing files does not load a graph, enable inference, or migrate instance IRIs.

## Agent workflow

1. Query Quipu for existing facts, decisions and provenance before changing data.
2. Find terms in the human catalog; read descriptions and replacement pointers.
3. Inspect the Turtle vocabulary for exact IRIs and prefer referenced public terms.
4. Choose only the required shape profiles and validate before activating them.

## Core commands

| Command | Use |
| --- | --- |
| `quechua prime` | Guidance, vocabulary release version and local metadata |
| `quechua prime --brief` | Short orientation for stack aggregation |
| `quechua prime --json` | Structured `stack-prime/1` orientation |
| `quechua prime --static` | Embedded guidance/version without package-state reads |
| `quechua prime --section agent --static` | One section by heading prefix |
| `quechua prime --data-dir DIRECTORY` | Inspect one explicit package directory |
| `quechua prime --help` | Flags and usage |

## MCP tools

None. Quechua has no MCP server or graph-writing command. Its surfaces are this
primer, the skill, the public catalog and the vocabulary/shape files. In a source
checkout, run `python3 scripts/prime.py prime`.

## Find terms

Use the [human catalog](https://scbrown.github.io/quechua/ns) and
[the Turtle vocabulary](https://scbrown.github.io/quechua/ns.ttl). For local
lookup, inspect the installed `quechua-ns-vVERSION.ttl` file. The registered
stable namespace is `https://w3id.org/intigraph/quechua/ns#`. Earlier identifiers
remain declared; consult compatibility notes before changing stored predicates.
Publication is not a consumer migration.

## Reading live state

Prime reads at most 64 KiB of the local release identity with a 650 ms deadline.
It never creates files, opens a database, installs hooks, contacts a service or
loads vocabulary into Quipu. Missing identities are `absent`, malformed or
unreadable identities are `unreadable`, and the deadline reports `partial`.
Static guidance remains usable and these degraded reads still exit 0.

Source mode reports the checkout version. Installed mode reports the release
tag and number of digest-listed assets, not an integrity check of their bytes
or a running store's loaded version. JSON includes elapsed milliseconds and
`ok`/`degraded` status. `--static` skips live reads. Usage errors exit 2.

## Next steps

- [README](https://github.com/scbrown/quechua#readme)
- [Installation, vocabulary and shapes](https://github.com/scbrown/quechua/blob/main/docs/installation-reference.md)
- [Agent skill](https://github.com/scbrown/quechua/blob/main/skills/quechua/SKILL.md)
- Command help: `quechua prime --help` (no shipped man page).
<!-- END quechua prime -->
