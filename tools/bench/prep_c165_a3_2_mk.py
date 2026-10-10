# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-2.md
# ---
r"""prep_c165_a3_2_mk - card 165-3-2 (OFFLINE, json only, never launched): re-make plan_ring_p5s02e.json (K3f K4 K4f) on graph 2a5fa0c4 with the
PRIME-fixed stagexec 1d5309f4, by RE-RUNNING the step-5 maker tools/bench/prep_c165_a2_1_mk.py (brief step 3), not by copying it.
WHAT EXISTED FIRST: prep_c165_a2_1_mk.py (the maker; module-level script, no arguments) -> prep_plan_flow_lib.make_step_plan (shared);
stagexec.dry_run (shared; the PRIME pass logs PRIME-SKIP, stagexec.py:2630-2635); selftest_c165_prime.py (its ex_run is inline, not shared).
WHY NOT `py prep_c165_a2_1_mk.py` VERBATIM: its M0/U pins are read from task_165-2-1.json (stagexec 6ea6637f, prep_c165_a2_1_mk.py:28) so M0 is a
certain fatal FAIL on the fixed stagexec 1d5309f4, and its side files are named prep_c165_a2_1_* (165-2-1's record; outside this card's write globs).
So the maker's OWN source is executed with exactly these parameter substitutions (each asserted to occur the stated number of times):
  S1 pin source task_165-2-1.json -> task_165-3-2.json minus this card's two outputs (plan_ring_p5s02e.json / _in.json), + plan_ring_p5s02d 97837e2a
  S2 side files prep_c165_a2_1_{census,session,pd401b}.json -> prep_c165_a3_2_*   S3 pd401b "card" 165-2-1 -> 165-3-2
  S4 the maker's gate object = this script's gate (one RESULT line); its final sys.exit -> return to this script.
  Plan-affecting arguments (card tag "c165-2-1", goal and probe texts, groups, graph, sources, census rows) are NOT changed.
PREDICTION CONTRACT: H every card input == pin, VI 6dcd5c3d, stagexec 1d5309f4 (drift = FAIL, stop before the maker); ASIDE prev 20bde81a kept;
  maker gates all PASS: M0, GRP [(72,73,2),(74,82,9),(83,84,2)], OWN/MAP new:OK3 -> 31803, FRM, ROWS, STUB, C x3 (every delete_wire a checkpoint),
  X10 K3f 642.6 / K3f+K4 657.1 / K3f+K4+K4f 665.0 <= 675 -> 13 rows, SPLIT, PROBE, TIE, S1, SB final True route PASS 0 UNROUTABLE 0 PROVISIONAL,
  C-OUT, IDS, X8, X17, B1, RC, E2, END-STUB x2, END-FACE x2, DWSTEP x2, U; plan_in byte-equal b5b35f8a (FACT only);
  DRY stagexec.dry_run(plan) PASS with exactly 2 PRIME-SKIP lines: #8776 / w10362 / dw_10362 and #24342 / w25232 / dw_25232; POST pins unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c165_a3_2_mk.log -- py -u tools/bench/prep_c165_a3_2_mk.py"""
import os, shutil, sys                                                                        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT, SX = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT, FL.SX
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
CARD = J("tools/bench/cards/task_165-3-2.json")
OUTS = ["tools/bench/plan_ring_p5s02e.json", "tools/bench/plan_ring_p5s02e_in.json"]
VID = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi")
gate = L.Gate(fatal_default=False)
# ---- H: hash first (bytes only)
for i in CARD["inputs"]:
    h = md5(os.path.join(ROOT, i["path"]))
    gate("H {0} md5 {1} == pin {2}".format(i["path"], h[:8], i["md5"][:8]), h == i["md5"], h)
gate("H VI {0} md5 {1} == 6dcd5c3d".format(os.path.basename(VID), md5(VID)), md5(VID).startswith("6dcd5c3d"))
gate("H stagexec 1d5309f4", md5(P("../stagexec.py")).startswith("1d5309f4"), md5(P("../stagexec.py")))
if gate.G["fail"]:
    sys.exit(gate.result())
