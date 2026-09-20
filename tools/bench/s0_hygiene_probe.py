"""s0_hygiene_probe.py - D1 stage S0, PHASE 1: measure the leak and read the ops before repairing anything.

WHY THIS SCRIPT EXISTS, and what already exists (CLAUDE.md "check what already exists"):
  - `tools/bench/handle_audit.py` (2026-09-06) already measures LabVIEW's KERNEL handle count across phases
    A-F. It is the pattern this file follows for `handles()`. It does NOT measure private bytes and it does
    not touch the traverse ops' internals, so it does not answer S0.
  - `tools/bench/bench_prep.py:64 labview_handles()` / `:74 restart_labview()` are reused, not rewritten.
  - `tools/gscript.py:233 ref_counts()` is IN-PROCESS only and its own docstring (`:227-228`, `:236-239`)
    records that the kernel handle count "cannot see VI Server refnums at all" and that these counters
    "CANNOT see refnum-class exhaustion inside an op VI". That is the reason this probe measures PRIVATE
    BYTES as well as handles: `docs/cycle27-plan.md:321-324` (item 21a) names private bytes as the meter for
    `error 2` and calls the handle-count argument a category error.
  - No existing script makes N consecutive traverse calls and records memory per call. That is the gap.

PREDICTION CONTRACT (machine-checkable; every line is printed as GATE PASS/FAIL):
  P1  The op census reads: `OpReport_v3.vi`, `OpWireSource_v5.vi` and `OpReportAll_v0.vi` each contain ZERO
      node whose class or label matches /close.?ref/i.  (If one already closes its refs, the S0 premise is
      wrong and this probe says so.)
  P2  `KernelBuilder_v1.vi` (the ancestor `docs/REFERENCES.md:126` says the Close Reference was removed FROM)
      contains at least ONE such node - i.e. a donor for the repair exists on disk.
  P3  20 consecutive `count(target,'Node')` calls on a scratch copy of the route-B original leave the KERNEL
      HANDLE count within +-100 of its pre-loop value.  Expected to PASS even though the op leaks, because
      VI Server refnums are not kernel handles - this is the brief's stated criterion and this line measures
      whether it can discriminate at all.
  P4  The same 20 calls grow LabVIEW's PRIVATE BYTES by more than 20 MB (monotone-ish).  This is the leak
      claim of `docs/cycle27-plan.md:325-328` (item 21b): ~626 GObject refs leaked per call.
  P5  20 consecutive `report_all(target,'Diagram')` calls complete WITHOUT error 2.
Nothing in this script branches on a result; every phase runs and every number is printed.

Run:  py tools/bgrun.py --material --max-min 30 --log tools/bench/s0_hygiene_probe.log -- py -u tools/bench/s0_hygiene_probe.py
Read-only on every original (rule 1): the only file written is a uniquely-named scratch COPY under
claudeDev, deleted at the end of the same run.

================================================================================================
S0-b MODE (`--s0b`), ADDED 2026-09-19 (cycle 45, act 3) — THIS FILE IS **EXTENDED**, NOT REPLACED
================================================================================================
`docs/cycle27-plan.md` Pre-decided 27 orders S0-b to run next and its prior-art finding B2 orders it to
EXTEND this probe (`:451`) rather than author a fresh one; precedent for extending a bench script with a
second mode is `tools/bench/handle_audit.py:69-70`. What already exists and is REUSED verbatim here:
`mem()` (handles + private bytes), `md5()`, `gate()`, `bench_prep.restart_labview()`, and phases D/E's
"N consecutive traverses, meters per call" shape. **Only the MUTATION INTERLEAVE is new** — phases D and E
are pure traverse loops, and Pre-decided 27 asks for a BUILD-SHAPED workload (traverses INTERLEAVED with
mutations, S3w-like).

WHAT IS PROFILED: the UNREPAIRED ops, exactly as they sit on disk, all three of them —
  `OpReport_v3.vi`     driven by `gscript.count()`      (`tools/gscript.py:1005-1006`, OP_REPORT)
  `OpReportAll_v0.vi`  driven by `gscript.report_all()` (`tools/gscript.py:488-498`, OP_REPORT_ALL)
  `OpWireSource_v5.vi` driven directly, UID-addressed, with the control labels recorded in
                       `tools/bench/opwiresource_v5_labels.json` (`docs/toolkit-capabilities.md:60`: the
                       op is UID-addressed, so `UID 2` must be set or index 0 is already past the end;
                       `build_opwiresource_v5.read_terminal:161` hard-codes the ORIGINAL as `vi path`,
                       which is why this mode sets `vi path` itself)
and the mutation is `gscript.build_property()` (`tools/gscript.py:2188-2228`), whose own docstring records
("632A800", False) + "VI Server:GObject" as the VERIFIED combination (2026-09-06). Each mutation carries two
further traverses inside the wrapper (`uids()` before, `new_since()` after), which is the build's real shape.

S0-b PREDICTION CONTRACT (printed before the workload runs; every line is a machine-checkable GATE):
  Q0  All three op VIs and the route-B original are byte-identical BEFORE and AFTER (rule 1: the ops are
      READ, never written; the only file written is the run-stamped claudeDev scratch copy).
  Q1  The interleave completes >= 20 iterations of (count -> report_all -> wire-source -> build_property).
  G-A No `error 2` (LabVIEW "Memory is full", NI KB kA00Z0000019KhWSAU) is raised by ANY call.
  G-B Kernel handle count flat within +-100, COUNTED FROM CALL 1 — call 0 is the ~473 KB VI load
      (`tools/bench/s0_hygiene_probe_run2.log:75`, `:95`), not a traverse.
  G-C LabVIEW private-byte drift <= 5 MB over the same call-1..call-N window. Both meters or neither:
      the kernel handle count is blind to VI Server refnums (`tools/gscript.py:227-228`).
This step is PURE MEASUREMENT — Pre-decided 25's S0-b row says "no outcome of it fails this step". A failing
G gate is a reported number, not a broken run; nothing here branches on a result.
Artefact: `tools/bench/s0b_refleak_profile.json` (md5 printed in the log).

Run:  py tools/bgrun.py --material --max-min 30 --log tools/bench/s0b_refleak_profile.log \
          -- py -u tools/bench/s0_hygiene_probe.py --s0b

================================================================================================
S0-b-MUT MODE (`--s0bmut`), ADDED 2026-09-19 (cycle 45, act 4) — THE THIRD ARM, SAME FILE AGAIN
================================================================================================
`docs/cycle27-plan.md` Pre-decided 28 (judgement, cycle 45) rules that S0-b's `+34.6 MB` is
UNATTRIBUTED, because the build-shaped interleave both TRAVERSES and MUTATES (20 Property nodes
created, node count 626 -> 645). G-C asks whether OUR TRAVERSE OPS leak, so the growth must be
subtracted. This mode is the discriminating arm it orders: "The same 20-call loop, same scratch
copy, same meters, with the `count`/`report_all` traverses REMOVED and the `build_property`
mutations kept" (`docs/cycle27-plan.md:567-570`). Prior art B2 again applies - this file is
EXTENDED, not replaced; `mem()`, `md5()`, `gate()`, `_op_md5s()`, `bench_prep.restart_labview()`
and the whole s0b phase skeleton are reused verbatim, and NOTHING of the `--s0b` path is edited
(its log and its artefact `s0b_refleak_profile.json` md5 b3ddf21f... stay exactly as they are; this
mode writes a SEPARATE artefact).

WHAT IS REMOVED, EXACTLY — the three EXPLICIT op legs of the `--s0b` interleave:
  1. `g.count(SCRATCH, "Node")`             -> OpReport_v3.vi      (626 matched objects per call)
  2. `g.report_all(SCRATCH, "Diagram")`     -> OpReportAll_v0.vi   (170 matched objects per call)
  3. the UID-addressed `OpWireSource_v5.vi` run
WHAT IS KEPT, UNCHANGED: `g.build_property(SCRATCH, "VI Server:GObject", [("632A800", False)],
(60, 60 + 24*i), diagram_index=0)` - the same call, same coordinates, same diagram, 20 times.
⚠️ **This arm is NOT traverse-free, and must not be reported as such.** `gscript.build_property`
calls `uids(target,"Property")` before and `new_since(...)` after (`tools/gscript.py:2196`, `:2225`),
and `uids` IS `report_all` (`tools/gscript.py:1017-1021`). Those two Property traverses run in BOTH
arms, identically, so they cancel: the difference between this arm and `--s0b` is exactly the three
legs listed above. That is what makes the subtraction valid, and it is why "mutate-only" here means
"the s0b workload minus its explicit traverse legs", not "no traverse at all".
Call 0 (the VI load) is taken with `g.ensure_loaded()` instead of a `count()`, so that the load
itself contributes no explicit traverse; as in `--s0b` it is EXCLUDED from both meters.

S0-b-MUT PREDICTION CONTRACT (printed before the workload runs; every line a machine-checkable GATE):
  M0  All three op VIs and the route-B original are byte-identical BEFORE and AFTER (rule 1).
  M1  The loop completes >= 20 `build_property` mutations on the run-stamped scratch copy.
  G-A No `error 2` ("Memory is full") is raised by ANY call.
  G-B Kernel handle count flat within +-100, COUNTED FROM CALL 1 (call 0 = the VI load).
  G-C LabVIEW private-byte drift <= 5 MB over the same call-1..call-N window.
Pure measurement; nothing branches on a result. The log ends with the THREE-ARM TABLE:
  traverse-only   -0.1 MB  (on file: `tools/bench/s0_hygiene_probe_run2.log:121-123`)
  traverse+mutate +34.6 MB (on file: `tools/bench/s0b_refleak_profile.log:61-64`)
  mutate-only     measured here
and the classification Pre-decided 28 pre-decided: within 5 MB of +34.6 => traverses contribute ~0,
G-C MET on traverse-attributable drift; <= 5 MB total => the traverses carry it, G-C genuinely FAILS;
anything between => OPEN for judgement. The classification is PRINTED, never acted on by this script.
Artefact: `tools/bench/s0b_mutonly_profile.json` (md5 printed in the log).

Run:  py tools/bgrun.py --material --max-min 30 --log tools/bench/s0b_mutonly_profile.log \
          -- py -u tools/bench/s0_hygiene_probe.py --s0bmut
"""
import os
import re
import shutil
import subprocess
import sys
import time
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import bench_prep  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
# The route-B original sits ONE LEVEL ABOVE the project root - `tools/recipes/build_d1_routeb_v7.py:387`
# spells it `os.path.join(os.path.dirname(ROOT), ...)`. Run 1 of this probe used ROOT and died FileNotFoundError.
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CD = g.CLAUDEDEV
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(CD, f"SCRATCH_s0probe_{STAMP}.vi")

