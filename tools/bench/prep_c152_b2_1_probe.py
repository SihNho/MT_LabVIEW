# ---
# labview: none
# hardware: none
# ---
r"""prep_c152_b2_1_probe - card 152-b2-1 (re-issue of 152-a2-2): the discriminator RE-RUN. COPY of prep_c152_a2_2_probe.py (c8ccd0c2) with ONLY the card
id (task_152-b2-1.json inputs, line 24 + docstring + the bgrun line); everything else unchanged. --- original docstring follows ---
prep_c152_a2_2_probe - card 152-a2-2 brief step 2 (PD368(d) DISCRIMINATOR, OFFLINE, read-only). COPY of prep_c151_a3_2_probe.py (6cc4085f) with ONLY:
card id 152-a2-2 (input md5 list from task_152-a2-2.json), the REAL graph = the DERIVED file graph_ring_p4s08_20261009_033522_fsowner.json (e26b4d90, card
152-a1-1) beside the original 44858dbf, and the DISCRIMINATOR added (gate D): (i) the MEASURED diagram of FS #29721 = the owner read
diag_c152_a1_1_owner.log:25 (parsed) == the derived file's fs_owner_read['29721'] (+ its cite); (ii) the diagram the v18 plan's own create action for
that FS targeted, after rebind: the creation map entry whose real uid is 29721 (kind obj) -> its action ids -> the v18 action's `diagram` field ->
(symbolic? resolved through END sym + creation map; numeric = a base uid) -> the same action in the session plan that created it (after that
session's rebase) -> the creation map's owner_real; every hop printed. Writes nothing.
PREDICTION CONTRACT: inputs == card md5; D measured #23166 == v18 create target after rebind (equal => s09 is made; else RETURN with both values).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c152_b2_1_probe.log -- py -u tools/bench/prep_c152_b2_1_probe.py"""
import glob, hashlib, json, os, re, sys                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX                                                       # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
FS = 29721
card = J(os.path.join(B, "cards", "task_152-b2-1.json"))
bad = [(i["path"], md5(os.path.join(ROOT, i["path"])), i["md5"]) for i in card["inputs"] if md5(os.path.join(ROOT, i["path"])) != i["md5"]]
print("INPUTS bad", bad, flush=True)
P = J(os.path.join(B, "plan_ring_p4_s08v18.json"))
f = P["finalized"]
END8F = os.path.join(ROOT, f["step_files"][-1]["path"])
E = J(END8F)
print("END8", os.path.relpath(END8F, ROOT), md5(END8F), "fs_unmeasured", E["state"].get("fs_unmeasured"), "owners 29721", (E["state"].get("owners") or {}).get(str(FS)), flush=True)
print("S09 existing", sorted(glob.glob(os.path.join(B, "*s09*")) + glob.glob(os.path.join(ROOT, "tools", "recipes", "*s09*")) + glob.glob(os.path.join(B, "sim", "*s09*"))), flush=True)
v18 = J(os.path.join(B, "plan_ring_p4_v18.json"))
A, OPS = v18["actions"], SX.compile_plan(v18)
print("V18 ops", len(OPS), "actions", len(A), flush=True)
for k in range(185, len(OPS) + 1):
    o = OPS[k - 1]
    for n in o["acts"]:
        a = A[n - 1]
        refs = dict((x, a.get(x)) for x in ("dest_diagram", "loop", "body", "parent", "uid", "diagram", "at", "src", "dst", "born_on", "on", "of", "as") if a.get(x) is not None)
        print("V18OP {0} kind {1} act #{2} {3} op {4} refs {5}".format(k, o["kind"], n, a["id"], a.get("op"), json.dumps(refs)[:500]), flush=True)
# ---- (i) the MEASURED diagram
OWNLOG = os.path.join(B, "diag_c152_a1_1_owner.log")
ln25 = open(OWNLOG, encoding="utf-8", errors="replace").read().splitlines()[24]
mm = re.search(r"uid (\d+) -> owner '(\w+)' uid (\d+) \| self '(\w+)'#(\d+)", ln25)
meas = (mm.group(2), int(mm.group(3))) if mm and int(mm.group(1)) == FS else None
print("HOP i.1 {0}:25 md5 {1}: {2!r} -> owner {3}, echo {4}".format(os.path.relpath(OWNLOG, ROOT), md5(OWNLOG), ln25.strip(), meas,
      mm and (mm.group(4), int(mm.group(5)))), flush=True)
