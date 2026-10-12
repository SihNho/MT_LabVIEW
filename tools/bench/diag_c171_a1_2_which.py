# ---
# labview: none
# hardware: none
# ---
r"""diag_c171_a1_2_which - card 171-a1-2 step 1a (throwaway diagnosis, OFFLINE: stage_prerun dry, COM stubbed, --no-record).
EXISTING checked first: selftest_c134_1_dry.py builds T1's bytes (reconstructed 133-3 recipe) inline at import (not importable
without running the whole suite), so the same reconstruction is called here through its own text: the T1 block is exec'd up to
its write, nothing else (no copy of its logic). stage_prerun's _name_step / _gate_reads_tainted_name are wrapped (not edited).
    py -u tools/bench/diag_c171_a1_2_which.py t1      -> the reconstructed 133-3 bytes
    py -u tools/bench/diag_c171_a1_2_which.py p170    -> tools/recipes/stage_replay_swap.py --plan 170
PREDICTION: t1 - FR (and the gates after it) report NAME-TAINT rows naming the names + binding lines; p170 - A2 reads c0 bound
at stage_replay_swap.py:39 (L.census). Each NAME-TAINT row: gate label, ok, statement taint, names, binding line, value kind.
"""
import os, sys, tempfile                                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
os.chdir(ROOT)
import protocol as P                                                                # noqa: E402

mode = sys.argv[1] if len(sys.argv) > 1 else "t1"
if mode == "t1":
    src = open(os.path.join(HERE, "selftest_c134_1_dry.py"), encoding="utf-8").read()
    head = src.split('gate("T0 the 133-3 FR rule bytes')[0]           # imports, helpers, the reconstruction of b
    ns = {"__file__": os.path.join(HERE, "selftest_c134_1_dry.py"), "__name__": "c134_part"}
    exec(compile(head, "selftest_c134_1_dry.py(head)", "exec"), ns)
    recipe = os.path.join(tempfile.mkdtemp(prefix="c171_which_"), "stage_d1_ring_p3b2a_ababd4ed.py")
    open(recipe, "wb").write(ns["b"])
    print("FACT  T1 bytes:", ns["how"], "->", recipe, flush=True)
    argv = ["--dry", recipe, "--no-record"]
else:
    recipe = os.path.join(ROOT, "tools", "recipes", "stage_replay_swap.py")
    argv = ["--dry", recipe, "--no-record", "--plan", "170"]

sys.argv = ["stage_prerun.py"] + argv
import stage_prerun as SP                                                           # noqa: E402

BIND = {}            # (frame id, name) -> (file:lines of the binding unit, value kind)
ROWS = []


def kind(v, depth=0):
    if isinstance(v, SP.Fake):
        return "Fake"
    if depth < 2 and isinstance(v, dict):
        ks = set(kind(x, depth + 1) for x in list(v.values())[:50])
        return "dict[{0}]{1}".format(len(v), "(has Fake)" if any("Fake" in k for k in ks) else "")
    if depth < 2 and isinstance(v, (list, tuple, set, frozenset)):
        ks = set(kind(x, depth + 1) for x in list(v)[:50])
        return "{0}[{1}]{2}".format(type(v).__name__, len(v), "(has Fake)" if any("Fake" in k for k in ks) else "")
    return type(v).__name__


orig_step, orig_reads = SP._name_step, SP._gate_reads_tainted_name
FAKE = [0]                     # taint moved by a Fake (COM-stub value) use; the rest of D.taint = static-graph reads after mutation
orig_t = SP.Fake._t


def _t(self):
    FAKE[0] += 1
    return orig_t(self)


SP.Fake._t = _t
F0 = {}                        # frame id -> (unit key, FAKE at unit start, D.taint at unit start)


def step(frame, event):
    st = SP.D.frames.get(id(frame))
    before = set(st["tainted"]) if st is not None and st["frame"] is frame else set()
    prev = st["unit"] if st is not None and st["frame"] is frame else None
    f0 = F0.get(id(frame))
    orig_step(frame, event)
    st = SP.D.frames.get(id(frame))
    if st is None or event != "line":
        return
    if f0 is None or st["unit"][0] != f0[0] or prev is None:
        F0[id(frame)] = (st["unit"][0], FAKE[0], SP.D.taint)
    if prev is None or f0 is None:
        return
    for n in st["tainted"] - before:
        units = SP._line_units(frame.f_code.co_filename)
        lines = sorted(ln for ln, u in units.items() if u[0] == prev[0])
        df, dt = FAKE[0] - f0[1], SP.D.taint - f0[2]
        BIND[(id(frame), n)] = ("{0}:{1}".format(os.path.basename(frame.f_code.co_filename), lines[:1] + lines[-1:]),
                                kind(frame.f_locals.get(n, "<unbound>")), "taint +{0} (Fake +{1}, graph-after-mutation +{2})".format(
                                    dt, df, dt - df))


def reads():
    got = orig_reads()
    gf = sys._getframe(1)                          # Stage.gate wrapper frame: label, ok, tainted (statement taint)
    lab, ok, t = gf.f_locals.get("label"), gf.f_locals.get("ok"), gf.f_locals.get("tainted")
    f = gf
    while f is not None and not (SP.D.frames.get(id(f)) and SP.D.frames[id(f)]["frame"] is f):
        f = f.f_back
    where = "{0}:{1}".format(os.path.basename(f.f_code.co_filename), f.f_lineno) if f is not None else "?"
    if got:
        names = dict((n, BIND.get((id(f), n), ("?", "?"))) for n in sorted(got))
        ROWS.append((lab, ok, t, where, names))
        print("  NAME-TAINT  gate={0!r} ok={1} stmt_taint={2} at {3} names={4}".format(str(lab)[:70], ok, t, where, names),
              flush=True)
    return got


SP._name_step, SP._gate_reads_tainted_name = step, reads
try:
    SP.main(argv)
except SystemExit:
    pass
flip = [r for r in ROWS if not r[1] and not r[2]]          # FALSE gates the name taint alone relabelled
print("FACT  name-tainted gates {0}; FALSE gates relabelled by the name taint alone: {1}".format(
    len(ROWS), [(str(r[0])[:40], r[3], r[4]) for r in flip]), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
