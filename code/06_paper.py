"""Step 6: the paper. Fills code/paper_template.tex from data/results.json, adds the word table, compiles with xelatex.
Output: release/paper/Hotham_Battle_Streets.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder (https://doi.org/10.5281/zenodo.24086515 printed) unless DOI is set: DOI=10.5281/zenodo.N python3 code/06_paper.py"""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Battle_Streets"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "f5": return f"{float(v):.5f}"
    return tex(str(v))


import pandas as pd
BT = pd.read_csv(f"{DATA}/battles.csv", keep_default_na=False)
BT = BT[BT.streets > 0]
ST = {"clock": "", "before 1793": "old", "ambiguous": "amb."}
rows = "".join(f"{tex(r.battle)} & {r.date} & {tex(r.war)} & {ST[r.status]} & {r.streets}\\\\\n" for r in BT.itertuples())
TW = ("\\begin{small}\\begin{longtable}{llp{5.2cm}lr}\\caption{The battles found in street names: date used, war, status (old: before 1793, set aside; "
      "amb.: ambiguous name, set aside) and number of streets.}\\label{tab:battles}\\\\\\toprule Battle & Date & War & Status & Streets\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{small}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{TABLE_BATTLES}}", TW)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24086515", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
