# ---
# labview: none
# hardware: none
# ---
r"""selftest_t3 - card chat-T3 (PD347, user 2026-10-07 "세 가지 다 고치도록"): the three tool faults every bench arm hit.
Offline; never opens LabVIEW; plan / graph files are read, copies go to %TEMP%.
Existing first (checked): stagexec.selftest (T-series), selftest_rebind_c132_5 / selftest_rebase_c132_6 (rebind / rebase on
older recorded graphs) - kept and re-run beside this file; nothing here re-tests what they cover.
Fixtures (tools/bench/fixtures/cmap_s03s04/, copied from bench arm A13K, every arm failed this case): the s04 provisional base,
the REAL graph of the adopted s03 file (D1_ring_p4s03_20261007_102011.vi md5 9a45274c), the s04 plan before its rebase, and
the s03 scratch run log (md5 46a887e8) whose STEPX `bound` records are the identities that run measured - converted here into
a creation-map/1 file (what Executor._cmap_record now writes at the moment of creation).
PREDICTION
  A1 docstring echo with 'ExecStop' / 'MEMSTOP' words + all gates PASS + RESULT PASS -> adopt ok (the bench fault)
  A2 the recorded s03 scratch log (the log every arm's adopt refused) -> adopt ok with its 8 required gates
  A3 a real `STOP {json}` line -> refused; A4 no RESULT line -> refused; A5 an old-style traceback (RESULT fail 1, no FAIL line,
     no STOP line) -> refused; A6 a malformed STOP line still refuses; A7 a LOG-class FAIL line covering RESULT fail 1 -> ok
  A8 stop_line round trip, unknown kind raises, stop_kind_of MEMSTOP / ExecStop; A9 report_stop prints a STOP line;
  A10 stagekit.run / excepthook / bgrun TIMEOUT / lv_stallcheck carry the STOP line (source check: stagekit imports LabVIEW)
  C1 the executor's writer: header + one row per new binding with class / owner, step row; auto mode writes nothing for a
     SimBackend (also wrapped), something for a real one; C2 tag switch file says OFF; tag text round trip; switch ON with a
     backend lacking the verbs -> ExecStop; with fake verbs -> tags recorded, a mismatch recorded not hidden
  C3 s03 -> s04 rebind WITH the map: every created node bound, 0 node fallbacks, the two identical-shape register pairs
     -27/-28 -> 29403/29548 and -36/-37 -> 29648/29655, the row-less While -45 -> 16483, its body -46 -> 29699
  C4 the two pairs' entries SWAPPED in the map -> refused (never bound wrong); C5 entry -33 dropped -> bound by inference,
     one FALLBACK node line; C6 load_creation_map finds the map by plan + md5 + VI, refuses a wrong md5 when explicit
  C7 full rebase (no re-simulation) of a %TEMP% copy with the map: passes the BINDING stage (any refusal is not MAP/BINDING/
     CONNECTIVITY - the address-face stage is reported as a fact)
  W1 loop_parent of the row-less While 16483 on the recorded real graph (no diagrams map) = 23166 from owners; W2 SimReader
     lists 16483 on exactly ONE diagram (was every diagram); W3 without an owners entry -> None (unchanged)
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_t3.log -- py -u tools/bench/selftest_t3.py"""
import ast, copy, io, json, os, re, shutil, sys, tempfile, types, contextlib                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(B)
R = os.path.dirname(T)
sys.path.insert(0, T)
import protocol as P, gateclass as G, stagexec as SX, stage_prerun as SP                    # noqa: E401,E402
FX = os.path.join(B, "fixtures", "cmap_s03s04")
NP, NF = [0], []


def gate(name, ok, val=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:500]), flush=True)
    if ok:
        NP[0] += 1
    else:
        NF.append(name)


