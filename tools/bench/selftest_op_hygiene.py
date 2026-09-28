r"""selftest_op_hygiene.py - card 117-3 D4/D6: gscript.op() refuses a NEW op VI with no PASS op-hygiene/1 record.
OFFLINE: pythoncom / win32com are replaced in sys.modules by fakes BEFORE gscript is loaded, their Dispatch RAISES, and
gscript._lv is a fake Application whose GetVIReference only records the path - no LabVIEW process, no COM call (gate G0
checks both counters). Writes only a tempfile.mkdtemp sandbox (removed at exit).
FOUND FIRST: gscript.op (the one op-VI open path in gscript; vi_ref opens TARGETS), tools/bench/op_hygiene/OpWireJoints_v1.json
(the first record, card 117-1), selftest_c116a_landed.py (sandbox pattern).
PREDICTION CONTRACT
  H1 new op, no record -> OpHygieneRefused naming the op and the record path; GetVIReference not called
  H2 same op + PASS record with the file md5 -> reference returned
  H3 record md5 != file md5 -> refused;  H3b admitted op whose FILE then changes -> refused on the next (cached) call
  H4 status FAIL / errors 1 / schema x -> refused (3 gates)
  H5 old op (mtime <= install time), no record -> allowed (grandfathered)
  H6 OpWireJoints_v1 (real file, real record) allowed even with the install time moved before its mtime
  H7 hygiene_probe(op) admits that op only: another new op inside the probe refused; the op refused again after it
  H8 no environment bypass: op_hygiene_check / op / hygiene_probe source has no `environ`
  H9 regression: every Op*.vi in claudeDev is admitted at the real install time (no existing caller changes)
  G0 fake Dispatch called 0 times
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_op_hygiene.log -- py -u tools/bench/selftest_op_hygiene.py
"""
import atexit, hashlib, importlib, inspect, json, os, shutil, sys, tempfile, time, types
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "tools")]
import protocol as P  # noqa: E402

DISPATCH = []


def _no_com(*a, **k):
    DISPATCH.append(a); raise RuntimeError("selftest: COM Dispatch is forbidden offline")


sys.modules["pythoncom"] = types.ModuleType("pythoncom")
w32, cl, dyn = types.ModuleType("win32com"), types.ModuleType("win32com.client"), types.ModuleType("win32com.client.dynamic")
dyn.Dispatch = _no_com; cl.dynamic = dyn; w32.client = cl                                      # noqa: E702
sys.modules.update({"win32com": w32, "win32com.client": cl, "win32com.client.dynamic": dyn})
g = importlib.import_module("gscript")


class FakeApp:
    def __init__(self): self.calls = []
    def GetVIReference(self, path, *a): self.calls.append(path); return ("REF", path)   # noqa: E301,E704


APP = FakeApp(); g._lv = APP
G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-74s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:220]), flush=True)


def call(path):
    try:
        return g.op(path), None
    except g.OpHygieneRefused as e:
        return None, str(e)


T = tempfile.mkdtemp(prefix="op_hygiene_"); atexit.register(shutil.rmtree, T, True)
REC = os.path.join(T, "op_hygiene"); os.makedirs(REC)
REAL_DIR, REAL_SINCE = g.OP_HYGIENE_DIR, g.OP_HYGIENE_SINCE
g.OP_HYGIENE_DIR, g.OP_HYGIENE_SINCE = REC, time.time() - 3600


def vi(name, data, old=False):
    p = os.path.join(T, name + ".vi"); open(p, "wb").write(data)
    if old: os.utime(p, (g.OP_HYGIENE_SINCE - 100, g.OP_HYGIENE_SINCE - 100))   # noqa: E701
    return p


def record(name, path, **kw):
    r = dict(schema="op-hygiene/1", op=name, md5=hashlib.md5(open(path, "rb").read()).hexdigest(), status="PASS", errors=0)
    r.update(kw); json.dump(r, open(os.path.join(REC, name + ".json"), "w"))


