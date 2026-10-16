# Candidate namespace release synchronization

Base `04071d1b4340692d0b33ed5aca856dd3b994efce` tells the release bot to
update only `ns.ttl`. The actual next bot tree `67feb8a` had legacy version
0.8.0 and candidate version 0.7.0, so exact graph parity refused it.
Implementation `c1508ad` includes both catalogs and annotates the candidate's
version line. Watch the matching-version fixture pass, then the stale-candidate
control refuse. No release or vocabulary is activated by this demonstration.

From the repository root:

```sh
python3 docs/demos/stable-namespace-release/reproduce.py
```

[Actual transcript](output.log) and [timing](timing.log) are retained beside
the existing repository demos. Download both and use
`scriptreplay --log-out output.log --log-timing timing.log`, or read the
transcript. This is a source-checkout/configuration demonstration. Natural bot
regeneration and its CI still need separate observation after landing.