J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
RES = lambda ok, n=1: P.result_line(P.make_result(n if ok else 0, 0 if ok else n, None if ok else "x"))   # noqa: E731
print("---------- A adopt reads RESULT / STOP / gate lines only")
echo = ("BGRUN START 2026-10-07 05:18:16 limit 50.0 min: py -u x.py\nr\"\"\"x - card 143-P2 ported: SX.save_for_resume before "
        "SX.report_stop on ExecStop (PD329(b)); MEMSTOP 695 is the stop\nTraceback words in prose are prose\n\"\"\"\n"
        "  PASS  E1 the run reached its last op\n  PASS  PB parity\n" + RES(True, 2) + "\nBGRUN END rc=0 after 5s\n")
v = SX.adopt_verdict(echo, ["E1", "PB"])
gate("A1 docstring echo ('ExecStop', 'MEMSTOP' in prose) + PASS gates + RESULT PASS -> adopt ok", v["ok"], v["why"])
s03 = open(os.path.join(FX, "s03_scratch_run.txt"), encoding="utf-8", errors="replace").read()
v = SX.adopt_verdict(s03[s03.rfind("BGRUN START"):], ["E1", "NG", "PRIM", "FR", "D", "TD", "PB", "PS"])
gate("A2 the recorded s03 scratch log (refused by every arm's adopt) -> ok, 8 required gates PASS", v["ok"], (v["why"], v["n_pass"]))
v = SX.adopt_verdict(echo.replace("  PASS  PB", P.stop_line("execstop", "STEP-DIFF after real op 4") + "\n  PASS  PB"), ["E1"])
gate("A3 a real STOP line -> refused", not v["ok"] and any("STOP line" in w for w in v["why"]), v["why"])
v = SX.adopt_verdict("  PASS  E1 x\nBGRUN END rc=0\n", ["E1"])
gate("A4 no RESULT line -> refused", not v["ok"] and "no RESULT line" in v["why"], v["why"])
old_tb = ("  PASS  E1 x\nTraceback (most recent call last):\n  File x\nKeyError: 3\n" +
          P.result_line(P.make_result(1, 1, "KeyError: 3")) + "\n")
v = SX.adopt_verdict(old_tb, ["E1"])
gate("A5 old-style traceback (RESULT fail 1, no FAIL / STOP line) -> refused by the RESULT count", not v["ok"], v["why"])
v = SX.adopt_verdict(echo + "STOP {not json}\n", ["E1"])
gate("A6 a malformed STOP line still refuses", not v["ok"] and v["stops"] and v["stops"][0]["kind"] == "malformed", v["why"])
log_lab = next((l for l in ("NAME-GATE op 3 x", "E1 op 4 tunnel face row only_sim", "L-NAME x")
                if G.classify_line("  FAIL  " + l) == "log"), None)
if log_lab:
    t7 = "  PASS  E1 x\n  FAIL  {0}\n{1}\n".format(log_lab, P.result_line(P.make_result(1, 1, log_lab)))
    v = SX.adopt_verdict(t7, ["E1"])
    gate("A7 a LOG-class FAIL line ({0!r}) covering RESULT fail 1 -> ok (PD329 allowance kept)".format(log_lab), v["ok"], v["why"])
else:
    print("  FACT  A7 skipped: no candidate label classifies LOG in this gateclass", flush=True)
ln = P.stop_line("memstop", "MEMSTOP: 700 MB", op=4)
d = P.all_stop_lines("x\n" + ln + "\ny\n")
try:
    P.stop_line("nonsense", "x")
    bad_kind = False
except ValueError:
    bad_kind = True
gate("A8 stop_line round trip / unknown kind raises / stop_kind_of", len(d) == 1 and d[0]["kind"] == "memstop" and d[0]["op"] == 4
     and bad_kind and P.stop_kind_of("MEMSTOP: x") == "memstop" and P.stop_kind_of(SX.ExecStop("a")) == "execstop"
     and P.stop_kind_of(KeyError("a")) == "exception", (d, bad_kind))


class _Stop(Exception):
    pass


