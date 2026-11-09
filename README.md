# Waterloo Road and the clock in the streets

Battle street names and the growth of British towns. 6,885 OpenStreetMap highways whose names contain one of 111 battle names, joined into 3,352 streets; battles before 1793 and ambiguous names set aside; the remaining 1,690 streets dated by their battle and tested for a "clock": do streets named after later battles lie farther from the town centre?

Interactive page: https://maps.tristanhotham.com/battle-streets/
Paper: https://doi.org/10.5281/zenodo.24086515
Blog post: https://blog.tristanhotham.com/2026/10/31/battle-streets/
Code and data: https://github.com/Tristan-Hotham/battle-streets

## Headline results

- Waterloo (367), Alma (340) and Trafalgar (241) are the commonest battles from 1793 on; Blenheim (478) is the commonest battle name of all, but often via the palace.
- Bursts: the four Crimean battles gave 425 streets, more than both world wars together (315); the battles of 1816 to 1853 gave 18.
- World-war names are far more often estate names: 39% end in Close, Drive, Way, Court or Gardens, against 13% for battles of 1854 to 1902.
- The clock: in 53 of 75 towns (traditional street words, four or more streets) later battles lie farther out, in 19 the other way; mean within-town Spearman rho 0.25, none of 4,000 within-town permutations as high. Counting clusters of same-war streets within 500 m once, rho is 0.16 (27 of 4,000 permutations as high): weaker, still there. Median distance from the centre: 1.5 km (Napoleonic), 2.0 km (Crimea), 2.4 km (Boer War).
- A coarse clock: Napoleonic streets nearer the centre than Boer War ones in 30 of 40 towns, but nearer than Crimean ones in only 47 of 92. London barely shows it (rho 0.12); Bristol, Glasgow and Hull do.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: MapLibre on the OpenFreeMap Positron base map, every battle street coloured by the battle's date, a date slider, rings at each war's median distance per town, search and popups. |
| `header.png` | Social card, 1200 x 630. |
| `data/streets.csv` | Every battle street (3,352): battle, date, war, era, status (clock, old, ambiguous), name, street word, position, county, nation, town, distance from the town centre, nearby place of the same name, OSM way ids. ODbL. |
| `data/battles.csv` | The battle table: 111 battles with the date used, war, status and note, and the number of streets. |
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
- Set aside: battles before 1793 (1,008 streets), ambiguous names (654 streets: Aboukir, Alexandria, Cabul, Copenhagen, Crimea, Delhi, Dunkirk, Falklands, Gibraltar, Kandahar, Kimberley, Magenta, Minorca, Nile, Portobello, Quebec, Scinde, St Vincent and Vigo), streets within 3 km of a place of the same name (32), and 9 non-streets or non-battles removed by hand.
- Town: nearest Wikidata town of 20,000 or more within 10 km (Greater London as one); distance from its Wikidata point.
- Test: streets with a traditional street word; Spearman rho of battle year and distance in each town with four or more; mean rho against 4,000 within-town permutations; within-town distance percentile by war with bootstrap intervals. Sensitivity: all street words, six or more streets, up to 1902, without London, same-war clusters within 500 m counted once.
- Caveats: the name dates the battle, not the street; towns did not grow in rings; conurbations compress distances; ambiguity rules are judgements; Alma is also a woman's name (50 of 340 Alma streets are newer-style names away from any Alma Street or Road).

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

Hotham, T. (2026) Waterloo Road and the clock in the streets: battle street names and the growth of British towns. Zenodo. https://doi.org/10.5281/zenodo.24086515

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
