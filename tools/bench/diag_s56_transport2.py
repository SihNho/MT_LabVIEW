"""diag_s56_transport2 — cycle 56 material #3. A DIAGNOSTIC under tools/bench/, never a recipe.

WHAT IT IS FOR (the brief's two tests, each on its OWN fresh scratch copy of claudeDev\\D1_s2_loops.vi):

  TEST L — the LOCAL-VARIABLE verb. Routes L1 (`New VI Object` style `Local Variable`, ID 2061, created on
           `Diagram #23058`, bound by writing `Local.Control Name` 6355400 and `Local.Write?` 6355401 = False)
           and L2 (`Control` -> `Create:Local Variable`), from the UNVERIFIED peer answer
           archive/peer/2026-09-20-c56-localvar-scripting.md. Bind target: the EXISTING panel indicator whose
           ControlTerminal uid is 34200, whose label is READ OFF THE MACHINE here and never retyped.
  TEST I — the documented indicator remedy. I1 `create_indicator` on a TOP-LEVEL `Nodes[]` node terminal (the
           only thing it can address, docs/NAMES.md:278-282 and :474-475); I2 `wire_indicators(...
           node_class='Function', diagram_index=<frame>)` branching `#10686` t0 `'x .and. y?'` (wire 10799,
           Diagram #639) onto an indicator — the remedy those same lines name.

PREDICTION CONTRACT (gates below; every one REPORTED, the 34(j)/37(e) pattern — this script interprets nothing):
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T2  claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                                (FATAL)
  T3  each scratch is byte-identical to the S2 artefact at creation                                    (FATAL)
  P1  the REPAIRED gscript.create_indicator surfaces a NON-EMPTY error string on a call that provokes the
      1055 dialog (the proof the swallow at :2396-2400 is gone)
  L0  the bind target's label is read off the machine for ControlTerminal uid 34200
  L1  a call implementing `New VI Object` + style `Local Variable` is REACHABLE with the ops on disk
  L2  a call implementing `Control` -> `Create:Local Variable` is REACHABLE with the ops on disk
  L3  `Local` count is unchanged by Test L (8 before, 8 after — nothing was created)
  I0  the TOP-LEVEL `Nodes[]` census (read through create_indicator's OWN ladder, g.node_info) is non-empty
  I1  `create_indicator` produces a ControlTerminal on a top-level node terminal
  I2a `#10686` resolves on this scratch as class `Function`, Traverse index read live, t0 wire 10799
  I2b `wire_indicators` produces a branch onto the target indicator (its wire uid changes from 0)
  I2c the ORDERED SECOND-PASS `Is Broken?` read returns a boolean (True is a LEGITIMATE reading, not a failure)
  I2d `#637`'s terminal count is unchanged (no new tunnel/border object)                               (37(e))
  Z1  ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged after everything
  Z2  refs opened == refs closed, 0 live

BOUNDS (brief, 🔴): at most 3 attempts per verb; NO loop over indices. NO VI IS RUN (34(f)). NO NEW OP VI
(Pre-decided 2). No new device. No motor / ASI / camera (rig 조립). No GUI action. Originals never opened for
write. `allow_broken` stays False and `gui_save` is NEVER called.

WHAT ALREADY EXISTED (checked before writing a line of this, per the material brief):
  * tools/gscript.py — `create_indicator` :2385, `create_control` :2360, `wire_indicators` :1756,
    `node_info` :2462 (the TOP-LEVEL Nodes[] census through the SAME `VI -> Block Diagram -> Nodes[]` ladder
    create_indicator uses), `node_terms`/`node_terms_uid` :870/:925, `panel_wiring` :826, `report` :455,
    `count` :1005, `exec_state` :1977, `save` :2062.
  * tools/recipes/build_opconnectnested_v1.py:418 `connect_nested_v1` — the ONLY built carrier of
    `Wire.Is Broken?` 6371004 reachable from Python (docs/NAMES.md:902-911); used here ONLY as the ORDERED
    second pass, as an IDEMPOTENT re-connect of an EXISTING connection on the same net (wire_delta must be 0).
  * tools/bench/diag_s2_scaffold.py — `fresh()` (the restart), `Preload`, `file_facts`, the md5 pins.
  * tools/bench/diag_typectl_v2.py — the two-leg / one-scratch-per-leg shape this file follows.
  * files-first censuses: tools/bench/diagram_tree_main.json, main_vi_nodeterms.json, main_vi_panel_wiring.json.
  NOTHING NEW WAS BUILT. No op VI was created, and no recipe was added.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import diag_index                                                # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
import build_opconnectnested_v1 as CN1                                            # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s56_transport2.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

BIND_CT_UID = 34200          # 'current image number' per docs/main-vi-panel-map.md:383 - label READ LIVE below
LOCAL_STYLE = "Local Variable"        # style ID 2061 (peer, UNVERIFIED)
LOCAL_CTLNAME_PROP = 6355400          # Local.Control Name, String, R/W (peer, UNVERIFIED)
LOCAL_WRITE_PROP = 6355401            # Local.Write?, Boolean (peer, UNVERIFIED)
BODY_DIAG_UID = 23058                 # loop 1.5's body (37(h))
D639 = 639                            # the frame that holds #10686 / #10757 / #10407 / #48
D686 = 686                            # loop 1.1's body; #637 is Nodes[4] there
SRC_UID = 10686                       # class Function, label 'And'; t0 'x .and. y?' is a SOURCE, wire 10799
SRC_TERM_NAME = "x .and. y?"
LOOP11_UID = 637
# files-first: the FIRST unwired indicator rows of tools/bench/main_vi_panel_wiring.json (wire 0), in file order
FALLBACK_INDICATORS = ["File # Saved", "Image"]

LEFTOVERS = [os.path.join(g.CLAUDEDEV, "DIAG_s3aind_20260920_204915_A-nomove.vi"),
             os.path.join(g.CLAUDEDEV, "DIAG_s3aind_20260920_204915_B-movedin.vi")]

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "cycle 56 dispatch 3: (L) is a LOCAL VARIABLE placeable and bindable by scripting with the ops "
                 "on disk? (I) does the documented create_indicator / wire_indicators remedy reach a transport "
                 "indicator for 1.5's two 1.2-sourced inputs?",
     "chooses_no_route": True, "interprets_nothing": True, "no_vi_was_run": True, "no_new_op": True,
     "no_new_device": True, "no_gui_action": True, "rig_state": "조립 (motors/ASI forbidden, camera not needed)",
     "repair_under_test": "gscript.create_control:2360 / create_indicator:2385 no longer swallow the modal-dialog "
                          "RuntimeError (mirrors delete_object:2264-2272)",
     "peer_answer_unverified": "archive/peer/2026-09-20-c56-localvar-scripting.md - RECORDED AS FACTS, acted on "
                               "in no way beyond trying the two routes it names",
     "citations": {"create_indicator_scope": "docs/NAMES.md:278-282, :474-475",
                   "is_broken": "docs/NAMES.md:902-911",
                   "ordered_second_pass": "Pre-decided 42(b)"},
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "handles": {}, "hash_probe": [], "leftover_cleanup": [], "test_L": {}, "test_I": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Local", "LoopTunnel", "Wire", "ControlTerminal", "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                    # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                        # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def make_scratch(rec, tag, path):
    if os.path.exists(path):
        os.remove(path)
    shutil.copy2(S2_ARTEFACT, path)
    p = probe("T3 %s scratch at creation" % tag, path)
    rec["scratch"] = path
    rec["scratch_at_creation"] = p
    gate("T3 the %s scratch is byte-identical to the S2 artefact" % tag, p.get("md5") == S2_MD5,
         p.get("md5", "?"), fatal=True)
    return path


def panel_rows(target):
    try:
        pw = g.panel_wiring(target)
    except Exception as e:                                                        # noqa: BLE001
        fact("panel_wiring raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []
    rows = pw["rows"] if isinstance(pw, dict) and "rows" in pw else pw
    return list(rows or [])


def finish(rec, tag, target, save_as_is=True):
    """census, ExecState, the conditional save, close_panel."""
    census(rec, "after", target)
    es = read_exec_state(rec, "%s immediately before the save attempt" % tag, target)
    size, serr = None, None
    if save_as_is and isinstance(es, int) and es == 1:
        try:
            size = g.save(target)        # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                    # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:250])
    else:
        serr = ("NOT ATTEMPTED: ExecState is %r and the brief permits a save only at ExecState 1." % (es,))
    rec["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr,
                   "allow_broken": False, "gui_save": False, "exec_state_before_save": es}
    fact("%s g.save() returned %r; exception/reason VERBATIM %r" % (tag, size, serr))
    rec["save"]["file_after"] = D.file_facts("%s scratch after the save attempt" % tag, target)
    try:
        g.close_panel(target)
    except Exception as e:                                                        # noqa: BLE001
        fact("close_panel raised %s: %s" % (type(e).__name__, e))


# ============================================================================================= TEST L
def test_L():
    rec = R["test_L"]
    rec["routes_spec"] = {
        "L1": {"verb": "New VI Object", "style": LOCAL_STYLE, "style_id": 2061,
               "owner_diagram_uid": BODY_DIAG_UID, "bind_prop": LOCAL_CTLNAME_PROP,
               "direction_prop": LOCAL_WRITE_PROP, "direction_value": False},
        "L2": {"verb": "Control -> Create:Local Variable (LV2018+)"}}
    target = make_scratch(rec, "L", os.path.join(g.CLAUDEDEV, "DIAG_s56_localvar_%s.vi" % STAMP))
    print("\n=================== TEST L  (local-variable verb)  scratch %s" % os.path.basename(target), flush=True)

    with D.Preload("P-L"):
        g.open_panel(target)
        time.sleep(1.0)
        census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "L BEFORE", target)

        # ---- L0: the bind target's label, READ OFF THE MACHINE, never retyped
        rows = panel_rows(target)
        rec["panel_rows_read"] = len(rows)
        row = next((r for r in rows if r.get("uid") == BIND_CT_UID), None)
        rec["bind_target_row"] = row
        lab = (row or {}).get("label")
        fact("L0 ControlTerminal uid %d reads label %r (VERBATIM, repr) - indicator=%r, wire=%r"
             % (BIND_CT_UID, lab, (row or {}).get("indicator"), (row or {}).get("wire")))
        gate("L0 the bind target's label is READ OFF THE MACHINE for ControlTerminal uid %d" % BIND_CT_UID,
             bool(lab), repr(lab))

        # ---- the Local inventory this VI already carries
        try:
            locs = g.report(target, "Local")
        except Exception as e:                                                    # noqa: BLE001
            locs = "ERROR %s: %s" % (type(e).__name__, str(e)[:140])
        rec["local_objects_before"] = locs
        n_before = rec["censuses"]["before"].get("Local")
        fact("Traverse class `Local` on this scratch BEFORE: count %r, objects %r" % (n_before, locs))

        # ---- L1 / L2: is either verb REACHABLE with the ops on disk?  (measured, not assumed)
        ops = sorted(f for f in os.listdir(g.CLAUDEDEV) if f.lower().endswith(".vi") and f.startswith("Op"))
        rec["op_inventory_count"] = len(ops)
        with open(os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8") as f:
            gs = f.read()
        style_wrappers = [ln for ln in gs.splitlines()
                          if "SetControlValue" in ln and ("tyle" in ln or "Style" in ln)]
        rec["gscript_style_setters"] = style_wrappers
        reachable_L1 = bool(style_wrappers) or any("NewObj" in o or "NewVIObj" in o or "Local" in o for o in ops)
        rec["L1"] = {"attempts": 0, "reachable": reachable_L1,
                     "op_candidates": [o for o in ops if "New" in o or "Local" in o],
                     "blocker": None if reachable_L1 else
                     ("NO op VI on disk implements `New VI Object` with a settable style, and no gscript wrapper "
                      "writes a `style` control: %d Op*.vi files in claudeDev, 0 style setters in gscript.py. "
                      "docs/stage2-assembly-step-b.md:34 measured why - 'a New VI Object op cannot be "
                      "parameterised: style is a typed ring, unretargetable by scripting'; "
                      "docs/toolkit-capabilities.md:274 says the same for front-panel objects. Building one is a "
                      "NEW OP VI, which this brief forbids (Pre-decided 2). 0 calls were made." % len(ops))}
        gate("L1 a call implementing `New VI Object` + style %r is REACHABLE with the ops on disk" % LOCAL_STYLE,
             reachable_L1, rec["L1"]["blocker"] or "reachable")
        fact("L1 VERDICT: %s" % (rec["L1"]["blocker"] or "reachable"))

        writers = [ln.strip() for ln in gs.splitlines() if "def " in ln and ("set_" in ln or "write" in ln)]
        rec["gscript_property_writers"] = writers
        reachable_L2 = any("Create" in o and "Local" in o for o in ops)
        rec["L2"] = {"attempts": 0, "reachable": reachable_L2,
                     "blocker": None if reachable_L2 else
                     ("NO op VI carries an Invoke node for `Control -> Create:Local Variable`, and Python cannot "
                      "pass a LabVIEW Control reference into a method - that is why every verb here is a "
                      "pre-built op VI. `build_invoke` WOULD build one, but the product is a NEW OP VI "
                      "(Pre-decided 2 forbids it). The same holds for the binding write `Local.Control Name` "
                      "%d and `Local.Write?` %d: gscript has only special-purpose writers (%s) and no generic "
                      "property WRITER. 0 calls were made."
                      % (LOCAL_CTLNAME_PROP, LOCAL_WRITE_PROP,
                         ", ".join(w.split("(")[0].replace("def ", "") for w in writers[:6])))}
        gate("L2 a call implementing `Control` -> `Create:Local Variable` is REACHABLE with the ops on disk",
             reachable_L2, rec["L2"]["blocker"] or "reachable")
        fact("L2 VERDICT: %s" % (rec["L2"]["blocker"] or "reachable"))

        rec["local_count_after"] = g.count(target, "Local")
        gate("L3 `Local` count unchanged by Test L (nothing was created)",
             rec["local_count_after"] == n_before, "%r -> %r" % (n_before, rec["local_count_after"]))
        rec["exec_state_after"] = read_exec_state(rec, "L AFTER", target)
        finish(rec, "L", target)
    dump()


# ============================================================================================= TEST I
def op_indicators():
    """OpConnectNested_v1's own readouts, re-read AFTER a run (g.op caches the reference)."""
    rd = {}
    try:
        vi = g.op(CN1.OP)
        for k in ("UID", "Name", "UID 2", "Is Broken?"):
            try:
                rd[k] = vi.GetControlValue(k)
            except Exception as e:                                                # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                        # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return rd


