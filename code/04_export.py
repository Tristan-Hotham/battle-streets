"""Step 4: page data. data/streets.json (every battle street, compact rows, with the battle table), data/rings.geojson
(for towns with three or more clock streets: a circle at the median distance of each war's streets), data/places.json
(towns of 5,000 people or more, for the search)."""
import pandas as pd, numpy as np
from common import *
from battles import B, BKEY

S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False, dtype={"first_way": str})
BI = {b[0]: i for i, b in enumerate(B)}
cnt = S.battle.value_counts()
FLAG = {"": 0, "old": 1, "amb": 2}
rows = []
for r in S.itertuples():
    f = FLAG[r.flag] if not (r.flag == "" and r.place) else 3
    rows.append([round(r.lon, 5), round(r.lat, 5), BI[r.battle], r.name, r.town, round(float(r.dist_km), 2) if r.dist_km != "" else None, f,
                 int(r.first_way), int(r.n_ways), r.county, r.place, r.style])
battles = [[b[0], b[1], "%04d-%02d-%02d" % b[3], b[4], b[5], b[6], int(cnt.get(b[0], 0))] for b in B]
jsave({"battles": battles, "rows": rows}, f"{DATA}/streets.json")
RG = pd.read_csv(f"{WORK}/rings.csv")
COL = {"Napoleonic 1793 to 1815": 1805, "Crimea 1854 to 1856": 1855, "Boer War 1899 to 1902": 1900, "First World War": 1916, "Second World War": 1942}
feats = []
for r in RG.itertuples():
    k = r.km / 6371.0
    ang = np.linspace(0, 2 * np.pi, 73)
    la = np.degrees(np.arcsin(np.sin(np.radians(r.lat)) * np.cos(k) + np.cos(np.radians(r.lat)) * np.sin(k) * np.cos(ang)))
    lo = r.lon + np.degrees(np.arctan2(np.sin(ang) * np.sin(k) * np.cos(np.radians(r.lat)), np.cos(k) - np.sin(np.radians(r.lat)) * np.sin(np.radians(la))))
    feats.append({"type": "Feature", "properties": {"town": r.town, "era": r.era, "y": COL[r.era], "n": int(r.n), "km": round(r.km, 2)},
                  "geometry": {"type": "LineString", "coordinates": [[round(a, 5), round(b, 5)] for a, b in zip(lo, la)]}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/rings.geojson")
T = settlements(5000)
jsave({"places": [[r.name, round(r.lon, 4), round(r.lat, 4)] for r in T.sort_values("pop", ascending=False).itertuples()]}, f"{DATA}/places.json")
print("streets.json", os.path.getsize(f"{DATA}/streets.json") // 1024, "KB; rings", len(feats))