fs = types.SimpleNamespace(R={}, fact=lambda *_a: None)
fs.gate = lambda *a, **k: (_ for _ in ()).throw(_Stop(a[0]))
fx = types.SimpleNamespace(report=[], diffs=[], cur={"k": 7, "op": "connect"})
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        SX.report_stop(fs, fx, types.SimpleNamespace(), SX.ExecStop("MEMSTOP: private bytes 701 MB"))
    except _Stop:
        pass
st = P.all_stop_lines(buf.getvalue())
gate("A9 stagexec.report_stop prints ONE STOP line (kind memstop, op 7)", len(st) == 1 and st[0]["kind"] == "memstop" and st[0]["op"] == 7, st)
src_k = open(os.path.join(T, "stagekit.py"), encoding="utf-8").read()
src_b = open(os.path.join(T, "bgrun.py"), encoding="utf-8").read()
src_s = open(os.path.join(T, "lv_stallcheck.ps1"), encoding="utf-8").read()
gate("A10 STOP line wired: stagekit.run (gate + exception), excepthook, bgrun TIMEOUT, lv_stallcheck",
     src_k.count("_protocol.stop_line(") >= 3 and 'stop_line("timeout"' in src_b and "schema = 'stop-line/1'" in src_s)

print("---------- C creation map")
tmp = tempfile.mkdtemp(prefix="t3_")
plan3 = os.path.join(R, "tools", "bench", "plan_ring_p4_s03v18.json")
X = SX.Executor.__new__(SX.Executor)
X.__dict__.update(_cmap_arg=os.path.join(tmp, "m.jsonl"), cmap_path=None, cmap_rows=0, _tag_arg=False, tags=[],
                  bind={"obj": {}, "term": {}, "diag": {}}, plan_path=plan3, from_step=None, log=lambda m: None,
                  be=types.SimpleNamespace(s=types.SimpleNamespace(work=r"C:\x\D1_t.vi")))
snap = X._cmap_snap()
X.bind["obj"][-2], X.bind["term"][-3] = 29432, 29433
aft = {"terminals": [{"term_uid": -3, "owner_uid": -2, "owner_class": "DigitalNumericConstant", "term_class": "Terminal"}],
       "owners": {"-2": ["Diagram", 23166]}, "loops": []}
rows = X._cmap_record(2, {"kind": "create", "acts": [2]}, snap, aft, ["p4_c_bufdiff"])
X._cmap_step(2, {"kind": "create"}, 0)
head, ent, steps = SP.read_creation_map(X.cmap_path)
gate("C1a writer: header (plan md5, work) + obj -2 (DigitalNumericConstant, owner 23166) + term -3 (owner -2 -> 29432) + step",
     head["plan_md5"] == SX.SS.md5_file(plan3) and head["work"].endswith("D1_t.vi") and ent["obj"][-2]["class"] == "DigitalNumericConstant"
     and ent["obj"][-2]["owner"] == 23166 and ent["term"][-3]["owner_real"] == 29432 and steps == {2: 0} and len(rows) == 2, (head, ent))
sim_be = SX.SimBackend.__new__(SX.SimBackend)
wrapped = SX.RetireGuardBE.__new__(SX.RetireGuardBE)
wrapped.__dict__["_be"] = sim_be
gate("C1b auto mode: no map for SimBackend / wrapped SimBackend, a map for a real backend",
     not SX.is_real_backend(sim_be) and not SX.is_real_backend(wrapped) and SX.is_real_backend(types.SimpleNamespace(s=None)))
tt = SX.tag_text("ring_p4_s03v18", "p4_w1", -45)
gate("C2a tag switch OFF in tools/bench/creation_tag.json; tag text round trip",
     SX.tag_switch() is False and SX.parse_tag(tt) == ("ring_p4_s03v18", "p4_w1", -45), tt)
X._tag_arg = True
try:
    X._tag_created(2, rows[:1], ["p4_c_bufdiff"])
    c2b = False
except SX.ExecStop:
    c2b = True
