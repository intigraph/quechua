# Apply a shared vocabulary shape locally

Quechua supplies public vocabulary and SHACL rules; Quipu executes those rules. This 20-second recording uses the real local validator: an APIEndpoint without a label fails one min-count constraint, then the same entity with its label passes. No server, graph import, credentials or installed shape set is used. Both tiny inputs are public fixtures.

Recorded from Quechua source `0ac75143e034d660d63b386264f11fc6159d3595` with Quipu 0.16.5. The manifest pins the executable and every input. The shape bytes are copied unchanged from `shapes/ontology.shapes.ttl`; this example uses its published vocabulary namespace and does not claim a namespace migration or a release-pin change.

With a verified Quipu 0.16.5 executable, prepare a new, absent workspace from the repository root:

```sh
mkdir /tmp/quechua-demo
cp shapes/ontology.shapes.ttl docs/demos/terminal/fixture/*.ttl /tmp/quechua-demo/
touch /tmp/quechua-demo/.terminal-demo-sandbox
python3 docs/demos/terminal/render.py docs/demos/terminal/demo.tape.json \
  --workspace /tmp/quechua-demo --tool quipu="$(command -v quipu)" \
  --output /tmp/quechua-render
```

The expected invalid command exits 1, and the labelled positive control exits 0. The native output is preserved, including the violation path. Deliberate reading holds are separate from execution timings. Read `terminal/transcript.txt` for a static alternative.

The recorder is byte-identical to Tambo’s canonical `stack-terminal-24` harness at `b0765b5d8f16a6a26acb3595552f17826d965b44`, SHA-256 `bebbe000565314f18a58731f2a1a4690577db127b3673fa10a45ce74eef0f23c`.
