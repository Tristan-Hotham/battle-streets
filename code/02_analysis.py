"""Step 2: false friends out, towns and distances, the battle clock test, results.json and the data tables.
The clock: streets named after battles from 1793 on (not ambiguous names, not near a place of the same name), with a
traditional street word (Street, Road, Terrace, Place...), in a town of 20,000 people or more within 10 km. Within each
town: does distance from the town centre rise with the battle's date? Spearman rank correlation per town, pooled by a
permutation test (battle years shuffled within towns), and the within-town distance percentile of each war."""
import pandas as pd, numpy as np
from scipy.spatial import cKDTree
from scipy.stats import spearmanr, binomtest
from common import *
from battles import B, BKEY, era, ERAS

S = pd.read_csv(f"{WORK}/streets_raw.csv", keep_default_na=False, dtype={"ways": str})
S["place_km"] = pd.to_numeric(S.place_km, errors="coerce")
O = pd.read_csv(os.path.join(ROOT, "code", "overrides.csv"), keep_default_na=False)
drop = np.zeros(len(S), bool)
for o in O.itertuples():
    m = (S.battle == o.battle) & (S.name == o.name) & ((S.county == o.county) if o.county else True)
    assert m.any(), o
    drop |= m.values
n_raw = len(S)
S = S[~drop].copy()
S["year"] = S.battle.map(lambda k: BKEY[k][3][0])
S["date"] = S.battle.map(lambda k: "%04d-%02d-%02d" % BKEY[k][3])
S["war"] = S.battle.map(lambda k: BKEY[k][4])
S["flag"] = S.battle.map(lambda k: BKEY[k][5])
S["label"] = S.battle.map(lambda k: BKEY[k][1])
S["era"] = S.year.map(era)
TRAD = {"street", "road", "terrace", "place", "row", "square", "grove", "crescent", "lane", "villas", "buildings", "cottages", "parade", "mount", "hill", "walk", "vale"}
MODERN = {"close", "drive", "way", "court", "mews", "rise", "view", "gardens", "chase", "croft", "green", "link", "heights", "park", "fields", "boulevard", "lawn", "meadow", "paddock"}
S["style"] = np.where(S.suffix.isin(TRAD), "traditional", np.where(S.suffix.isin(MODERN), "modern", "other"))
# towns: nearest Wikidata town of 20,000 or more within 10 km; all of Greater London is London (centre: Wikidata's London point)
T = settlements(20000)
tx, ty = bng(T.lon.values, T.lat.values)
d, i = cKDTree(np.c_[tx, ty]).query(S[["x", "y"]].values)
S["town"] = np.where(d <= 10000, T.name.values[i], "")
S["town_qid"] = np.where(d <= 10000, T.qid.values[i], "")
lon_i = int(np.where(T.name.values == "London")[0][0])
S.loc[S.county == "Greater London", "town"] = "London"; S.loc[S.county == "Greater London", "town_qid"] = T.qid.values[lon_i]
TC = T.set_index("qid")
S["town_lon"] = S.town_qid.map(lambda q: TC.lon.get(q, np.nan) if q else np.nan)
S["town_lat"] = S.town_qid.map(lambda q: TC.lat.get(q, np.nan) if q else np.nan)
S["town_pop"] = S.town_qid.map(lambda q: TC["pop"].get(q, np.nan) if q else np.nan)
S["dist_km"] = km(S.lat.values, S.lon.values, S.town_lat.values, S.town_lon.values)
S["clock"] = (S.flag == "") & (S.place == "") & (S.year >= 1793)
S = S.sort_values(["year", "battle", "county", "name"]).reset_index(drop=True)
S["id"] = np.arange(len(S))
S["first_way"] = S.ways.str.split(";").str[0]
cols = ["id", "battle", "label", "date", "year", "war", "era", "flag", "name", "suffix", "style", "lon", "lat", "county", "nation", "town", "town_pop",
        "dist_km", "place", "clock", "n_ways", "hws", "first_way", "ways"]
S[cols].round({"lon": 5, "lat": 5, "dist_km": 3}).to_csv(f"{DATA}/streets.csv", index=False)
pd.DataFrame([{"key": b[0], "battle": b[1], "date": "%04d-%02d-%02d" % b[3], "war": b[4], "era": era(b[3][0]), "status": {"": "clock", "old": "before 1793", "amb": "ambiguous"}[b[5]],
               "note": b[6], "streets": int((S.battle == b[0]).sum())} for b in B]).to_csv(f"{DATA}/battles.csv", index=False)