# ---- ASIDE: copy the old plan first (the maker's keep_prev copies it again, same bytes)
OUT, PIN = P("plan_ring_p5s02e.json"), P("plan_ring_p5s02e_in.json")
prev, pin_before = md5(OUT), md5(PIN)
KEEP = P("plan_ring_p5s02e_prev{0}.json".format(prev[:8]))
shutil.copyfile(OUT, KEEP)
gate("ASIDE0 {0} == old plan {1} (copied before the maker)".format(os.path.basename(KEEP), prev[:8]), md5(KEEP) == prev and prev.startswith("20bde81a"), md5(KEEP))
# ---- the maker, executed from its own file with S1..S4
MK = P("prep_c165_a2_1_mk.py")
src = open(MK, encoding="utf-8").read()
SUBS = [('for i in J("tools/bench/cards/task_165-2-1.json")["inputs"])', 'for i in J("tools/bench/cards/task_165-3-2.json")["inputs"] if i["path"] not in OUTS_)', 1),
        ('P("prep_c164_a3_1_census.json"): "bb30814a"})', 'P("prep_c164_a3_1_census.json"): "bb30814a", P("plan_ring_p5s02d.json"): "97837e2a"})', 1),
        ("prep_c165_a2_1_census.json", "prep_c165_a3_2_census.json", 1), ("prep_c165_a2_1_session.json", "prep_c165_a3_2_session.json", 1),
        ("prep_c165_a2_1_pd401b.json", "prep_c165_a3_2_pd401b.json", 4), ('PRED = {"card": "165-2-1"', 'PRED = {"card": "165-3-2"', 1),
        ("gate = L.Gate()", "gate = GATE_", 1), ("sys.exit(gate.result())", "pass", 1)]
for a, b, n in SUBS:
    gate("SUB {0!r} occurs {1}x in {2} (md5 {3})".format(a[:60], n, os.path.basename(MK), md5(MK)[:8]), src.count(a) == n, src.count(a), fatal=True)
    src = src.replace(a, b)
print("FACT MAKER {0} md5 {1}; executed with {2} substitutions".format(rel(MK), md5(MK), len(SUBS)), flush=True)
G_ = {"__file__": MK, "__name__": "__main__", "GATE_": gate, "OUTS_": OUTS}
exec(compile(src, MK, "exec"), G_)                                                           # fatal gates inside exit with the RESULT line
print("FACT plan_ring_p5s02e_in.json before {0} after {1} (byte-equal {2})".format(pin_before, md5(PIN), pin_before == md5(PIN)), flush=True)
print("FACT plan_ring_p5s02e.json {0} final {1}".format(md5(OUT), J(OUT).get("final")), flush=True)
# ---- DRY: stagexec.dry_run on the new plan -> the PRIME-SKIP lines
lines = []
st, ff, ex = SX.dry_run(OUT, log=lines.append)
for ln in lines:
    if "PRIME" in ln or "UNROUTABLE" in ln:
        print("FACT DRY " + ln.strip()[:400], flush=True)
sk = [(s.get("line") or "") for s in getattr(ex, "prime_skips", [])]
want = [("#8776", "w10362", "dw_10362"), ("#24342", "w25232", "dw_25232")]
gate("DRY stagexec.dry_run(plan_ring_p5s02e.json) {0}; first_fail {1}".format(st, str(ff)[:300]), st == "PASS")
gate("PRIME-SKIP exactly 2 lines naming #8776 w10362 dw_10362 / #24342 w25232 dw_25232", len(sk) == 2 and all(all(x in s for x in w) for s, w in zip(sk, want)), sk)
# ---- POST: inputs other than this card's outputs unchanged
for i in CARD["inputs"]:
    if i["path"] not in OUTS:
        h = md5(os.path.join(ROOT, i["path"]))
        gate("POST {0} {1} UNCHANGED".format(i["path"], h[:8]), h == i["md5"], h)
gate("POST VI 6dcd5c3d UNCHANGED", md5(VID).startswith("6dcd5c3d"))
for p in (OUT, KEEP, P("prep_c165_a3_2_pd401b.json"), P("prep_c165_a3_2_session.json"), P("prep_c165_a3_2_census.json"), PIN):
    if os.path.isfile(p) and rel(p) not in [a["path"] for a in gate.ARTS]:
        gate.ARTS.append({"path": rel(p), "md5": md5(p)})
sys.exit(gate.result())
