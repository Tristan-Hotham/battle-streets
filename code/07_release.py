"""Step 7: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24086515, https://doi.org/10.5281/zenodo.24086515 and https://blog.tristanhotham.com/2026/10/31/battle-streets/ stay as placeholders for the publisher."""
import shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Battle_Streets"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

post = fill(open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read(), R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Waterloo Road and the clock in the streets",
        "slug": "battle-streets",
        "excerpt": f"Victorian builders named streets after the latest victory. I mapped every UK street named after a battle: {R['top_clock'][0]['n']} Waterloos, {R['top_clock'][1]['n']} Almas, and in {R['test']['positive']} of {R['test']['towns']} towns the later battles lie farther from the centre. A clock in the streets, if a slow one.",
        "seo_description": f"Every UK street named after a battle, mapped: Waterloo, Alma, Trafalgar, Mafeking. In {R['test']['positive']} of {R['test']['towns']} towns later battles lie farther out.",
        "tags": ["maps", "street names", "history", "battles", "Victorian", "Crimean War", "Boer War", "urban growth", "OpenStreetMap", "data visualisation"],
        "header_alt": f"Title card reading 'Waterloo Road and the clock in the streets' beside rings around Bristol city centre, with battle streets coloured from purple for the French wars to yellow for the world wars, and the line {R['top_clock'][0]['n']} Waterloos, {R['top_clock'][1]['n']} Almas."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dd in ("code", "js"):
        for fn in sorted(os.listdir(os.path.join(ROOT, dd))):
            if fn.endswith(".pyc") or fn == "__pycache__" or fn.endswith(".png"):
                continue
            z.write(os.path.join(ROOT, dd, fn), f"{SLUG}/{dd}/{fn}")
    for fn in sorted(os.listdir(os.path.join(ROOT, "data"))):
        z.write(os.path.join(ROOT, "data", fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab).replace("$p<0.001$", "p < 0.001").replace("$p<0.01$", "p < 0.01")
assert "\\" not in ab and "$" not in ab, ab
zmeta = {"title": "Waterloo Road and the Clock in the Streets: Battle Street Names and the Growth of British Towns",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive page: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/battle-streets/}}.</p><p>Sources: OpenStreetMap contributors (ODbL), queried with QLever; Wikidata (CC0); ONS boundaries (OGL v3.0). The street tables are derived from OpenStreetMap and released under the Open Database Licence; text and figures CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["street names", "commemoration", "urban growth", "toponymy", "battles", "Victorian Britain", "OpenStreetMap"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "Text and figures CC BY 4.0; code MIT; data/streets.csv, streets.json, rings.geojson and the other street tables derived from OpenStreetMap, ODbL.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.openstreetmap.org/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = json.dumps(zmeta, ensure_ascii=False) + json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj and "https://blog.tristanhotham.com/2026/10/31/battle-streets/" in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
