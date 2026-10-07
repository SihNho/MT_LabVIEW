# ---
# labview: none
# hardware: none
# ---
r"""selftest_t4 - card chat-T4 (PD348): bench arm A13K's address fix (its card 145-a3-1, PD346(c) there) ported to main -
addrcheck.real_face / cond_bind + the face/'cond' branch of stage_prerun.rebase's address check. Offline; never opens LabVIEW;
every rebase runs on a %TEMP% copy with out_root %TEMP% (nothing under tools/bench/sim is written).
Existing first (checked): A13K tools/bench/selftest_c145_a3_1.py (bind-log seeding, which main does not have - main binds by the
creation map, card chat-T3); selftest_t3.py C7 (stops at this refusal). Negatives N1-N8 are A13K's, with A13K's mode 'record'
translated to main's 'map-pos' (addrcheck.py BOUND_MODES comment).
Fixtures: tools/bench/fixtures/cmap_s03s04/ (from A13K; s04 input plan 66d94bad, provisional base, real s03 graph a5d7ca5e,
the s03 scratch log whose STEPX `bound` records become a creation-map/1 file, as selftest_t3 does).
PREDICTION
  P1 a13/a15 #-28.'inner' -> real row 29582 by face; 29582 == M[sim row] (mode in map/map-pos/conn); rebased src {'uid': 29548, 'term': 'inner'}
  P2 a20 #-45.'cond' -> body 29699, the one unnamed sink 29710; rebased dst {'uid': 16483, 'term': 'cond'}
  P3 no ADDRESS-UNRESOLVED / LLM-OWED; rebase simulate=False ok
  P4 rebase WITH re-simulation on the real base (out_root %TEMP%): ok, final=True, 49 uid(s) bound, 23 STEP lines all ok,
     completeness PASS, end_cdiff_rows 16, open_rows_match True (A13K card 145-a3-2 measured these on its own rebase)
  P5 fixture files unchanged; no tools/bench/sim/ring_p4_s04v18* written in main
  N1-N8 synthetic tables refused with the reason; R1/R2 resolve / real_match unchanged
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_t4.log -- py -u tools/bench/selftest_t4.py"""
import ast, glob, json, os, re, shutil, sys, tempfile                                     # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(B)
R = os.path.dirname(T)
sys.path.insert(0, T)
import protocol as P, stage_prerun as SP, addrcheck as AC, vigraph as V                   # noqa: E401,E402
FX = os.path.join(B, "fixtures", "cmap_s03s04")
NP, NF = [0], []


def gate(name, ok, val=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:600]), flush=True)
    NP[0] += bool(ok)
    if not ok:
        NF.append(name)


J = lambda p: json.load(open(p, encoding="utf-8"))                                        # noqa: E731
fx_md5 = dict((f, SP.md5(os.path.join(FX, f))) for f in sorted(os.listdir(FX)))
sim_before = sorted(glob.glob(os.path.join(B, "sim", "ring_p4_s04v18*")))
pl = J(os.path.join(FX, "plan_ring_p4_s04v18_in.json"))
so = pl["base"]["sim_of"]
gb, before = SP._terms(os.path.join(B, "sim", "ring_p4_s03v18_base_real_fsmap.json"))
gp, prov = SP._terms(os.path.join(FX, "prov_s04_base_provisional.json"))
gr, real = SP._terms(os.path.join(FX, "real_graph_s03.json"))
pobj = SP._obj_id(gp)
s03 = open(os.path.join(FX, "s03_scratch_run.txt"), encoding="utf-8", errors="replace").read()
STEPX = re.compile(r"^\s*STEPX (\d+) (\S+)\s+acts \[([^\]]*)\] ids \[([^\]]*)\] bound (\{[^}]*\}) diff (\d+)")


def write_map(path):                                     # as selftest_t3.write_map (no drop / swap)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"schema": "creation-map/1", "rec": "run", "plan": so["plan"], "plan_md5": so["md5"], "stage": "x",
                             "work": gr["vi"], "from_step": None, "source": "fixture: STEPX bound records of s03_scratch_run.txt"}) + "\n")
        for ln in s03.splitlines():
            m = STEPX.match(ln)
            if m:
                for s, r in ast.literal_eval(m.group(5)).items():
                    kind = "diag" if (pobj.get(s) or (None,))[0] == "Diagram" else "obj"
                    fh.write(json.dumps({"schema": "creation-map/1", "rec": "bind", "k": int(m.group(1)), "op": m.group(2),
                                         "kind": kind, "sim": s, "real": r}) + "\n")
    return path


