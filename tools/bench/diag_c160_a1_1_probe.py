# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-a1-1.md
# ---
r"""diag_c160_a1_1_probe - card 160-a1-1, OFFLINE read of the saved 94ffff94 graph before the edit: w10394's object row, its terminal
rows, termless Wire objects, a Wire with terminals, a non-Wire object; and keeps the PRE-EDIT bytes of stagesim/stagexec as .txt copies
(selftest_c160_delwire_<name>_<md5>.txt) for the self-test's T4 comparison (same precedent as selftest_c159_cen2_ends_stagekit_9cd8822e.txt).
PREDICTION: w10394 is one Wire obj with 0 terminal rows; copies written with md5 eb99c6ba / 7a712ccb."""
import hashlib, json, os, shutil, sys  # noqa: E401
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()   # noqa: E731
g = json.load(open(os.path.join(HERE, "graph_ring_p5s02a_20261010_032547.json"), encoding="utf-8"))
print("keys", sorted(g))
print("obj 10394", [o for o in g["objs"] if int(o["uid"]) == 10394])
print("rows 10394", sum(1 for r in g["terminals"] if r["wire_uid"] == 10394))
W = [int(o["uid"]) for o in g["objs"] if o["class"] == "Wire"]
tw = Counter(r["wire_uid"] for r in g["terminals"] if r["wire_uid"])
print("Wire objs", len(W), "termless", [w for w in W if w not in tw])
print("wires with rows, first 5 (uid, n)", [(w, tw[w]) for w in W if w in tw][:5])
print("row0", g["terminals"][0])
print("obj0", g["objs"][0])
owners = set(r["owner_uid"] for r in g["terminals"])
print("non-Wire objs with rows, first 3", [o for o in g["objs"] if o["class"] != "Wire" and int(o["uid"]) in owners][:3])
print("classes", Counter(o["class"] for o in g["objs"]).most_common(12))
ok = 0
for name, want in (("stagesim", "eb99c6ba"), ("stagexec", "7a712ccb")):
    src = os.path.join(ROOT, "tools", name + ".py")
    dst = os.path.join(HERE, "selftest_c160_delwire_{0}_{1}.txt".format(name, want))
    if md5(src)[:8] == want:
        shutil.copy(src, dst)
        ok += md5(dst)[:8] == want
    print("copy", name, md5(src)[:8], "->", dst, os.path.exists(dst))
n10394 = [o for o in g["objs"] if int(o["uid"]) == 10394]
p = ok + (len(n10394) == 1 and n10394[0]["class"] == "Wire" and tw[10394] == 0)
print(protocol.result_line(protocol.make_result(p, 3 - p, None if p == 3 else "probe", [])), flush=True)
