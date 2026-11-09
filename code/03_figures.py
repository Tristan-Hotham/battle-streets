"""Step 3: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px) and the paper (release/paper/f_*.png)."""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from PIL import Image
from figstyle import *
from battles import B, BKEY, ERAS

R = jload(f"{DATA}/results.json")
S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False)
S["clock"] = S.clock.astype(str) == "True"
S["dist_km"] = pd.to_numeric(S.dist_km, errors="coerce")
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
for d in (BLOG, PAPERD):
    os.makedirs(d, exist_ok=True)
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
STOPS = ["#2D1E6B", "#5B2A86", "#8E3A88", "#BF4F6E", "#DE7445", "#E9A33A", "#D9C23A"]   # 1793 .. 1945, dark to light
YCMAP = LinearSegmentedColormap.from_list("yr", STOPS)
YN = Normalize(1793, 1945)
WARCOL = {"Napoleonic 1793 to 1815": YCMAP(YN(1805)), "1816 to 1853": YCMAP(YN(1835)), "Crimea 1854 to 1856": YCMAP(YN(1855)), "Indian Rebellion 1857": YCMAP(YN(1857)),
          "1859 to 1898": YCMAP(YN(1880)), "Boer War 1899 to 1902": YCMAP(YN(1900)), "First World War": YCMAP(YN(1916)), "Second World War": YCMAP(YN(1942))}
f27 = projector(27700)
S["X"], S["Y"] = f27(S.lon.values, S.lat.values)