CLOSE_RE = re.compile(r"close.?ref", re.I)

_P = _F = 0


def gate(label, ok, detail=""):
    global _P, _F
    if ok:
        _P += 1
        print(f"  PASS {label}  {detail}", flush=True)
    else:
        _F += 1
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print(f"  FAIL {label}  {detail}", flush=True)
    return ok


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def mem():
    """(handles, private_bytes) of the LabVIEW process, or (0, 0)."""
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$p=Get-Process LabVIEW -ErrorAction SilentlyContinue|Select-Object -First 1;"
         "if($p){\"{0} {1}\" -f $p.HandleCount,$p.PrivateMemorySize64}else{'0 0'}"],
        capture_output=True, text=True)
    try:
        a, b = r.stdout.strip().split()
        return int(a), int(b)
    except Exception:
        return 0, 0


def census(path):
    """[(class, label)] for every Node on the top diagram of a small op VI, plus the node count."""
    rows = g.report_all(path, "Node")
    try:
        labs = {r["uid"]: r["label"] for r in g.node_labels(path, 0, strict=False)[0]}
    except Exception as e:
        print(f"    node_labels({os.path.basename(path)}) raised: {e}", flush=True)
        labs = {}
    return [(r["class"], labs.get(r["uid"], ""), r["uid"]) for r in rows]


