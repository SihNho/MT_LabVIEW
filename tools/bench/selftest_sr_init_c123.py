r"""selftest_sr_init_c123 - card 123-3 S2, OFFLINE (no LabVIEW, no COM): the SR-initialisation route.
T1-T5 stagexec.connect_route: a bare constant -> a LEFT shift register's OUTER face routes 'const_sr' (loop by the owner map, face by
its loop's Terminals[] uid echo); negatives keep refusing. T6 LVBackend.connect 'const_sr' calls gscript.wire_const_sr with the loop's
class traverse index and the face index (stub Stage/gscript). T7 the SimBackend/SimReader path routes the same row. T8 stagesim op_wire
on a const -> L-outer face on the same diagram = one NEW wire, both ends on it. T9 gscript.sr_init_const / wire_const_sr / loop_face_index
exist (ast, gscript is not imported: it pulls COM). T10 opmodels/sr_init_const.json (when present) loads in stagesim.load_models.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_sr_init_c123.log -- py -u tools/bench/selftest_sr_init_c123.py"""
import ast, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as X                                                                        # noqa: E402
import stagesim as SS                                                                       # noqa: E402
import protocol as P                                                                        # noqa: E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def row(t, n, s, w, o, oc, fd, tc="Terminal"):
    return {"term_uid": t, "term_name": n, "is_source": s, "wire_uid": w, "owner_uid": o, "owner_class": oc, "frame_diagram": fd, "term_class": tc}


T = [row(3101, "", True, 0, 310, "RightShiftRegister", 1, "OuterTerminal"), row(3102, "", False, 0, 310, "RightShiftRegister", 8, "InnerTerminal"),
     row(3111, "", False, 0, 311, "LeftShiftRegister", 1, "OuterTerminal"), row(3112, "", True, 0, 311, "LeftShiftRegister", 8, "InnerTerminal"),
     row(3201, "", True, 0, 320, "RightShiftRegister", 1, "OuterTerminal"), row(3202, "", False, 0, 320, "RightShiftRegister", 8, "InnerTerminal"),
     row(3211, "", False, 0, 321, "LeftShiftRegister", 1, "OuterTerminal"), row(3212, "", True, 0, 321, "LeftShiftRegister", 8, "InnerTerminal"),
     row(211, "", False, 0, 210, "LoopTunnel", 1, "OuterTerminal"), row(212, "", True, 30, 210, "LoopTunnel", 9, "InnerTerminal"),
     row(901, "", True, 0, 900, "DigitalNumericConstant", 1), row(951, "", True, 0, 950, "DigitalNumericConstant", 8)]


class FT(object):
    st = {"owners": {"8": ["WhileLoop", 300], "9": ["ForLoop", 200]}, "objs": [], "terminals": T,
          "loops": [{"class": "WhileLoop", "loop_uid": 300, "left_of": {"310": [311], "320": [321]}, "right_uids": [310, 320]},
                    {"class": "ForLoop", "loop_uid": 200, "left_of": {}, "right_uids": []}]}


LO = {310: 300, 311: 300, 320: 300, 321: 300}
rd = X.SimReader(FT())
ad = X.Addr(rd, FT.st["owners"])
try:
    k, _rs, _rd, i1 = X.connect_route(ad, T, 901, 3111, LO)
    e_, nt = rd.node_terms(i1["dst"][0], i1["dst"][1])
    gate("T1 const #900 -> L register #311 OUTER face = 'const_sr': loop #300 WhileLoop, face by uid echo, constant by its class listing",
         k == "const_sr" and i1["loop"] == 300 and i1["loop_cls"] == "WhileLoop" and e_ == 300 and nt[i1["dst_term"]]["uid"] == 3111
         and i1["const"]["const"] == 900 and "uid echo" in str(i1.get("dst_how")), i1)
    k2, _a, _b, i2 = X.connect_route(ad, T, 901, 3211, LO)
    gate("T2 a second register's L outer face (#3211) -> a DIFFERENT Terminals[] index of the same loop", k2 == "const_sr" and i2["dst_term"] != i1["dst_term"]
         and rd.node_terms(i2["dst"][0], i2["dst"][1])[1][i2["dst_term"]]["uid"] == 3211, (i1["dst_term"], i2["dst_term"]))
except X.ExecStop as e:
    gate("T1/T2 const -> L register outer face routes 'const_sr'", False, e)
