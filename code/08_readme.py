"""Step 8: README.md, LICENSE and the Reddit post text (reddit/post.md), filled from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
N, T, E = R["n"], R["test"], R["era_pct"]
NAP, CRI, BOER = "Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Boer War 1899 to 1902"
readme = f"""# Waterloo Road and the clock in the streets

Battle street names and the growth of British towns. {N['ways']:,} OpenStreetMap highways whose names contain one of {N['battles_in_table']} battle names, joined into {N['streets']:,} streets; battles before 1793 and ambiguous names set aside; the remaining {N['clean']:,} streets dated by their battle and tested for a "clock": do streets named after later battles lie farther from the town centre?

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24086515}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/battle-streets/}}
Code and data: {REPO}

## Headline results

- Waterloo ({R['top_clock'][0]['n']}), Alma ({R['top_clock'][1]['n']}) and Trafalgar ({R['top_clock'][2]['n']}) are the commonest battles from 1793 on; Blenheim ({R['top'][0]['n']}) is the commonest battle name of all, but often via the palace.
- Bursts: the four Crimean battles gave {R['crimea_vs_before']['crimea']} streets, more than both world wars together ({R['world_wars']['n']}); the battles of 1816 to 1853 gave {R['by_era']['1816 to 1853']['clean']}.
- World-war names are far more often estate names: {R['world_wars']['modern_pc']:.0f}% end in Close, Drive, Way, Court or Gardens, against {R['victorian']['modern_pc']:.0f}% for battles of 1854 to 1902.
- The clock: in {T['positive']} of {T['towns']} towns (traditional street words, four or more streets) later battles lie farther out, in {T['negative']} the other way; mean within-town Spearman rho {T['mean_rho']:.2f}, none of {T['reps']:,} within-town permutations as high. Counting clusters of same-war streets within 500 m once, rho is {R['test_cluster']['mean_rho']:.2f} ({R['test_cluster']['perm_count']} of {T['reps']:,} permutations as high): weaker, still there. Median distance from the centre: {E[NAP]['median_km']:.1f} km (Napoleonic), {E[CRI]['median_km']:.1f} km (Crimea), {E[BOER]['median_km']:.1f} km (Boer War).
- A coarse clock: Napoleonic streets nearer the centre than Boer War ones in {R['pairs']['nap_boer']['inside']} of {R['pairs']['nap_boer']['towns']} towns, but nearer than Crimean ones in only {R['pairs']['nap_crimea']['inside']} of {R['pairs']['nap_crimea']['towns']}. London barely shows it (rho {R['tc']['London']:.2f}); Bristol, Glasgow and Hull do.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: MapLibre on the OpenFreeMap Positron base map, every battle street coloured by the battle's date, a date slider, rings at each war's median distance per town, search and popups. |
| `header.png` | Social card, 1200 x 630. |
| `data/streets.csv` | Every battle street ({N['streets']:,}): battle, date, war, era, status (clock, old, ambiguous), name, street word, position, county, nation, town, distance from the town centre, nearby place of the same name, OSM way ids. ODbL. |
| `data/battles.csv` | The battle table: {N['battles_in_table']} battles with the date used, war, status and note, and the number of streets. |
| `data/town_clock.csv`, `data/town_rings.csv` | Per-town correlations, and towns with streets from three or more of the big wars. |
| `data/by_county.csv` | Battle streets by county and era. |
| `data/streets.json`, `data/rings.geojson`, `data/places.json` | Page data. |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `img/` | Figures on the page. |
| `code/` | Numbered scripts, `battles.py` (the battle table), `overrides.csv` (names removed by hand), templates, `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Whole-word match of names against the battle table; twin-town names (Villiers-sur-Marne Avenue) excluded; pieces of one name joined within 600 m (1.5 km for through roads).
- Set aside: battles before 1793 ({N['old']:,} streets), ambiguous names ({N['ambiguous']} streets: {R['amb_list']}), streets within 3 km of a place of the same name ({N['place_named']}), and {N['dropped_by_hand']} non-streets or non-battles removed by hand.
- Town: nearest Wikidata town of 20,000 or more within 10 km (Greater London as one); distance from its Wikidata point.
- Test: streets with a traditional street word; Spearman rho of battle year and distance in each town with four or more; mean rho against {T['reps']:,} within-town permutations; within-town distance percentile by war with bootstrap intervals. Sensitivity: all street words, six or more streets, up to 1902, without London, same-war clusters within 500 m counted once.
- Caveats: the name dates the battle, not the street; towns did not grow in rings; conurbations compress distances; ambiguity rules are judgements; Alma is also a woman's name ({R['alma_check']['isolated']} of {R['alma_check']['n']} Alma streets are newer-style names away from any Alma Street or Road).

## How to rerun

Needs Python 3 with pandas, numpy, scipy, geopandas, pyproj, shapely, matplotlib, Pillow; xelatex, pdftotext, pdfinfo; node with Playwright for `code/qa.js`. Raw inputs are listed in `code/common.py`; intermediates go to `BS_WORK`.

```
python3 code/01_streets.py     # match, join, places of the same name
python3 code/02_analysis.py    # towns, distances, the clock test, results.json
python3 code/03_figures.py     # figures
python3 code/04_export.py      # page data
python3 code/05_build_site.py  # index.html
python3 code/06_paper.py       # paper PDF (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py      # collage and header
python3 code/08_readme.py      # README, LICENSE, Reddit post
python3 code/07_release.py     # blog post, Zenodo files
```

## Sources and licences

- OpenStreetMap (https://www.openstreetmap.org/), © OpenStreetMap contributors, Open Database Licence, queried with QLever (University of Freiburg). The street tables are derived databases under the ODbL.
- Wikidata (CC0) for towns; ONS boundaries (Open Government Licence v3.0) for counties.
- Battle dates: standard reference dates, in `code/battles.py` and `data/battles.csv`.
- Base map: OpenFreeMap Positron (OpenStreetMap data, ODbL). MapLibre GL JS (BSD 3-Clause). Fonts: Fraunces, Source Serif 4, IBM Plex Mono, MedievalSharp, IM Fell (SIL Open Font License).

## Citation

Hotham, T. (2026) Waterloo Road and the clock in the streets: battle street names and the growth of British towns. Zenodo. {{https://doi.org/10.5281/zenodo.24086515}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in "\\n".join(l for l in readme.replace("```", "").splitlines() if not l.startswith("|---")), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = open("/home/claude/studies/river-names/LICENSE", encoding="utf-8").read()
lic = lic.split("Text and figures:")[0] + """Text and figures: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Tristan Hotham, 2026.
Street data (data/streets.csv, streets.json, rings.geojson, town_clock.csv, town_rings.csv, by_county.csv): derived from OpenStreetMap, © OpenStreetMap contributors, Open Database Licence 1.0 (https://opendatacommons.org/licenses/odbl/1-0/).
data/places.json: from Wikidata (CC0). data/battles.csv and data/results.json: CC BY 4.0.
Fonts under the SIL Open Font License.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Victorian builders named streets after the latest battle. I mapped all {N['clean']:,} UK streets named after battles from Camperdown (1797) to Arnhem (1944): in {T['positive']} of {T['towns']} towns, the later battles lie farther from the centre

**Body:**

Alma Road (1854), Inkerman Street, Ladysmith Road (1900): new streets were often named after the latest victory. If towns grew outwards, the battle names should be a clock in the street plan. So I matched every OpenStreetMap street in the UK against a table of battles and dates.

- Waterloo ({R['top_clock'][0]['n']}), Alma ({R['top_clock'][1]['n']}) and Trafalgar ({R['top_clock'][2]['n']}) lead.
- The two-year Crimean War gave {R['crimea_vs_before']['crimea']} street names, more than both world wars together ({R['world_wars']['n']}).
- {R['world_wars']['modern_pc']:.0f}% of world-war battle streets are Closes, Drives and Ways (many probably named later, on new estates), against {R['victorian']['modern_pc']:.0f}% for Victorian battles.
- The clock is real but slow: typical distance from the town centre {E[NAP]['median_km']:.1f} km for Napoleonic battles, {E[CRI]['median_km']:.1f} km for the Crimea, {E[BOER]['median_km']:.1f} km for the Boer War. It tells the French wars from the Boer War, not Waterloo from the Alma, and it weakens (but survives) when streets of one war standing together are counted once.

Set aside: {N['old']:,} streets after battles before 1793 (Blenheim, Naseby) and {N['ambiguous']} with ambiguous names (Nile, Quebec, Kimberley, Gibraltar).

Interactive map with a date slider and town rings: {PAGE}

**Source comment:**

Data: OpenStreetMap contributors (ODbL) via QLever; towns from Wikidata (CC0). Tools: Python (pandas, geopandas, scipy, matplotlib), MapLibre with OpenFreeMap tiles. Battle table, rules and hand decisions in the repo: {REPO}
"""
for bad in ("—", "–", "--"):
    assert bad not in post, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README, LICENSE, post written")
