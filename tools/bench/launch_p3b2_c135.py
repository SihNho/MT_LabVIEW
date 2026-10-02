r"""launch_p3b2_c135 - card 134-P1 (PD290(d)): the ONE chained launch runner of RING P3b-2 for cycle 135 (WRITTEN, NOT LAUNCHED).
CHAIN (live, `--launch`): L0 pins + bed md5 + no LabVIEW + stage_prerun.check_launch of BOTH recipes -> A session a from the BED
(child launch_p3b2_c135_a.py = recipe a unchanged, saves claudeDev\D1_ring_p3b2a_<ts>.vi) -> LabVIEW gone -> G FS graph read of
that file (child launch_p3b2_c135_graph.py = diag_c134_1_graph.py unchanged + 4 literals) -> LabVIEW gone -> C compare with
graph_ring_p3b2a_fs_20261002_102553.json (node classes = (uid, class) of every obj; terminal rows; wires = wire uid -> its term uids;
fs_measured fs_frames + borders; PD290(b)) -> EQUAL: plan b ae6b6111 as is, check_launch(recipe b) again | DIFFERENT: snapshot plan b
/ in / pred, memory_model load_by_vi[a md5] from G's 'MEM after load' FACT, plan b bytes restored to 1451ba90 from commit 0b72718d
(the pin of the unchanged finalize script, as diag_c134_4_restore_b.py did), diag_c134_1_finalize_b.py <new graph>, stage_prerun
--dry + --prerun recipe b, check_launch -> B session b on the a-file (child launch_p3b2_c135_b.py = recipe b unchanged, saves
D1_ring_p3b2b_<ts>.vi) -> LabVIEW gone -> E FULL Error List read (child launch_p3b2_c135_el.py) -> total in 49..52 and every class
in lo..hi of errorlist_expect_p3b2ab.json -> LabVIEW gone. The FIRST failing gate stops the chain (no later LabVIEW child), LabVIEW
is killed and verified gone, RESULT FAIL. The bed is read-only throughout (md5 checked before, after every child, at the end).
Every child runs under a NESTED tools/bgrun.py (its own deadline + END line; stage runs of child commands are not counted by
record_started, so the runner gates each recipe with stage_prerun.check_launch on the recipe's own command - dry rule 2 + prerun
records of its current sha/plan, decision 4, retry cap, scratch rule - before its child starts).
WHAT EXISTED (reused, nothing rewritten): stage_d1_ring_p3b2{a,b}_scratch.py (Stage + R.body wrapper), diag_c134_1_graph.py,
diag_c134_1_finalize_b.py, diag_c134_4_restore_b.py (git cat-file --filters), stage_d1_ring_p3b1_el.py (EC.main + max_steps 180),
stage_prerun.check_launch/--dry/--prerun, stagexec.kill_labview_at_exit's taskkill/tasklist pair.
MODES: no argument / --dry = OFFLINE walk, NOTHING spawned and nothing killed (children, tasklist, taskkill, git restore and file
writes are stubbed; check_launch and md5 reads are real and read-only); `--branch equal|different|fail-a|fail-graph|fail-b|fail-el`
picks the stubbed outcome (default equal). `--launch` = the live chain (cycle 135 card: labview build, gui true).
CARD 134-6 (PD291(d)): the graph child runs with gate B SCOPED (diag_c134_1_graph.py, uses_plan = plan b): the 7 nested tunnels are
LISTED, the gate passes unless plan b uses one, so the child ends rc 0; the old rc=1 special case (the 7-tunnel set) is removed. R and FS2 are
skipped in the child (same_rows_as / fs_watch null): this runner's compare C covers terminals, wires, fs_frames and borders.
PREDICTION (live): A peak <= 690 (scratch a 650.9); G rc 0, gates G1 G2 G3 FS1 B X PASS (B lists 7 UNMEASURED); C EQUAL
(LabVIEW uid allocation deterministic, PD290(d)); B peak <= 690 and <= X10 667.0 + 10; E total 49..52, classes in lo..hi; bed unchanged.
    py tools/bgrun.py --material --max-min 200 --log tools/bench/launch_p3b2_c135.log -- py -u tools/bench/launch_p3b2_c135.py --launch"""
