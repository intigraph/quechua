# Deferred directive admission demo

A private RDF fixture containing a Directive and only a typed evaluation
deadline fails the base shape and passes the candidate. Missing both alternatives
and an untyped date still fail; existing typed links still pass.

The [terminal output](output.log) and [timing](timing.log) form a replayable
recording (not an inline video). Both are small sanitized source artifacts
retained with this example. Replay with:

```sh
scriptreplay --log-out output.log --log-timing timing.log
```

The recording identifies exact base revision and candidate shape SHA256.
It demonstrates source SHACL behavior using pySHACL, not installed Quipu
acceptance. Repeat from the repository root:

```sh
uv run --with rdflib==7.1.4 --with pyshacl==0.30.1 python docs/demos/directive-deferral/demo.py
```