DER = os.path.join(B, "graph_ring_p4s08_20261009_033522_fsowner.json")
GD = J(DER)
fr = (GD.get("fs_owner_read") or {}).get(str(FS))
print("HOP i.2 derived {0} md5 {1}: fs_owner_read[{2}] = {3}; cite {4}".format(os.path.basename(DER), md5(DER), FS, fr, json.dumps(GD.get("fs_owner_read_cite"))[:600]), flush=True)
sd = SS.base_state(GD, P.get("context") or {})
try:
    ch = SS._diag_chain(sd, 29869, {})
except Exception as ex:                                                                       # noqa: BLE001
    ch = "RAISED {0}".format(ex)
print("HOP i.3 stagesim.base_state(derived): owners[{0}] {1}; fs_unmeasured {2}; _diag_chain(29869) {3}".format(FS, sd["owners"].get(str(FS)), sd.get("fs_unmeasured"), ch), flush=True)
# ---- (ii) the v18 create target after rebind
hits = []
for cm in sorted(glob.glob(os.path.join(B, "creation_map", "plan_ring_p4_*.jsonl"))):
    for k, ln in enumerate(open(cm, encoding="utf-8").read().splitlines(), 1):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get("rec") == "bind" and r.get("kind") == "obj" and r.get("real") == FS:
            hits.append((os.path.relpath(cm, ROOT).replace("\\", "/"), k, r))
for h in hits:
    print("HOP ii.1 creation map {0}:{1} real #{2} <- sim #{3} ids {4} op {5}; owner {6} owner_real {7}".format(h[0], h[1], FS, h[2]["sim"], h[2]["ids"], h[2]["op"], h[2]["owner"], h[2]["owner_real"]), flush=True)
cur = [h for h in hits if "f349c39a" in h[0]]                                              # the map of the plan the s05 maker used (prep_c151_a3_2_mk.py:46,62)
aid = cur[0][2]["ids"][0] if len(cur) == 1 and len(cur[0][2]["ids"]) == 1 else None
va = next((a for a in A if a.get("id") == aid), None)
print("HOP ii.2 v18 action {0} (#{1}): op {2} class {3} diagram {4!r} as {5}".format(aid, A.index(va) + 1 if va else None, va and va.get("op"), va and va.get("class"),
      va and va.get("diagram"), va and va.get("as")), flush=True)
s04 = J(os.path.join(B, "plan_ring_p4_s04v18.json"))
sa = next((a for a in s04["actions"] if a.get("id") == aid), None)
print("HOP ii.3 s04 plan (md5 {0}, rebased {1}) action {2}: diagram {3!r} class {4}".format(md5(os.path.join(B, "plan_ring_p4_s04v18.json")),
      bool((s04.get("finalized") or {}).get("rebase")), aid, sa and sa.get("diagram"), sa and sa.get("class")), flush=True)
tgt_v18 = va and va.get("diagram")
sym = isinstance(tgt_v18, str)
print("HOP ii.4 v18 target {0!r} is {1}".format(tgt_v18, "SYMBOLIC (needs END sym + creation map)" if sym else "a numeric BASE uid (no creation-map / rebase hop)"), flush=True)
G8 = J(os.path.join(B, "graph_ring_p4s08_20261009_033522.json"))
o23 = [o for o in G8.get("objs") or [] if o.get("uid") == tgt_v18]
print("HOP ii.5 graph 44858dbf objs #{0}: {1}; owners[{0}] {2}".format(tgt_v18, o23[:2], (G8.get("owners") or {}).get(str(tgt_v18))), flush=True)
after = None if sym else (sa.get("diagram") if sa else None)
okD = (meas is not None and meas[0] == "Diagram" and fr == ["Diagram", meas[1]] and not sym and isinstance(tgt_v18, int) and after == tgt_v18
       and len(cur) == 1 and cur[0][2]["owner_real"] == tgt_v18 and meas[1] == tgt_v18)
print("GATE {0} | D measured diagram of FS #{1} = {2} (owner log :25, derived fs_owner_read {3}) vs v18 create target after rebind = {4} (v18 {5!r}, s04 plan {6!r}, "
      "creation map owner_real {7}) | equal {8}".format("PASS" if okD else "FAIL", FS, meas, fr, after, tgt_v18, sa and sa.get("diagram"),
                                                         cur and cur[0][2]["owner_real"], okD), flush=True)
print(protocol.result_line(protocol.make_result(int(not bad) + int(okD), int(bool(bad)) + int(not okD), ("inputs" if bad else ("D" if not okD else None)), [])), flush=True)
sys.exit(0 if (okD and not bad) else 1)