import collections, copy, glob, hashlib, json, os, re, subprocess, sys, time        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                 # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                        # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                          # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b1_20261002_060910.vi"
BED_MD5 = "9d7bf28738b7c154280e5e7c2c9d4961"
REF_GRAPH = "tools/bench/graph_ring_p3b2a_fs_20261002_102553.json"
RA, RB = "tools/recipes/stage_d1_ring_p3b2a.py", "tools/recipes/stage_d1_ring_p3b2b.py"
PA, PB, PBI, PBP = "tools/bench/plan_ring_p3b2a.json", "tools/bench/plan_ring_p3b2b.json", "tools/bench/plan_ring_p3b2b_in.json", "tools/bench/plan_ring_p3b2b_pred.json"
PINS = {RA: "bb5ba064b6220d16e3a5c77d19b9c70f", RB: "e6636785aa3483ff313bf75ec452e3d6", PA: "a419f23f29760447da8b43e1154fa470",
        PB: "ae6b6111d766a4ba27d0695f29958c23", REF_GRAPH: "b885fa4af1df203a8dd68b631ab86752",
        "tools/bench/diag_c134_1_graph.py": "3bd108c5e07fc002b0f4aae3d44064b4", "tools/bench/diag_c134_1_finalize_b.py": "4dce0e4cfa51295c542cb132aff77556"}
PB_FINALIZE_PIN, PB_COMMIT = "1451ba90aadc594fe74f97793eb04e92", "0b72718d"   # finalize_b's F-1 pin; the commit that holds those bytes
G_REQ = ("G1", "G2", "G3", "FS1", "B", "X")                                      # card 134-6: every gate the graph child runs, all PASS
EL_RANGE = "tools/bench/errorlist_expect_p3b2ab.json"
STATE = os.path.join(B, "launch_p3b2_c135_state.json")
STEPS = {"A": ("launch_p3b2_c135_a.py", 45), "G": ("launch_p3b2_c135_graph.py", 15), "B": ("launch_p3b2_c135_b.py", 45),
         "E": ("launch_p3b2_c135_el.py", 40)}


def recipe_cmd(r):
    return "py -u {0}".format(r)


# ------------------------------------------------------------------ the compare (PD290(b)(d)); pure, offline-testable
def graph_key(g):
    objs = sorted((int(o["uid"]), str(o.get("class"))) for o in g["objs"])
    rows = sorted(json.dumps(r, sort_keys=True, default=str) for r in g["terminals"])
    wires = collections.defaultdict(set)
    for r in g["terminals"]:
        if r.get("wire_uid"):
            wires[int(r["wire_uid"])].add(int(r["term_uid"]))
    fm = g.get("fs_measured") or {}
    return {"node_classes": objs, "terminals": rows, "wires": sorted((w, sorted(t)) for w, t in wires.items()),
            "fs_frames": json.dumps(fm.get("fs_frames"), sort_keys=True), "borders": json.dumps(fm.get("borders"), sort_keys=True, default=str)}


def compare(new, ref):
    """(equal, diff) - diff lists per field the first differing items (never absorbed: rule 1a, PD288(e))."""
    kn, kr = graph_key(new), graph_key(ref)
    diff = {}
    for f in kn:
        if kn[f] != kr[f]:
            a, b = kn[f], kr[f]
            if isinstance(a, list):
                sa, sb = set(map(str, a)), set(map(str, b))
                diff[f] = {"only_new": sorted(sa - sb)[:5], "only_ref": sorted(sb - sa)[:5], "n": [len(a), len(b)]}
            else:
                diff[f] = {"new": a[:200], "ref": b[:200]}
    return not diff, diff