def fresh():
    g._cache.clear(); g._hygiene_ok.clear()


NEW = vi("OpFakeNew_v0", b"new op bytes")
n0 = len(APP.calls); ref, err = call(NEW)
gate(ref is None and err and "OpFakeNew_v0" in err and os.path.join(REC, "OpFakeNew_v0.json") in err and len(APP.calls) == n0,
     "H1 new op, no record -> refused, names op + record path, no GetVIReference", err)
record("OpFakeNew_v0", NEW); fresh(); ref, err = call(NEW)
gate(ref == ("REF", NEW) and err is None, "H2 PASS record with matching md5 -> allowed", (ref, err))
record("OpFakeNew_v0", NEW, md5="0" * 32); fresh(); ref, err = call(NEW)
gate(err and "record md5" in err, "H3 record md5 != file md5 -> refused", err)
record("OpFakeNew_v0", NEW); fresh(); call(NEW); open(NEW, "wb").write(b"new op bytes, edited after the record")
ref, err = call(NEW)
gate(err and "record md5" in err and NEW in g._cache, "H3b file changed after admission -> refused on the cached call", err)
record("OpFakeNew_v0", NEW)
for lab, kw, want in (("status FAIL", dict(status="FAIL"), "status"), ("errors 1", dict(errors=1), "errors"),
                      ("schema x", dict(schema="x"), "schema")):
    record("OpFakeNew_v0", NEW, **kw); fresh(); ref, err = call(NEW)
    gate(err and want in err, "H4 %s -> refused" % lab, err)
OLD = vi("OpFakeOld_v0", b"old op", old=True); fresh(); ref, err = call(OLD)
gate(ref == ("REF", OLD), "H5 old op without record -> allowed (grandfathered)", (ref, err))
V1 = os.path.join(g.CLAUDEDEV, "OpWireJoints_v1.vi"); g.OP_HYGIENE_DIR = REAL_DIR
g.OP_HYGIENE_SINCE = os.path.getmtime(V1) - 60; fresh(); ref, err = call(V1)
gate(ref == ("REF", V1), "H6 OpWireJoints_v1 on its real record, install time before its mtime -> allowed", err)
g.OP_HYGIENE_DIR, g.OP_HYGIENE_SINCE = REC, time.time() - 3600
os.remove(os.path.join(REC, "OpFakeNew_v0.json")); OTHER = vi("OpFakeOther_v0", b"another new op"); fresh()
with g.hygiene_probe(NEW):
    ra, ea = call(NEW); rb, eb = call(OTHER)
rc, ec = call(NEW)
gate(ra == ("REF", NEW) and eb and ec, "H7 probe admits its op only; other op refused inside, op refused after", (ea, eb, ec))
src = "".join(inspect.getsource(f) for f in (g.op_hygiene_check, g.op, g.hygiene_probe))
gate("environ" not in src, "H8 no environment-variable bypass in the gate's source")
g.OP_HYGIENE_DIR, g.OP_HYGIENE_SINCE = REAL_DIR, REAL_SINCE; fresh()
vis = [os.path.join(g.CLAUDEDEV, f) for f in os.listdir(g.CLAUDEDEV) if f.lower().endswith(".vi") and f.startswith("Op")]
refused = [os.path.basename(p) for p in vis if g.op_hygiene_check(p)]
gate(not refused, "H9 all %d claudeDev Op*.vi admitted at the real install time %s" % (
    len(vis), time.strftime("%Y-%m-%d %H:%M", time.localtime(REAL_SINCE))), refused)
gate(not DISPATCH, "G0 COM Dispatch never called", len(DISPATCH))
npass = sum(1 for x in G if x[0]); nfail = len(G) - npass
print(P.result_line(P.make_result(npass, nfail, next((x[1] for x in G if not x[0]), None))), flush=True)
sys.exit(0 if nfail == 0 else 1)
