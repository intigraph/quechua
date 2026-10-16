# Candidate namespace identity demonstration

The base `1c48fe1fc135fd2200b99919e0390fffa0b43654` has the existing
catalog and no candidate artifact. Implementation `ea05734` adds a candidate
representation of the same 449 terms, preserving annotations and adding
one-to-one legacy identity links. The five graph/HTML mutations must refuse;
the original catalog documents must remain unchanged.

From the repository root:

```sh
python3 docs/demos/stable-namespace/reproduce.py
```

The [actual terminal transcript](output.log) and [timing](timing.log) are small
recordings retained in this existing demo directory. Download both and replay
with `scriptreplay --log-out output.log --log-timing timing.log`, or read the
transcript directly. The recording is source-checkout behavior, not a live
w3id redirect, consumer alias installation, or stored-data migration. Registration
is pending. The later demo commit changes no implementation bytes.
