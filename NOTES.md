# battle-streets: working notes

Brief: /home/claude/work/new10/BRIEFS.md (study 2) + shared rules in new8/new9 BRIEFS.md and /home/claude/newdata/BRIEF.md.
Format refs: studies/river-names (code layout), studies/tower-shadows (plain MapLibre Positron basemap); sibling alleyway-words (same raw data, same engine).
Work files: /home/claude/scratch/battle-streets (delete at the end).

## Pipeline
01_streets (whole-word match to code/battles.py, join pieces 600 m / 1.5 km for through roads, places of the same name within 3 km)
-> 02_analysis (code/overrides.csv, towns >= 20k within 10 km, distances, clock test with within-town permutations, results.json)
-> 03_figures -> 04_export -> 05_build_site -> 06_paper -> reddit/collage.py -> 08_readme -> 07_release -> qa.js.

## Data checks (whole set)
- Read the full list of distinct names for every clock battle (and the per-battle review files in WORK with highway, county,
  nearest town, nearby same-name place). Removed by hand 9 (overrides.csv): Jutland Pothole Markers, Talavera Residential
  Moorings, Waterloo Social Sidings, Waterloo Clump, Alma Leisure Park, Alma Martin Way (a person), Ionad Assaye, Arras Hill
  (E Yorks place name Arras), De-Verdun Avenue (family name). Twin-town names (Villiers-sur-Marne Avenue, Champs sur Marne) excluded by rule.
- Ambiguous names set aside (654 streets, 19% of all battle-named streets): Aboukir, Alexandria, Cabul, Copenhagen, Crimea, Delhi,
  Dunkirk (an old English place name: Dunkirk Kent/Notts/Cheshire; Dunkirk Way Ellesmere Port), Falklands, Gibraltar, Kandahar,
  Kimberley, Magenta, Minorca, Nile, Portobello, Quebec, Scinde, St Vincent, Vigo. Pre-1793 battles (1,008 streets) set aside.
- Place-named: 32 clock streets within 3 km of a Wikidata place containing the battle word (Waterloo London/Merseyside/Gwent/GM,
  Inkerman Co Durham, Camperdown Dundee, Maida Vale) set aside from the clock; settlement labels with digits/commas (buildings) ignored.
- Duplicated segments: joined same name within 600 m, through roads within 1.5 km (3,509 pieces joined). 11 same-name pairs
  within 1.5 km remain (residential streets, possibly distinct); listed by the check in 02_analysis.
- Spion Kop: several are hills/hamlets named after the battle (kept, Boer era). Arras, Marne, Somme, Verdun kept as WWI.
- Bug fixed: DataFrame.style attribute clash (use S["style"]).

## Findings (results.json)
- Waterloo 367, Alma 340, Trafalgar 241 (clock battles); Blenheim 478 (pre-1793). Crimea 425 > both world wars 315.
- Modern street word (Close/Drive/Way/Court...): 12.9% for 1854 to 1902 battles vs 39.4% for world wars.
- Clock test (traditional street words, towns >= 4 streets): 75 towns, mean rho 0.25, 53+/19-, 0 of 4,000 permutations as high.
  Sensitivity: all words 0.14 (6/4000), >= 6 streets 0.25, to 1902 0.18 (4/4000), no London 0.26.
- Within-town percentile: Napoleonic 0.54, Crimea 0.58, Boer 0.68, WWI 0.66, WWII 0.62; median km 1.45 / 2.01 / 2.36 / 3.00.
- Coarse: Nap inside Boer 30/40 towns, Nap inside Crimea 47/92 (coin toss), Crimea inside Boer 23/38, Boer inside WWI 8/17.
- London rho 0.12; Bristol 0.66, Glasgow 0.75, Hull 0.84; Preston -0.33, Lincoln -0.84.

## References and claims to verify (cited from memory)
- Azaryahu, M. (1996) The power of commemorative street names. Environment and Planning D 14(3), 311 to 330.
- Alderman, D. H. (2000) A street fit for a King. The Professional Geographer 52(4), 672 to 684.
- Rose-Redwood, R., Alderman, D. and Azaryahu, M. (2010) Geographies of toponymic inscription. Progress in Human Geography 34(4), 453 to 470.
- Conzen, M. R. G. (1960) Alnwick, Northumberland: A Study in Town-Plan Analysis. IBG Publication 27. London: George Philip.
- Whitehand, J. W. R. (1972) Building cycles and the spatial pattern of urban growth. Transactions of the IBG 56, 39 to 55.
- Haklay (2010); Bast and Buchhold (2017) as in alleyway-words.
- Battle dates in code/battles.py (standard dates; sieges dated by relief/fall: Ladysmith 28 Feb 1900, Mafeking 17 May 1900,
  Kimberley 15 Feb 1900, Sebastopol 9 Sep 1855, Lucknow 16 Nov 1857, Khartoum 26 Jan 1885, Chitral 20 Apr 1895). Year is
  what the analysis uses.
- Claims: London's Copenhagen Street named from Copenhagen House; Maida Vale named after the battle via an inn (Hero of Maida);
  Magenta the colour named after the battle; Jutland Road in Bristol at Avonmouth/Shirehampton (from coordinates).

## Status
- All files built; QA desktop + phone in qa/, 0 console errors.

## Independent review (2026)
- Pipeline rerun from raw: identical results.json. Battle dates and wars checked; all 7 references verified (titles, venues, volumes, pages).
- Fixed: "53 of 72 towns" -> 53 of 75 (19 negative, 3 level) everywhere; README "mostly late estate names" (39% is not most);
  Reddit title "from Trafalgar" (Camperdown 1797 is earliest); "Glasgow and Hull run in order" softened (Glasgow WWI < Boer);
  paper said streets placed at first point of first piece (actually mean of pieces' first points); Copenhagen Street wording.
- Added test_cluster: same-war streets within 500 m in a town counted once -> rho 0.16, 51 towns, 27/4000 (p 0.007). Street-level test
  overstates precision; reported in paper, page, blog, README, Reddit.
- Added alma_check: 70 of 340 Alma streets not traditional, 50 of them >1 km from any traditional Alma street (possible forename);
  Crimea minimum 375 still > 315 world wars. Caveat in paper, page, blog, README.
