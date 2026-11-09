"""Step 5: index.html from code/page_template.html, filled from data/results.json, with the facts stated in words checked.
10.5281/zenodo.24086515, https://doi.org/10.5281/zenodo.24086515 and https://blog.tristanhotham.com/2026/10/31/battle-streets/ stay as placeholders for the publisher."""
import time
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False)
# facts stated in words
assert [x["battle"] for x in R["top_clock"][:3]] == ["Waterloo", "Alma", "Trafalgar"]
assert R["crimea_vs_before"]["crimea"] > R["world_wars"]["n"]
assert R["test"]["perm_count"] == 0 and R["test"]["positive"] > 2 * R["test"]["negative"]
assert R["era_pct"]["Napoleonic 1793 to 1815"]["mean"] < R["era_pct"]["Crimea 1854 to 1856"]["mean"] < R["era_pct"]["Boer War 1899 to 1902"]["mean"]
assert R["era_pct"]["Napoleonic 1793 to 1815"]["median_km"] < R["era_pct"]["Crimea 1854 to 1856"]["median_km"] < R["era_pct"]["Boer War 1899 to 1902"]["median_km"]
assert 0.45 < R["pairs"]["nap_crimea"]["inside"] / R["pairs"]["nap_crimea"]["towns"] < 0.56                  # "close to a coin toss"
assert R["pairs"]["nap_boer"]["inside"] / R["pairs"]["nap_boer"]["towns"] > 0.7
assert R["victorian"]["modern_pc"] < 15 and R["world_wars"]["modern_pc"] > 35
assert R["tc"]["Glasgow"] > 0.5 and R["tc"]["Kingston upon Hull"] > 0.5 and R["tc"]["Preston"] < 0 and R["tc"]["Lincoln"] < 0 and R["tc"]["London"] < 0.2
assert ((S.battle == "jutland") & (S.town == "Bristol")).any()
assert [c["county"] for c in R["counties"][:3]] == ["Greater London", "Greater Manchester", "West Yorkshire"]
assert {"Hampshire", "Devon"} <= set(R["trafalgar_top_counties"])
eng = S[(S.flag == "") & (S.nation == "England")]
tops = eng.groupby("county").battle.agg(lambda s: s.value_counts().index[0]).value_counts()
assert tops.index[0] == "alma" and tops.iloc[0] > tops.iloc[1], tops.head()
pl = {(b, c) for b, p, c, n in R["place_examples"]}
assert ("waterloo", "Greater London") in pl and ("waterloo", "Merseyside") in pl and ("inkerman", "Durham") in pl and ("camperdown", "Dundee City") in pl
assert R["by_era"]["1816 to 1853"]["clean"] < 30
CH = "".join(f'<button class="chip" data-t="{t}" aria-pressed="false">{t.replace("Kingston upon Hull", "Hull")}</button>' for t in ["Bristol", "Glasgow", "Kingston upon Hull", "Cheltenham", "Leeds", "London"])
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
css = open(os.path.join(ROOT, "code", "page.css"), encoding="utf-8").read()
fs = open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", css).replace("{{CHIPS}}", CH).replace("{{FULLSCREEN}}", fs)
t = t.replace("{{BYLINE}}", BYLINE).replace("{{AI}}", AI).replace("{{VERSION}}", time.strftime("%Y%m%d")).replace("{{REPO}}", REPO)
t = fill(t, R)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= {"DOI", "DOI_URL", "BLOG_URL"}, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
js = open(os.path.join(ROOT, "js", "page.js"), encoding="utf-8").read()
assert "—" not in js and "–" not in js
print("index.html", len(t) // 1024, "KB")