tmp = tempfile.mkdtemp(prefix="t4_")
try:
    cm = write_map(os.path.join(tmp, "s03.jsonl"))
    info = {}
    M, why = SP.rebind(before, prov, real, prov_doc=gp, real_doc=gr, before_doc=gb, info=info, named=SP.plan_named_uids(pl),
                       cmap=SP.read_creation_map(cm)[1])
    dprov, dreal = V.dedupe_rows(prov)[0], V.dedupe_rows(real)[0]
    r28, h28, _c = AC.resolve(dprov, -28, "inner", want_source=True)
    st28 = r28["term_uid"] if r28 else None
    md28 = info.get("mode", {}).get(st28)
    print("  INFO  sim -28.'inner' -> #{0} by {1}; M[{0}] = {2} (mode {3}); M[-28] = {4}; M[-45] = {5}".format(
        st28, h28, (M or {}).get(st28), md28, (M or {}).get(-28), (M or {}).get(-45)), flush=True)
    okf, whyf = AC.real_face(dprov, st28, dreal, (M or {}).get(-28), "inner", True, (M or {}).get(st28), md28)
    sk, whyc = AC.cond_bind({"uid": -45, "term": "cond"}, gp, dprov, -45, gr, dreal, (M or {}).get(-45), M)

    def run_rebase(name, simulate):
        pc = json.loads(json.dumps(pl))
        pc["base"]["path"] = os.path.join(FX, "prov_s04_base_provisional.json")
        od = os.path.join(tmp, name)
        os.makedirs(od)
        pp = os.path.join(od, "plan_ring_p4_s04v18.json")
        json.dump(pc, open(pp, "w", encoding="utf-8"), indent=1)
        lines = []
        ok, det = SP.rebase(pp, os.path.join(FX, "real_graph_s03.json"), log=lines.append, simulate=simulate, out_root=od,
                            creation_map=cm)
        return ok, det, lines, (J(pp) if ok else {"actions": []}), od
    ok3, det3, lines3, new3, _od3 = run_rebase("nosim", False)
    for s in lines3:
        if s.startswith(("MAP-BOUND", "FALLBACK-COUNT", "REBIND", "ADDRESS-")):
            print("  LOG   " + s[:300], flush=True)
    act = dict((n, a) for n, a in enumerate(new3.get("actions") or [], 1))
    res = [s for s in lines3 if s.startswith("ADDRESS-RESOLVED")]
    a13, a15, a20 = ([s for s in res if " a{0}:{1} ".format(n, f) in s] for n, f in ((13, "src"), (15, "src"), (20, "dst")))
    gate("P1 a13/a15 #-28.'inner' -> 29582 by face == the map binding M[{0}] (mode {1}); rebased src keeps 'inner'".format(st28, md28),
         M is not None and okf and M.get(st28) == 29582 and md28 in AC.BOUND_MODES and len(a13) == 1 and len(a15) == 1
         and "(row #29582) by face" in a13[0] and "(row #29582) by face" in a15[0]
         and (act.get(13) or {}).get("src") == {"uid": 29548, "term": "inner"} and (act.get(15) or {}).get("src") == {"uid": 29548, "term": "inner"},
         "helper {0} {1}; a13 {2}; a15 {3}; rebased {4} {5}".format(okf, whyf, a13, a15, (act.get(13) or {}).get("src"), (act.get(15) or {}).get("src")))
    gate("P2 a20 #-45.'cond' -> {'uid': 16483, 'term': 'cond'}; body 29699, the one unnamed sink 29710",
         sk == 29710 and "[29699]" in whyc and len(a20) == 1 and "(row #29710)" in a20[0]
         and (act.get(20) or {}).get("dst") == {"uid": 16483, "term": "cond"},
         "helper {0} {1}; a20 {2}; rebased {3}".format(sk, whyc, a20, (act.get(20) or {}).get("dst")))
    un = [s for s in lines3 if s.startswith(("ADDRESS-UNRESOLVED", "ADDRESS-LLM-OWED"))]
    gate("P3 no ADDRESS-UNRESOLVED / LLM-OWED; rebase (simulate=False) ok", ok3 and not un, un or det3[:300])
    ok4, det4, lines4, new4, od4 = run_rebase("sim", True)
    steps = [s for s in lines4 if re.match(r"^\s*STEP\b", s)]
    fz = new4.get("finalized") or {}
    print("  FACT  P4 {0}".format(det4[:400]), flush=True)
    print("  FACT  P4 STEP lines {0}, not ok {1}; end_cdiff_rows {2}; open_rows_match {3}; open_rows {4}; actions {5}".format(
        len(steps), [s[:120] for s in steps if " ok" not in s][:3], len(fz.get("end_cdiff_rows") or []), fz.get("open_rows_match"),
        len(new4.get("open_rows") or []), len(new4.get("actions") or [])), flush=True)
    gate("P4 rebase WITH re-simulation on the real base: ok, final, 49 uids, completeness PASS, 23 STEP ok, cdiff 16, open_rows_match",
         ok4 and "final=True" in det4 and "49 uid(s) bound" in det4 and "completeness PASS" in det4 and len(steps) == 23
         and all(" ok" in s for s in steps) and len(fz.get("end_cdiff_rows") or []) == 16 and fz.get("open_rows_match") is True,
         det4[:300])
    if ok4:
        shutil.copyfile(os.path.join(od4, "plan_ring_p4_s04v18.json"), os.path.join(tmp, "..", "t4_s04_rebased_sim.json"))
    gate("P5 fixtures unchanged; nothing new under tools/bench/sim/ring_p4_s04v18*",
         fx_md5 == dict((f, SP.md5(os.path.join(FX, f))) for f in sorted(os.listdir(FX)))
         and sorted(glob.glob(os.path.join(B, "sim", "ring_p4_s04v18*"))) == sim_before, sim_before)

    def row(t, own, cls, src, name="", ocls="LeftShiftRegister"):
        return {"term_uid": t, "term_name": name, "is_source": src, "wire_uid": 0, "owner_uid": own, "owner_class": ocls,
                "frame_diagram": 1, "term_class": cls}
    sim = [row(-1, -10, "InnerTerminal", True), row(-2, -10, "OuterTerminal", False)]
    good = [row(11, 100, "InnerTerminal", True), row(12, 100, "OuterTerminal", False)]
    gate("C1 synthetic face table resolves", AC.real_face(sim, -1, good, 100, "inner", True, 11, "map-pos") == (True, "face"))
    n1 = AC.real_face(sim, -1, good + [row(13, 100, "InnerTerminal", True)], 100, "inner", True, 11, "map-pos")
    gate("N1 two same-face rows of the wanted direction -> REFUSED", not n1[0] and "2 InnerTerminal" in n1[1], n1)
    n2 = AC.real_face(sim, -1, good, 100, "inner", True, 12, "map-pos")
    gate("N2 face row #11 != the map-bound row #12 -> REFUSED", not n2[0] and "!= the bound row #12" in n2[1], n2)
    n2b = AC.real_face(sim, -1, good, 100, "inner", True, 11, "shape")
    gate("N2b bound by shape (not conn/map/map-pos) -> REFUSED", not n2b[0] and "bound by shape" in n2b[1], n2b)

    def wdoc(loop, cls, body, sinks):
        rows = [row(body * 10 + 1, body, "Terminal", True, ocls="Diagram")]
        rows += [row(body * 10 + 2 + i, body, "Terminal", False, name=nm, ocls="Diagram") for i, nm in enumerate(sinks)]
        return {"objs": [{"uid": loop, "class": cls}, {"uid": body, "class": "Diagram"}], "owners": {str(body): [cls, loop]}}, rows
    sd, sr = wdoc(-45, "WhileLoop", -46, [""])
    rd, rr = wdoc(500, "WhileLoop", 501, [""])
    A = {"uid": -45, "term": "cond"}
    gate("C2 synthetic While table resolves (sink #5012)", AC.cond_bind(A, sd, sr, -45, rd, rr, 500, {})[0] == 5012)
    for lab, args, want in (
            ("N3 'cond' on a real ForLoop", (A, sd, sr, -45) + wdoc(500, "ForLoop", 501, [""]) + (500, {}), "real #500 is ForLoop"),
            ("N3b 'cond' on a sim node that is not a While", (A, {"objs": [{"uid": -45, "class": "Diagram"}], "owners": {}}, sr, -45, rd, rr, 500, {}), "sim #-45 is Diagram"),
            ("N4 real body with 0 unnamed sinks", (A, sd, sr, -45) + wdoc(500, "WhileLoop", 501, []) + (500, {}), "real []"),
            ("N5 real body with 2 unnamed sinks", (A, sd, sr, -45) + wdoc(500, "WhileLoop", 501, ["", ""]) + (500, {}), "real [5012, 5013]"),
            ("N6 the one real body sink is NAMED", (A, sd, sr, -45) + wdoc(500, "WhileLoop", 501, ["stop"]) + (500, {}), "is named 'stop'"),
            ("N7 an extra key beside uid/term", ({"uid": -45, "term": "cond", "side": "x"}, sd, sr, -45, rd, rr, 500, {}), "PD316"),
            ("N8 sim sink bound to another real sink", (A, sd, sr, -45, rd, rr, 500, {-458: 9999}), "bound to #9999")):
        n = AC.cond_bind(*args)
        gate(lab + " -> REFUSED", n[0] is None and want in n[1], n)
    rr0 = AC.resolve(good, 100, "inner", want_source=True)
    gate("R1 addrcheck.resolve unchanged: 'inner' -> #11 by side", rr0[0] and rr0[0]["term_uid"] == 11 and rr0[1] == "side", rr0[:2])
    gate("R2 addrcheck.real_match unchanged: unique-dir", AC.real_match(sim, -1, good, 11, 100) == (True, "unique-dir"))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(P.result_line(P.make_result(NP[0], len(NF), NF[0] if NF else None)), flush=True)
sys.stdout.flush()
os._exit(0 if not NF else 1)
