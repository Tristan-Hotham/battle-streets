"""Reddit collage (r/dataisbeautiful style) and the 1200 x 630 header card.
Light parchment background; labels on the sea or paper; full legend; source footer.
Output: reddit/battle_streets_collage.png (3000 x 2100 px) and header.png. Run after code/03_figures.py."""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from figstyle import *
from battles import BKEY

R = jload(f"{DATA}/results.json")
S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False)
S["clock"] = S.clock.astype(str) == "True"
S["dist_km"] = pd.to_numeric(S.dist_km, errors="coerce")
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
STOPS = ["#2D1E6B", "#5B2A86", "#8E3A88", "#BF4F6E", "#DE7445", "#E9A33A", "#D9C23A"]
YC = LinearSegmentedColormap.from_list("yr", STOPS); YN = Normalize(1793, 1945)
OUT = os.path.join(ROOT, "reddit", "battle_streets_collage.png")
f27 = projector(27700)
S["X"], S["Y"] = f27(S.lon.values, S.lat.values)
E = R["era_pct"]; T = R["test"]
NAP, CRI, BOER, WWI = "Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Boer War 1899 to 1902", "First World War"


def ukmap(ax, ext_ll=(-8.0, 1.9, 49.9, 58.8), s=7):
    ext, f = ink_base(ax, 27700, ext_ll, coast_lw=0.5, ripple_m=(6e3, 15e3), countries=False, min_area=2e7)
    c = S[S.flag == ""].sort_values("year")
    ax.scatter(c.X, c.Y, s=s, c=[YC(YN(y)) for y in c.year], edgecolor=INKC, lw=0.15, zorder=5)
    ax.set_xlim(ext[0] + 0.6e5, ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_facecolor("none")
    return ext, f


fig = plt.figure(figsize=(10, 7), dpi=300); parchment(fig, seed=13)
fig.text(0.035, 0.955, "Waterloo Road and the clock in the streets", fontproperties=HAND, fontsize=27, color=RED, va="center")
fig.text(0.035, 0.912, f"{R['n']['clean']:,} UK streets named after battles from 1793 to 1944, coloured by the date of the battle", fontproperties=FELL, fontsize=12, color=INKC, va="center")
fig.text(0.035, 0.885, "Victorian builders named new streets after the latest victory. Do later battles lie farther from the town centre?", fontproperties=FELL, fontsize=10, color=MUT, va="center")
ax = fig.add_axes([0.0, 0.05, 0.45, 0.81])
ext, f = ukmap(ax)
cb = fig.add_axes([0.355, 0.5, 0.012, 0.28])
cb.imshow(np.linspace(1945, 1793, 200)[:, None], aspect="auto", cmap=YC, norm=YN, extent=[0, 1, 1793, 1945])
cb.set_xticks([]); cb.yaxis.tick_right(); cb.set_yticks([1805, 1815, 1855, 1900, 1916, 1944])
cb.set_yticklabels(["Trafalgar 1805", "Waterloo 1815", "Alma 1854", "Mafeking 1900", "Somme 1916", "Arnhem 1944"], fontproperties=FELL, fontsize=7.5)
for s_ in cb.spines.values(): s_.set_linewidth(0.4)
fig.text(0.33, 0.795, "Date of the battle", fontproperties=FELLSC, fontsize=9, color=RED)

# ---- bursts
bx = fig.add_axes([0.5, 0.58, 0.46, 0.24])
cnt = S[S.flag == ""].groupby("battle").size()
for k, n in cnt.items():
    y = BKEY[k][3][0] + (BKEY[k][3][1] - 1) / 12
    bx.bar(y, n, width=1.2, color=YC(YN(y)), edgecolor=INKC, lw=0.3)
for k, ha, dx_ in [("waterloo", "left", 1.2), ("trafalgar", "right", -1.2), ("alma", "center", 0), ("ladysmith", "center", 0), ("jutland", "center", 0), ("arnhem", "center", 0)]:
    y = BKEY[k][3][0] + (BKEY[k][3][1] - 1) / 12
    bx.text(y + dx_, cnt[k] + (8 if ha == "center" else -30), f"{BKEY[k][1]} {cnt[k]}", ha=ha, fontproperties=FELL, fontsize=8, color=INKC)
bx.set_xlim(1790, 1950); bx.set_ylim(0, cnt.max() * 1.18)
for s_ in ("top", "right", "left"): bx.spines[s_].set_visible(False)
bx.set_yticks([]); bx.tick_params(labelsize=8)
for l in bx.get_xticklabels(): l.set_fontproperties(FELL)
fig.text(0.5, 0.855, "Every war leaves a layer of names", fontproperties=FELLSC, fontsize=12, color=RED)
fig.text(0.5, 0.833, f"Streets per battle. The two-year Crimean War gave {R['crimea_vs_before']['crimea']}, both world wars together {R['world_wars']['n']}.", fontproperties=FELL, fontsize=8.8, color=MUT)

# ---- the clock
fig.text(0.5, 0.49, "The clock: later battles, farther out", fontproperties=FELLSC, fontsize=12, color=RED)
fig.text(0.5, 0.468, f"Typical distance of each war's streets from their town centre. In {T['positive']} of {T['towns']} towns", fontproperties=FELL, fontsize=8.8, color=MUT)
fig.text(0.5, 0.449, f"later battles lie farther out (none of {T['reps']:,} random shuffles matched it).", fontproperties=FELL, fontsize=8.8, color=MUT)
cx = fig.add_axes([0.5, 0.17, 0.25, 0.25])
eras = [NAP, CRI, BOER, WWI]
labs = ["French wars\n1793 to 1815", "Crimea\n1854 to 1856", "Boer War\n1899 to 1902", "First\nWorld War"]
yrs = [1805, 1855, 1900, 1916]
for i, (e, y) in enumerate(zip(eras, yrs)):
    cx.barh(3 - i, E[e]["median_km"], color=YC(YN(y)), edgecolor=INKC, lw=0.4, height=0.62)
    cx.text(E[e]["median_km"] + 0.08, 3 - i, f"{E[e]['median_km']:.1f} km", va="center", fontproperties=FELL, fontsize=9, color=INKC)
cx.set_yticks(range(4)); cx.set_yticklabels(labs[::-1], fontproperties=FELL, fontsize=8)
cx.set_xlim(0, 3.8); cx.set_xticks([])
for s_ in ("top", "right", "bottom"): cx.spines[s_].set_visible(False)
# ---- Bristol rings
rx = fig.add_axes([0.78, 0.17, 0.19, 0.25])
g = S[S.clock & (S["style"] == "traditional") & (S.town == "Bristol")]
TC = settlements(20000).set_index("name")
x0, y0 = f27(TC.lon["Bristol"], TC.lat["Bristol"])
dx, dy = (g.X - x0) / 1000, (g.Y - y0) / 1000
for e, y in zip(eras, yrs):
    m = g[g.era == e].dist_km.median()
    rx.add_patch(plt.Circle((0, 0), m, fill=False, ec=YC(YN(y)), lw=1.6))
rx.scatter(dx, dy, s=14, c=[YC(YN(y)) for y in g.year], edgecolor=INKC, lw=0.3, zorder=5)
rx.plot(0, 0, "+", color=RED, ms=7, mew=1.5)
Rr = float(np.hypot(dx, dy).max()) * 1.05
rx.set_xlim(-Rr, Rr); rx.set_ylim(-Rr, Rr); rx.set_aspect("equal"); rx.axis("off")
rx.text(0, -Rr * 1.04, f"Bristol: rings at each war's median (+ centre)", ha="center", va="top", fontproperties=FELLIT, fontsize=8.5, color=INKC)
fig.text(0.5, 0.125, f"But it is a slow clock: it tells the French wars from the Boer War ({R['pairs']['nap_boer']['inside']} of {R['pairs']['nap_boer']['towns']} towns in order),", fontproperties=FELL, fontsize=8.8, color=INKC)
fig.text(0.5, 0.105, f"not Waterloo from the Alma ({R['pairs']['nap_crimea']['inside']} of {R['pairs']['nap_crimea']['towns']}). And {R['world_wars']['modern_pc']:.0f}% of world-war battle streets are", fontproperties=FELL, fontsize=8.8, color=INKC)
fig.text(0.5, 0.085, "Closes and Drives, many probably named later on new estates.", fontproperties=FELL, fontsize=8.8, color=INKC)
fig.text(0.035, 0.034, f"Data: OpenStreetMap contributors (ODbL), via QLever; Wikidata (CC0). Set aside: {R['n']['old']:,} streets after battles before 1793 (Blenheim, Naseby) and {R['n']['ambiguous']} with ambiguous", fontproperties=FELL, fontsize=7.2, color=MUT)
fig.text(0.035, 0.016, "names (Nile, Quebec, Kimberley). Clock test: Street, Road, Terrace and similar names, towns of 20,000 or more, within-town rank correlation.", fontproperties=FELL, fontsize=7.2, color=MUT)
fig.text(0.965, 0.018, "maps.tristanhotham.com/battle-streets", fontproperties=FELL, fontsize=8, color=RED, ha="right")
fig.savefig(OUT, dpi=300, facecolor=fig.get_facecolor())
plt.close(fig)

# ---- header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100); parchment(fig, seed=5)
ax = fig.add_axes([0.56, 0.0, 0.44, 1.0])
ukmap(ax, ext_ll=(-6.6, 1.9, 50.0, 58.7), s=9)
fig.text(0.05, 0.78, "Waterloo Road", fontproperties=HAND, fontsize=50, color=INKC)
fig.text(0.05, 0.64, "and the clock", fontproperties=HAND, fontsize=44, color=RED)
fig.text(0.05, 0.53, "in the streets", fontproperties=HAND, fontsize=44, color=RED)
fig.text(0.05, 0.40, f"{R['n']['clean']:,} UK streets named after battles,", fontproperties=FELL, fontsize=21, color=INKC)
fig.text(0.05, 0.34, "coloured by the date of the battle", fontproperties=FELL, fontsize=21, color=INKC)
fig.text(0.05, 0.22, f"{R['top_clock'][0]['n']} Waterloos, {R['top_clock'][1]['n']} Almas, {R['top_clock'][2]['n']} Trafalgars.", fontproperties=FELLIT, fontsize=19, color=RED)
fig.text(0.05, 0.08, "Dr Tristan Hotham · maps.tristanhotham.com/battle-streets", fontproperties=FELL, fontsize=13, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=fig.get_facecolor())
from PIL import Image
im = Image.open(os.path.join(ROOT, "header.png")); assert im.size == (1200, 630), im.size
print("collage", Image.open(OUT).size)