for lab, s_, d_, lo, want in (("T3 NEGATIVE: a constant on the loop BODY (#8) -> the outer face (#1) is refused", 951, 3111, LO, None),
                              ("T4 NEGATIVE: const -> LoopTunnel outer sink still refused (unchanged route)", 901, 211, LO, "NO-VERB"),
                              ("T5 NEGATIVE: the register's loop unknown (loop_of empty) -> STOP", 901, 3111, {}, None)):
    try:
        X.connect_route(ad, T, s_, d_, lo)
        gate(lab, False, "routed")
    except X.ExecStop as e:
        gate(lab, want is None or want in str(e), str(e)[:160])


class StubS(object):
    work, calls = "W.vi", []

    def uid_index(self, cls, uid):
        return {("DigitalNumericConstant", 900): 4, ("WhileLoop", 300): 2}.get((cls, uid))

    def _op(self, verb, fn, detail=""):
        self.calls.append((verb, detail))
        return {"verb": verb, "err": "", "result": fn()}

    def junk_purge(self, tag):
        pass


class StubG(object):
    got = []

    def wire_const_sr(self, *a):
        self.got.append(a)
        return 1, ""


be = X.LVBackend.__new__(X.LVBackend)
be.addr, be.s, be.g = ad, StubS(), StubG()
try:
    out = X.LVBackend.connect(be, 901, 3111, T, LO, {})
    gate("T6 LVBackend.connect 'const_sr' -> gscript.wire_const_sr(work, DigitalNumericConstant, 4, WhileLoop, 2, face index)",
         StubG.got == [("W.vi", "DigitalNumericConstant", 4, "WhileLoop", 2, i1["dst_term"])] and out["how"][0] == "const_sr", (StubG.got, out))
except Exception as e:                                                                    # noqa: BLE001
    gate("T6 LVBackend.connect 'const_sr' -> gscript.wire_const_sr", False, "{0}: {1}".format(type(e).__name__, e))
try:
    k7 = X.connect_route(X.Addr(X.SimReader(FT()), FT.st["owners"]), T, 901, 3111, LO)[0]
    gate("T7 the simulated backend's reader routes the same row (connect_route is shared)", k7 == "const_sr", k7)
except X.ExecStop as e:
    gate("T7 simulated reader routes const_sr", False, e)
st = {"terminals": [dict(r) for r in T], "objs": [], "loops": FT.st["loops"], "owners": FT.st["owners"], "sym": {}, "diagrams": {}, "neg": 0}
try:
    eff, _x = SS.op_wire(st, {"src": {"uid": "900", "term_uid": 901},
                              "dst": {"uid": "311", "term": "outer"}}, {"same_diagram": True}, None, {})
    ws = [r["term_uid"] for r in st["terminals"] if r["wire_uid"] == eff["wire"]]
    gate("T8 stagesim op_wire: const -> L outer face on the same diagram = ONE new wire carrying exactly both ends", eff["how"] == "new" and sorted(ws) == [901, 3111], (eff, ws))
except Exception as e:                                                                    # noqa: BLE001
    gate("T8 stagesim op_wire const -> L outer face", False, "{0}: {1}".format(type(e).__name__, e))
src = open(os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8").read()
defs = dict((n.name, [a.arg for a in n.args.args]) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef))
gate("T9 gscript defines sr_init_const / wire_const_sr / loop_face_index with the documented arguments",
     defs.get("sr_init_const", [])[:6] == ["target", "loop_uid", "face_uid", "diagram_uid", "donor", "pos"]
     and defs.get("wire_const_sr", [])[:6] == ["target", "const_cls", "const_i", "loop_cls", "loop_i", "face_index"] and "loop_face_index" in defs,
     dict((k, defs.get(k)) for k in ("sr_init_const", "wire_const_sr", "loop_face_index")))
om = os.path.join(HERE, "opmodels", "sr_init_const.json")
if os.path.exists(om):
    m = SS.load_models().get("sr_init_const") or {}
    gate("T10 opmodels/sr_init_const.json loads with samples", isinstance(m.get("data"), dict) and (m["data"].get("samples") or []), m.get("path"))
else:
    print("  NOTE  T10 opmodels/sr_init_const.json not written yet (the LabVIEW scratch run writes it)", flush=True)
n_ok = sum(1 for _l, ok in G if ok)
print(P.result_line({"status": "PASS" if n_ok == len(G) else "FAIL", "gates": {"pass": n_ok, "fail": len(G) - n_ok},
                     "first_fail": next((l for l, ok in G if not ok), None), "artefacts": []}), flush=True)
sys.exit(0 if n_ok == len(G) else 1)
