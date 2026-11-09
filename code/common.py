"""Shared paths, constants and helpers for the battle-streets study ("Waterloo Road and the clock in the streets").

Raw inputs (read in place, never modified):
  STREETS /home/claude/newdata/raw_new10/streets_uk.tsv.gz
          OpenStreetMap via QLever: UK ways with highway=* whose name contains a battle name (Waterloo, Trafalgar, Alma,
          Inkerman, Mafeking...) or an alley word (shared with the alleyway-words study). Columns: way, highway, name,
          first part of the geometry (WKT).
  SETTLE  /home/claude/newdata/raw_new8/uk_settlements.tsv  Wikidata UK settlements with population (CC0).
  GEO     /home/claude/newdata/raw/geo/counties_uk.geojson (ONS boundaries, OGL v3) and Natural Earth (public domain).
Intermediates go to WORK (/home/claude/scratch/battle-streets), outside the repository.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREETS = os.environ.get("BS_STREETS", "/home/claude/newdata/raw_new10/streets_uk.tsv.gz")
SETTLE = os.environ.get("BS_SETTLE", "/home/claude/newdata/raw_new8/uk_settlements.tsv")
GEO = os.environ.get("BS_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("BS_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("BS_INK", "/home/claude/studies/ink-map")
INKFONTS = os.path.join(INK, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.environ.get("BS_WORK", "/home/claude/scratch/battle-streets")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "battle-streets"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "x": return f"{float(v):.1f}"
    raise ValueError(f)


def fill(t, R, keep=("DOI", "DOI_URL", "BLOG_URL"), tf=None):
    """replace {{path|fmt}} tokens from results.json; leave the publisher's placeholders and IMG tokens"""
    f = tf or fmt
    return re.sub(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in keep else f(get(R, m.group(1)), m.group(3)), t)


def read_tsv(path):
    """QLever TSV: header line, IRIs in <...>, literals in "..." (possibly @lang or ^^type)."""
    def lit(s):
        s = s.strip()
        if s.startswith("<") and s.endswith(">"):
            return s[1:-1]
        m = re.match(r'^"(.*)"(?:@[\w-]+|\^\^.*)?$', s, re.S)
        if m:
            return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
        return s
    with gzip.open(path, "rt", encoding="utf-8") as f:
        head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
        for line in f:
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(head) - len(parts))
            yield {h: lit(p) for h, p in zip(head, parts)}


def point(wkt):
    """first coordinate pair of a POINT or a (truncated) LINESTRING"""
    m = re.search(r"(?:POINT|LINESTRING|POLYGON)\s*\(+\s*([-\d.eE]+)\s+([-\d.eE]+)", wkt or "")
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))


def elevations(lons, lats):
    """ground height (m) from the zoom-10 Terrarium tiles, bilinear; NaN where no tile"""
    import numpy as np
    from PIL import Image
    n = 256 * 2 ** 10
    lons, lats = np.asarray(lons, float), np.asarray(lats, float)
    X = (lons + 180) / 360 * n
    la = np.radians(lats)
    Y = (1 - np.log(np.tan(la) + 1 / np.cos(la)) / np.pi) / 2 * n
    out = np.full(len(lons), np.nan)
    tx, ty = (X // 256).astype(int), (Y // 256).astype(int)
    cache = {}
    for k in set(zip(tx.tolist(), ty.tolist())):
        p = f"{TILES}/{k[0]}/{k[1]}.png"
        if os.path.exists(p):
            a = np.asarray(Image.open(p).convert("RGB")).astype(float)
            cache[k] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    for i in range(len(lons)):
        h = cache.get((tx[i], ty[i]))
        if h is None:
            continue
        px, py = X[i] - tx[i] * 256 - 0.5, Y[i] - ty[i] * 256 - 0.5
        x0, y0 = int(min(max(np.floor(px), 0), 254)), int(min(max(np.floor(py), 0), 254))
        fx, fy = min(max(px - x0, 0), 1), min(max(py - y0, 0), 1)
        out[i] = (h[y0, x0] * (1 - fx) * (1 - fy) + h[y0, x0 + 1] * fx * (1 - fy) + h[y0 + 1, x0] * (1 - fx) * fy + h[y0 + 1, x0 + 1] * fx * fy)
    return out


TOWN_TYPES = {"town", "market town", "city", "county town", "big city", "new town (UK)", "seaside resort", "town of the United Kingdom",
              "city of United Kingdom", "college town", "port city", "largest city", "railway town", "city status in the United Kingdom",
              "border city", "national capital", "cathedral city", "spa town", "post town", "port settlement", "mill town", "market municipality"}


def settlements(min_pop=10000):
    """Wikidata UK settlements whose types include a town or city type, one row per item (largest population stated),
    with population at least min_pop. Areas of London, suburbs, conurbations and built-up areas are left out; London is
    kept as one city at its Wikidata point."""
    import pandas as pd
    d = pd.read_csv(SETTLE, sep="\t", dtype=str, quoting=3)
    d.columns = [c.lstrip("?") for c in d.columns]
    d["pl"] = d.pl.str.replace(r'^"|"(@\w+)?$', "", regex=True)
    d["typel"] = d.typel.str.replace(r'^"|"(@\w+)?$', "", regex=True)
    d["pop"] = pd.to_numeric(d["pop"], errors="coerce")
    xy = d.coord.str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
    d["lon"], d["lat"] = xy[0], xy[1]
    d["qid"] = d.p.str.extract(r"(Q\d+)")[0]
    g = d.groupby("qid").agg(name=("pl", "first"), lon=("lon", "median"), lat=("lat", "median"), pop=("pop", "max"),
                             types=("typel", lambda s: set(s)))
    g = g[g.types.apply(lambda s: bool(s & TOWN_TYPES)) & (g["pop"] >= min_pop)]
    g = g[~g.name.str.contains("Greater London|metropolitan|Urban Area|Built-up", regex=True)]
    g = g[(g.lat > 49.8) & (g.lat < 61) & (g.lon > -8.7) & (g.lon < 2)]
    g["types"] = g.types.apply(lambda s: "; ".join(sorted(s)))
    return g.reset_index()


def bng(lon, lat):
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 27700, always_xy=True)
    return tr.transform(lon, lat)


def merge_close(df, dist_m, key="norm"):
    """single-linkage groups of rows with the same key whose points (x, y in metres) chain within dist_m"""
    import numpy as np
    from scipy.spatial import cKDTree
    gid = np.full(len(df), -1)
    nxt = 0
    for _, idx in df.groupby(key).indices.items():
        idx = np.asarray(idx)
        if len(idx) == 1:
            gid[idx] = nxt; nxt += 1; continue
        P = df[["x", "y"]].values[idx]
        par = list(range(len(idx)))
        def f(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        for a, b in cKDTree(P).query_pairs(dist_m):
            ra, rb = f(a), f(b)
            if ra != rb: par[ra] = rb
        roots = {}
        for i in range(len(idx)):
            r = f(i)
            if r not in roots:
                roots[r] = nxt; nxt += 1
            gid[idx[i]] = roots[r]
    return gid