R = {"n": {"ways": int(len(pd.read_csv(f"{WORK}/ways.csv", usecols=["way"]))), "streets_raw": int(n_raw), "dropped_by_hand": int(drop.sum()), "streets": int(len(S)),
           "merged_ways": int(S.n_ways.sum() - len(S)), "battles_in_table": len(B), "battles_found": int(S.battle.nunique()),
           "ambiguous": int((S.flag == "amb").sum()), "old": int((S.flag == "old").sum()), "place_named": int(((S.place != "") & (S.flag == "")).sum()),
           "place_named_all": int((S.place != "").sum()), "clean": int((S.flag == "").sum()), "clock": int(S.clock.sum()), "clock_town": int((S.clock & (S.town != "")).sum())}}
R["n"]["ambiguous_battles"] = sorted({BKEY[k][1] for k in S[S.flag == "amb"].battle})
# ---- the most common names and the bursts
top = S.battle.value_counts()
R["top"] = [{"battle": BKEY[k][1], "key": k, "n": int(n), "year": BKEY[k][3][0], "flag": BKEY[k][5]} for k, n in top.head(15).items()]
R["top_clock"] = [{"battle": BKEY[k][1], "n": int(n), "year": BKEY[k][3][0]} for k, n in S[S.flag == ""].battle.value_counts().head(10).items()]
R["by_era"] = {e: {"n": int((S.era == e).sum()), "clean": int(((S.era == e) & (S.flag == "")).sum()),
                   "modern_pc": 100 * float(((S.era == e) & (S["style"] == "modern") & (S.flag == "")).sum() / max(1, ((S.era == e) & (S.flag == "") & (S["style"] != "other")).sum()))}
               for e in ERAS}
R["wars"] = {}
for w, g in S[S.flag == ""].groupby("war"):
    R["wars"][w] = {"n": int(len(g)), "battles": int(g.battle.nunique())}
ww = S[(S.flag == "") & S.era.isin(["First World War", "Second World War"])]
R["world_wars"] = {"n": int(len(ww)), "pc": 100 * len(ww) / int((S.flag == "").sum()), "modern_pc": 100 * float((ww["style"] == "modern").mean()),
                   "wwi": int((ww.era == "First World War").sum()), "wwii": int((ww.era == "Second World War").sum())}
vic = S[(S.flag == "") & S.year.between(1854, 1902)]
R["victorian"] = {"n": int(len(vic)), "modern_pc": 100 * float((vic["style"] == "modern").mean()), "traditional_pc": 100 * float((vic["style"] == "traditional").mean())}
for k in ("waterloo", "trafalgar", "alma", "inkerman", "ladysmith", "mafeking", "arnhem", "alamein", "jutland", "mons", "blenheim", "kimberley"):
    g = S[S.battle == k]
    R.setdefault("battle", {})[k] = {"n": int(len(g)), "modern_pc": 100 * float((g["style"] == "modern").mean()), "traditional_pc": 100 * float((g["style"] == "traditional").mean()),
                                     "towns": int(g[g.town != ""].town.nunique())}
# Crimea burst: 1854 to 1856 battles against the whole 1816 to 1853 run
R["crimea_vs_before"] = {"crimea": int(((S.era == "Crimea 1854 to 1856") & (S.flag == "")).sum()), "before": int(((S.era == "1816 to 1853") & (S.flag == "")).sum())}
# counties
cc = S[S.flag == ""].county.value_counts()
R["counties"] = [{"county": c, "n": int(n), "top": S[(S.county == c) & (S.flag == "")].battle.map(lambda k: BKEY[k][1]).value_counts().index[0]} for c, n in cc.head(10).items()]
S[S.flag == ""].pivot_table(index="county", columns="era", values="id", aggfunc="size", fill_value=0).to_csv(f"{DATA}/by_county.csv")
R["nations"] = {n: int(v) for n, v in S[S.flag == ""].nation.value_counts().items()}

# ---- the clock test
CK = S[S.clock & (S.town != "")].copy()
CT = CK[CK["style"] == "traditional"].copy()


def town_rhos(D, min_n=4):
    out = []
    for t, g in D.groupby("town"):
        if len(g) >= min_n and g.year.nunique() >= 2:
            r = spearmanr(g.year, g.dist_km).statistic
            out.append((t, len(g), r, g.year.nunique()))
    return pd.DataFrame(out, columns=["town", "n", "rho", "years"])


