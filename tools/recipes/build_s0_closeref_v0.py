r"""build_s0_closeref_v0.py - D1 stage S0: `Close Reference` restored in the two traverse ops, as NEW FILES.

  OpReport_v3.vi   -> OpReport_v4.vi        (the op behind gscript.count / gscript.report)
  OpWireSource_v5.vi -> OpWireSource_v6.vi  (the UID-addressed wire-source reader)

The OLD files are never opened for writing and never saved. Each stage SAVES its artefact and prints its md5
before the next stage starts (CLAUDE.md s3 "Big or blocked work is SPLIT into steps that each SAVE an
intermediate artefact"), so a later failure cannot take an earlier artefact with it.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "check what already exists"):
  * `tools/gscript.py:1479 copy_by_index()` is the fleet's PRIMITIVE COPIER (built-in primitives cannot be found
    by label or name - error 1054 x3). Nothing new is built here; this recipe only calls it.
  * `tools/recipes/build_opconstvalue_v1.py:169,199` is the worked example of copy_by_index + a `finish` hook
    that wires the copied node until the VI is runnable; its `lv_pid/com_preflight/fresh` helpers are reused
    (a copy_by_index session needs a restarted LabVIEW - `gscript.py:1501-1505`).
  * `tools/recipes/build_track_v6_core.py:77,84,98` supplies `must/walk/term`. No new helper.
  * `tools/recipes/build_opconnectfromwire_v0.py:423 wire_source_owner()` is the existing caller shape for
    OpWireSource (and records the caller bug: the op is UID-addressed, `UID 2` must be set). The local
    `ws_call()` below is that function with the op PATH as a parameter, so v5 and v6 can be compared.
  * `tools/bench/handle_audit.py` (2026-09-06) is the existing handle-measurement pattern; it measures no
    private bytes and does not touch these ops, which is why `tools/bench/s0_hygiene_probe.py` was written.
  * `docs/NAMES.md:741` gives `Traverse for GObjects.vi`'s exact terminal names, `References` among them.

MEASURED FACTS THIS BUILD RESTS ON (`tools/bench/s0_hygiene_probe.log`, `..._run2.log`, 2026-09-19 17:3x):
  * OpReport_v3 = 5 nodes: Function#43 'Open VI Reference', SubVI#124 'Traverse for GObjects.vi',
    IndexArray#167, Property#241, Property#482. ZERO close-ref-like nodes.
  * OpWireSource_v5 = 19 nodes, containing that SAME chain (#43/#124/#167/#241/#482). ZERO close-ref nodes.
  * OpReportAll_v0 = 5 nodes (Open VI Reference, Traverse, For Loop, 2 Property). ZERO close-ref nodes.
  * `KernelBuilder_v1.vi` HOLDS the donor: Function #157 'Close Reference' - the node `docs/REFERENCES.md:126`
    records as REMOVED from OpSubVI_v0.
  * BASELINE LEAK, measured on a scratch copy of the route-B original, OLD ops:
      20x count(Node)          handles 34134 -> 34349 (+215)   private 586.5 -> 613.7 MB (+27.2 MB)
      20x report_all(Diagram)  handles 34349 -> 34358 (+9)     private 613.7 -> 613.6 MB (-0.1 MB)
    The +215/+27 MB is dominated by the FIRST call, which loads the 473 KB VI and its dependency tree; the
    report_all window, taken with the VI already loaded, is FLAT. Hence the warm-up in `twenty()`.

WHAT IS AND IS NOT CLOSED HERE, and why (stated so a reviewer can attack it):
  * CLOSED: the `References` ARRAY that `Traverse for GObjects.vi` returns - the ~N-per-call reference class
    `docs/cycle27-plan.md:325-328` (Pre-decided 21b) names as the live cause of `error 2`.
  * NOT CLOSED: the VI refnum from `Open VI Reference` (1 per call). Closing it can let the target VI LEAVE
    MEMORY, and this project has already lost a whole chain build that way
    (`tools/gscript.py:1293-1295`: "closing a panel can let the VI leave memory - a whole chain build was lost
    that way on 2026-08-28"). Readers deliberately do NOT call `ensure_loaded`
    (`tools/gscript.py:1330-1333`), so on a target held in memory by nothing else a closed VI ref would
    discard unsaved scripted edits - i.e. the D1 working copy. That half is REPORTED as an OPEN item for a
    judgement session, not decided here.

PREDICTION CONTRACT - every line is a gate, printed PASS/FAIL; the first fatal FAIL stops that stage:
  G1  Each new file starts byte-identical to its source and reads ExecState 1.
  G2  copy_by_index adds exactly ONE node and it is Close Reference (expect_uid 157 guard).
  G3  `References` (Traverse source) wires into Close Reference's refnum sink as a BRANCH - read back
      non-zero and EQUAL on both ends. *** ALSO THE DISCRIMINATING TEST for "does Close Reference accept an
      ARRAY of refnums?": if it does not, G5 reads ExecState 0 and the stage STOPS and says so. ***
  G4  The LAST Property node's `error out` (identified from the machine: the PN whose error-out wire is the
      wire the panel's `error out` indicator carries) branches into Close Reference's error input, so the
      close runs AFTER the property reads. If that PN cannot be identified the stage STOPS - it never wires
      a close that might run BEFORE the reads.
  G5  ExecState is 1 after the wiring.
  G6  The saved file exists; its md5 is printed; the SOURCE op's md5 is unchanged; the new md5 differs.
  G7  EQUIVALENCE on a scratch copy of the route-B original: v4's count(Diagram/Node/Wire) and report() row 0
      equal v3's; v6's `ws_call` row equals v5's on the same wire uid.
  G8  PROOF: 20 consecutive calls of each op, handles and private bytes recorded per call, measured AFTER one
      warm-up call. Brief's criterion: handles flat within +-100.
Nothing branches on a result; every stage runs and every number is printed.

  py tools/bgrun.py --material --max-min 55 --log tools/bench/build_s0_closeref_v0.log -- py -u tools/recipes/build_s0_closeref_v0.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402

must, walk, term = B.must, B.walk, B.term

CD = g.CLAUDEDEV
OP_V3 = os.path.join(CD, "OpReport_v3.vi")
OP_V4 = os.path.join(CD, "OpReport_v4.vi")
WS_V5 = os.path.join(CD, "OpWireSource_v5.vi")
WS_V6 = os.path.join(CD, "OpWireSource_v6.vi")
WS_MAP = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_v5_labels.json")
DONOR = os.path.join(CD, "KernelBuilder_v1.vi")
CLOSEREF_UID = 157                      # measured, tools/bench/s0_hygiene_probe.log run 1
TRAVERSE_LABEL = "Traverse for GObjects.vi"
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(CD, f"SCRATCH_s0_{STAMP}.vi")

g._run.__defaults__ = (6.0, 120.0)
STATE = {}
RESULT = {}


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lv_pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return out or None


def mem():
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


def com_preflight(tries=15, gap=4.0):
    """Two spaced round-trips agreeing against an unchanged pid (build_opconstvalue_v1.py:57-76)."""
    probe = os.path.join(CD, "OpWhileCast_v0.vi")
    last = None
    for k in range(tries):
        try:
            p0 = lv_pid()
            n = g.count(probe, "Wire")
            time.sleep(gap)
            n2 = g.count(probe, "Wire")
            p1 = lv_pid()
            if n == n2 and p0 and p0 == p1:
                print(f"   COM preflight OK (pid {p0}, two round-trips agree: {n} wires)", flush=True)
                return True
            last = f"pid {p0}->{p1}, wires {n}->{n2}"
        except Exception as e:
            last = str(e)[:160]
        print(f"   COM preflight attempt {k + 1}/{tries}: {last}", flush=True)
        time.sleep(gap)
    raise B.Stop(f"COM preflight FAILED after {tries} attempts: {last}")


def fresh():
    print(f"   fresh(): killing LabVIEW pid {lv_pid()}", flush=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) "
                    "{ Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{LV_EXE}'"],
                   capture_output=True, text=True, timeout=60)
    time.sleep(35)
    g.OP_REPORT = OP_V3          # preflight must use a KNOWN-GOOD reader
    g.reset()
    com_preflight()
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def sinks(rows):
    return [r for r in rows if not r["is_source"]]


def pick(rows, want, source):
    """The terminal whose name matches `want` (exact, then substring), among sources or sinks. Names are exact
    bytes (CLAUDE.md), so what matched is printed and gated, never assumed."""
    w = want.strip().lower()
    for r in rows:
        if r["is_source"] == source and r["name"].strip().lower() == w:
            return r
    for r in rows:
        if r["is_source"] == source and w in r["name"].strip().lower():
            return r
    return None


# ---------------------------------------------------------------- the finish hook (runs on MOVE_DST)
def FINISH(dst):
    tag = STATE["tag"]
    w = walk(dst, 0)
    added = [u for u, v in w.items() if u not in STATE["before"]]
    print(f"   [{tag}] FINISH: added node uids {added}", flush=True)
    must(f"G2 {tag}: exactly ONE node added by the copy", len(added) == 1, str(added))
    cr = added[0]
    print(f"   [{tag}] Close Reference #{cr} terminals: "
          f"{[(r['i'], r['name'], r['is_source']) for r in w[cr][2]]}", flush=True)

    tv = next((u for u, v in w.items() if v[1] == TRAVERSE_LABEL), None)
    must(f"G2b {tag}: the Traverse node is present", tv is not None,
         str([(u, v[1]) for u, v in w.items()]))
    print(f"   [{tag}] Traverse #{tv} terminals: "
          f"{[(r['i'], r['name'], r['is_source'], r['wire']) for r in w[tv][2]]}", flush=True)

    refs_t = pick(w[tv][2], "References", True)
    must(f"G3a {tag}: the Traverse has a 'References' SOURCE terminal", refs_t is not None,
         str([r["name"] for r in w[tv][2] if r["is_source"]]))
    cr_in = None
    for cand in ("reference", "refnum", "ref"):
        cr_in = pick(w[cr][2], cand, False)
        if cr_in is not None:
            break
    if cr_in is None:
        cands = [r for r in sinks(w[cr][2]) if "error" not in r["name"].strip().lower()]
        cr_in = cands[0] if len(cands) == 1 else None
    must(f"G3b {tag}: Close Reference has a refnum SINK terminal", cr_in is not None,
         str([r["name"] for r in sinks(w[cr][2])]))
    print(f"   [{tag}] refnum input terminal = {cr_in['name']!r}", flush=True)

    fi = lambda cls, u: [o["uid"] for o in g.report_all(dst, cls)].index(u)
    g.wire(dst, "SubVI", fi("SubVI", tv), refs_t["name"], "Function", fi("Function", cr), cr_in["name"],
           branch=True)
    w = walk(dst, 0)
    a = term(w[tv][2], refs_t["name"], True)["wire"]
    b = term(w[cr][2], cr_in["name"], False)["wire"]
    must(f"G3 {tag}: References -> Close Reference on BOTH ends", a and a == b, f"{a}/{b}")
    print(f"   [{tag}] ExecState after the ARRAY wire: {g.exec_state(dst)}", flush=True)

    # --- G4: order the close AFTER every property read, by branching the LAST PN's error out into it.
    pns = [u for u, v in w.items() if v[1] == "Property Node"]
    pw = g.panel_wiring(dst)
    err_ind = next((r for r in pw if str(r.get("label", "")).strip().lower().startswith("error out")), None)
    print(f"   [{tag}] panel error-out indicator: {err_ind}", flush=True)
    last_pn = None
    if err_ind and err_ind.get("wire"):
        for u in pns:
            t = pick(w[u][2], "error out", True)
            if t and t["wire"] and t["wire"] == err_ind["wire"]:
                last_pn = u
                break
    must(f"G4a {tag}: the LAST Property node in the error chain was identified FROM THE MACHINE",
         last_pn is not None,
         f"pns={pns} err_ind={err_ind}")
    src_t = pick(w[last_pn][2], "error out", True)
    dst_t = pick(w[cr][2], "error in", False)
    must(f"G4b {tag}: both error terminals exist", src_t is not None and dst_t is not None,
         f"{src_t}/{dst_t}")
    g.wire(dst, "Property", fi("Property", last_pn), src_t["name"],
           "Function", fi("Function", cr), dst_t["name"], branch=True)
    w = walk(dst, 0)
    a = term(w[last_pn][2], src_t["name"], True)["wire"]
    b = term(w[cr][2], dst_t["name"], False)["wire"]
    must(f"G4 {tag}: PN#{last_pn}.error out -> Close Reference.error in on BOTH ends", a and a == b, f"{a}/{b}")

    es = g.exec_state(dst)
    print(f"   [{tag}] FINISH ExecState {es}", flush=True)
    must(f"G5 {tag}: repaired op RUNNABLE (ExecState 1) - Close Reference ACCEPTS the refnum ARRAY",
         es == 1, f"ExecState {es}")
    STATE["closeref_uid"] = cr


def repair(src, dst_path, tag):
    """One stage: fresh instance -> byte copy -> copy Close Reference in and wire it -> SAVED file + md5."""
    print(f"\n=== STAGE {tag}: {os.path.basename(src)} -> {os.path.basename(dst_path)} ===", flush=True)
    m_src = md5(src)
    print(f"  source md5 BEFORE {m_src}", flush=True)
    fresh()
    shutil.copy2(src, dst_path)
    must(f"G1a {tag}: the copy is byte-identical", md5(dst_path) == m_src, md5(dst_path))
    es = g.exec_state(dst_path)
    must(f"G1 {tag}: the copy is RUNNABLE before anything is changed", es == 1, f"ExecState {es}")

    fn_uids = [o["uid"] for o in g.report_all(DONOR, "Function")]
    must(f"G2c {tag}: the donor holds Close Reference #157", CLOSEREF_UID in fn_uids, str(fn_uids))
    i_cr = fn_uids.index(CLOSEREF_UID)
    STATE["tag"] = tag
    STATE["before"] = set(walk(dst_path, 0).keys())
    print(f"  donor Function index of #157 = {i_cr}; target nodes before = {len(STATE['before'])}", flush=True)
    g.copy_by_index(DONOR, "Function", i_cr, dst_path, expect_uid=CLOSEREF_UID, finish=FINISH)

    es = g.exec_state(dst_path)
    must(f"G6a {tag}: the SAVED file is runnable", es == 1, f"ExecState {es}")
    m_new = md5(dst_path)
    print(f"  SAVED {dst_path}", flush=True)
    print(f"  md5   {m_new}   ({os.path.getsize(dst_path)} B)", flush=True)
    must(f"G6b {tag}: the SOURCE op is UNTOUCHED", md5(src) == m_src, md5(src))
    must(f"G6c {tag}: the new file differs from its source", m_new != m_src, m_new)
    RESULT[tag] = {"path": dst_path, "md5": m_new, "bytes": os.path.getsize(dst_path)}
    return m_new


# ---------------------------------------------------------------- callers used for equivalence + the proof
def ws_call(op_path, target, wire_uid, idx=0):
    """`build_opconnectfromwire_v0.py:423 wire_source_owner()` with the op PATH as a parameter, so v5 and v6
    can be compared. UID-addressed: `uid_in` MUST be set (docs/toolkit-capabilities.md:48,:51)."""
    with open(WS_MAP, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(op_path)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(lab["uid_in"], int(wire_uid))
    vi.SetControlValue(lab["term_index"], int(idx))
    g._run(vi)
    return dict(is_source=bool(vi.GetControlValue(lab["is_source"])),
                owner_class=vi.GetControlValue(lab["ownercls"]),
                owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                recip=int(vi.GetControlValue(lab["recip_wire"])),
                err=g._err(vi, "error out") or "")


def twenty(label, call, warm=True):
    """20 consecutive calls of `call()`, measured AFTER one warm-up call.

    THE WARM-UP IS NOT COSMETIC. Measured (`tools/bench/s0_hygiene_probe_run2.log`, D vs E): the FIRST call on
    a not-yet-loaded target loads the 473 KB VI and its dependency tree, by itself +215 handles / +27 MB - so a
    window including call 0 measures the LOAD, not the per-call cost, and fails a +-100 gate on the UNREPAIRED
    op for a reason that has nothing to do with references. Both windows are printed; the gate uses the warmed
    one."""
    time.sleep(2)
    hraw, praw = mem()
    if warm:
        call()
        time.sleep(2)
    h0, p0 = mem()
    print(f"   {label} warm-up: handles {hraw} -> {h0} ({h0-hraw:+d}), "
          f"private {praw/1e6:.1f} -> {p0/1e6:.1f} MB  (the LOAD, excluded from the gate)", flush=True)
    rows, err = [], None
    for i in range(20):
        try:
            v = call()
        except Exception as e:
            err = (i, str(e)[:200])
            print(f"   {label} call {i:2d}: RAISED {str(e)[:160]}", flush=True)
            break
        h, pb = mem()
        rows.append((i, h, pb))
        print(f"   {label} call {i:2d}: {str(v)[:60]} handles={h} private={pb/1e6:.1f} MB", flush=True)
    time.sleep(2)
    h1, p1 = mem()
    print(f"   {label} TOTAL over {len(rows)} calls: handles {h0} -> {h1} ({h1-h0:+d})   "
          f"private {p0/1e6:.1f} -> {p1/1e6:.1f} MB ({(p1-p0)/1e6:+.1f} MB)", flush=True)
    return {"label": label, "h0": h0, "h1": h1, "p0": p0, "p1": p1, "n": len(rows), "err": err}


def main():
    t0 = time.time()
    print(f"=== D1 STAGE S0 - Close Reference restored  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    must("G0 the route-B original is the pinned one", md5(ORIGINAL) == ORIG_MD5, md5(ORIGINAL))

    # ---- stage A: OpReport_v4 -------------------------------------------------
    repair(OP_V3, OP_V4, "OpReport_v4")

    # ---- stage B: OpWireSource_v6 --------------------------------------------
    try:
        repair(WS_V5, WS_V6, "OpWireSource_v6")
    except B.Stop as e:
        print(f"  STAGE OpWireSource_v6 STOPPED at gate: {e}  "
              f"(OpReport_v4 is already SAVED and unaffected)", flush=True)
        # copy_by_index writes the target only at the END of its protocol, so a FINISH that raises leaves
        # OpWireSource_v6.vi as the byte-identical COPY of v5. Removing it stops the proof section from
        # measuring v5 twice and reporting it as the repaired op.
        if "OpWireSource_v6" not in RESULT and os.path.exists(WS_V6):
            try:
                os.remove(WS_V6)
                print("  removed the unrepaired OpWireSource_v6.vi stub", flush=True)
            except Exception as ex:
                print(f"  could not remove the v6 stub: {ex}", flush=True)

    # ---- equivalence + the 20-call proof -------------------------------------
    print("\n=== PROOF: equivalence, then 20 consecutive calls of each op ===", flush=True)
    fresh()
    shutil.copy2(ORIGINAL, SCRATCH)
    must("G7a scratch is byte-identical to the original", md5(SCRATCH) == ORIG_MD5, os.path.basename(SCRATCH))

    eq = {}
    for path, tag in ((OP_V3, "v3"), (OP_V4, "v4")):
        g.OP_REPORT = path
        g._cache.pop(path, None)                 # cache key is the raw path string (gscript.py:210-215)
        eq[tag] = {c: g.count(SCRATCH, c) for c in ("Diagram", "Node", "Wire")}
        eq[tag + "_row0"] = g.report(SCRATCH, "Diagram")[0]
        print(f"   {tag}: {eq[tag]}   row0 {eq[tag + '_row0']}", flush=True)
    must("G7 OpReport_v4 counts EQUAL OpReport_v3 counts", eq["v3"] == eq["v4"], f"{eq['v3']} vs {eq['v4']}")
    must("G7b OpReport_v4 report() row 0 equals v3's", eq["v3_row0"] == eq["v4_row0"],
         f"{eq['v3_row0']} vs {eq['v4_row0']}")

    g.OP_REPORT = OP_V3
    wire_uid = g.report_all(SCRATCH, "Wire")[0]["uid"]
    print(f"   equivalence wire uid for OpWireSource = {wire_uid}", flush=True)
    ws_eq = {}
    for path, tag in ((WS_V5, "v5"), (WS_V6, "v6")):
        if not os.path.exists(path):
            print(f"   {tag}: {os.path.basename(path)} not on disk - skipped", flush=True)
            continue
        g._cache.pop(path, None)
        try:
            ws_eq[tag] = ws_call(path, SCRATCH, wire_uid, 0)
        except Exception as e:
            ws_eq[tag] = {"exc": str(e)[:160]}
        print(f"   {tag}: {ws_eq[tag]}", flush=True)
    if "v5" in ws_eq and "v6" in ws_eq:
        must("G7c OpWireSource_v6 returns the SAME row as v5", ws_eq["v5"] == ws_eq["v6"],
             f"{ws_eq['v5']} vs {ws_eq['v6']}")

    proof = {}
    g.OP_REPORT = OP_V3
    fresh()
    g.OP_REPORT = OP_V3
    proof["v3"] = twenty("OLD OpReport_v3", lambda: g.count(SCRATCH, "Node"))
    fresh()
    g.OP_REPORT = OP_V4
    g._cache.pop(OP_V4, None)
    proof["v4"] = twenty("NEW OpReport_v4", lambda: g.count(SCRATCH, "Node"))
    g.OP_REPORT = OP_V3

    fresh()
    proof["ws5"] = twenty("OLD OpWireSource_v5", lambda: ws_call(WS_V5, SCRATCH, wire_uid, 0))
    if os.path.exists(WS_V6):
        fresh()
        proof["ws6"] = twenty("NEW OpWireSource_v6", lambda: ws_call(WS_V6, SCRATCH, wire_uid, 0))

    # ---- verdict -------------------------------------------------------------
    print("\n=== VERDICT ===", flush=True)
    for k, r in proof.items():
        print(f"  {r['label']:<24} {r['n']:2d} calls  handles {r['h0']} -> {r['h1']} ({r['h1']-r['h0']:+d})   "
              f"private {(r['p1']-r['p0'])/1e6:+.1f} MB   err={r['err']}", flush=True)
    for tag, r in RESULT.items():
        print(f"  SAVED {tag}: {r['path']}  md5 {r['md5']}  {r['bytes']} B", flush=True)

    must("G8 NEW OpReport_v4: 20 consecutive calls leave the handle count flat within +-100",
         abs(proof["v4"]["h1"] - proof["v4"]["h0"]) <= 100,
         f"delta {proof['v4']['h1']-proof['v4']['h0']:+d}")
    must("G8b NEW OpReport_v4: all 20 calls completed without error", proof["v4"]["err"] is None,
         str(proof["v4"]["err"]))
    if "ws6" in proof:
        must("G8c NEW OpWireSource_v6: 20 consecutive calls leave the handle count flat within +-100",
             abs(proof["ws6"]["h1"] - proof["ws6"]["h0"]) <= 100,
             f"delta {proof['ws6']['h1']-proof['ws6']['h0']:+d}")
        must("G8d NEW OpWireSource_v6: all 20 calls completed without error", proof["ws6"]["err"] is None,
             str(proof["ws6"]["err"]))

    try:
        os.remove(SCRATCH)
        print(f"  deleted {os.path.basename(SCRATCH)}", flush=True)
    except Exception as e:
        print(f"  could not delete scratch: {e}", flush=True)
    must("G9 the route-B original md5 is unchanged", md5(ORIGINAL) == ORIG_MD5, md5(ORIGINAL))
    print(f"\n({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except B.Stop as e:
        print(f"\nSTOPPED at gate: {e}", flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        npass = sum(1 for _n, ok in B.PASS if ok)
        nfail = sum(1 for _n, ok in B.PASS if not ok)
        print(f"\nGATES: {npass} PASS / {nfail} FAIL", flush=True)
        if nfail:
            print("failing: " + ", ".join(n for n, ok in B.PASS if not ok), flush=True)
        for tag, r in RESULT.items():
            print(f"ARTEFACT {tag}: {r['path']}  md5 {r['md5']}", flush=True)
    sys.exit(0 if (rc == 0 and not any(not ok for _n, ok in B.PASS)) else 1)