def wired_counts(rec, tag, target, diag, node_i, uid_expect):
    """(node uid readback, n terminals, n WIRED terminals, the rows) - the 37(e) per-node metric."""
    out = {"tag": tag, "diagram_index": diag, "node_index": node_i, "uid_expect": uid_expect}
    try:
        u, rows = g.node_terms_uid(target, diag, node_i)
        out.update({"node_uid_readback": u, "n_terms": len(rows),
                    "n_wired": sum(1 for r in rows if r.get("wire")),
                    "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                               "wire": r["wire"]} for r in rows]})
    except Exception as e:                                                        # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
    rec.setdefault("wired_counts", []).append(out)
    fact("%s: node uid readback %r, %r terminals, %r WIRED"
         % (tag, out.get("node_uid_readback"), out.get("n_terms"), out.get("n_wired")))
    return out


def test_I():
    rec = R["test_I"]
    target = make_scratch(rec, "I", os.path.join(g.CLAUDEDEV, "DIAG_s56_wireind_%s.vi" % STAMP))
    print("\n=================== TEST I  (indicator remedy)  scratch %s" % os.path.basename(target), flush=True)

    with D.Preload("P-I"):
        g.open_panel(target)
        time.sleep(1.0)
        census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "I BEFORE", target)

        # ---------------------------------------------------------------- I0: the TOP-LEVEL Nodes[] census,
        # read through create_indicator's OWN ladder (VI -> Block Diagram -> Nodes[]), g.node_info:2462.
        try:
            top = g.node_info(target, max_n=40)
        except Exception as e:                                                    # noqa: BLE001
            top = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        rec["top_level_nodes"] = top
        fact("I0 TOP-LEVEL Nodes[] through create_indicator's own ladder (g.node_info, max_n=40): %r" % (top,))
        gate("I0 the TOP-LEVEL Nodes[] census is non-empty", isinstance(top, list) and len(top) > 0,
             "%r entries" % (len(top) if isinstance(top, list) else top))

        # the Traverse-index-0 Diagram, for comparison with the files-first census
        # (diagram_tree_main.json key '0' = owner '', uids [22963] = net_map's junk node only)
        probes = []
        for i in (0, 1, 2):
            try:
                u, rows = g.node_terms_uid(target, 0, i)
                probes.append({"node_index": i, "node_uid": u, "n_terms": len(rows)})
            except Exception as e:                                                # noqa: BLE001
                probes.append({"node_index": i, "error": "%s: %s" % (type(e).__name__, str(e)[:120])})
        rec["traverse_diagram0_probe"] = probes
        fact("I0b Traverse Diagram index 0, Nodes[0..2] (node_uid 0 = index out of range): %r" % probes)

        # ---------------------------------------------------------------- I1: create_indicator, <= 3 attempts
        cands = [(0, 0)]
        if isinstance(top, list) and top:
            cands = [(top[i][0], 0) for i in range(min(2, len(top)))] + [(top[0][0], 1)]
        cands = cands[:3]                                   # HARD BOUND: <= 3 attempts, no loop over indices
        rec["I1"] = {"candidates": cands, "attempts": [], "new_indicator": None, "new_label": None}
        fact("I1 candidate (Nodes[] index, terminal index) list, from the top-level census: %r" % (cands,))
        for (ni, ti) in cands:
            a = {"node_index": ni, "terminal_index": ti}
            try:
                new = g.create_indicator(target, ni, ti)
                a.update({"error_verbatim": "", "new": new})
            except Exception as e:                                                # noqa: BLE001
                a.update({"error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:400]), "new": None})
            rec["I1"]["attempts"].append(a)
            fact("I1 create_indicator(Nodes[%d].Terminals[%d]) -> new %r ; error VERBATIM %r"
                 % (ni, ti, a.get("new"), a.get("error_verbatim")))
            if a.get("new"):
                rec["I1"]["new_indicator"] = a["new"]
                break
        errs = [a["error_verbatim"] for a in rec["I1"]["attempts"]]
        gate("P1 the REPAIRED create_indicator surfaces a NON-EMPTY error string on a refused call",
             any(e for e in errs) or bool(rec["I1"]["new_indicator"]),
             "errors %r" % (errs,))
        gate("I1 create_indicator produced a ControlTerminal on a top-level node terminal",
             bool(rec["I1"]["new_indicator"]), repr(rec["I1"]["new_indicator"]))

        # ---------------------------------------------------------------- I2: wire_indicators
        def _di(uid):
            try:
                return diag_index(target, uid)
            except Exception as e:                                                # noqa: BLE001
                fact("diag_index(#%d) raised %s: %s" % (uid, type(e).__name__, str(e)[:140]))
                return None
        d639 = _di(D639)
        d686 = _di(D686)
        rec["I2"] = {"diagram_index_639": d639, "diagram_index_686": d686}
        fact("I2 Diagram #%d reads Traverse index %r; Diagram #%d reads %r (re-resolved live, 38(e))"
             % (D639, d639, D686, d686))
        try:
            fn = [o["uid"] for o in g.report(target, "Function")]
            fn_i = fn.index(SRC_UID)
        except Exception as e:                                                    # noqa: BLE001
            fn, fn_i = [], None
            fact("report(Function) / index raised %s: %s" % (type(e).__name__, str(e)[:160]))
        rec["I2"].update({"function_class_count": len(fn), "src_function_traverse_index": fn_i})
        fact("I2 #%d sits at Traverse index %r of class `Function` (%d members) - wire_indicators' `index`"
             % (SRC_UID, fn_i, len(fn)))

        src_before = wired_counts(rec, "I2 BEFORE #%d (the source node)" % SRC_UID, target, d639, 25, SRC_UID)
        loop_before = wired_counts(rec, "I2 BEFORE #%d (loop 1.1, the tunnel check)" % LOOP11_UID,
                                   target, d686, 4, LOOP11_UID)
        t0 = next((t for t in src_before.get("terms", []) if t["i"] == 0), None)
        gate("I2a #%d resolves live, is class `Function`, and its t0 %r carries wire 10799"
             % (SRC_UID, SRC_TERM_NAME),
             src_before.get("node_uid_readback") == SRC_UID and fn_i is not None
             and bool(t0) and t0.get("name") == SRC_TERM_NAME and t0.get("wire") == 10799,
             repr(t0))

        # the target indicator: I1's new one if I1 produced one, else the pre-specified fallback rule
        rows = panel_rows(target)
        rec["I2"]["panel_rows_read"] = len(rows)
        unwired = [r for r in rows if r.get("indicator") and not r.get("wire")]
        rec["I2"]["unwired_indicator_rows"] = unwired
        if rec["I1"]["new_indicator"]:
            new_uids = {o.get("uid") for o in rec["I1"]["new_indicator"] if isinstance(o, dict)}
            tr = next((r for r in rows if r.get("uid") in new_uids), None)
            why = "I1's new indicator"
        else:
            tr = unwired[0] if unwired else next((r for r in rows
                                                  if r.get("label") in FALLBACK_INDICATORS), None)
            why = ("the FIRST unwired (wire 0) indicator row read live; the files-first order in "
                   "tools/bench/main_vi_panel_wiring.json is %r" % (FALLBACK_INDICATORS,))
        rec["I2"]["target_row_before"] = tr
        rec["I2"]["target_chosen_because"] = why
        fact("I2 target indicator = %r (uid %r, wire %r) - chosen because %s"
             % ((tr or {}).get("label"), (tr or {}).get("uid"), (tr or {}).get("wire"), why))

        rec["I2"]["exec_state_before_wiring"] = read_exec_state(rec, "I2 BEFORE the wiring", target)
        rec["I2"]["attempts"] = []
        if tr and fn_i is not None:
            for lab in [tr["label"]][:2]:                      # <= 2 attempts, no loop over indices
                a = {"indicator_label": lab, "src_term": SRC_TERM_NAME}
                try:
                    dt = g.wire_indicators(target, fn_i, [SRC_TERM_NAME], [lab],
                                           diagram_index=d639, node_class="Function")
                    a.update({"error_verbatim": "", "seconds": dt})
                except Exception as e:                                            # noqa: BLE001
                    a.update({"error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:400]), "seconds": None})
                rec["I2"]["attempts"].append(a)
                fact("I2 wire_indicators(Function[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
                     % (fn_i, SRC_TERM_NAME, lab, d639, a["error_verbatim"]))
                break
        else:
            fact("I2 NOT ATTEMPTED: target row %r / Function index %r could not be resolved. That is the "
                 "reading, reported as one." % (tr, fn_i))

        rec["I2"]["exec_state_after_wiring"] = read_exec_state(
            rec, "I2 IMMEDIATELY AFTER the wiring (before any Is Broken? read)", target)
        rows_after = panel_rows(target)
        tr_after = next((r for r in rows_after if r.get("uid") == (tr or {}).get("uid")), None) if tr else None
        rec["I2"]["target_row_after"] = tr_after
        fact("I2 target indicator AFTER: %r" % (tr_after,))
        src_after = wired_counts(rec, "I2 AFTER #%d (the source node)" % SRC_UID, target, d639, 25, SRC_UID)
        loop_after = wired_counts(rec, "I2 AFTER #%d (loop 1.1, the tunnel check)" % LOOP11_UID,
                                  target, d686, 4, LOOP11_UID)
        rec["I2"]["new_wire_uid_on_target"] = (tr_after or {}).get("wire")
        gate("I2b wire_indicators gave the target indicator a wire (uid was 0 before)",
             bool((tr_after or {}).get("wire")),
             "before %r -> after %r" % ((tr or {}).get("wire"), (tr_after or {}).get("wire")))
        gate("I2d #%d terminal count unchanged - no new tunnel/border object (37(e))" % LOOP11_UID,
             loop_before.get("n_terms") == loop_after.get("n_terms"),
             "%r -> %r terminals, %r -> %r wired" % (loop_before.get("n_terms"), loop_after.get("n_terms"),
                                                     loop_before.get("n_wired"), loop_after.get("n_wired")))
        fact("I2 source node #%d wired-terminal count %r -> %r (of %r / %r terminals)"
             % (SRC_UID, src_before.get("n_wired"), src_after.get("n_wired"),
                src_before.get("n_terms"), src_after.get("n_terms")))

        # ------------------------------------------------ the ORDERED SECOND PASS for `Is Broken?` (42(b))
        # The carriers of 6371004 hang off a Nodes[]-addressable SINK TERMINAL, and a front-panel
        # ControlTerminal is NOT in Nodes[], so the resulting wire is read on the SAME NET at a sink that IS
        # addressable: #10407 t0, already sourced by wire 10799 (main_vi_nodeterms.json d43 idx 24). An
        # IDEMPOTENT re-connect of that EXISTING connection - wire_delta must be 0.
        print("\n--- I2c PASS 2: the ORDERED `Is Broken?` reading, an IDEMPOTENT re-connect of the EXISTING "
              "#10686 t0 -> #10407 t0 connection on the same net (42(b); wire_delta must be 0)", flush=True)
        rec["I2"]["pass2"] = {"sink": "#10407 t0 (Nodes[24] of Diagram #639), already sourced by wire 10799",
                              "why": "a ControlTerminal is not in Nodes[], so the 6371004 carriers cannot "
                                     "address the indicator end; the same NET is read instead"}
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es, err = CONNECT_V1(target, d639, 24, 0, d639, 25, 0, V1_LABELS)
            rec["I2"]["pass2"].update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
        except Exception as e:                                                    # noqa: BLE001
            rec["I2"]["pass2"].update({"wire_delta": None, "exec_state_returned": None,
                                       "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
        for ln in buf.getvalue().rstrip().splitlines():
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        rec["I2"]["pass2"]["op_indicators"] = op_indicators()
        ib = rec["I2"]["pass2"]["op_indicators"].get("Is Broken?")
        rec["I2"]["is_broken_ordered"] = ib
        fact("I2c ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r). A True here is "
             "a LEGITIMATE reading (type mismatch), not a failure to hide."
             % (ib, rec["I2"]["pass2"]["op_indicators"].get("UID 2"),
                rec["I2"]["pass2"].get("error_verbatim"), rec["I2"]["pass2"].get("wire_delta")))
        gate("I2c the ORDERED second-pass `Is Broken?` read returned a boolean", isinstance(ib, bool), repr(ib))
        rec["I2"]["exec_state_after_is_broken_SUSPECT"] = read_exec_state(
            rec, "I2 after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918)", target)

        finish(rec, "I", target)
    dump()


# ============================================================================================= MAIN
def main():
    print("=== diag_s56_transport2  %s   (cycle 56 dispatch 3; TEST L + TEST I; NO VI IS RUN, 34(f); no new "
          "op, no new device, no GUI action; CHOOSES NO ROUTE)" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (dispatch 2 left the instance UP after a bgrun kill; fresh baseline ~31,500): %r"
         % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---- B: the restart the brief orders (44(e); dispatch 2 left pid 4704 up)
    D.fresh("T2b RESTART (mechanical pre-batch restart, 44(e); standing restart permission, CLAUDE.md 3)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    # ---- the cleanup owed from dispatch 2: ONE attempt each, no retry, no workaround
    for p in LEFTOVERS:
        e = {"path": p, "existed": os.path.exists(p)}
        if e["existed"]:
            try:
                os.remove(p)
                e["removed"] = not os.path.exists(p)
                e["error_verbatim"] = ""
            except Exception as ex:                                               # noqa: BLE001
                e["removed"] = False
                e["error_verbatim"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
        R["leftover_cleanup"].append(e)
        fact("cleanup (ONE attempt, no retry): %s existed=%r removed=%r error VERBATIM %r"
             % (os.path.basename(p), e["existed"], e.get("removed"), e.get("error_verbatim")))
    dump()

    # ---- TEST L first (it has no dependency on indicator creation), then TEST I
    try:
        test_L()
    except Stop as s:
        fact("TEST L stopped at a FATAL gate: %s" % s)
    try:
        test_I()
    except Stop as s:
        fact("TEST I stopped at a FATAL gate: %s" % s)

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                        # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])
    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as s:
        fact("FATAL: %s" % s)
        dump()
        print("\n=== GATES %d pass / %d fail (FATAL stop)" % (len(passes), len(fails)), flush=True)
        sys.exit(1)
