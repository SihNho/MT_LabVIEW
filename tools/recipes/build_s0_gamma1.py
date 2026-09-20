r"""build_s0_gamma1.py - S0-gamma, FIRST ported difference: the body node is CREATED IN THE BODY (D2/D4).

AUTHORITY: `docs/cycle27-plan.md` Pre-decided 26 (judgement, cycle 45) on the fact `docs/s0-diff.md` produced -
23 ordered construction differences between the build that ends `ExecState` 1
(`tools/recipes/build_opreportall_v1.py`, 2026-09-13) and the one that ends 0 four times
(`tools/recipes/build_s0_closeref_v3.py`). gamma1 ports D2/D4 and nothing else that can be held constant.

=========================================================================================================
WHAT THE ORDERED VERIFICATION OF THE CALLEE FOUND - read this before judging the design (Pre-decided 21(f))
=========================================================================================================
Pre-decided 26 names the working path as `build_opreportall_v1.py:144-149` -> `tools/gscript.py:2188`. That
callee is **`gscript.build_property(target, cls, props, location, diagram_index=0)`** and it does two things
this step needs, verified by reading it, not by citing the call site:
  * `tools/gscript.py:2195` `ensure_loaded(target)` then `:2198-2202` set `vi path = target`,
    `Class Name = "Diagram"`, `index = diagram_index`, `location` - so the node is created **on the TARGET's own
    diagram**, the one addressed by `diagram_index`, with no fixture and no reparent;
  * `tools/gscript.py:2225-2227` `new_since(target, "Property", before)` - the identity of what was created is a
    before/after delta taken on that same target.
**But it creates a `Property` node.** It cannot create the Application-Control primitive `Close Reference`, and
NOTHING IN THIS FLEET CAN: there is no creator for a primitive outside a per-primitive op
(`gscript.queue_node:1122` is one such op family, built one style at a time), and the style ring that `New VI
Object` needs "is a typed ring, unretargetable by string" - `docs/stage2-assembly-step-b.md:34`, with
`docs/toolkit-capabilities.md:274` saying the same for front-panel styles. `docs/vi-server-ids.json` has no
`Close` method id, so the Invoke-node route does not exist either. That is why v3 COPIES the node out of
`KernelBuilder_v1.vi` in the first place.

CONSEQUENCE, FLAGGED AND NOT DECIDED HERE (CLAUDE.md 3 "what a material session does not decide"):
porting D2/D4 with the tools that exist drags TWO further differences along:
  * **D3** - the body node becomes a **Property** node (`GObject.Position` read), not a `Close Reference`. It
    carries the SAME two sinks the construction wires (`reference`, `error in (no error)`, `docs/NAMES.md:226-227`),
    so every wiring row below is the row v3 wrote; only the node's class differs.
  * **D1** - with no copy there is no `copy_by_index`, hence no Move fixture: the edits land on the TARGET FILE
    (`tools/gscript.py:1518`, `:1536-1543` is the fixture path v3 used). Counter-evidence already on file says
    D1 alone does not break a VI - `tools/bench/build_opconnectfromwire_v0.log:58` reached `ExecState 1` inside
    that same hook - which is exactly why Pre-decided 26(c) ranked D1 behind D2/D4.
So this run measures **D2+D4+D3+D1 together**, not one difference. It is still discriminating in one direction:
if the final `ExecState` is **0**, the copy-and-reparent path is EXONERATED and the cause is elsewhere (D7, D11,
D18). If it is **1**, the four together are implicated and the next gamma step must separate them. Whether that
is an acceptable first gamma step is a JUDGEMENT call; this file states it rather than quietly widening the step.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "check what already exists"):
  * `tools/recipes/build_s0_closeref_v3.py` - the failing build; its ordered rows are reproduced here
    (`_finish_new_loop:507-573`): For Loop at `(max x + 220, min y + 40)`, the `References` wire BRANCHED into the
    body node's `reference`, IndexMode settled to 1, the panel `error out` net branched into `error in (no error)`,
    IndexMode 0, auto error handling OFF. **`remove_bad_wires_scripted` is still NOT called** - that is D7, the
    SECOND ported difference by Pre-decided 26(c), deliberately not in this step.
  * `tools/recipes/build_opreportall_v1.py` - the working build, source of the `build_property(..., diagram_index=body)`
    call this step ports.
  * `tools/recipes/build_opconnectfromwire_v0.py:381 connect_from_wire()` - the branch writer, with its own ordered
    `Wire.Is Broken?` 6371004 readback; `:423 wire_source_owner()` for provenance.
  * `gscript.for_loop / find_at / tunnels / set_index_mode / panel_wiring / set_auto_error_handling / save` - built.
  * NO NEW OP IS BUILT HERE (`docs/cycle27-plan.md` Pre-decided 2; user, 2026-09-18 08:53).

PREDICTION CONTRACT - printed before anything runs; the FIRST TWO are the only fatal ones.
  P1  the scratch copy reads `ExecState` **1** COLD in a fresh instance (measured seven times,
      `docs/cycle27-plan.md:434-439`). **If it reads 0 the run STOPS** - that is a failed prediction and the
      chain's premise is dead.
  P2  an intermediate `ExecState 0` right after the bare For Loop insert is **EXPECTED and does not fail the
      step** (finding A2, `docs/cycle27-plan.md:465-468`; `archive/WORKLOG.md:86-87`).
  P3  the FINAL `ExecState` after the full construction IS THE MEASUREMENT. It has NO predicted value.
  G1  the scratch is byte-identical to `OpReport_v3.vi` before anything changes; `OpReport_v3.vi` and the
      route-B original are unchanged at the end (rule 1).
  G2  the new Property node is on the LOOP BODY diagram - the D2/D4 port, verified by walking that diagram.
  G3  the `References` branch reads back a NON-BARE sink and `Is Broken?` is not True; a LoopTunnel appears and
      its IndexMode is read BEFORE it is written.
  G4  the panel `error out` net branches into `error in (no error)`; its tunnel settles to IndexMode 0.
  G5  `ExecState` is read and printed after EVERY edit, each labelled with its condition - never inferred.
  SAVE final `ExecState` 1 -> the VI is SAVED under claudeDev and its md5 printed. Final `ExecState` 0 -> the VI
      is **NOT saved** (finding B1: `tools/gscript.py:2065-2068` diverts to `gui_save`, failed at seven logged
      sites) and `tools/bench/s0_gamma1_readings.json` is written instead, with its own md5.

  py tools/bgrun.py --material --max-min 30 --log tools/bench/build_s0_gamma1.log -- py -u tools/recipes/build_s0_gamma1.py
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
from build_opconnectfromwire_v0 import connect_from_wire, wire_source_owner  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
CD = g.CLAUDEDEV
OP_V3 = os.path.join(CD, "OpReport_v3.vi")
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(CD, f"SCRATCH_s0g1_{STAMP}.vi")
READINGS = os.path.join(BENCH, "s0_gamma1_readings.json")

TRAVERSE_LABEL = "Traverse for GObjects.vi"
REFS_TERM = "References"                # tools/bench/s0_terminal_names.log
REF_TERM = "reference"                  # docs/NAMES.md:226 (Property node terminal 0)
ERRIN_TERM = "error in (no error)"      # docs/NAMES.md:226 (Property node terminal 2)
ERROUT_TERM = "error out"
P_POSITION = "632A800"                  # GObject.Position, docs/vi-server-ids.json

g._run.__defaults__ = (6.0, 120.0)
GATES = []
R = {"readings": [], "branches": [], "gates": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    GATES.append((name, bool(ok)))
    R["gates"].append({"name": name, "pass": bool(ok), "detail": str(detail)[:300]})
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return bool(ok)


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
    raise Stop(f"COM preflight FAILED after {tries} attempts: {last}")


def fresh():
    print(f"   fresh(): killing LabVIEW pid {lv_pid()}", flush=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) "
                    "{ Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{LV_EXE}'"],
                   capture_output=True, text=True, timeout=60)
    time.sleep(35)
    g.reset()
    com_preflight()
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def walk(target, diagram):
    try:
        labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    except Exception as e:
        print(f"      node_labels(D[{diagram}]) EXC {str(e)[:120]}", flush=True)
        labels = {}
    out = {}
    for n in range(80):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def pick(rows, want, source):
    w = want.strip().lower()
    for r in rows:
        if r["is_source"] == source and r["name"].strip().lower() == w:
            return r
    return None


def es(label):
    """Read ExecState and LOG IT WITH ITS CONDITION. Never inferred (docs/s0-diff.md D18: the failing build had
    no reading between the node copy and the first wire, so it could not say which edit broke the VI)."""
    v = g.exec_state(SCRATCH)
    print(f"   EXECSTATE {v}   <- condition: {label}", flush=True)
    R["readings"].append({"condition": label, "exec_state": v})
    return v


def tun_uids():
    return [o["uid"] for o in g.report_all(SCRATCH, "LoopTunnel")]


def classify(claimed, got):
    """Pre-decided 18: EXACT = the claimed uid, SEGMENTED = a different non-zero uid, BARE = nothing."""
    if not got:
        return "BARE"
    return "EXACT" if got == claimed else "SEGMENTED"


def settle(tag, new_tuns, want_mode, label):
    for u in new_tuns:
        i = tun_uids().index(u)
        t = g.tunnels(SCRATCH, i)
        print(f"   [{tag}] new LoopTunnel #{u} (index {i}) IndexMode AS READ {t['index_mode']} "
              f"outer w{t['out_wire']} inner {t['in_wires']} ({label})", flush=True)
        R["branches"].append({"tag": tag, "tunnel": u, "index_mode_as_read": t["index_mode"],
                              "out_wire": t["out_wire"], "in_wires": t["in_wires"]})
        if t["index_mode"] != want_mode:
            g.set_index_mode(SCRATCH, i, want_mode)
            t = g.tunnels(SCRATCH, tun_uids().index(u))
            print(f"   [{tag}] set IndexMode -> {want_mode}; read back {t['index_mode']}", flush=True)
        gate(f"G3t {tag}: tunnel IndexMode == {want_mode}", t["index_mode"] == want_mode,
             f"#{u} mode {t['index_mode']}")


def branch_into(tag, what, wire_uid, owner_uid, body_i, node_i, term_i, sink_getter):
    rows = wire_source_owner(SCRATCH, wire_uid, n=8)
    src = next((r for r in rows if r.get("is_source") and r.get("owner_uid") == owner_uid), None)
    gate(f"G3s {tag}: w{wire_uid} ({what}) has a SOURCE terminal owned by #{owner_uid}", src is not None,
         str(rows)[:240], fatal=True)
    dw, e, err, sub = connect_from_wire(SCRATCH, wire_uid, src["i"], body_i, node_i, term_i, CFW_LABELS)
    got = sink_getter()
    kind = classify(wire_uid, got)
    broken = sub.get("Is Broken?")
    print(f"   [{tag}] BRANCH {what}: claimed w{wire_uid} -> sink w{got} = {kind}, Is Broken? {broken!r}, "
          f"dw={dw}, ExecState after the write {e}, err={err!r} sub={sub}", flush=True)
    R["branches"].append({"tag": tag, "what": what, "claimed": wire_uid, "got": got, "class": kind,
                          "is_broken": broken, "dw": dw, "exec_state_after": e, "err": str(err)[:160]})
    gate(f"G3 {tag}: {what} branched into the body - sink is not BARE", kind != "BARE", f"sink wire {got}")
    gate(f"G3k {tag}: {what} is not reported BROKEN by the op's own ordered `Wire.Is Broken?`",
         broken is not True, f"Is Broken? {broken!r}")
    return got


def build():
    # ---- 0. preconditions, rule 1 ------------------------------------------------------------------
    m_src = md5(OP_V3)
    m_orig = md5(ORIGINAL) if os.path.exists(ORIGINAL) else None
    print(f"   OpReport_v3.vi md5 BEFORE {m_src}", flush=True)
    print(f"   original       md5 BEFORE {m_orig}", flush=True)
    gate("G1o the route-B original is the pinned md5 BEFORE", m_orig == ORIG_MD5, str(m_orig))
    R["md5"] = {"OpReport_v3_before": m_src, "original_before": m_orig}

    fresh()
    shutil.copy2(OP_V3, SCRATCH)
    gate("G1a the scratch is a byte copy of OpReport_v3", md5(SCRATCH) == m_src, md5(SCRATCH), fatal=True)
    print(f"   scratch {SCRATCH}", flush=True)

    # ---- P1. cold ExecState ------------------------------------------------------------------------
    v = es("COLD - fresh LabVIEW instance, COM-preflighted, byte copy of OpReport_v3, NOTHING edited")
    gate("P1 the scratch copy reads ExecState 1 COLD (docs/cycle27-plan.md:434-439, measured 7x)", v == 1,
         f"ExecState {v} - a 0 kills the chain's premise", fatal=True)

    # ---- the `References` wire, read from the machine ----------------------------------------------
    w0 = walk(SCRATCH, 0)
    tv = next((u for u in w0 if w0[u][1] == TRAVERSE_LABEL), None)
    gate("G2v the Traverse node is present on diagram 0", tv is not None,
         str([(u, w0[u][1]) for u in w0])[:240], fatal=True)
    refs = pick(w0[tv][2], REFS_TERM, True)
    gate(f"G2r the Traverse exposes the '{REFS_TERM}' SOURCE terminal", refs is not None,
         str([r["name"] for r in w0[tv][2] if r["is_source"]]), fatal=True)
    wref = refs["wire"]
    gate(f"G2w '{REFS_TERM}' already drives a wire (the branch needs one; D11 unchanged - the consumers are "
         f"NOT deleted, exactly as v3 left them)", bool(wref), f"wire {wref}", fatal=True)

    # ---- 1. the bare For Loop (D9 unchanged: v3's position formula) --------------------------------
    pos = g.report_all(SCRATCH, "Node")
    loc = (max(p["pos"][0] for p in pos) + 220, min(p["pos"][1] for p in pos) + 40)
    g.for_loop(SCRATCH, loc)
    loop = g.find_at(SCRATCH, "ForLoop", loc, tol=80)
    print(f"   For Loop #{loop['uid']} created at {loc} (found at {loop['pos']})", flush=True)
    es("after the BARE For Loop insert - P2 says 0 is EXPECTED here and does NOT fail the step")

    dias = [d for d in g.report(SCRATCH, "Diagram") if d["owner"] == "ForLoop"]
    gate("G2d exactly one ForLoop-owned Diagram", len(dias) == 1,
         str([(d["i"], d["uid"], d["owner"]) for d in dias]), fatal=True)
    body_i = dias[0]["i"]
    print(f"   loop body Diagram[{body_i}] uid {dias[0]['uid']}", flush=True)

    # ---- 2. THE PORTED DIFFERENCE (D2/D4): the body node is CREATED, on the body diagram -----------
    before_pn = set(o["uid"] for o in g.report_all(SCRATCH, "Property"))
    g.build_property(SCRATCH, "VI Server:GObject", [(P_POSITION, False)],
                     (loc[0] + 80, loc[1] + 80), diagram_index=body_i)
    new_pn = [o["uid"] for o in g.report_all(SCRATCH, "Property") if o["uid"] not in before_pn]
    gate("G2p exactly one Property node was created", len(new_pn) == 1, str(new_pn), fatal=True)
    pn = new_pn[0]
    wb = walk(SCRATCH, body_i)
    gate("G2 THE PORT (D2/D4): the created node is ON THE LOOP BODY DIAGRAM - no copy, no reparent",
         pn in wb, f"body nodes {sorted(wb)}, new Property #{pn}", fatal=True)
    node_i, _lab, rows = wb[pn]
    print(f"   body Property #{pn} (node index {node_i}) terminals "
          f"{[(r['i'], r['name'], r['is_source']) for r in rows]}", flush=True)
    ref_t = pick(rows, REF_TERM, False)
    ein_t = pick(rows, ERRIN_TERM, False)
    gate(f"G2t the created node carries the SAME two sinks v3 wired ('{REF_TERM}', '{ERRIN_TERM}')",
         ref_t is not None and ein_t is not None, f"{ref_t}/{ein_t}", fatal=True)
    es("after the body node was CREATED IN THE BODY (the D2/D4 port), nothing wired yet")

    # ---- 3. the refnum: BRANCH the References net into the body node (D10/D11 unchanged) ------------
    t0 = set(tun_uids())
    branch_into("refs", f"the `{REFS_TERM}` array", wref, tv, body_i, node_i, ref_t["i"],
                lambda: (pick(walk(SCRATCH, body_i)[pn][2], REF_TERM, False) or {}).get("wire", 0))
    new_t = [u for u in tun_uids() if u not in t0]
    gate("G3x a LoopTunnel appeared for the crossing", len(new_t) >= 1, f"new tunnels {new_t}")
    settle("refs", new_t, 1, "References (auto-index: the array supplies N)")
    es("after the References branch and the IndexMode settle")

    # ---- 4. the error chain (D14 unchanged) --------------------------------------------------------
    pw = g.panel_wiring(SCRATCH)
    cand = [r for r in pw if str(r.get("label", "")).strip().lower() == "error out" and r.get("wire")]
    gate("G4a exactly one panel indicator labelled 'error out' carrying a wire", len(cand) == 1,
         str(cand)[:240], fatal=True)
    ewire = cand[0]["wire"]
    owner = [u for u in w0 if (pick(w0[u][2], ERROUT_TERM, True) or {}).get("wire") == ewire]
    gate("G4b the node driving the panel's error-out net was identified FROM THE MACHINE", len(owner) == 1,
         f"ewire {ewire} owners {owner}", fatal=True)
    last = owner[0]
    print(f"   last error-chain node #{last} ('{w0[last][1]}') drives panel error out on w{ewire}", flush=True)
    t1 = set(tun_uids())
    branch_into("errchain", "the panel error-out net", ewire, last, body_i, node_i, ein_t["i"],
                lambda: (pick(walk(SCRATCH, body_i)[pn][2], ERRIN_TERM, False) or {}).get("wire", 0))
    new_t = [u for u in tun_uids() if u not in t1]
    gate("G4x a LoopTunnel appeared for the error crossing", len(new_t) >= 1, f"new tunnels {new_t}")
    settle("errchain", new_t, 0, "error chain (scalar: NOT auto-indexed)")
    es("after the error-chain branch and the IndexMode settle")

    # ---- 5. auto error handling OFF (D16 unchanged) ------------------------------------------------
    try:
        g.set_auto_error_handling(SCRATCH, False)
        print("   auto error handling OFF", flush=True)
    except Exception as e:
        print(f"   set_auto_error_handling failed (non-fatal): {str(e)[:140]}", flush=True)

    # NOTE: `remove_bad_wires_scripted` is DELIBERATELY NOT CALLED - that is D7, the SECOND ported
    # difference (Pre-decided 26(c)), and porting two differences in one artefact is what this step avoids.

    final = es("FINAL - the full construction, D2/D4 ported. P3: this reading has NO predicted value")
    R["final_exec_state"] = final
    return final


def main():
    print(__doc__, flush=True)
    print(f"\n=== S0-gamma1  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    h0, p0 = mem()
    print(f"   LabVIEW handles BEFORE {h0}, private bytes {p0}", flush=True)
    final = None
    try:
        final = build()
    except Stop as e:
        print(f"   STOPPED at gate: {e}", flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"   RAISED: {str(e)[:220]}", flush=True)

    # ---- the saved artefact - required either way -------------------------------------------------
    if final == 1:
        g.save(SCRATCH)
        R["saved_vi"] = {"path": SCRATCH, "md5": md5(SCRATCH), "bytes": os.path.getsize(SCRATCH)}
        print(f"\n   SAVED {SCRATCH}\n   md5 {R['saved_vi']['md5']}  ({R['saved_vi']['bytes']} B)", flush=True)
    else:
        # finding B1: a broken VI is NEVER saved (tools/gscript.py:2065-2068 diverts to gui_save, which has
        # failed at seven logged sites). The step's artefact is the DATA file instead.
        print(f"\n   NOT SAVING the VI (final ExecState {final}) - finding B1. The artefact is the data file.",
              flush=True)
        if os.path.exists(SCRATCH):
            R["scratch_vi"] = {"path": SCRATCH, "md5": md5(SCRATCH), "bytes": os.path.getsize(SCRATCH),
                               "note": "LEFT ON DISK, unsaved-from-memory: the bytes are the untouched copy of "
                                       "OpReport_v3; every edit lived in LabVIEW memory and is recorded here"}
            print(f"   scratch on disk {SCRATCH} md5 {R['scratch_vi']['md5']}", flush=True)

    m_src_after = md5(OP_V3)
    m_orig_after = md5(ORIGINAL) if os.path.exists(ORIGINAL) else None
    R["md5"]["OpReport_v3_after"] = m_src_after
    R["md5"]["original_after"] = m_orig_after
    gate("G1b OpReport_v3.vi is UNTOUCHED", m_src_after == R["md5"]["OpReport_v3_before"], m_src_after)
    gate("G1c the route-B original is UNTOUCHED", m_orig_after == ORIG_MD5, str(m_orig_after))

    h1, p1 = mem()
    print(f"   LabVIEW handles AFTER {h1} (delta {h1 - h0}), private bytes {p1} "
          f"(delta {(p1 - p0) / 1e6:.1f} MB)", flush=True)
    R["handles"] = {"before": h0, "after": h1}
    R["private_bytes"] = {"before": p0, "after": p1}
    try:
        R["ref_counts"] = g.ref_counts()
        print(f"   gscript VI Server reference counters: {R['ref_counts']}", flush=True)
    except Exception:
        pass

    with open(READINGS, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2)
    print(f"\n   READINGS WRITTEN {READINGS}\n   readings md5 {md5(READINGS)} "
          f"({os.path.getsize(READINGS)} B)", flush=True)

    npass = sum(1 for _n, ok in GATES if ok)
    print(f"\n=== {npass} PASS / {len(GATES) - npass} FAIL; FINAL ExecState {final} ===", flush=True)
    for n, ok in GATES:
        if not ok:
            print(f"   FAIL {n}", flush=True)
    return 0 if final == 1 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        try:
            g.reset()
        except Exception:
            pass
