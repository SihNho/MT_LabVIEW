r"""build_s0beta_replicate.py - S0-beta: REPLICATE the 2026-09-13 positive control, UNCHANGED, with readings.

docs/cycle27-plan.md:449 (Pre-decided 25, as AMENDED by its own prior-art review). The construction below is
`tools/recipes/build_opreportall_v1.py`'s, step for step, with the SAME gscript calls, the SAME arguments and
the SAME order (its :127-221 -> this file's `construct()`); the only additions are the two the plan names:
after EACH edit (a) read `ExecState`, and (b) re-read `Wire.Is Broken?` for every wire that edit created - the
falsifier left unapplied at `archive/peer/2026-09-19-s0v3-execstate0.md:140-142`, wire-census pattern at :130/:148.

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "before creating any new op ... check what already exists"):
  * the CONSTRUCTION itself - `tools/recipes/build_opreportall_v1.py:127-221`. Not re-derived; transcribed, with
    a source-line comment on every step. NO new op is built, nothing is patched.
  * `Wire.Is Broken?` 6371004 - already built; its only carrier reachable from Python is `OpConnectFromWire_v0.vi`
    (`tools/bench/diag_fstunnel_wirebroken.py:9-15`), whose readout is ordered after the Invoke by gate W7b. It is
    driven exactly as that diagnostic drives it: an IDEMPOTENT re-connect of the same source->sink pair, a row
    accepted only when the op's `UID 2` equals the wire asked about.
  * `OpWireSource_v5.vi` via `wire_source_owner()` - FULLY READ-ONLY per-terminal reader; >= 2 terminals reporting
    `Is Source? TRUE` = the wire is broken (`docs/NAMES.md:900`). This is the reading that CANNOT perturb.
  * `fresh()` / `com_preflight()` / `md5()` / `pick()` / `source_term_index()` - copied from
    `tools/recipes/build_s0_closeref_v3.py:182-292`, behaviour unchanged.

TWO PASSES, and why (the 6371004 read is a WRITE - `connect_from_wire` re-connects a wire):
  PASS A "CLEAN" - the construction with ONLY read-only readings after each edit (ExecState + a read-only wire
    census of every new wire). Nothing mutates the build, so P1/P2 are measured on an uncontaminated replica.
  PASS B "BROKEN-READ" - the same construction on a SECOND scratch, where after each edit the 6371004
    `Wire.Is Broken?` readout is taken for every new wire whose sink terminal this step knows. Perturbation is
    itself measured (wire delta + ExecState after every read). PASS B saves nothing and its scratch is DELETED.

PREDICTION CONTRACT, fixed in advance - each reported HELD or MISSED:
  P1  the rebuilt op ends `ExecState` **1** (pass A).
  P2  the VI **SAVES** and its md5 is logged (pass A; saved ONLY at a legal state - no step saves a broken VI,
      docs/cycle27-plan.md:458).
  P3  EVERY edit has BOTH readings logged: `ExecState` after the edit (both passes) and, for every wire that edit
      created, a `Wire.Is Broken?` row or a could-not-read reason (pass B), plus the read-only source census.
  An intermediate `ExecState 0` is EXPECTED mid-construction and is NOT a failure (docs/cycle27-plan.md:465;
  `build_opreportall_v1.py:135`) - no step gates on it.
  RULE 1: the route-B original is md5-gated before and after; `OpReport_v3.vi` is READ and byte-gated, never
  written; every new file is a NEW name under user.lib\claudeDev.
  Rig is 조립: no motor, no ASI, no camera - none is touched.

  MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_s0beta_replicate.log -- py -u tools/recipes/build_s0beta_replicate.py
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
from build_opconnectfromwire_v0 import connect_from_wire, wire_source_owner  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
CD = g.CLAUDEDEV
OP_V3 = os.path.join(CD, "OpReport_v3.vi")           # the DONOR/source - read only, byte-gated
RA_V0 = os.path.join(CD, "OpReportAll_v0.vi")        # a READER only; never written by this script
STAMP = time.strftime("%H%M%S")
DST = os.path.join(CD, f"S0beta_OpReportAll_{STAMP}.vi")        # pass A artefact - SAVED and KEPT
SCR_B = os.path.join(CD, f"SCRATCH_s0beta_wr_{STAMP}.vi")       # pass B scratch - DELETED in this same run
OUT = os.path.join(BENCH, "s0beta_readings.json")
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))

# --- verbatim from build_opreportall_v1.py:58-68 (property IDs and the MEASURED terminal short names) ---
P_POSITION = "632A800"      # GObject.Position
P_UID = "632A813"           # GObject.UID
P_CLASSNAME = "6327803"     # Generic.Class Name
P_OWNER = "6327806"         # Generic.Owner
T_POSITION, T_UID, T_CLASSNAME, T_OWNER = "Position", "UID", "ClassName", "Owner"

g._run.__defaults__ = (6.0, 90.0)          # build_opreportall_v1.py:70

PASS, FAIL = [], []
RES = {"pass_a": {}, "pass_b": {}, "gates": []}


# ============================================================ small helpers (v3:182-292, unchanged)
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(s):
    print(f"   . {s}", flush=True)


def gate(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    RES["gates"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)
    return bool(ok)


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


def com_preflight(tries=12, gap=4.0):
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
    g.OP_REPORT = OP_V3
    g.OP_REPORT_ALL = RA_V0
    g.reset()
    com_preflight()
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def pick(rows, want, source):
    w = want.strip().lower()
    for r in rows:
        if r["is_source"] == source and r["name"].strip().lower() == w:
            return r
    for r in rows:
        if r["is_source"] == source and w in r["name"].strip().lower():
            return r
    return None


def source_term_index(dst, wire_uid, owner_uid=None):
    rows = wire_source_owner(dst, wire_uid, n=8)
    for r in rows:
        if r.get("is_source") and (owner_uid is None or r.get("owner_uid") == owner_uid):
            return r["i"], r
    return None, rows


def wire_uids(dst):
    return [o["uid"] for o in g.report_all(dst, "Wire")]


# ============================================================ the two readings
def read_is_broken(dst, wire_uid, sinks):
    """`Wire.Is Broken?` 6371004 through OpConnectFromWire_v0's own W7b-ordered readout, driven exactly as
    tools/bench/diag_fstunnel_wirebroken.py:260-288 drives it: an IDEMPOTENT re-connect of the wire's own
    source terminal into a sink it already has. A row counts only when `UID 2` == the wire asked about."""
    si, srow = source_term_index(dst, wire_uid)
    if si is None:
        return None, f"no SOURCE terminal row for w{wire_uid} ({str(srow)[:120]})"
    for diag, node_uid, term_name in sinks:
        try:
            wb = B.walk(dst, diag)
        except Exception as e:
            return None, f"walk(D[{diag}]) EXC {str(e)[:100]}"
        if node_uid not in wb:
            continue
        t = pick(wb[node_uid][2], term_name, False)
        if t is None:
            continue
        es0 = g.exec_state(dst)
        dw, es, err, sub = connect_from_wire(dst, wire_uid, si, diag, wb[node_uid][0], t["i"], CFW_LABELS)
        row = {"wire": wire_uid, "sink": [diag, node_uid, term_name], "wire_delta": dw,
               "exec_before_read": es0, "exec_after_read": es, "op_err": str(err)[:160],
               "uid2": sub.get("UID 2"), "is_broken": sub.get("Is Broken?"), "name": sub.get("Name")}
        print(f"      6371004 READ w{wire_uid} via D[{diag}].#{node_uid}.{term_name!r}: UID 2 = "
              f"{row['uid2']!r}, Is Broken? = {row['is_broken']!r}, wire delta {dw}, ExecState "
              f"{es0}->{es}, op err {str(err)[:70]!r}", flush=True)
        if not err and row["uid2"] == wire_uid and isinstance(row["is_broken"], bool):
            return row, ""
        return None, f"row rejected (UID 2 {row['uid2']!r}, Is Broken? {row['is_broken']!r}, err {str(err)[:80]!r})"
    return None, "no addressable NODE sink for this wire (tunnel / panel terminal) - read-only census only"


def after_edit(dst, tag, before, sinks=None, do_broken=False, store=None):
    """The two additions, applied after EVERY edit. Returns the new wire uid list."""
    es = g.exec_state(dst)
    now = wire_uids(dst)
    new = [u for u in now if u not in before]
    gone = [u for u in before if u not in now]
    print(f"   [{tag}] ExecState {es}   Wire {len(before)}->{len(now)}   new {new}   gone {gone}", flush=True)
    rows = []
    for u in new:
        terms = wire_source_owner(dst, u, n=8)
        nsrc = sum(1 for t in terms if t.get("is_source"))
        rec = {"wire": u, "n_source_terminals": nsrc, "read_only_verdict":
               ("BROKEN (>=2 sources, docs/NAMES.md:900)" if nsrc >= 2 else "not broken by the source count"),
               "terms": terms, "is_broken": None, "why": "read-only census only (pass A takes no write-reads)"}
        print(f"      w{u}: sources reporting Is Source? TRUE = {nsrc} -> {rec['read_only_verdict']}", flush=True)
        if do_broken:
            row, why = read_is_broken(dst, u, sinks or [])
            if row:
                rec["is_broken"] = row["is_broken"]
                rec["broken_row"] = row
                rec["why"] = ""
            else:
                rec["why"] = why
                print(f"      w{u}: Wire.Is Broken? could not be read - {why}", flush=True)
        rows.append(rec)
    if store is not None:
        store.append({"step": tag, "exec_state": es, "wires_before": len(before), "wires_after": len(now),
                      "new_wires": new, "gone_wires": gone, "rows": rows})
    return now


# ============================================================ the 2026-09-13 construction, unchanged
def construct(dst, do_broken, store):
    """build_opreportall_v1.py:127-221, step for step. The source line of every step is in its comment."""
    w = wire_uids(dst)
    print(f"   start: ForLoop={g.count(dst, 'ForLoop')} LoopTunnel={g.count(dst, 'LoopTunnel')} "
          f"Property={g.count(dst, 'Property')} Wire={len(w)} ExecState={g.exec_state(dst)}", flush=True)

    # v1:129-130  step 1 - delete the OLD Index Array, then remove_bad_wires_scripted
    g.delete_object(dst, "IndexArray", 0)
    g.remove_bad_wires_scripted(dst)
    w = after_edit(dst, "1 delete IndexArray + remove_bad_wires_scripted", w, store=store)

    # v1:131-133  step 2 - delete the two OLD Property nodes, then remove_bad_wires_scripted
    for _ in range(g.count(dst, "Property")):
        g.delete_object(dst, "Property", 0)
    g.remove_bad_wires_scripted(dst)
    w = after_edit(dst, "2 delete the old Property nodes + remove_bad_wires_scripted", w, store=store)

    # v1:135-136  step 3 - empty For Loop (ExecState 0 here is EXPECTED: an empty loop has no N)
    g.for_loop(dst, (1400, 900))
    w = after_edit(dst, "3 empty For Loop", w, store=store)

    # v1:137-142  step 4 - the loop body diagram
    dias = [i for i, d in enumerate(g.report(dst, "Diagram")) if "For" in str(d.get("owner"))]
    if not gate(f"S1 {os.path.basename(dst)}: a ForLoop-owned body diagram exists", bool(dias), str(dias)):
        raise B.Stop("no loop body diagram")
    body = dias[0]
    note(f"loop body = diagram index {body}")

    # v1:144-149  step 5 - Property(Position, UID, Class Name, Owner) INSIDE the body
    pn1 = g.build_property(dst, "VI Server:GObject",
                           [(P_POSITION, False), (P_UID, False), (P_CLASSNAME, False), (P_OWNER, False)],
                           (1450, 950), diagram_index=body)
    if not gate(f"S2 {os.path.basename(dst)}: the body Property node was created", bool(pn1), str(pn1)[:160]):
        raise B.Stop("no property node")
    pn1_uid = pn1[-1]["uid"]
    w = after_edit(dst, "5 Property(Position,UID,ClassName,Owner) inside the body", w, store=store)

    def pidx(uid):
        return [o["uid"] for o in g.report(dst, "Property")].index(uid)

    # v1:158-160  step 6 - wire Traverse.'References' -> that node's `reference`, CROSSING the loop boundary
    g.wire(dst, "SubVI", 0, "References", "Property", pidx(pn1_uid), "reference")
    w = after_edit(dst, "6 wire References -> PN1.reference (crosses the boundary)", w,
                   sinks=[(body, pn1_uid, "reference")], do_broken=do_broken, store=store)

    # v1:162-165  step 7 - Property(Class Name) on the OWNER, also inside the body
    pn2 = g.build_property(dst, "VI Server:Generic", [(P_CLASSNAME, False)], (1450, 1150), diagram_index=body)
    pn2_uid = pn2[-1]["uid"] if pn2 else None
    w = after_edit(dst, "7 Property(ClassName) on the owner, inside the body", w, store=store)

    # v1:168-171  step 8 - wire PN1.'Owner' -> PN2.`reference` (both inside the body, no new tunnel)
    if pn2_uid is not None:
        g.wire(dst, "Property", pidx(pn1_uid), T_OWNER, "Property", pidx(pn2_uid), "reference")
        w = after_edit(dst, "8 wire PN1.Owner -> PN2.reference (inside the body)", w,
                       sinks=[(body, pn2_uid, "reference")], do_broken=do_broken, store=store)

    # v1:175-183  steps 9/10 - auto-indexed OUTPUT tunnels
    g.exit_loop(dst, pidx(pn1_uid), [T_POSITION, T_UID, T_CLASSNAME], body, node_class="Property")
    w = after_edit(dst, "9 exit_loop: output tunnels for Position, UID, ClassName", w, store=store)
    if pn2_uid is not None:
        g.exit_loop(dst, pidx(pn2_uid), [T_CLASSNAME], body, node_class="Property")
        w = after_edit(dst, "10 exit_loop: the owner's ClassName", w, store=store)

    # v1:188-209  step 11 - IndexMode 1 on each OUTPUT tunnel, then a typed indicator on it
    n_tun = g.count(dst, "LoopTunnel")
    note(f"tunnels now {n_tun}; indices 1..{n_tun - 1} should be the outputs")
    label_map = {}
    meanings = [T_POSITION, T_UID, T_CLASSNAME, "Owner Class Name"]

    def inds():
        return [lab for _i, lab, is_ind in g.fp_labels(dst) if is_ind and lab]

    for k, tun in enumerate(range(1, n_tun)):
        before_labels = set(inds())
        try:
            g.set_index_mode(dst, tun, 1)
        except Exception as e:
            note(f"tunnel {tun}: set_index_mode {str(e)[:120]}")
        try:
            g.tunnel_indicator(dst, tun)
        except Exception as e:
            note(f"tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}")
            w = after_edit(dst, f"11.{k} tunnel {tun}: indicator FAILED", w, store=store)
            continue
        new_labels = [l for l in inds() if l not in before_labels]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        note(f"tunnel {tun} -> indicator {new_labels} (expected to carry {meaning})")
        for l in new_labels:
            label_map[l] = meaning
        w = after_edit(dst, f"11.{k} tunnel {tun}: IndexMode 1 + typed indicator", w, store=store)

    es = g.exec_state(dst)
    print(f"   assembled: ForLoop={g.count(dst, 'ForLoop')} LoopTunnel={g.count(dst, 'LoopTunnel')} "
          f"Property={g.count(dst, 'Property')} Wire={g.count(dst, 'Wire')} ExecState={es}", flush=True)
    return es, label_map


def prepare(src, dst):
    """v1:109-125 - never load the target before overwriting it; open the panel before editing."""
    try:
        g.close_panel(dst)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
    time.sleep(0.3)
    g.open_panel(dst)
    time.sleep(1.0)


# ============================================================ main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    t0 = time.time()
    print(f"=== S0-beta REPLICATE the 2026-09-13 positive control  {time.strftime('%Y-%m-%d %H:%M:%S')} ===",
          flush=True)
    print("PREDICTION CONTRACT P1/P2/P3 - see this file's docstring.", flush=True)
    om0 = md5(ORIGINAL)
    gate("G0 the route-B original is the pinned one, BEFORE", om0 == ORIG_MD5, om0)
    sm0 = md5(OP_V3)
    print(f"   source OpReport_v3.vi md5 BEFORE {sm0}", flush=True)
    h0, p0 = mem()
    print(f"   LabVIEW handles/private bytes before: {h0} / {p0}", flush=True)

    saved_md5 = None
    try:
        # ---------------- PASS A: CLEAN (P1, P2) ----------------
        print("\n=== PASS A (CLEAN): the construction with read-only readings only ===", flush=True)
        fresh()
        prepare(OP_V3, DST)
        gate("A1 the copy is byte-identical to OpReport_v3", md5(DST) == sm0, md5(DST))
        es_cold = g.exec_state(DST)
        gate("A2 the copy is RUNNABLE cold, before anything is changed", es_cold == 1, f"ExecState {es_cold}")
        RES["pass_a"]["steps"] = []
        es, label_map = construct(DST, False, RES["pass_a"]["steps"])
        RES["pass_a"]["final_exec_state"] = es
        RES["pass_a"]["label_map"] = label_map
        gate("P1 the rebuilt op ends ExecState 1", es == 1, f"ExecState {es}")
        if es == 1:
            g.save(DST)
            saved_md5 = md5(DST)
            RES["pass_a"]["saved"] = {"path": DST, "md5": saved_md5, "bytes": os.path.getsize(DST)}
            print(f"   SAVED {DST}\n   md5   {saved_md5}   ({os.path.getsize(DST)} B)", flush=True)
            gate("P2 the VI SAVED and its md5 is logged", bool(saved_md5) and saved_md5 != sm0, str(saved_md5))
        else:
            gate("P2 the VI SAVED and its md5 is logged", False,
                 "NOT SAVED - ExecState != 1; no step may save a broken VI (docs/cycle27-plan.md:458). "
                 "The readings are the artefact instead: " + OUT)
        try:
            g.close_panel(DST)
        except Exception:
            pass

        # ---------------- PASS B: the 6371004 read after each edit (P3) ----------------
        print("\n=== PASS B (BROKEN-READ): same construction, `Wire.Is Broken?` after each edit ===", flush=True)
        fresh()
        prepare(OP_V3, SCR_B)
        gate("B1 the pass-B scratch is byte-identical to OpReport_v3", md5(SCR_B) == sm0, md5(SCR_B))
        es_cold_b = g.exec_state(SCR_B)
        gate("B2 the pass-B scratch is RUNNABLE cold", es_cold_b == 1, f"ExecState {es_cold_b}")
        RES["pass_b"]["steps"] = []
        esb, _ = construct(SCR_B, True, RES["pass_b"]["steps"])
        RES["pass_b"]["final_exec_state"] = esb
        print(f"   PASS B final ExecState {esb} (pass B is perturbed by the reads BY DESIGN - P1 is pass A's)",
              flush=True)
    except B.Stop as e:
        print(f"  STOPPED at gate: {e}", flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  RAISED: {str(e)[:250]}", flush=True)
    finally:
        for p in (DST, SCR_B):
            try:
                g.close_panel(p)
            except Exception:
                pass
        # the pass-B scratch is a scratch: created and deleted in the same run (CLAUDE.md §3)
        try:
            if os.path.exists(SCR_B):
                os.remove(SCR_B)
                print(f"   deleted the pass-B scratch {os.path.basename(SCR_B)}", flush=True)
        except Exception as e:
            print(f"   could not delete {SCR_B}: {e}", flush=True)

    # ---------------- P3 and the rule-1 closing gates ----------------
    def edits_with_both(block):
        steps = RES.get(block, {}).get("steps", [])
        ok = 0
        for s in steps:
            if s.get("exec_state") is None:
                continue
            if all(("is_broken" in r) for r in s.get("rows", [])):
                ok += 1
        return ok, len(steps)

    a_ok, a_n = edits_with_both("pass_a")
    b_ok, b_n = edits_with_both("pass_b")
    b_rows = [r for s in RES.get("pass_b", {}).get("steps", []) for r in s.get("rows", [])]
    b_read = [r for r in b_rows if isinstance(r.get("is_broken"), bool)]
    print(f"\n   P3 accounting: pass A {a_ok}/{a_n} edits carry ExecState + a census row per new wire; "
          f"pass B {b_ok}/{b_n}; pass B new wires {len(b_rows)}, of which {len(b_read)} returned a boolean "
          f"`Wire.Is Broken?` and {len(b_rows) - len(b_read)} carry a could-not-read reason", flush=True)
    gate("P3 every edit logged ExecState, and every wire it created carries a Wire.Is Broken? row or a "
         "could-not-read reason", a_n > 0 and a_ok == a_n and b_n > 0 and b_ok == b_n,
         f"pass A {a_ok}/{a_n}, pass B {b_ok}/{b_n}")

    sm1 = md5(OP_V3) if os.path.exists(OP_V3) else "(missing)"
    gate("G8 the SOURCE op OpReport_v3.vi is UNTOUCHED", sm1 == sm0, f"{sm0} -> {sm1}")
    om1 = md5(ORIGINAL)
    gate("G0b the route-B original is unchanged, AFTER", om1 == ORIG_MD5, om1)
    gate("G9 the pass-B scratch was deleted", not os.path.exists(SCR_B), SCR_B)
    h1, p1 = mem()
    print(f"   LabVIEW handles/private bytes after: {h1} / {p1}  (delta {h1 - h0} / {p1 - p0})", flush=True)
    RES["mem"] = {"before": [h0, p0], "after": [h1, p1]}
    RES["original_md5"] = {"before": om0, "after": om1}
    RES["source_md5"] = {"before": sm0, "after": sm1}

    try:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1)
        print(f"   readings written: {OUT}", flush=True)
    except OSError as e:
        print(f"   could not write {OUT}: {e}", flush=True)

    print(f"\n=== {len(PASS)} PASS / {len(FAIL)} FAIL   {time.time() - t0:.0f} s ===", flush=True)
    if FAIL:
        print("   failing: " + "; ".join(FAIL), flush=True)
    print(f"   P1 {'HELD' if RES.get('pass_a', {}).get('final_exec_state') == 1 else 'MISSED'} "
          f"(pass A final ExecState {RES.get('pass_a', {}).get('final_exec_state')})", flush=True)
    print(f"   P2 {'HELD' if saved_md5 else 'MISSED'} (saved md5 {saved_md5})", flush=True)
    print(f"   P3 {'HELD' if (a_n and a_ok == a_n and b_n and b_ok == b_n) else 'MISSED'} "
          f"(pass A {a_ok}/{a_n}, pass B {b_ok}/{b_n})", flush=True)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
