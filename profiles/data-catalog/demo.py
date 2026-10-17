"""Local profile comparison; uses no mapped sources or server."""
from pathlib import Path
from rdflib import Graph
from pyshacl import validate
import hashlib

root = Path(__file__).resolve().parents[2]
old = root / "tests/fixtures/data-catalog-proposal30.ttl"
new = root / "shapes/data-catalog.shapes.ttl"
ordinary = """@prefix s: <https://schema.org/> .
<urn:example:code> a s:SoftwareSourceCode; s:codeRepository <https://example.org/git> ."""
catalog = """@prefix d: <http://www.w3.org/ns/dcat#> .
@prefix t: <http://purl.org/dc/terms/> .
d:Catalog <http://www.w3.org/2000/01/rdf-schema#subClassOf> d:Dataset .
<urn:example:catalog> a d:Catalog; t:title "Catalogue"@fr ."""
marked = """<urn:example:bad> <http://purl.org/dc/terms/conformsTo>
<https://scbrown.github.io/quechua/ns#DataCatalogQueryShape> ."""
print("WITHHELD proposal30 fixture versus corrected source profile (not installed behavior)")
for label, text in (("ordinary repository code", ordinary), ("general Catalog subclass", catalog)):
    results=[]
    for shapes in (old,new):
        results.append(bool(validate(Graph().parse(data=text,format="turtle"), shacl_graph=Graph().parse(shapes))[0]))
    assert results == [False,True], (label,results)
    print(label + ": before=" + str(results[0]) + " after=" + str(results[1]))
positive=bool(validate(Graph().parse(root/"profiles/data-catalog/example.ttl"), shacl_graph=Graph().parse(new))[0])
negative=bool(validate(Graph().parse(data=marked,format="turtle"), shacl_graph=Graph().parse(new))[0])
assert positive and not negative
print("strict complete positive:", positive)
print("untyped marked incomplete query:", negative, "(expected refusal)")
for path in (old,new,root/"scripts/check_data_catalog.py",root/"scripts/check_shapes.py"):
 print("sha256",path.relative_to(root),hashlib.sha256(path.read_bytes()).hexdigest())