# ------------------------------------------------------------------ executors: live and stubbed (dry)
class Live:
    dry = False

    def child(self, step, extra=None):
        script, mx = STEPS[step] if step in STEPS else (None, 10)
        cmd = extra or ["py", "-u", os.path.join("tools", "bench", script)]
        log = os.path.join(B, "launch_p3b2_c135_{0}.log".format(step.lower()))
        full = ["py", os.path.join("tools", "bgrun.py"), "--material", "--max-min", str(mx), "--log", rel(log), "--"] + cmd
        print("  RUN   {0}: {1}".format(step, " ".join(full)), flush=True)
        rc = subprocess.run(full, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        txt = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
        seg = txt[txt.rfind("BGRUN START"):] if "BGRUN START" in txt else ""
        return rc, seg

    def labview_gone(self, kill=True):
        if kill:
            subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
            time.sleep(4.0)
        return "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()

    def write(self, path, data):
        json.dump(data, open(path, "w", encoding="utf-8"), indent=1)

    def restore_pb(self):
        flt = subprocess.run(["git", "cat-file", "--filters", "{0}:{1}".format(PB_COMMIT, PB)], cwd=ROOT, capture_output=True, check=True).stdout
        if hashlib.md5(flt).hexdigest() != PB_FINALIZE_PIN:
            return False
        open(os.path.join(ROOT, PB), "wb").write(flt)
        return md5(os.path.join(ROOT, PB)) == PB_FINALIZE_PIN


class Dry(Live):
    """Nothing spawned, nothing killed, nothing written: each child returns the branch's fixture."""
    dry = True

    def __init__(self, branch):
        self.branch, self.calls, self.mem = branch, [], {}

    def child(self, step, extra=None):
        self.calls.append(step)
        fail = self.branch == "fail-" + {"A": "a", "G": "graph", "B": "b", "E": "el"}.get(step, "?")
        print("  DRY   child {0} {1} -> {2}".format(step, extra or STEPS.get(step, ("?",))[0], "FAIL (stub)" if fail else "PASS (stub)"), flush=True)
        if step == "A":
            self.mem["a"] = {"rc": 0, "peak_mb": 650.9, "final": "<dry a-file>", "final_md5": "d" * 32, "bed_md5_ok": True, "gone": True}
            return (1, "") if fail else (0, "")
        if step == "G":
            seg = "".join("  PASS  {0} x\n".format(g) for g in ("G1", "G2", "G3", "FS1", "B", "X")) + \
                  "  FACT  MEM after load: 588.1 MB private; handles 1\n"
            if fail:
                return 1, seg.replace("PASS  G1", "FAIL  G1")
            return 0, seg                                                     # card 134-6: gate B scoped -> rc 0
        if step == "B":
            self.mem["b"] = {"rc": 0, "peak_mb": 667.0, "x10": 667.0, "final": "<dry b-file>", "final_md5": "e" * 32, "inputs_ok": True, "gone": True}
            return (1, "") if fail else (0, "")
        if step == "E":
            rg = J(EL_RANGE)
            cc = dict(rg["per_class_lo"])
            self.mem["e"] = {"gates": {"window_opened": True}, "item_count": sum(cc.values()) + (10 if fail else 0), "items": [], "cc": cc}
            return 0, "ERRORLIST-VERDICT: MISMATCH <dry el json>\n"
        return 0, "  PASS  (stub {0})\n".format(step)

    def labview_gone(self, kill=True):
        self.calls.append("gone")
        return True

    def write(self, path, data):
        self.calls.append("write:" + os.path.basename(path))

    def restore_pb(self):
        self.calls.append("restore_pb")
        return True


# ------------------------------------------------------------------ the chain
def run(X, branch="equal"):
    import stage_prerun as SP
    gates, arts, state = [], [], {}

    def gate(name, ok, det=""):
        gates.append((name, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)
        return bool(ok)

    started = []                                                                  # kill LabVIEW only once OUR first child ran

    def stop():
        started and X.labview_gone(kill=True)                                     # noqa: E701 - never kill another card's LabVIEW
        nf = sum(1 for _n, c in gates if not c)
        return gates, arts, state, (next((n for n, c in gates if not c), None) if nf else None)

    if not gate("L0c no LabVIEW running before the chain (one COM client)", X.labview_gone(kill=False)):
        return stop()
    pins = dict((p, md5(os.path.join(ROOT, p))) for p in PINS)
    if not gate("L0a pins: recipes a/b, plans a/b, graph 102553, graph diag, finalize script", pins == PINS,
                dict((p, m) for p, m in pins.items() if m != PINS[p])):
        return stop()
    if not gate("L0b bed md5 == {0} (read-only, never saved)".format(BED_MD5[:8]), os.path.exists(BED) and md5(BED) == BED_MD5):
        return stop()
    for r in (RA, RB):
        ok, why = SP.check_launch(recipe_cmd(r))
        if not gate("L0d check_launch({0}) ALLOW".format(os.path.basename(r)), ok, why.replace("\n", " | ")):
            return stop()
    # ---- A
    started.append("A")
    rc, seg = X.child("A")
    sa = X.mem.get("a") if X.dry else (J(os.path.join(B, "launch_p3b2_c135_a_sum.json")) if os.path.exists(os.path.join(B, "launch_p3b2_c135_a_sum.json")) else {})
    afile, amd5 = sa.get("final"), sa.get("final_md5")
    ok = rc == 0 and afile and (X.dry or (os.path.exists(afile) and md5(afile) == amd5)) and sa.get("peak_mb") is not None and sa["peak_mb"] <= 690.0
    if not gate("A session a: rc 0, saved file == its md5, peak {0} <= 690".format(sa.get("peak_mb")), ok, {"rc": rc, "final": afile, "md5": amd5}):
        return stop()
    state.update(a_file=afile, a_md5=amd5, a_peak=sa.get("peak_mb"))
    X.write(STATE, state)
    if not gate("A2 LabVIEW gone; bed unchanged", X.labview_gone() and md5(BED) == BED_MD5):
        return stop()
    # ---- G
    pl = J("tools/bench/diag_c134_1_graph_plan.json")
    pl["input"] = {"vi": afile, "md5": amd5, "same_rows_as": None}                 # card 134-6: compare C does R's job
    pl["fs_watch"], pl["uses_plan"] = None, PB                                    # FS2 -> compare C; gate B scoped by plan b
    pl["schema_note"] = "launch_p3b2_c135 (cards 134-P1, 134-6): the card-134-1 graph plan with input = session a's launched file"
    X.write(os.path.join(B, "launch_p3b2_c135_graph_plan.json"), pl)
    t0 = time.time()
    rc, seg = X.child("G")
    gl = dict((m.group(2), m.group(1)) for m in re.finditer(r"^\s+(PASS|FAIL)\s+(\w+)\s", seg, re.M))
    if not gate("G graph read: rc 0 and {0} all PASS, no FAIL line".format(G_REQ),
                rc == 0 and all(gl.get(k) == "PASS" for k in G_REQ) and "FAIL" not in gl.values(), {"gates": gl, "rc": rc}):
        return stop()
    if X.dry:
        newg = copy.deepcopy(J(REF_GRAPH))
        if branch == "different":
            newg["terminals"][0]["term_uid"] = int(newg["terminals"][0]["term_uid"]) + 1
        gpath = "<dry graph>"
    else:
        cand = [p for p in glob.glob(os.path.join(B, "graph_ring_p3b2a_fs_*.json")) if os.path.getmtime(p) >= t0]
        gpath = max(cand, key=os.path.getmtime) if cand else None
        newg = J(gpath) if gpath else None
    if not gate("G2 graph JSON written for the a-file ({0})".format(gpath), newg is not None and (X.dry or (newg.get("vi") == afile and newg.get("md5") == amd5))):
        return stop()
    state.update(graph=gpath if X.dry else rel(gpath), graph_md5=None if X.dry else md5(gpath))
    mem = re.search(r"FACT\s+MEM after load: ([\d.]+) MB", seg)
    if not gate("G3 LabVIEW gone; bed + a-file unchanged; 'MEM after load' read ({0})".format(mem and mem.group(1)),
                X.labview_gone() and md5(BED) == BED_MD5 and (X.dry or md5(afile) == amd5) and mem):
        return stop()
    # ---- C
    eq, diff = compare(newg, J(REF_GRAPH))
    state.update(compare="EQUAL" if eq else "DIFFERENT", compare_diff=diff)
    print("  FACT  C compare vs {0}: {1} {2}".format(REF_GRAPH, "EQUAL" if eq else "DIFFERENT", json.dumps(diff)[:900]), flush=True)
    X.write(STATE, state)
    if not eq:
        snap = dict((p, os.path.join(B, "launch_p3b2_c135_pre_" + os.path.basename(p))) for p in (PB, PBI, PBP))
        for p, s in snap.items():
            X.write(s, J(p))
        mm = os.path.join(B, "memory_model.json")
        m = J(mm)
        m.setdefault("load_by_vi", {})[amd5] = {"value": float(mem.group(1)), "vi": "claudeDev\\" + os.path.basename(afile or "?") + " (P3b-2 session a, launch_p3b2_c135)",
                                                "cite": "tools/bench/launch_p3b2_c135_g.log (MEM after load: {0} MB private)".format(mem.group(1))}
        X.write(mm, m)
        if not gate("R plan b bytes restored to {0} from commit {1} (finalize_b's F-1 pin)".format(PB_FINALIZE_PIN[:8], PB_COMMIT), X.restore_pb()):
            return stop()
        for st, cmd in (("F", ["py", "-u", "tools/bench/diag_c134_1_finalize_b.py", gpath]), ("D", ["py", "-u", "tools/stage_prerun.py", "--dry", RB]),
                        ("P", ["py", "-u", "tools/stage_prerun.py", "--prerun", RB])):
            rc, seg = X.child(st, cmd)
            if not gate("{0} {1} rc 0".format(st, " ".join(cmd[2:4])), rc == 0, seg[-400:]):
                return stop()
    ok, why = SP.check_launch(recipe_cmd(RB))
    if not gate("C2 check_launch({0}) ALLOW on plan b md5 {1}".format(os.path.basename(RB), md5(os.path.join(ROOT, PB))[:8]), ok, why.replace("\n", " | ")):
        return stop()
    # ---- B
    rc, seg = X.child("B")
    sb = X.mem.get("b") if X.dry else (J(os.path.join(B, "launch_p3b2_c135_b_sum.json")) if os.path.exists(os.path.join(B, "launch_p3b2_c135_b_sum.json")) else {})
    bfile, bmd5, pk, x10 = sb.get("final"), sb.get("final_md5"), sb.get("peak_mb"), sb.get("x10")
    ok = rc == 0 and bfile and (X.dry or (os.path.exists(bfile) and md5(bfile) == bmd5)) and pk is not None and x10 and pk <= 690.0 and pk <= x10 + 10
    if not gate("B session b: rc 0, saved file == its md5, peak {0} <= 690 and <= X10 {1} + 10; input = the a-file".format(pk, x10),
                ok and (X.dry or sb.get("input") == afile), {"rc": rc, "final": bfile, "md5": bmd5}):
        return stop()
    state.update(b_file=bfile, b_md5=bmd5, b_peak=pk)
    X.write(STATE, state)
    if not gate("B2 LabVIEW gone; bed + a-file unchanged", X.labview_gone() and md5(BED) == BED_MD5 and (X.dry or md5(afile) == amd5)):
        return stop()
    arts.extend([{"path": afile, "md5": amd5}, {"path": bfile, "md5": bmd5}])
    # ---- E
    rc, seg = X.child("E")
    mv = re.search(r"ERRORLIST-VERDICT: (\w+) (.+)$", seg, re.M)
    if X.dry:
        R = X.mem["e"]
        cc = R["cc"]
    else:
        R = J(mv.group(2).strip()) if mv and os.path.exists(mv.group(2).strip()) else {}
        import errorlist_check as EC
        cc = EC.class_counts(R.get("items"), ocr=True)
    rg = J(EL_RANGE)
    n = R.get("item_count")
    bad = dict((k, v) for k, v in cc.items() if not rg["per_class_lo"].get(k, 0) <= v <= rg["per_class_hi"].get(k, 0))
    bad.update(dict((k, 0) for k in rg["per_class_lo"] if k not in cc and rg["per_class_lo"][k] > 0))
    state.update(el_json=mv and mv.group(2).strip(), el_verdict=mv and mv.group(1), el_items=n, el_class_counts=cc)
    X.write(STATE, state)
    print("  FACT  E reader verdict {0} vs the recipe's expected file (53, placeholder); items {1}; per class {2}".format(
        mv and mv.group(1), n, json.dumps(cc, sort_keys=True)), flush=True)
    gate("E full Error List: reader gates all True, rc in (0, 1)", rc in (0, 1) and R.get("gates") and all(R["gates"].values()), R.get("gates"))
    gate("E2 total {0} in {1}..{2}".format(n, rg["total_lo"], rg["total_hi"]), n is not None and rg["total_lo"] <= n <= rg["total_hi"])
    gate("E3 every class within lo..hi of {0}".format(EL_RANGE), not bad, bad)
    gate("E4 LabVIEW gone; final, a-file and bed unchanged", X.labview_gone() and md5(BED) == BED_MD5
         and (X.dry or (md5(afile) == amd5 and md5(bfile) == bmd5)))
    return stop()


if __name__ == "__main__":
    live = "--launch" in sys.argv[1:]
    br = sys.argv[sys.argv.index("--branch") + 1] if "--branch" in sys.argv else "equal"
    print(__doc__, flush=True)
    print("MODE {0}{1}".format("LAUNCH" if live else "DRY (nothing spawned, nothing killed)", "" if live else ", branch " + br), flush=True)
    X = Live() if live else Dry(br)
    gates, arts, state, first = run(X, br)
    if not live:
        print("  FACT  DRY calls {0}".format(X.calls), flush=True)
    np_, nf = sum(1 for _n, c in gates if c), sum(1 for _n, c in gates if not c)
    print(P.result_line(P.make_result(np_, nf, first, [a for a in arts if live and a.get("path")])), flush=True)
    sys.exit(1 if nf else 0)