def main():
    t0 = time.time()
    print(f"=== S0 HYGIENE PROBE  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)

    # ---- A. fresh instance -------------------------------------------------
    print("\n[A] restart LabVIEW for a clean baseline (standing authority, CLAUDE.md s3)", flush=True)
    bench_prep.restart_labview()
    g.reset()
    time.sleep(5)
    h0, p0 = mem()
    print(f"A baseline: handles {h0}  private {p0/1e6:.1f} MB", flush=True)
    gate("A0 LabVIEW is up", h0 > 0, f"handles={h0}")

    # ---- B. op census ------------------------------------------------------
    print("\n[B] census of the traverse ops and the donor", flush=True)
    targets = ["OpReport_v3.vi", "OpWireSource_v5.vi", "OpReportAll_v0.vi",
               "KernelBuilder_v1.vi", "OpSubVI_v0.vi"]
    found = {}
    for name in targets:
        p = os.path.join(CD, name)
        if not os.path.exists(p):
            print(f"  {name}: MISSING on disk", flush=True)
            found[name] = None
            continue
        try:
            rows = census(p)
        except Exception as e:
            print(f"  {name}: census raised: {e}", flush=True)
            found[name] = None
            continue
        closers = [r for r in rows if CLOSE_RE.search(r[0] or "") or CLOSE_RE.search(r[1] or "")]
        found[name] = closers
        print(f"  {name}: {len(rows)} nodes, {len(closers)} close-ref-like", flush=True)
        for c, l, u in rows:
            print(f"      #{u:<7} {c:<24} {l!r}", flush=True)

    for name in ("OpReport_v3.vi", "OpWireSource_v5.vi", "OpReportAll_v0.vi"):
        gate(f"P1 {name} has NO Close Reference",
             found.get(name) is not None and len(found[name]) == 0,
             f"{found.get(name)}")
    gate("P2 KernelBuilder_v1.vi HAS a Close Reference donor node",
         bool(found.get("KernelBuilder_v1.vi")), f"{found.get('KernelBuilder_v1.vi')}")

    # ---- C. scratch copy ---------------------------------------------------
    print("\n[C] scratch copy of the route-B original", flush=True)
    m0 = md5(ORIGINAL)
    gate("C0 original md5 before", m0 == ORIG_MD5, m0)
    shutil.copy2(ORIGINAL, SCRATCH)
    gate("C1 scratch is byte-identical", md5(SCRATCH) == ORIG_MD5, os.path.basename(SCRATCH))

    # ---- D. 20 consecutive count(Node) -------------------------------------
    print("\n[D] 20 consecutive count(target,'Node') - the brief's 20-call test, OLD ops", flush=True)
    hA, pA = mem()
    series = []
    err_at = None
    n_nodes = None
    for i in range(20):
        try:
            n = g.count(SCRATCH, "Node")
            n_nodes = n
        except Exception as e:
            err_at = (i, str(e)[:200])
            print(f"  call {i:2d}: RAISED {str(e)[:160]}", flush=True)
            break
        h, pb = mem()
        series.append((i, n, h, pb))
        print(f"  call {i:2d}: nodes={n} handles={h} private={pb/1e6:.1f} MB", flush=True)
    hB, pB = mem()
    print(f"D total: handles {hA} -> {hB} ({hB-hA:+d})   private {pA/1e6:.1f} -> {pB/1e6:.1f} MB "
          f"({(pB-pA)/1e6:+.1f} MB)  over {len(series)} calls", flush=True)
    gate("P3 kernel handle count flat within +-100 over 20 count(Node) calls",
         abs(hB - hA) <= 100, f"delta {hB-hA:+d}")
    gate("P4 private bytes grew > 20 MB over 20 count(Node) calls",
         (pB - pA) > 20e6, f"delta {(pB-pA)/1e6:+.1f} MB, matched objects/call = {n_nodes}")
    gate("D-noerr the 20 count calls all completed", err_at is None, f"{err_at}")

    # ---- E. 20 consecutive report_all(Diagram) -----------------------------
    print("\n[E] 20 consecutive report_all(target,'Diagram') - OLD ops", flush=True)
    hC, pC = mem()
    err_e = None
    for i in range(20):
        try:
            rows = g.report_all(SCRATCH, "Diagram")
        except Exception as e:
            err_e = (i, str(e)[:200])
            print(f"  call {i:2d}: RAISED {str(e)[:160]}", flush=True)
            break
        h, pb = mem()
        print(f"  call {i:2d}: diagrams={len(rows)} handles={h} private={pb/1e6:.1f} MB", flush=True)
    hD, pD = mem()
    print(f"E total: handles {hC} -> {hD} ({hD-hC:+d})   private {pC/1e6:.1f} -> {pD/1e6:.1f} MB "
          f"({(pD-pC)/1e6:+.1f} MB)", flush=True)
    gate("P5 20 report_all(Diagram) calls without error 2", err_e is None, f"{err_e}")
    gate("E-handles flat within +-100", abs(hD - hC) <= 100, f"delta {hD-hC:+d}")

    # ---- F. cleanup + original intact --------------------------------------
    print("\n[F] cleanup", flush=True)
    try:
        g.reset()
    except Exception:
        pass
    try:
        os.remove(SCRATCH)
        print(f"  deleted {os.path.basename(SCRATCH)}", flush=True)
    except Exception as e:
        print(f"  could not delete scratch: {e}", flush=True)
    gate("F0 original md5 AFTER is unchanged", md5(ORIGINAL) == ORIG_MD5, md5(ORIGINAL))

    hE, pE = mem()
    print(f"\nEND: handles {h0} -> {hE}   private {p0/1e6:.1f} -> {pE/1e6:.1f} MB", flush=True)
    print(f"GATES: {_P} PASS / {_F} FAIL   ({time.time()-t0:.0f}s)", flush=True)
    return 0 if _F == 0 else 1


# =====================================================================================================
# S0-b : the UNREPAIRED ops under a BUILD-SHAPED workload.  Added 2026-09-19 (cycle 45, act 3).
# =====================================================================================================
ERR2_RE = re.compile(r"error\s*2\b|Memory is full", re.I)
PROFILE_JSON = os.path.join(HERE, "s0b_refleak_profile.json")
WS_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
OP_NAMES = ("OpReport_v3.vi", "OpWireSource_v5.vi", "OpReportAll_v0.vi")
S0B_SCRATCH = os.path.join(CD, f"SCRATCH_s0b_{STAMP}.vi")
N_ITER = 20


def _op_md5s():
    out = {}
    for n in OP_NAMES:
        p = os.path.join(CD, n)
        out[n] = md5(p) if os.path.exists(p) else None
    return out


def main_s0b():
    import json
    t0 = time.time()
    err2 = []          # every call whose error text looks like LabVIEW's "Memory is full"
    print(f"=== S0-b  BUILD-SHAPED PROFILE OF THE UNREPAIRED OPS  {time.strftime('%Y-%m-%d %H:%M:%S')} ===",
          flush=True)
    try:                                   # the prediction contract, printed BEFORE the workload runs
        print("S0-b PREDICTION CONTRACT"
              + __doc__.split("S0-b PREDICTION CONTRACT")[1].split("Artefact:")[0].rstrip(), flush=True)
    except Exception:                                        # noqa: BLE001 - a print must never stop a run
        print("S0-b PREDICTION CONTRACT: see this file's module docstring", flush=True)
    print(f"  N_ITER={N_ITER}  scratch={os.path.basename(S0B_SCRATCH)}", flush=True)

    # ---- A. fresh instance ------------------------------------------------------------------
    print("\n[A] restart LabVIEW for a clean baseline (standing authority, CLAUDE.md s3)", flush=True)
    bench_prep.restart_labview()
    g.reset()
    time.sleep(5)
    h0, p0 = mem()
    print(f"A baseline: handles {h0}  private {p0/1e6:.1f} MB", flush=True)
    gate("A0 LabVIEW is up", h0 > 0, f"handles={h0}")

    # ---- B. rule-1 md5 gate, BEFORE ---------------------------------------------------------
    print("\n[B] md5 of the three op VIs and the original, BEFORE the workload", flush=True)
    before = _op_md5s()
    for n, m in before.items():
        print(f"  {n}: {m}", flush=True)
    gate("B0 all three op VIs are on disk", all(v is not None for v in before.values()), f"{before}")
    om0 = md5(ORIGINAL)
    print(f"  ORIGINAL: {om0}", flush=True)
    gate("B1 original md5 before", om0 == ORIG_MD5, om0)

    # ---- C. scratch copy --------------------------------------------------------------------
    print("\n[C] run-stamped scratch copy under claudeDev (the ONLY file written)", flush=True)
    shutil.copy2(ORIGINAL, S0B_SCRATCH)
    gate("C0 scratch is byte-identical to the original", md5(S0B_SCRATCH) == ORIG_MD5,
         os.path.basename(S0B_SCRATCH))

    # ---- D. call 0 = the VI LOAD, excluded from both meters by Pre-decided 27 ---------------
    print("\n[D] call 0 : the VI load (EXCLUDED from G-B/G-C - s0_hygiene_probe_run2.log:75,:95)", flush=True)
    calls = []
    load_err = ""
    try:
        n0 = g.count(S0B_SCRATCH, "Node")
    except Exception as e:                                   # noqa: BLE001 - recorded, never branched on
        n0, load_err = None, str(e)[:200]
        if ERR2_RE.search(load_err):
            err2.append(("call0/count", load_err))
    h_load, p_load = mem()
    print(f"  call 0: nodes={n0} handles={h_load} private={p_load/1e6:.1f} MB  {load_err[:80]}", flush=True)
    calls.append({"i": 0, "phase": "load", "nodes": n0, "handles": h_load,
                  "private_bytes": p_load, "err": load_err})

    # wire uid for the OpWireSource_v5 leg, and the op's control labels
    wire_uid = None
    try:
        wrows = g.report_all(S0B_SCRATCH, "Wire")
        wire_uid = int(wrows[0]["uid"]) if wrows else None
        print(f"  wire-source leg will address wire #{wire_uid} ({len(wrows)} wires on the VI)", flush=True)
    except Exception as e:                                   # noqa: BLE001
        t = str(e)[:200]
        print(f"  could not pick a wire uid: {t}", flush=True)
        if ERR2_RE.search(t):
            err2.append(("setup/report_all(Wire)", t))
    ws_labels = None
    if os.path.exists(WS_LABELS):
        with open(WS_LABELS, "r", encoding="utf-8") as f:
            ws_labels = json.load(f)
    gate("D0 OpWireSource_v5 is drivable (labels + a wire uid)",
         bool(ws_labels) and wire_uid is not None, f"labels={bool(ws_labels)} wire={wire_uid}")

    # ---- E. THE INTERLEAVE ------------------------------------------------------------------
    print(f"\n[E] {N_ITER} iterations of  count(Node) -> report_all(Diagram) -> OpWireSource_v5 -> "
          f"build_property   (S3w-like: traverses INTERLEAVED with mutations)", flush=True)
    for i in range(1, N_ITER + 1):
        rec = {"i": i, "phase": "interleave"}
        # 1. OpReport_v3
        try:
            rec["count_nodes"] = g.count(S0B_SCRATCH, "Node")
        except Exception as e:                               # noqa: BLE001
            rec["count_err"] = str(e)[:200]
            if ERR2_RE.search(rec["count_err"]):
                err2.append((f"iter{i}/count", rec["count_err"]))
        # 2. OpReportAll_v0
        try:
            rec["diagrams"] = len(g.report_all(S0B_SCRATCH, "Diagram"))
        except Exception as e:                               # noqa: BLE001
            rec["report_all_err"] = str(e)[:200]
            if ERR2_RE.search(rec["report_all_err"]):
                err2.append((f"iter{i}/report_all", rec["report_all_err"]))
        # 3. OpWireSource_v5, UID-addressed (docs/toolkit-capabilities.md:60)
        if ws_labels and wire_uid is not None:
            try:
                vi = g.op(os.path.join(CD, "OpWireSource_v5.vi"))
                vi.SetControlValue("vi path", S0B_SCRATCH)
                vi.SetControlValue(ws_labels["uid_in"], wire_uid)
                vi.SetControlValue(ws_labels["term_index"], 0)
                g._run(vi)
                rec["ws_owner"] = str(vi.GetControlValue(ws_labels["ownercls"]))
                rec["ws_owner_uid"] = int(vi.GetControlValue(ws_labels["owner_uid"]))
                rec["ws_err"] = g._err(vi, "error out") or ""
            except Exception as e:                           # noqa: BLE001
                rec["ws_err"] = str(e)[:200]
            if ERR2_RE.search(rec.get("ws_err") or ""):
                err2.append((f"iter{i}/wiresource", rec["ws_err"]))
        # 4. THE MUTATION - a Property node created on the scratch copy's top diagram
        try:
            new = g.build_property(S0B_SCRATCH, "VI Server:GObject", [("632A800", False)],
                                   (60, 60 + 24 * i), diagram_index=0)
            rec["mutation_uid"] = int(new[0]["uid"]) if new else None
        except Exception as e:                               # noqa: BLE001
            rec["mutation_err"] = str(e)[:200]
            if ERR2_RE.search(rec["mutation_err"]):
                err2.append((f"iter{i}/build_property", rec["mutation_err"]))
        h, pb = mem()
        rec["handles"], rec["private_bytes"] = h, pb
        calls.append(rec)
        print(f"  iter {i:2d}: nodes={rec.get('count_nodes')} diagrams={rec.get('diagrams')} "
              f"wsOwner={rec.get('ws_owner','-')!r:.20} newProp=#{rec.get('mutation_uid')} "
              f"handles={h} private={pb/1e6:.1f} MB "
              f"{'ERR:' + str(rec.get('count_err') or rec.get('report_all_err') or rec.get('mutation_err') or rec.get('ws_err') or '')[:70] if (rec.get('count_err') or rec.get('report_all_err') or rec.get('mutation_err') or (rec.get('ws_err') or '')) else ''}",
              flush=True)

    done = [c for c in calls if c["phase"] == "interleave"]
    gate("Q1 the interleave completed >= 20 iterations", len(done) >= 20, f"{len(done)} iterations")

    # ---- F. THE THREE G GATES ---------------------------------------------------------------
    print("\n[F] the ONE S0 acceptance criterion (docs/cycle27-plan.md:453-457, :540)", flush=True)
    if done:
        h1, p1 = done[0]["handles"], done[0]["private_bytes"]
        hN, pN = done[-1]["handles"], done[-1]["private_bytes"]
    else:
        h1 = p1 = hN = pN = 0
    dh, dp = hN - h1, (pN - p1) / 1e6
    print(f"  call 0 (VI load)      : handles {h_load}  private {p_load/1e6:.1f} MB", flush=True)
    print(f"  call 1  -> call {len(done):2d}  : handles {h1} -> {hN} ({dh:+d})   "
          f"private {p1/1e6:.1f} -> {pN/1e6:.1f} MB ({dp:+.1f} MB)", flush=True)
    ga = gate("G-A no error 2 raised by any call", not err2, f"{err2[:2] if err2 else 'none'}")
    gb = gate("G-B kernel handles flat +-100 counted FROM CALL 1", abs(dh) <= 100, f"delta {dh:+d}")
    gc = gate("G-C LabVIEW private-byte drift <= 5 MB from call 1", abs(dp) <= 5.0, f"delta {dp:+.1f} MB")

    # ---- G. artefact ------------------------------------------------------------------------
    after = _op_md5s()
    om1 = md5(ORIGINAL)
    profile = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "what": "S0-b: the UNREPAIRED traverse ops under a build-shaped workload "
                "(traverses INTERLEAVED with mutations), docs/cycle27-plan.md Pre-decided 27",
        "ops_profiled": {"OpReport_v3.vi": "gscript.count(Node)",
                         "OpReportAll_v0.vi": "gscript.report_all(Diagram)",
                         "OpWireSource_v5.vi": "driven directly, UID-addressed"},
        "mutation": "gscript.build_property('VI Server:GObject', [('632A800', False)]) on the scratch copy",
        "target": os.path.basename(S0B_SCRATCH), "original_md5": om1,
        "op_md5_before": before, "op_md5_after": after,
        "iterations": len(done), "wire_uid": wire_uid,
        "baseline_call0": {"handles": h_load, "private_bytes": p_load},
        "window": {"from_call": 1, "to_call": len(done),
                   "handles": [h1, hN], "handle_delta": dh,
                   "private_bytes": [p1, pN], "private_delta_mb": round(dp, 3)},
        "gates": {"G_A_no_error2": bool(ga), "G_B_handles_flat_100": bool(gb),
                  "G_C_private_drift_le_5MB": bool(gc)},
        "error2_hits": err2,
        "calls": calls,
    }
    with open(PROFILE_JSON, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=1, default=str)
    pm = md5(PROFILE_JSON)
    print(f"\n[G] artefact: {os.path.relpath(PROFILE_JSON, ROOT)}  md5 {pm}  "
          f"{os.path.getsize(PROFILE_JSON)} B", flush=True)
    gate("G0 the profile artefact exists and is non-empty", os.path.getsize(PROFILE_JSON) > 0, pm)

    # ---- H. cleanup + rule-1 md5 gate, AFTER -------------------------------------------------
    print("\n[H] cleanup and the rule-1 md5 gate, AFTER", flush=True)
    try:
        g.reset()
    except Exception:                                        # noqa: BLE001
        pass
    try:
        os.remove(S0B_SCRATCH)
        print(f"  deleted {os.path.basename(S0B_SCRATCH)}", flush=True)
    except Exception as e:                                   # noqa: BLE001
        print(f"  could not delete scratch: {e}", flush=True)
    for n in OP_NAMES:
        gate(f"Q0 {n} md5 UNCHANGED", before.get(n) is not None and before[n] == after.get(n),
             f"{before.get(n)} -> {after.get(n)}")
    gate("Q0 original md5 UNCHANGED", om1 == ORIG_MD5, om1)

    hE, pE = mem()
    print(f"\nrefs: {g.ref_counts()}", flush=True)
    print(f"END: handles {h0} -> {hE}   private {p0/1e6:.1f} -> {pE/1e6:.1f} MB", flush=True)
    print(f"VERDICT  G-A={'PASS' if ga else 'FAIL'}  G-B={'PASS' if gb else 'FAIL'} (delta {dh:+d} handles)  "
          f"G-C={'PASS' if gc else 'FAIL'} (delta {dp:+.1f} MB)", flush=True)
    print(f"GATES: {_P} PASS / {_F} FAIL   ({time.time()-t0:.0f}s)", flush=True)
    return 0 if _F == 0 else 1


