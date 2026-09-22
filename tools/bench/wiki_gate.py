r"""wiki_gate - the plan step-3 PASS criteria for `tools/wiki_build.py`, run against the built wiki.

PREDICTION CONTRACT (docs/connectivity-map-plan.md step 3, "pass criterion" column)
  G1 all 94 `background VIs` copies + the main VI (its S1 copy) are present in `docs/wiki/index.json`,
     each with a JSON file on disk.
  G2 a re-run with NOTHING changed reads 0 files (every line is "skipped, unchanged").
  G3 a TOUCHED md5 re-reads EXACTLY 1. The touch is on the INDEX entry (the copies are byte-pinned to
     the originals and are not written to).
  G4 the index md5s equal the files' real md5s, and every copy is still byte-identical to its ORIGINAL.
Read-only apart from `docs/wiki/index.json`, which the run restores.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import gscript as g                                                                # noqa: E402

INDEX = os.path.join(ROOT, "docs", "wiki", "index.json")
WIKI = os.path.join(ROOT, "docs", "wiki", "subvi")
BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
P, F = [0], [0]


def gate(label, ok, detail=""):
    (P if ok else F)[0] += 1
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run():
    r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "wiki_build.py")],
                       capture_output=True, text=True, cwd=ROOT, timeout=1800)
    return r.stdout + r.stderr


doc = json.load(open(INDEX, encoding="utf-8"))
vis = doc["vis"]
copies = []
for dp, _d, fs in os.walk(BG):
    for f in fs:
        if f.lower().endswith(".vi"):
            copies.append(os.path.join(dp, f))
fact("index holds {0} VIs; copy folder holds {1} .vi files".format(len(vis), len(copies)))
missing = [p for p in copies
           if not any(v["file"] == p for v in vis.values())]
gate("G1a every background copy is in the index", not missing, str(missing[:4]))
gate("G1b the main VI's S1 copy is in the index", "D1_s1_copy" in vis,
     str(vis.get("D1_s1_copy", {}).get("terminals")))
no_json = [k for k in vis if not os.path.exists(os.path.join(WIKI, k + ".json"))]
gate("G1c every index entry has its JSON on disk", not no_json, str(no_json[:4]))

bad = [k for k, v in vis.items() if os.path.exists(v["file"]) and md5(v["file"]) != v["md5"]]
gate("G4a index md5 == the file's real md5", not bad, str(bad[:4]))
drift = []
for p in copies:
    o = os.path.join(ORIG, os.path.relpath(p, BG))
    if os.path.exists(o) and md5(o) != md5(p):
        drift.append(os.path.basename(p))
gate("G4b every copy is byte-identical to its ORIGINAL", not drift, str(drift[:4]))

out = run()
n_read = out.count("]  ") - out.count("UNREAD")
skip = out.count("  SKIP  ")
tail = [l for l in out.splitlines() if l.startswith("=== WIKI") or "to read:" in l]
fact("re-run (nothing changed): {0}".format(" | ".join(tail)))
gate("G2 a re-run with nothing changed reads 0 files", "to read: 0" in out and skip == len(vis),
     "skipped {0} of {1}".format(skip, len(vis)))

victim = sorted(vis)[len(vis) // 2]
saved = vis[victim]["md5"]
vis[victim]["md5"] = "0" * 32
json.dump(doc, open(INDEX, "w", encoding="utf-8"), indent=1)
out2 = run()
tail2 = [l for l in out2.splitlines() if "to read:" in l or l.startswith("=== WIKI")]
fact("after touching {0!r}: {1}".format(victim, " | ".join(tail2)))
gate("G3 a touched md5 re-reads EXACTLY 1", "to read: 1;" in out2 and "1 written" in out2,
     "victim {0!r}".format(victim))
doc = json.load(open(INDEX, encoding="utf-8"))
gate("G3b the touched entry's md5 is back to the file's own",
     doc["vis"][victim]["md5"] == saved, doc["vis"][victim]["md5"][:8])

print("\n=== GATES: {0} pass / {1} fail".format(P[0], F[0]), flush=True)
sys.exit(1 if F[0] else 0)
