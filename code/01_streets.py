"""Step 1: OSM ways -> battle-named streets. Matches each name against the battle table (whole words), joins the pieces of
one street (same name, first points chaining within 600 m), flags streets that probably take their name from a nearby
place of the same name, assigns county and town. Writes WORK/ways.csv, WORK/streets_raw.csv and WORK/review_*.txt."""
import pandas as pd, numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from common import *
from battles import B

rows = []
for r in read_tsv(STREETS):
    lon, lat = point(r["p"])
    if lon is None or not r["name"]:
        continue
    rows.append({"way": r["w"].rsplit("/", 1)[-1], "hw": r["hw"], "name": r["name"].strip(), "lon": lon, "lat": lat})
W = pd.DataFrame(rows)
RX = [(b[0], re.compile(r"(?<![a-z])(" + b[2] + r")(?![a-z])", re.I)) for b in B]


def match(name):
    s = name.lower()
    if re.search(r"\bsur\b|\bsur-|-sur-", s):                    # twin towns: Villiers-sur-Marne Avenue, Champs sur Marne
        return ""
    hits = [(m.start(), k) for k, rx in RX for m in [rx.search(s)] if m]
    return min(hits)[1] if hits else ""


W["battle"] = W.name.apply(match)
W = W[W.battle != ""].copy()
print("ways naming a battle", len(W))
x, y = bng(W.lon.values, W.lat.values)
W["x"], W["y"] = x, y
C = gpd.read_file(f"{GEO}/counties_uk.geojson").to_crs(27700)
P = gpd.GeoDataFrame(W[["way"]], geometry=gpd.points_from_xy(W.x, W.y), crs=27700)
J = gpd.sjoin_nearest(P, C[["county", "nation", "geometry"]], how="left", max_distance=3000)
J = J[~J.index.duplicated()]
W["county"], W["nation"] = J["county"].values, J["nation"].values
W["norm"] = W.name.str.lower().str.replace(r"[^a-z ]", " ", regex=True).str.replace(r"\bst\b", "street", regex=True).str.replace(r"\brd\b", "road", regex=True).str.split().str.join(" ")
W["gid"] = merge_close(W, 600)
# long roads (A, B and minor through roads, tracks, cycle paths) are often mapped with gaps: join their pieces within 1.5 km
ROADS = {"primary", "secondary", "tertiary", "trunk", "unclassified", "track", "cycleway", "primary_link", "secondary_link", "tertiary_link", "trunk_link"}
long_ = W.groupby("gid").hw.transform(lambda s: bool(set(s) & ROADS)).astype(bool)
L = W[long_].copy(); L["gid2"] = merge_close(L, 1500)
W.loc[long_, "gid"] = L.groupby("gid2").gid.transform("min").values
W.to_csv(f"{WORK}/ways.csv", index=False)
S = W.groupby("gid").agg(name=("name", lambda s: s.value_counts().index[0]), norm=("norm", "first"), battle=("battle", "first"),
                         lon=("lon", "mean"), lat=("lat", "mean"), x=("x", "mean"), y=("y", "mean"), n_ways=("way", "size"),
                         ways=("way", lambda s: ";".join(s)), hws=("hw", lambda s: ";".join(sorted(set(s)))),
                         county=("county", "first"), nation=("nation", "first")).reset_index(drop=True)
S["suffix"] = S.name.str.lower().str.replace(r"\(.*?\)", "", regex=True).str.strip().str.split().str[-1].str.replace(r"[^a-z]", "", regex=True)
# places of the same name: any Wikidata settlement (all types, incl. districts and hamlets) whose label contains the battle word
import gzip
d = pd.read_csv(SETTLE, sep="\t", dtype=str, quoting=3)
d.columns = [c.lstrip("?") for c in d.columns]
d["pl"] = d.pl.str.replace(r'^"|"(@\w+)?$', "", regex=True)
xy = d.coord.str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
d["lon"], d["lat"] = xy[0], xy[1]
d = d.dropna(subset=["lon"]).drop_duplicates(["pl", "lon", "lat"])
px, py = bng(d.lon.values, d.lat.values)
d["x"], d["y"] = px, py
S["place"] = ""; S["place_km"] = np.nan
for k, rx in RX:
    pl = d[d.pl.str.contains(rx.pattern, case=False, regex=True) & ~d.pl.str.contains(r"\d|,", regex=True)]
    m = S.battle == k
    if not len(pl) or not m.any():
        continue
    dist, i = cKDTree(pl[["x", "y"]].values).query(S.loc[m, ["x", "y"]].values)
    S.loc[m, "place"] = np.where(dist <= 3000, pl.pl.values[i], "")
    S.loc[m, "place_km"] = dist / 1000
S.to_csv(f"{WORK}/streets_raw.csv", index=False)
print("streets", len(S), "; near a place of the same name", (S.place != "").sum())
print(S[S.place != ""].groupby(["battle", "place"]).size().sort_values(ascending=False).head(40).to_string())
T = settlements(3000)
tx, ty = bng(T.lon.values, T.lat.values)
dist, i = cKDTree(np.c_[tx, ty]).query(S[["x", "y"]].values)
S["near"] = T.name.values[i]; S["near_km"] = (dist / 1000).round(1)
for k in sorted(S.battle.unique()):
    with open(f"{WORK}/review_{k}.txt", "w") as f:
        for r in S[S.battle == k].sort_values(["county", "name"]).itertuples():
            f.write(f"{r.ways.split(';')[0]}\t{r.name}\t{r.hws}\t{r.county}\t{r.near} {r.near_km} km\t{r.place}\n")