store = {}
X.be = types.SimpleNamespace(set_description=lambda u, t: store.__setitem__(u, t if u != 29432 else t + "x"),
                             get_description=lambda u: store.get(u))
X._tag_created(2, rows, ["p4_c_bufdiff"])
gate("C2b switch ON + no verbs -> ExecStop; with verbs -> tags recorded, a mismatch recorded (not hidden)",
     c2b and len(X.tags) == 2 and [t["ok"] for t in X.tags].count(False) == 1, X.tags)

pl = J(os.path.join(FX, "plan_ring_p4_s04v18_in.json"))
so = pl["base"]["sim_of"]
gb, before = SP._terms(os.path.join(R, "tools", "bench", "sim", "ring_p4_s03v18_base_real_fsmap.json"))
gp, prov = SP._terms(os.path.join(FX, "prov_s04_base_provisional.json"))
gr, real = SP._terms(os.path.join(FX, "real_graph_s03.json"))
pobj = SP._obj_id(gp)
STEPX = re.compile(r"^\s*STEPX (\d+) (\S+)\s+acts \[([^\]]*)\] ids \[([^\]]*)\] bound (\{[^}]*\}) diff (\d+)")


def write_map(path, drop=(), swap=None):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"schema": "creation-map/1", "rec": "run", "plan": so["plan"], "plan_md5": so["md5"], "stage": "x",
                             "work": gr["vi"], "from_step": None, "source": "fixture: STEPX bound records of s03_scratch_run.txt"}) + "\n")
        for ln in s03.splitlines():
            m = STEPX.match(ln)
            if not m:
                continue
            for s, r in ast.literal_eval(m.group(5)).items():
                if s in drop:
                    continue
                r = (swap or {}).get(s, r)
                kind = "diag" if (pobj.get(s) or (None,))[0] == "Diagram" else "obj"
                fh.write(json.dumps({"schema": "creation-map/1", "rec": "bind", "k": int(m.group(1)), "op": m.group(2),
                                     "kind": kind, "sim": s, "real": r}) + "\n")
    return SP.read_creation_map(path)[1]


named = SP.plan_named_uids(pl)
info0 = {}
M0, why0 = SP.rebind(before, prov, real, prov_doc=gp, real_doc=gr, before_doc=gb, info=info0, named=named)
print("  FACT  C0 without a map (inference only, with the ported dedupe): {0}".format(
    why0 or "bound {0} node(s); modes {1}".format(len(info0["nodes"]), sorted(set(info0["mode"].values())))), flush=True)
cm = write_map(os.path.join(tmp, "s03.jsonl"))
info = {}
M, why = SP.rebind(before, prov, real, prov_doc=gp, real_doc=gr, before_doc=gb, info=info, named=named, cmap=cm)
want = {-27: 29403, -28: 29548, -36: 29648, -37: 29655, -45: 16483, -46: 29699, -33: 29576, -42: 29662}
nf = [x for x in info.get("fallback", []) if x[0] == "node"]
gate("C3 s03->s04 rebind WITH the map: every created node bound, 0 node fallbacks, identical pairs / While / body as recorded",
     M is not None and not nf and all(M.get(k) == v for k, v in want.items()),
     why or {"wrong": dict((k, M.get(k)) for k, v in want.items() if M.get(k) != v), "node_fallbacks": nf,
             "map_nodes": len(info["map_nodes"]), "rowless": info["map_rowless"], "frames": info["map_frames"]})
info4 = {}
M4, why4 = SP.rebind(before, prov, real, prov_doc=gp, real_doc=gr, before_doc=gb, info=info4, named=named,
                     cmap=write_map(os.path.join(tmp, "swap.jsonl"), swap={-27: 29648, -36: 29403, -28: 29655, -37: 29548}))
gate("C4 identical pairs SWAPPED in the map -> refused (never bound wrong)", M4 is None, why4 or "bound: %s" % {k: M4.get(k) for k in (-27, -36)})
info5 = {}
M5, why5 = SP.rebind(before, prov, real, prov_doc=gp, real_doc=gr, before_doc=gb, info=info5, named=named,
                     cmap=write_map(os.path.join(tmp, "drop.jsonl"), drop=(-33,)))