def out(fig, name, dpi=200):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    im.resize((1600, round(im.size[1] * 1600 / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    w = min(2000, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


# ---------- 1. the bursts: streets per battle on a time line
C = S[S.flag == ""]
cnt = C.groupby(["battle"]).size()
fig = plt.figure(figsize=(12, 6.2)); parchment(fig)
ax = fig.add_axes([0.07, 0.12, 0.9, 0.7])
for k, n in cnt.items():
    y = BKEY[k][3][0] + (BKEY[k][3][1] - 1) / 12
    ax.bar(y, n, width=1.1, color=YCMAP(YN(y)), edgecolor=INKC, lw=0.4)
def yr(k):
    return BKEY[k][3][0] + (BKEY[k][3][1] - 1) / 12


GROUPS = [(1797, 1797.99, 1797.5), (1805, 1805.99, 1805.8), (1806, 1814.99, 1810.5, 125), (1815, 1815.99, 1815.5), (1816, 1853.99, 1835),
          (1854, 1856.99, 1855.5), (1857, 1858, 1863, 30), (1859, 1898.99, 1882), (1899, 1902.99, 1900.5), (1914, 1918.99, 1916.5), (1939, 1945, 1942.5)]
for G_ in GROUPS:
    lo, hi, xc = G_[:3]
    ks = [k for k in cnt.index if lo <= yr(k) <= hi]
    if not ks: continue
    ks.sort(key=lambda k: -cnt[k])
    top_n = max(cnt[k] for k in ks)
    lines = [f"{BKEY[k][1]} {cnt[k]}" for k in ks if cnt[k] >= 3][:6]
    if not lines: continue
    ax.text(xc, G_[3] if len(G_) > 3 else top_n + 8, "\n".join(lines), ha="center", va="bottom", fontproperties=FELL, fontsize=9.5, color=INKC, linespacing=1.15)
ax.set_xlim(1790, 1950); ax.set_ylim(0, cnt.max() * 1.25)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_ylabel("streets named after the battle", fontproperties=FELL, fontsize=11)
for lo, hi, nm in [(1793, 1815, "French wars"), (1854, 1856, "Crimea"), (1899, 1902, "Boer War"), (1914, 1918, "First World War"), (1939, 1945, "Second World War")]:
    ax.axvspan(lo, hi + 1, color="#E2D3AE", alpha=0.45, zorder=0)
fig.text(0.04, 0.95, "Streets named after battles, by the date of the battle", fontproperties=FELLSC, fontsize=15, color=RED)
fig.text(0.04, 0.915, f"{R["n"]["clean"]:,} streets named after {len(cnt)} battles from 1793 on. Left out: {R['n']['old']:,} streets after older battles (Blenheim, Naseby) and {R['n']['ambiguous']:,} with ambiguous names (Kimberley, Quebec, Nile).", fontproperties=FELL, fontsize=10.5, color=MUT)
out(fig, "bursts")

# ---------- 2. the clock: within-town distance percentile by war
E = [e for e in ERAS if e in R["era_pct"]]
fig = plt.figure(figsize=(11, 6.4)); parchment(fig)
ax = fig.add_axes([0.08, 0.18, 0.56, 0.64])
for i, e in enumerate(E):
    v = R["era_pct"][e]
    ax.plot([i, i], [v["lo"], v["hi"]], color=INKC, lw=1.2)
    ax.scatter(i, v["mean"], s=40 + v["n"] * 1.2, color=WARCOL[e], edgecolor=INKC, lw=0.6, zorder=5)
    ax.text(i, v["hi"] + 0.012, f"{v['n']}", ha="center", fontproperties=FELL, fontsize=9.5, color=MUT)
ax.axhline(0.5, color=MUT, ls=(0, (3, 2)), lw=0.8)
ax.text(len(E) - 0.5, 0.505, "no clock", ha="right", fontproperties=FELLIT, fontsize=10, color=MUT)
ax.set_xticks(range(len(E))); ax.set_xticklabels([e.replace(" 1793 to 1815", "\n1793 to 1815").replace(" 1854 to 1856", "\n1854 to 1856").replace(" 1899 to 1902", "\n1899 to 1902")
                                                  .replace("Indian Rebellion 1857", "Indian\nRebellion").replace("First World War", "First\nWorld War").replace("Second World War", "Second\nWorld War")
                                                  .replace("1816 to 1853", "1816 to\n1853").replace("1859 to 1898", "1859 to\n1898") for e in E], fontproperties=FELL, fontsize=9.5)
ax.set_ylabel("position in the town, centre (0) to edge (1)", fontproperties=FELL, fontsize=10.5)
ax.set_ylim(0.2, 0.85)
for s in ("top", "right"): ax.spines[s].set_visible(False)
T = R["test"]
bx = fig.add_axes([0.71, 0.18, 0.26, 0.64])
TR = pd.read_csv(f"{DATA}/town_clock.csv")
bx.hist(TR.rho.dropna(), bins=np.linspace(-1, 1, 17), color="#BF4F6E", edgecolor=INKC, lw=0.4)
bx.axvline(0, color=MUT, ls=(0, (3, 2)), lw=0.8); bx.axvline(T["mean_rho"], color=INKC, lw=1.4)
bx.text(T["mean_rho"] + 0.03, bx.get_ylim()[1] * 0.92, f"mean {T['mean_rho']:.2f}", fontproperties=FELL, fontsize=10, color=INKC)
bx.set_xlabel("rank correlation of date and distance", fontproperties=FELL, fontsize=10)
bx.set_ylabel("towns", fontproperties=FELL, fontsize=10)
for s in ("top", "right"): bx.spines[s].set_visible(False)
fig.text(0.04, 0.95, "The clock in the streets", fontproperties=FELLSC, fontsize=16, color=RED)
fig.text(0.04, 0.915, f"Left: where each war's streets sit within their town (mean rank of distance from the centre, with 95% intervals; {R['era_pct_n']} streets in {R['era_pct_towns']} towns).", fontproperties=FELL, fontsize=10.5, color=MUT)
fig.text(0.04, 0.89, f"Right: in {T['positive']} of {T['positive'] + T['negative']} towns later battles lie farther out (permutation p = {T['perm_p']:.4f}).", fontproperties=FELL, fontsize=10.5, color=MUT)
out(fig, "clock")

# ---------- 3. town clocks: streets around six town centres, with rings at each war's median distance
TOWNS = ["Bristol", "Glasgow", "Kingston upon Hull", "Cheltenham", "Leeds", "Preston"]
CT = S[S.clock & (S["style"] == "traditional") & S.town.isin(TOWNS)]
fig = plt.figure(figsize=(12, 8.4)); parchment(fig)
BIG = ["Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Boer War 1899 to 1902", "First World War"]
RINGC = {BIG[0]: "#2D1E6B", BIG[1]: "#BF4F6E", BIG[2]: "#DE7445", BIG[3]: "#C9A800"}
RINGLS = {BIG[0]: "-", BIG[1]: "-", BIG[2]: (0, (5, 2)), BIG[3]: (0, (2, 1.5))}
TC = settlements(20000).set_index("name")
for i, t in enumerate(TOWNS):
    r_, c_ = divmod(i, 3)
    ax = fig.add_axes([0.02 + c_ * 0.325, 0.52 - r_ * 0.42, 0.3, 0.36])
    g = CT[CT.town == t]
    lon0, lat0 = TC.lon[t], TC.lat[t]
    x0, y0 = f27(lon0, lat0)
    dx, dy = (g.X - x0) / 1000, (g.Y - y0) / 1000
    R_ = max(4.5, float(np.hypot(dx, dy).max()) * 1.15)
    for e in BIG:
        s = g[g.era == e]
        if len(s):
            m = s.dist_km.median()
            ax.add_patch(plt.Circle((0, 0), m, fill=False, ec=RINGC[e], lw=2.4, ls=RINGLS[e], alpha=0.95))
    ax.scatter(dx, dy, s=46, c=[YCMAP(YN(y)) for y in g.year], edgecolor=INKC, lw=0.5, zorder=5)
    sb = 1 if R_ < 6 else 2
    ax.plot([-R_ * 0.9, -R_ * 0.9 + sb], [-R_ * 0.92] * 2, color=INKC, lw=2)
    ax.text(-R_ * 0.9 + sb / 2, -R_ * 0.88, f"{sb} km", ha="center", fontproperties=FELL, fontsize=9, color=INKC)
    ax.plot(0, 0, "+", ms=12, color=RED, mew=2, zorder=7)
    ax.set_xlim(-R_, R_); ax.set_ylim(-R_, R_); ax.set_aspect("equal"); ax.axis("off")
    rho = [x for x in R["long_clocks"] if x["town"] == t]
    tt = pd.read_csv(f"{DATA}/town_clock.csv").set_index("town")
    ax.set_title(f"{t.replace('Kingston upon Hull', 'Hull')}   (rho {tt.rho[t]:+.2f}, {len(g)} streets)", fontproperties=FELLSC, fontsize=12, color=RED)
from matplotlib.lines import Line2D
hs = [Line2D([0], [0], color=RINGC[e], lw=2.4, ls=RINGLS[e]) for e in BIG] + [Line2D([0], [0], marker="+", color=RED, lw=0, ms=10, mew=2)]
fig.legend(hs, [f"median distance of {e} streets" for e in BIG] + ["town centre"], loc="lower center", ncol=3, prop=FELL, fontsize=10, frameon=False)
fig.text(0.04, 0.965, "Six town clocks: battle streets around the town centre, dots coloured by the battle's date", fontproperties=FELLSC, fontsize=14, color=RED)
out(fig, "towns")

# ---------- 4. map: every clock street coloured by year
fig = plt.figure(figsize=(10, 12.5)); parchment(fig)
ax = fig.add_axes([0.0, 0.03, 0.8, 0.88])
ext, f = ink_base(ax, 27700, (-8.0, 1.9, 49.9, 58.8), ripple_m=(8e3, 20e3), coast_lw=0.6, countries=False, min_area=2e7)
o = S[S.flag != ""]
ax.scatter(o.X, o.Y, s=5, color="#B9AC8E", alpha=0.6, lw=0, zorder=4)
c = S[S.flag == ""].sort_values("year")
ax.scatter(c.X, c.Y, s=12, c=[YCMAP(YN(y)) for y in c.year], edgecolor=INKC, lw=0.2, zorder=5)
ax.set_xlim(ext[0] + 0.6e5, ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_facecolor("none")
cb = fig.add_axes([0.78, 0.35, 0.025, 0.4])
cb.imshow(np.linspace(1945, 1793, 200)[:, None], aspect="auto", cmap=YCMAP, norm=YN, extent=[0, 1, 1793, 1945])
cb.set_xticks([]); cb.yaxis.tick_right(); cb.set_yticks([1805, 1815, 1855, 1900, 1916, 1944])
cb.set_yticklabels(["Trafalgar 1805", "Waterloo 1815", "Crimea 1854", "Boer War 1900", "Somme 1916", "Arnhem 1944"], fontproperties=FELL, fontsize=10)
fig.text(0.78, 0.31, "grey: older battles\nand ambiguous names", fontproperties=FELLIT, fontsize=10, color=MUT)
fig.text(0.04, 0.955, "Battle streets of the UK", fontproperties=HAND, fontsize=26, color=RED)
fig.text(0.04, 0.925, f"{len(c):,} streets named after battles from 1793 to 1944, coloured by the date of the battle", fontproperties=FELL, fontsize=12, color=INKC)
out(fig, "map")

# ---------- 5. street words by era: Victorian streets, later Closes
E2 = ["Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Boer War 1899 to 1902", "First World War", "Second World War"]
fig = plt.figure(figsize=(11, 5.4)); parchment(fig)
ax = fig.add_axes([0.24, 0.14, 0.7, 0.68])
for i, e in enumerate(E2):
    g = S[(S.flag == "") & (S.era == e)]
    tot = len(g)
    left = 0
    for st, col in [("traditional", "#5B2A86"), ("other", "#C9B583"), ("modern", "#DE7445")]:
        v = 100 * (g["style"] == st).sum() / tot
        ax.barh(len(E2) - 1 - i, v, left=left, color=col, edgecolor=INKC, lw=0.4, height=0.66)
        if v > 7: ax.text(left + v / 2, len(E2) - 1 - i, f"{v:.0f}%", ha="center", va="center", fontproperties=FELL, fontsize=10, color="white" if st != "other" else INKC)
        left += v
ax.set_yticks(range(len(E2))); ax.set_yticklabels([e for e in E2][::-1], fontproperties=FELL, fontsize=11)
ax.set_xlim(0, 100); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
fig.text(0.04, 0.94, "Street, Road and Terrace, or Close, Drive and Way?", fontproperties=FELLSC, fontsize=14, color=RED)
fig.text(0.04, 0.9, "The last word of battle streets' names, by war. Purple: Street, Road, Terrace, Place, Grove. Orange: Close, Drive, Way, Court, Gardens.", fontproperties=FELL, fontsize=10.5, color=MUT)
fig.text(0.04, 0.865, "Many world-war names were given decades later, on post-war estates.", fontproperties=FELL, fontsize=10.5, color=MUT)
out(fig, "style")
print("figures done")