def perm(D, min_n=4, reps=4000, seed=7):
    """mean within-town Spearman rho, and its permutation p-value (battle years shuffled within each town)"""
    from scipy.stats import rankdata
    rng = np.random.default_rng(seed)
    gs = []
    for _, g in D.groupby("town"):
        if len(g) >= min_n and g.year.nunique() >= 2:
            ry, rd = rankdata(g.year.values), rankdata(g.dist_km.values)
            gs.append(((ry - ry.mean()) / ry.std(), (rd - rd.mean()) / rd.std()))
    obs = np.mean([np.mean(a * b) for a, b in gs])
    null = np.zeros(reps)
    for a, b in gs:
        P_ = np.argsort(rng.random((reps, len(a))), axis=1)
        null += (a[P_] * b).mean(axis=1)
    null /= len(gs)
    global PERM_COUNT
    PERM_COUNT = int(np.sum(null >= obs))
    return float(obs), float((np.sum(null >= obs) + 1) / (reps + 1)), float(np.percentile(null, 97.5))


def summary(D, label, min_n=4, reps=4000):
    tr = town_rhos(D, min_n)
    tr = tr[tr.rho.notna()]
    obs, p, hi = perm(D, min_n, reps)
    pos = int((tr.rho > 0).sum()); neg = int((tr.rho < 0).sum())
    return {"label": label, "perm_count": PERM_COUNT, "reps": reps, "towns": int(len(tr)), "streets": int(tr.n.sum()), "mean_rho": float(tr.rho.mean()), "median_rho": float(tr.rho.median()),
            "positive": pos, "negative": neg, "sign_p": float(binomtest(pos, pos + neg, 0.5, alternative="greater").pvalue) if pos + neg else 1.0,
            "perm_p": p, "null_975": hi, "wmean_rho": float(np.average(tr.rho, weights=tr.n))}, tr


R["test"], TR = summary(CT, "traditional street words, towns with 4 or more")
R["test_all"], _ = summary(CK, "all street words, towns with 4 or more")
R["test_min6"], _ = summary(CT, "traditional, towns with 6 or more", min_n=6)
R["test_victorian"], _ = summary(CT[CT.year.between(1793, 1902)], "traditional, 1793 to 1902 only")
nl = CT[CT.town != "London"]
R["test_no_london"], _ = summary(nl, "traditional, without London")
# spatial clustering: streets of one war close together in a town were probably named together, so the permutation test,
# which treats each street as independent, may overstate the evidence. Count each cluster of same-war streets within 500 m once.
CU = CT.copy(); CU["k"] = CU.town + "|" + CU.era
CU["g"] = merge_close(CU, 500, key="k")
CU = CU.groupby("g").agg(town=("town", "first"), year=("year", "first"), dist_km=("dist_km", "mean")).reset_index()
R["test_cluster"], _ = summary(CU, "traditional, same-war streets within 500 m counted once")
R["test_cluster"]["units_all"] = int(len(CU))
TR.sort_values("n", ascending=False).round(3).to_csv(f"{DATA}/town_clock.csv", index=False)
# within-town distance percentile by era (towns with 3 or more traditional clock streets)
CT["pct"] = CT.groupby("town").dist_km.rank(pct=True, method="average")
CT["tn"] = CT.groupby("town").id.transform("size")
P = CT[CT.tn >= 3]
rng = np.random.default_rng(3)
R["era_pct"] = {}
for e in ERAS[1:]:
    v = P[P.era == e].pct.values
    if len(v) < 5:
        continue
    bs = [rng.choice(v, len(v)).mean() for _ in range(2000)]
    R["era_pct"][e] = {"n": int(len(v)), "mean": float(v.mean()), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                       "median_km": float(np.median(P[P.era == e].dist_km))}
R["era_pct_n"] = int(len(P)); R["era_pct_towns"] = int(P.town.nunique())
# relative distance: distance / town median, by era
CT["rel"] = CT.dist_km / CT.groupby("town").dist_km.transform("median")
# towns with the longest clock: traditional clock streets in at least three of the four big wars
BIG = ["Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Boer War 1899 to 1902", "First World War"]
rows = []
for t, g in CT.groupby("town"):
    eras = [e for e in BIG if (g.era == e).any()]
    if len(eras) >= 3:
        rows.append({"town": t, "n": int(len(g)), "eras": len(eras), "rho": float(spearmanr(g.year, g.dist_km).statistic) if g.year.nunique() > 1 else np.nan,
                     **{e: float(g[g.era == e].dist_km.median()) if (g.era == e).any() else None for e in BIG},
                     "lon": float(TC.lon[g.town_qid.iloc[0]]), "lat": float(TC.lat[g.town_qid.iloc[0]])})
LC = pd.DataFrame(rows).sort_values(["eras", "n"], ascending=False)
LC.round(3).to_csv(f"{DATA}/town_rings.csv", index=False)
R["long_clocks"] = [{"town": r.town, "n": int(r.n), "eras": int(r.eras), "rho": r.rho, "nap": r[BIG[0]], "crimea": r[BIG[1]], "boer": r[BIG[2]], "wwi": r[BIG[3]]}
                    for _, r in LC.head(12).iterrows()]
