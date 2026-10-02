r"""selftest_c135_2_device - card 135-2 pass 4: the acceptance tests written in docs/violation-decisions.md (2026-10-02 12:2x) for
the device stagesim.completeness_gate + stagesim.WriteGuard (finalize: diag_c134_1_finalize_b.py FC + guard; rebase:
stage_prerun.rebase). OFFLINE; the finalize run is a subprocess on a TEMP bench (--bench), never on tools/bench.
PREDICTION: D1 pre-134-4 base (frame owners ['FlatSequenceFrame', 0], no FS owner, no fs_unmeasured: base_state without the
PD289(f) block) on 102553 FAILS before step 1 naming FS 27509's frames 27641 32464 27722; D2 current base_state on 102553 PASSES with
uses = plan b's actions, UNMEASURED [2499, 14682, 43914]; D3 uses naming frame 14037 of UNMEASURED FS 14682 -> FAIL used;
D4 a graph without fs_measured -> N/A; D5 the 135-1 failed finalize replayed on a temp bench (plan b 1451ba90 from 0b72718d, graph
123012) ends rc 1 on F3 and leaves plan b / _in / _pred / provisional copy and the sim step dir byte-identical; D6 WriteGuard
round trip (changed, removed, added file) restores. 6/0.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_c135_2_device.log -- py -u tools/bench/selftest_c135_2_device.py"""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile                  # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS                                               # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
J = lambda n: json.load(open(os.path.join(B, n), encoding="utf-8"))                # noqa: E731
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("  {0}  {1}  {2}".format("PASS" if c else "FAIL", n, json.dumps(d, default=str)[:700]), flush=True)


G = J("graph_ring_p3b2a_fs_20261002_102553.json")
acts = J("plan_ring_p3b2b.json")["actions"]
old = SS.base_state(G)
m = SS.fs_measured_state(G)
for f in m["frame_owner"]:
    old["owners"][str(f)] = [SS.FS_FRAME_CLS, 0]
for fs in m["fs_parent"]:
    old["owners"].pop(str(fs), None)
old.pop("fs_unmeasured", None)
r1 = SS.completeness_gate(G, uses={"actions": acts}, st=old)
gate("D1 pre-134-4 base FAILS naming FS 27509's frames", r1["status"] == "FAIL" and all(str(f) in r1["bad_owner"] for f in (27641, 32464, 27722)),
     {"bad_owner_n": len(r1["bad_owner"]), "27509": [r1["bad_owner"].get(str(f)) for f in (27641, 32464, 27722)]})
r2 = SS.completeness_gate(G, uses={"actions": acts})
gate("D2 current base PASSES, UNMEASURED [2499, 14682, 43914]", r2["status"] == "PASS" and r2["unmeasured"] == [2499, 14682, 43914],
     dict((k, r2[k]) for k in ("status", "fs", "frames", "unmeasured", "bad_owner", "stuck", "inferred", "used")))
r3 = SS.completeness_gate(G, uses={"actions": acts, "probe": [14037]})
gate("D3 a use of frame 14037 (UNMEASURED FS 14682) FAILS", r3["status"] == "FAIL" and "14682" in r3["used"], r3["used"])
g4 = copy.deepcopy(G)
g4.pop("fs_measured")
gate("D4 graph without fs_measured -> N/A", SS.completeness_gate(g4)["status"] == "N/A")
tmp = os.path.join(B, "selftest_c135_2_device_tmp")   # same drive as ROOT: finalize's rel() needs it (C: temp -> ValueError)
shutil.rmtree(tmp, ignore_errors=True)
os.makedirs(tmp)
pb = subprocess.run(["git", "cat-file", "--filters", "0b72718d:tools/bench/plan_ring_p3b2b.json"], cwd=ROOT, capture_output=True, check=True).stdout
open(os.path.join(tmp, "plan_ring_p3b2b.json"), "wb").write(pb)
for n in ("plan_ring_p3b2.json", "plan_ring_p3b2b_in.json", "plan_ring_p3b2b_in_provisional_c134_1.json", "plan_ring_p3b2b_pred.json",
          "census_samples.json", "errorlist_expected_D1_ring_p3b1_20261002_060910.json"):
    shutil.copyfile(os.path.join(B, n), os.path.join(tmp, n))
shutil.copytree(os.path.join(B, "sim", "ring_p3b2b"), os.path.join(tmp, "sim", "ring_p3b2b"))
snap = SS.WriteGuard(files=[os.path.join(tmp, n) for n in os.listdir(tmp) if n.endswith(".json")], dirs=(os.path.join(tmp, "sim", "ring_p3b2b"),))
real = SS.WriteGuard(files=[os.path.join(B, n) for n in ("plan_ring_p3b2b.json", "plan_ring_p3b2b_in.json", "plan_ring_p3b2b_pred.json")],
                     dirs=(os.path.join(B, "sim", "ring_p3b2b"),))
p = subprocess.run([sys.executable, "-u", os.path.join(B, "diag_c134_1_finalize_b.py"), os.path.join(B, "graph_ring_p3b2a_fs_20261002_123012.json"),
                    "--bench", tmp], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
lines = [ln for ln in p.stdout.splitlines() if ln.startswith(("PASS", "FAIL", "  FACT  WRITE")) or ln.startswith("RESULT")]
print("    " + "\n    ".join(ln[:220] for ln in lines), flush=True)
gate("D5 failed finalize (F3, md5 1451ba90 base {0}) -> rc 1, temp bench bytes unchanged, real bench untouched".format(hashlib.md5(pb).hexdigest()[:8]),
     p.returncode == 1 and any(ln.startswith("FAIL  F3") for ln in lines) and snap.unchanged() and real.unchanged(),
     {"rc": p.returncode, "tmp_unchanged": snap.unchanged(), "real_unchanged": real.unchanged(), "stderr": p.stderr[-300:]})
d6 = os.path.join(tmp, "d6")
os.makedirs(d6)
open(os.path.join(d6, "a.json"), "w").write("1")
open(os.path.join(d6, "b.json"), "w").write("2")
w = SS.WriteGuard(files=(os.path.join(tmp, "nofile.json"),), dirs=(d6,))
open(os.path.join(d6, "a.json"), "w").write("X")
os.remove(os.path.join(d6, "b.json"))
open(os.path.join(d6, "c.json"), "w").write("3")
open(os.path.join(tmp, "nofile.json"), "w").write("4")
gate("D6 WriteGuard restores changed/removed/added files", not w.unchanged() and w.restore() and sorted(os.listdir(d6)) == ["a.json", "b.json"]
     and not os.path.exists(os.path.join(tmp, "nofile.json")))
shutil.rmtree(tmp, ignore_errors=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