# =====================================================================================================
# S0-b-MUT : the MUTATION-ONLY arm.  Added 2026-09-19 (cycle 45, act 4), docs/cycle27-plan.md Pre-dec 28.
# =====================================================================================================
MUT_JSON = os.path.join(HERE, "s0b_mutonly_profile.json")
S0BM_SCRATCH = os.path.join(CD, f"SCRATCH_s0bm_{STAMP}.vi")
ARM_TRAVERSE_ONLY_MB = -0.1      # tools/bench/s0_hygiene_probe_run2.log:121-123 (20 x report_all(Diagram))
ARM_TRAV_PLUS_MUT_MB = 34.6      # tools/bench/s0b_refleak_profile.log:61-64     (the --s0b interleave)


def main_s0b_mut():
    import json
    t0 = time.time()
    err2 = []
    print(f"=== S0-b-MUT  MUTATION-ONLY ARM  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    try:                                   # the prediction contract, printed BEFORE the workload runs
        print("S0-b-MUT PREDICTION CONTRACT"
              + __doc__.split("S0-b-MUT PREDICTION CONTRACT")[1].split("Artefact:")[0].rstrip(), flush=True)
    except Exception:                                        # noqa: BLE001 - a print must never stop a run
        print("S0-b-MUT PREDICTION CONTRACT: see this file's module docstring", flush=True)
    print(f"  N_ITER={N_ITER}  scratch={os.path.basename(S0BM_SCRATCH)}  artefact="
          f"{os.path.basename(MUT_JSON)}", flush=True)

    # ---- A. fresh instance ------------------------------------------------------------------
    print("\n[A] restart LabVIEW for a clean baseline (standing authority, CLAUDE.md s3)", flush=True)
    bench_prep.restart_labview()
    g.reset()
    time.sleep(5)
    h0, p0 = mem()
    print(f"A baseline: handles {h0}  private {p0/1e6:.1f} MB", flush=True)
    gate("A0 LabVIEW is up", h0 > 0, f"handles={h0}")

    # ---- B. rule-1 md5 gate, BEFORE ---------------------------------------------------------
    print("\n[B] md5 of the three op VIs and the original, BEFORE the workload", flush=True)
    before = _op_md5s()
    for n, m in before.items():
        print(f"  {n}: {m}", flush=True)
    gate("B0 all three op VIs are on disk", all(v is not None for v in before.values()), f"{before}")
    om0 = md5(ORIGINAL)
    print(f"  ORIGINAL: {om0}", flush=True)
    gate("B1 original md5 before", om0 == ORIG_MD5, om0)

    # ---- C. scratch copy --------------------------------------------------------------------
    print("\n[C] run-stamped scratch copy under claudeDev (the ONLY file written)", flush=True)
    shutil.copy2(ORIGINAL, S0BM_SCRATCH)
    gate("C0 scratch is byte-identical to the original", md5(S0BM_SCRATCH) == ORIG_MD5,
         os.path.basename(S0BM_SCRATCH))

    # ---- D. call 0 = the VI LOAD, excluded from both meters (as in --s0b) -------------------
    print("\n[D] call 0 : the VI load via ensure_loaded() - NO explicit traverse, EXCLUDED from G-B/G-C",
          flush=True)
    calls = []
    load_err = ""
    try:
        g.ensure_loaded(S0BM_SCRATCH)
    except Exception as e:                                   # noqa: BLE001 - recorded, never branched on
        load_err = str(e)[:200]
        if ERR2_RE.search(load_err):
            err2.append(("call0/ensure_loaded", load_err))
    h_load, p_load = mem()
    print(f"  call 0: handles={h_load} private={p_load/1e6:.1f} MB  {load_err[:80]}", flush=True)
    calls.append({"i": 0, "phase": "load", "handles": h_load,
                  "private_bytes": p_load, "err": load_err})
    gate("D0 the VI loaded without raising", not load_err, load_err or "clean")

    # ---- E. THE MUTATION-ONLY LOOP ----------------------------------------------------------
    print(f"\n[E] {N_ITER} iterations of  build_property  ONLY  (the --s0b legs count(Node), "
          f"report_all(Diagram) and OpWireSource_v5 are REMOVED; the wrapper's own two "
          f"report_all(Property) calls remain, identically to --s0b)", flush=True)
    for i in range(1, N_ITER + 1):
        rec = {"i": i, "phase": "mutate_only"}
        try:
            new = g.build_property(S0BM_SCRATCH, "VI Server:GObject", [("632A800", False)],
                                   (60, 60 + 24 * i), diagram_index=0)
            rec["mutation_uid"] = int(new[0]["uid"]) if new else None
        except Exception as e:                               # noqa: BLE001
            rec["mutation_err"] = str(e)[:200]
            if ERR2_RE.search(rec["mutation_err"]):
                err2.append((f"iter{i}/build_property", rec["mutation_err"]))
        h, pb = mem()
        rec["handles"], rec["private_bytes"] = h, pb
        calls.append(rec)
        print(f"  iter {i:2d}: newProp=#{rec.get('mutation_uid')} handles={h} "
              f"private={pb/1e6:.1f} MB "
              f"{'ERR:' + str(rec.get('mutation_err'))[:70] if rec.get('mutation_err') else ''}",
              flush=True)

    done = [c for c in calls if c["phase"] == "mutate_only"]
    made = [c for c in done if c.get("mutation_uid")]
    gate("M1 the loop completed >= 20 build_property mutations", len(made) >= 20,
         f"{len(made)} created / {len(done)} iterations")

    # ---- F. THE THREE G GATES ---------------------------------------------------------------
    print("\n[F] the ONE S0 acceptance criterion (docs/cycle27-plan.md:453-457, :540)", flush=True)
    if done:
        h1, p1 = done[0]["handles"], done[0]["private_bytes"]
        hN, pN = done[-1]["handles"], done[-1]["private_bytes"]
    else:
        h1 = p1 = hN = pN = 0
    dh, dp = hN - h1, (pN - p1) / 1e6
    print(f"  call 0 (VI load)      : handles {h_load}  private {p_load/1e6:.1f} MB", flush=True)
    print(f"  call 1  -> call {len(done):2d}  : handles {h1} -> {hN} ({dh:+d})   "
          f"private {p1/1e6:.1f} -> {pN/1e6:.1f} MB ({dp:+.1f} MB)", flush=True)
    ga = gate("G-A no error 2 raised by any call", not err2, f"{err2[:2] if err2 else 'none'}")
    gb = gate("G-B kernel handles flat +-100 counted FROM CALL 1", abs(dh) <= 100, f"delta {dh:+d}")
    gc = gate("G-C LabVIEW private-byte drift <= 5 MB from call 1", abs(dp) <= 5.0, f"delta {dp:+.1f} MB")

    # ---- G. the THREE-ARM TABLE and the pre-decided classification --------------------------
    print("\n[G] THREE ARMS (docs/cycle27-plan.md Pre-decided 28)", flush=True)
    print(f"  traverse-only    private {ARM_TRAVERSE_ONLY_MB:+.1f} MB   "
          f"(on file: tools/bench/s0_hygiene_probe_run2.log:121-123)", flush=True)
    print(f"  traverse+mutate  private {ARM_TRAV_PLUS_MUT_MB:+.1f} MB   "
          f"(on file: tools/bench/s0b_refleak_profile.log:61-64)", flush=True)
    print(f"  mutate-only      private {dp:+.1f} MB   (MEASURED HERE)", flush=True)
    if abs(dp - ARM_TRAV_PLUS_MUT_MB) <= 5.0:
        verdict = ("BRANCH-A  mutate-only accounts for the drift (within 5 MB of +34.6): the traverses "
                   "contribute ~0, G-C is MET on traverse-attributable drift")
    elif abs(dp) <= 5.0:
        verdict = ("BRANCH-B  mutate-only is ~0: the traverses carry the drift, G-C genuinely FAILS")
    else:
        verdict = (f"BRANCH-OPEN  neither arm cleanly accounts for the drift ({dp:+.1f} MB vs "
                   f"{ARM_TRAV_PLUS_MUT_MB:+.1f} MB) - judgement, not a material call")
    print(f"  CLASSIFICATION: {verdict}", flush=True)

    # ---- H. artefact ------------------------------------------------------------------------
    after = _op_md5s()
    om1 = md5(ORIGINAL)
    profile = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "what": "S0-b MUTATION-ONLY arm: the same 20-call loop as --s0b with the explicit traverse legs "
                "(count(Node), report_all(Diagram), OpWireSource_v5) REMOVED and build_property kept. "
                "docs/cycle27-plan.md Pre-decided 28.",
        "removed_vs_s0b": ["gscript.count(Node) -> OpReport_v3.vi",
                           "gscript.report_all(Diagram) -> OpReportAll_v0.vi",
                           "OpWireSource_v5.vi UID-addressed run"],
        "kept": "gscript.build_property('VI Server:GObject', [('632A800', False)]) x N, which itself "
                "runs report_all(Property) twice per call in BOTH arms (gscript.py:2195,:2225,:1017-1021)",
        "target": os.path.basename(S0BM_SCRATCH), "original_md5": om1,
        "op_md5_before": before, "op_md5_after": after,
        "iterations": len(done), "mutations_created": len(made),
        "baseline_call0": {"handles": h_load, "private_bytes": p_load},
        "window": {"from_call": 1, "to_call": len(done),
                   "handles": [h1, hN], "handle_delta": dh,
                   "private_bytes": [p1, pN], "private_delta_mb": round(dp, 3)},
        "gates": {"G_A_no_error2": bool(ga), "G_B_handles_flat_100": bool(gb),
                  "G_C_private_drift_le_5MB": bool(gc)},
        "three_arms_private_delta_mb": {"traverse_only": ARM_TRAVERSE_ONLY_MB,
                                        "traverse_plus_mutate": ARM_TRAV_PLUS_MUT_MB,
                                        "mutate_only": round(dp, 3)},
        "classification": verdict,
        "error2_hits": err2,
        "calls": calls,
    }
    with open(MUT_JSON, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=1, default=str)
    pm = md5(MUT_JSON)
    print(f"\n[H] artefact: {os.path.relpath(MUT_JSON, ROOT)}  md5 {pm}  "
          f"{os.path.getsize(MUT_JSON)} B", flush=True)
    gate("H0 the profile artefact exists and is non-empty", os.path.getsize(MUT_JSON) > 0, pm)

    # ---- I. cleanup + rule-1 md5 gate, AFTER ------------------------------------------------
    print("\n[I] cleanup and the rule-1 md5 gate, AFTER", flush=True)
    try:
        g.reset()
    except Exception:                                        # noqa: BLE001
        pass
    try:
        os.remove(S0BM_SCRATCH)
        print(f"  deleted {os.path.basename(S0BM_SCRATCH)}", flush=True)
    except Exception as e:                                   # noqa: BLE001
        print(f"  could not delete scratch: {e}", flush=True)
    for n in OP_NAMES:
        gate(f"M0 {n} md5 UNCHANGED", before.get(n) is not None and before[n] == after.get(n),
             f"{before.get(n)} -> {after.get(n)}")
    gate("M0 original md5 UNCHANGED", om1 == ORIG_MD5, om1)

    hE, pE = mem()
    print(f"\nrefs: {g.ref_counts()}", flush=True)
    print(f"END: handles {h0} -> {hE}   private {p0/1e6:.1f} -> {pE/1e6:.1f} MB", flush=True)
    print(f"VERDICT  G-A={'PASS' if ga else 'FAIL'}  G-B={'PASS' if gb else 'FAIL'} (delta {dh:+d} handles)  "
          f"G-C={'PASS' if gc else 'FAIL'} (delta {dp:+.1f} MB)", flush=True)
    print(f"GATES: {_P} PASS / {_F} FAIL   ({time.time()-t0:.0f}s)", flush=True)
    return 0 if _F == 0 else 1


if __name__ == "__main__":
    if "--s0bmut" in sys.argv:
        sys.exit(main_s0b_mut())
    sys.exit(main_s0b() if "--s0b" in sys.argv else main())