R["long_clocks_n"] = int(len(LC))
both = LC[LC[BIG[1]].notna() & LC[BIG[2]].notna()]
R["crimea_boer_towns"] = int(len(both)); R["crimea_inside_boer"] = int((both[BIG[1]] < both[BIG[2]]).sum())
both = LC[LC[BIG[0]].notna() & LC[BIG[1]].notna()]
R["nap_crimea_towns"] = int(len(both)); R["nap_inside_crimea"] = int((both[BIG[0]] < both[BIG[1]]).sum())
# all towns (3+ traditional clock streets), each pair of wars: share of towns where the earlier war's median is nearer the centre
PW = {}
for a, b in [(BIG[0], BIG[1]), (BIG[1], BIG[2]), (BIG[2], BIG[3]), (BIG[0], BIG[2])]:
    med = CT.groupby(["town", "era"]).dist_km.median().unstack()
    if a in med and b in med:
        m2 = med[[a, b]].dropna()
        PW[{BIG[0]: "nap", BIG[1]: "crimea", BIG[2]: "boer", BIG[3]: "wwi"}[a] + "_" + {BIG[0]: "nap", BIG[1]: "crimea", BIG[2]: "boer", BIG[3]: "wwi"}[b]] = {"towns": int(len(m2)), "inside": int((m2[a] < m2[b]).sum())}
R["pairs"] = PW
# rings for the map: per town (3 or more traditional clock streets), median distance per big war
rings = []
for t, g in CT.groupby("town"):
    if len(g) < 3: continue
    for e in BIG + ["Second World War"]:
        s = g[g.era == e]
        if len(s):
            rings.append({"town": t, "era": e, "n": int(len(s)), "km": float(s.dist_km.median()), "lon": float(TC.lon[g.town_qid.iloc[0]]), "lat": float(TC.lat[g.town_qid.iloc[0]])})
pd.DataFrame(rings).round(4).to_csv(f"{WORK}/rings.csv", index=False)
# duplicates left after joining: same name within 1.5 km
from collections import Counter
dup = 0
for nm, g in S.groupby("norm" if "norm" in S else "name"):
    if len(g) > 1:
        P2 = np.c_[g.x.values, g.y.values]
        dup += len(cKDTree(P2).query_pairs(1500))
R["n"]["near_duplicates_1500m"] = int(dup)
# derived numbers quoted in the text
R["test_towns_signed"] = R["test"]["positive"] + R["test"]["negative"]
R["n_battles_clean"] = int(S[S.flag == ""].battle.nunique())
R["amb_list"] = ", ".join(R["n"]["ambiguous_battles"][:-1]) + " and " + R["n"]["ambiguous_battles"][-1]
R["lc"] = {x["town"]: x for x in R["long_clocks"]}
R["tc"] = {r.town: float(r.rho) for r in TR.itertuples()}
eng = S[(S.flag == "") & (S.nation == "England")]
tops = eng.groupby("county").battle.agg(lambda s: s.value_counts().index[0])
R["counties_england"] = int(len(tops)); R["alma_top_counties"] = int((tops == "alma").sum()); R["trafalgar_top_counties"] = sorted(tops[tops == "trafalgar"].index)
# Alma is also a woman's name: Alma streets without a traditional street word and more than 1 km from any Alma Street, Road or
# Terrace may be named after a person or a house rather than the battle (an upper bound on that contamination)
from scipy.spatial import cKDTree as _KD
A = S[(S.battle == "alma") & (S.flag == "")]
At, An = A[A["style"] == "traditional"], A[A["style"] != "traditional"]
dA, _i = _KD(At[["x", "y"]].values).query(An[["x", "y"]].values)
R["alma_check"] = {"n": int(len(A)), "not_traditional": int(len(An)), "isolated": int((dA > 1000).sum())}
R["alma_check"]["n_min"] = R["alma_check"]["n"] - R["alma_check"]["isolated"]
R["alma_check"]["crimea_min"] = R["crimea_vs_before"]["crimea"] - R["alma_check"]["isolated"]
R["test_level"] = R["test"]["towns"] - R["test"]["positive"] - R["test"]["negative"]
R["place_examples"] = S[(S.place != "") & (S.flag == "")].groupby(["battle", "place", "county"]).size().sort_values(ascending=False).head(8).reset_index().values.tolist()
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("n", "test", "test_all", "test_min6", "test_victorian", "test_no_london", "era_pct", "world_wars", "victorian")}, indent=0)[:4000])
print(R["top"][:8]); print(R["long_clocks"][:6]); print(R["counties"][:5]); print(R["by_era"])