nf5 = [x for x in info5.get("fallback", []) if x[0] == "node"]
gate("C5 entry -33 dropped -> -33 inferred (29576), exactly one node FALLBACK", M5 is not None and M5.get(-33) == 29576
     and [x[1] for x in nf5] == [-33], why5 or nf5)
cdir = os.path.join(tmp, "cmapdir")
os.makedirs(cdir)
shutil.copyfile(os.path.join(tmp, "s03.jsonl"), os.path.join(cdir, "ring_p4_s03v18_da66a030_x.jsonl"))
f1, w1, m1 = SP.load_creation_map(so, gr, cmap_dir=cdir)
f2, w2, _m2 = SP.load_creation_map(dict(so, md5="0" * 32), gr, cmap_dir=cdir)
f3, w3, _m3 = SP.load_creation_map(dict(so, md5="0" * 32), gr, explicit=os.path.join(cdir, "ring_p4_s03v18_da66a030_x.jsonl"))
gate("C6 load_creation_map: found by plan + md5 + VI; none for another md5; explicit wrong md5 refused",
     f1 is not None and f2 is None and f3 is None and "not the map of this run" in (w3 or ""), (w1, w2, w3))
pc = copy.deepcopy(pl)
pc["base"]["path"] = os.path.join(FX, "prov_s04_base_provisional.json")
pp = os.path.join(tmp, "plan_ring_p4_s04v18.json")
json.dump(pc, open(pp, "w", encoding="utf-8"), indent=1)
lines = []
ok7, why7 = SP.rebase(pp, os.path.join(FX, "real_graph_s03.json"), log=lines.append, simulate=False, out_root=tmp,
                      creation_map=os.path.join(tmp, "s03.jsonl"))   # chat-T4: out_root - since PD348 C7 reaches carry_fs
for x in lines:
    if x.startswith(("CREATION-MAP", "MAP-BOUND", "FALLBACK-COUNT", "REBIND", "ADDRESS-UNRESOLVED")):
        print("  FACT  C7 " + x[:400], flush=True)
gate("C7 full rebase with the map passes the BINDING stage (refusal, if any, is not MAP/BINDING/CONNECTIVITY)",
     ok7 or not re.search(r"MAP:|BINDING|CONNECTIVITY|UID-REUSE", str(why7)), why7)
print("  FACT  C7 rebase outcome: {0} {1}".format(ok7, str(why7)[:300]), flush=True)

print("---------- W row-less While owner")
st = {"terminals": real, "owners": gr.get("owners") or {}, "loops": gr.get("loops") or []}
L = next(x for x in st["loops"] if int(x["loop_uid"]) == 16483)
gate("W1 loop_parent(While 16483) on the recorded real graph (no diagrams map) = 23166 from owners", SX.loop_parent(st, L) == 23166,
     SX.loop_parent(st, L))
rd = SX.SimReader(types.SimpleNamespace(st=st))
ds = rd.diagrams()
hits = [ds[i] for i in range(len(ds)) if 16483 in rd.node_uids(i)]
gate("W2 SimReader lists While 16483 on exactly one diagram (23166), was every diagram", hits == [23166], (len(ds), hits[:6]))
st2 = dict(st, owners=dict((k, v) for k, v in st["owners"].items() if k != "16483"))
gate("W3 no owners entry -> None (unchanged legacy behaviour)", SX.loop_parent(st2, L) is None, SX.loop_parent(st2, L))
shutil.rmtree(tmp, ignore_errors=True)
print("=== GATES: {0} pass / {1} fail{2}".format(NP[0], len(NF), "; failing: " + ", ".join(NF) if NF else ""), flush=True)
print(P.result_line(P.make_result(NP[0], len(NF), NF[0] if NF else None)), flush=True)
sys.exit(1 if NF else 0)
