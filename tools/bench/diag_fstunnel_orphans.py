r"""diag_fstunnel_orphans.py - READ-ONLY DIAGNOSTIC (builds no op, saves no VI, writes no op file).

WHY: tools/bench/build_opfstunnelterm_v1_run1.log:76 named the unwired sinks at the B4 failure as nodes
  43 ('password ("")', 'type specifier VI Refnum (for type only)', 'options', 'application reference (local)'),
  124 ('', 'Other Refnum', 'Traverse Generated Code (F)', '') and 990 (SIX sinks with EMPTY names).
Nobody has ever read WHAT those three nodes ARE. This file measures their class, label/style and full terminal
list (a) on a FRESH copy of the donor, before any edit, and (b) at the same point the failing run reached, after
the recipe's edit sequence. Measurement only - no diagnosis is written here.

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "before creating any new op, tool or recipe"):
  * `grep "^def " tools/gscript.py` - node_terms_uid, node_info (Nodes[] style + label, gscript.py:2394),
    report_all (per-object ClassName, :434), uids, count, exec_state, open_panel/close_panel, build_property,
    create_control, wire, wire_control, delete_object, fp_labels: ALL reused, NONE added. No reader for a
    Property Node's SELECTED ITEMS exists anywhere in the fleet (grep 'Property Item|Items\[\]|prop_items' over
    tools/gscript.py + docs/toolkit-capabilities.md returns only the 6DE8D802 id line, :185) - so that part of
    the question is answered by what CAN be read (class, style, label, terminal names) and the gap is REPORTED,
    not inferred around.
  * `tools/recipes/build_opfstunnelterm_v1.py` module-level helpers (sweep/trow/twire/has/cidx/node_index_of/
    ctl_labels/SPEC/T_CAST_OUT/DONOR/P_UID/P_CONN_WIRE) are IMPORTED, so stage 2 is the same edit path that
    failed. Importing has no side effects (its work is under `if __name__ == "__main__"`).
  * `tools/bench/diag_fstunnel_wire_semantics.py` - the scratch/md5/handle/cleanup skeleton and the stage-2
    reproduction are taken from it, not re-invented. `ls tools/recipes tools/bench` - no existing file reads a
    node's class+label+terminals by uid.
NO op VI is created or written to disk; the recipe's own OP_OUT/OP_IN paths are never touched. The scratch is a
copy of the DONOR under a unique pid-stamped name, closed WITHOUT saving and DELETED in the same run. No motor,
no serial, no camera; `motor_gate.py --execute` is not called (P1).

PREDICTION CONTRACT (every line prints PASS/FAIL; the run continues past a miss):
  P0a md5 of Min_Track...3StateClamping.vi, Min_Track...V6_ParallelLoop.vi and OpWireSource_v5.vi identical
      before and after.  P0b the scratch VI is created AND deleted in the same run.
  P1  the fresh donor copy loads with ExecState 1 and the sweep finds >=19 nodes on diagram 0.
  P2  all three uids 43, 124, 990 are present in the FRESH copy's sweep (i.e. they come from the donor and are
      not created by the recipe). A miss is itself the answer and is printed, not worked around.
  P3  for each of 43/124/990 a class (report_all ClassName), a Nodes[] style + label (node_info) and the full
      terminal list (index, name or the literal string EMPTY, direction, wire uid) are printed for the FRESH
      copy. Pure measurement - always PASS if the reads returned.
  P4  the edit sequence of build_opfstunnelterm_v1.build_one('OUT') up to the B4 gate is reproduced on the
      scratch, ExecState 0 is reached, and the SAME three nodes are re-read in that state, so the two states can
      be compared line by line.
  P5  the recipe-created uids (PN_A, PN_B, the two UID nodes, the Connected-Wire node) are listed with the
      recipe line that creates each, so "created by the recipe" vs "from the donor" is a citation, not a claim.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_orphans.log -- py -u tools/bench/diag_fstunnel_orphans.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                                   # noqa: E402
import build_opfstunnelterm_v1 as R                   # noqa: E402  - helpers + SPEC reused verbatim
from build_opconstvalue_v1 import fresh, lv_pid       # noqa: E402

SCR = os.path.join(g.CLAUDEDEV, f"SCRATCH_fsorphans_{os.getpid()}.vi")
OUT = os.path.join(HERE, "diag_fstunnel_orphans.json")
FILES = [R.ORIG_3STATE, R.V6, R.DONOR]
TARGETS = [43, 124, 990]
# uid -> the recipe line that CREATES it, from tools/recipes/build_opfstunnelterm_v1.py (read 2026-09-18)
CREATED_BY = {
    "pn_a": "build_opfstunnelterm_v1.py:451  g.build_property(op, cls, [(pid_a, False)], (900, 1250))",
    "seed control": "build_opfstunnelterm_v1.py:455  g.create_control(op, n_a, 0)",
    "pn_b": "build_opfstunnelterm_v1.py:481  g.build_property(op, cls, [(pid_b, False)], (900, 1450))",
    "pn_a_uid": "build_opfstunnelterm_v1.py:484  g.build_property(op, 'VI Server:GObject', [(P_UID, False)])",
    "pn_b_uid": "build_opfstunnelterm_v1.py:487  g.build_property(op, 'VI Server:GObject', [(P_UID, False)])",
    "pn_b_cw": "build_opfstunnelterm_v1.py:492  g.build_property(op, 'VI Server:Terminal', [(P_CONN_WIRE, False)])",
    "pn_b_cwu": "build_opfstunnelterm_v1.py:495  g.build_property(op, 'VI Server:GObject', [(P_UID, False)])",
}
CLASSES = ["Property", "Invoke", "Function", "SubVI", "Constant", "Node"]
RES = {"gates": [], "md5": {}, "handles": {}, "fresh": {}, "at_b4": {}, "created": {}, "notes": []}
g._run.__defaults__ = (6.0, 120.0)


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:400]}", flush=True)
    RES["notes"].append({"label": label, "value": str(value)[:600]})


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def snapshot(tag):
    d = {os.path.basename(p): md5(p) for p in FILES}
    RES["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for k, v in d.items():
        print(f"   {v}  {k}", flush=True)
    return d


def handles(tag):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                              "Measure-Object -Property HandleCount -Sum).Sum"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out else 0
    except Exception as e:
        n = f"ERR {str(e)[:60]}"
    RES["handles"][tag] = n
    print(f"  HANDLES {tag}: {n}  (fresh baseline ~31,500)", flush=True)
    return n


def class_map():
    """uid -> [(Traverse class asked for, ClassName the reporter returned)] for every class we ask about."""
    m = {}
    for cls in CLASSES:
        try:
            for o in g.report_all(SCR, cls):
                m.setdefault(int(o["uid"]), []).append((cls, o["class"], tuple(o["pos"]), o["owner"]))
        except Exception as e:
            note(f"report_all({cls}) raised", str(e)[:160])
    return m


def styles():
    """Nodes[] index -> (style name, label text) from OpNodeInfo_v0 (gscript.node_info)."""
    try:
        return {i: (st, lab) for i, st, lab in g.node_info(SCR, max_n=40)}
    except Exception as e:
        note("node_info raised", str(e)[:200])
        return {}


def read_targets(tag):
    """Measure class / style / label / full terminal list for every uid in TARGETS, in the CURRENT state."""
    by = R.sweep(SCR)
    cm = class_map()
    st = styles()
    rec = {"uids_on_diagram": sorted(by), "node_count": len(by), "exec_state": None, "nodes": {}}
    try:
        rec["exec_state"] = g.exec_state(SCR)
    except Exception as e:
        rec["exec_state"] = f"EXC {str(e)[:80]}"
    print(f"\n   ===== STATE '{tag}': {len(by)} nodes on diagram 0, ExecState {rec['exec_state']}", flush=True)
    print(f"         uids: {sorted(by)}", flush=True)
    for u in TARGETS:
        if u not in by:
            rec["nodes"][u] = {"present": False}
            print(f"\n   --- uid {u}: NOT PRESENT on diagram 0 in state '{tag}'", flush=True)
            continue
        idx, rows = by[u]
        terms = [{"i": r["i"], "name": (r["name"] if r["name"] != "" else "EMPTY"),
                  "direction": ("source/output" if r["is_source"] else "sink/input"),
                  "wire": int(r["wire"])} for r in rows]
        style, label = st.get(idx, (None, None))
        rec["nodes"][u] = {"present": True, "nodes_index": idx, "classes": cm.get(u, []),
                           "style": style, "label": label, "terminals": terms}
        print(f"\n   --- uid {u}  Nodes[{idx}]  style={style!r}  label={label!r}", flush=True)
        print(f"       report_all classes: {cm.get(u, 'NOT RETURNED BY ANY report_all CLASS ASKED')}", flush=True)
        for t in terms:
            print(f"       T[{t['i']:2d}] {t['name']!r:52s} {t['direction']:13s} wire {t['wire']}", flush=True)
    RES[tag] = rec
    return rec


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("READ-ONLY DIAGNOSTIC - no op built, no VI saved. Contract P0..P5 in the docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    snapshot("before")
    rc = 0
    try:
        fresh()
        handles("after a fresh LabVIEW")
        print(f"   LabVIEW pid after fresh(): {lv_pid()}", flush=True)
        op_path, cls, pid_a, short_a, pid_b, short_b, _lab = R.SPEC["OUT"]
        print(f"\n   STAGE 1: a FRESH scratch copy of the donor, no edits\n      donor  {R.DONOR}\n"
              f"      scratch {SCR}", flush=True)
        shutil.copy2(R.DONOR, SCR)
        time.sleep(0.4)
        g.open_panel(SCR)
        time.sleep(1.0)
        fr = read_targets("fresh")
        must("P1 the fresh donor copy is LEGAL (ExecState 1) and has >=19 nodes on diagram 0",
             fr["exec_state"] == 1 and fr["node_count"] >= 19,
             f"ExecState {fr['exec_state']}, {fr['node_count']} nodes")
        missing = [u for u in TARGETS if not fr["nodes"][u].get("present")]
        must("P2 uids 43, 124 and 990 are ALL present in the FRESH donor copy (so the recipe does not create them)",
             not missing, f"missing in the fresh copy: {missing}" if missing else "all three present")
        must("P3 class + style + label + full terminal list were read for every target uid", True,
             {u: (fr["nodes"][u].get("style"), len(fr["nodes"][u].get("terminals") or [])) for u in TARGETS})
        for k, v in CREATED_BY.items():
            print(f"   P5 recipe-created object {k:9s} <- {v}", flush=True)
        RES["created"] = CREATED_BY

        # ---------------------------------------------------------------- STAGE 2: reach the B4 failure state
        print("\n   STAGE 2: reproducing build_opfstunnelterm_v1.build_one('OUT') edits on the SAME scratch, "
              "up to the B4 gate (nothing is saved)", flush=True)
        inv0 = g.uids(SCR, "Invoke")

        def purge():
            junk = [u for u in g.uids(SCR, "Invoke") if u not in inv0]
            if junk:
                order = [o["uid"] for o in g.report_all(SCR, "Invoke")]
                for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                    g.delete_object(SCR, "Invoke", i, verify=False)
                print(f"   purged {len(junk)} junk Invoke(s)", flush=True)

        by = R.sweep(SCR)
        pn_terms = next((u for u in by if R.has(by, u, "Terms[]", True)), None)
        w_terms = R.twire(by, pn_terms, "Terms[]") if pn_terms else None
        ia = next((u for u in by if R.has(by, u, "array", False) and R.twire(by, u, "array") == w_terms), None) \
            if w_terms else None
        el_w = R.twire(by, ia, "element") if ia else None
        tmsc = next((u for u in by if R.has(by, u, "target class") and R.has(by, u, R.T_CAST_OUT, True)
                     and R.twire(by, u, R.T_CAST_OUT) == R.twire(by, pn_terms, "reference")), None) \
            if pn_terms else None
        consumers = [u for u in by if R.trow(by, u, "reference") is not None
                     and R.twire(by, u, "reference") == el_w] if el_w else []
        w_tc0 = R.twire(by, tmsc, "target class") if tmsc else None
        print(f"   Terms[] PN {pn_terms} | Index Array {ia} | TMSC {tmsc} | back-half sinks {consumers}", flush=True)
        if not must("P4a the front section was found on the scratch (same sweep as the recipe)",
                    bool(pn_terms and ia and tmsc and consumers),
                    f"terms {pn_terms} ia {ia} tmsc {tmsc} consumers {consumers}"):
            return 3
        for _cls, uid in (("Node", pn_terms), ("Node", ia)):
            order = [o["uid"] for o in g.report_all(SCR, _cls)]
            if uid in order:
                g.delete_object(SCR, _cls, order.index(uid), verify=False)
                print(f"   deleted {_cls} #{uid}", flush=True)
        for w in (w_terms, el_w, w_tc0):
            if not w:
                continue
            order = [o["uid"] for o in g.report_all(SCR, "Wire")]
            if w in order:
                g.delete_object(SCR, "Wire", order.index(w), verify=False)
                print(f"   deleted Wire #{w}", flush=True)
        pn_a = g.build_property(SCR, cls, [(pid_a, False)], (900, 1250))[0]["uid"]
        purge()
        n_a = R.node_index_of(SCR, pn_a)
        c0 = set(R.ctl_labels(SCR))
        g.create_control(SCR, n_a, 0)
        purge()
        new_c = [l for l in R.ctl_labels(SCR) if l not in c0]
        print(f"   PN_A uid {pn_a} (Nodes[{n_a}], {short_a}); new control(s): {new_c}", flush=True)
        if not must("P4b create_control on the PN's `reference` made exactly one new CONTROL", len(new_c) == 1,
                    str(new_c)):
            return 3
        seed = new_c[0]
        by = R.sweep(SCR)
        w_seed = R.twire(by, pn_a, "reference")
        if w_seed:
            order = [o["uid"] for o in g.report_all(SCR, "Wire")]
            if w_seed in order:
                g.delete_object(SCR, "Wire", order.index(w_seed), verify=False)
                print(f"   deleted the seed->PN_A wire #{w_seed}", flush=True)
        g.wire_control(SCR, [seed], "Function", R.cidx(SCR, "Function", tmsc), ["target class"])
        by = R.sweep(SCR)
        print(f"   seed {seed!r} -> TMSC `target class` wire {R.twire(by, tmsc, 'target class')}", flush=True)
        R.wire_checked(SCR, "Function", tmsc, R.T_CAST_OUT, "Property", pn_a, "reference", tag="[SCR] TMSC->PN_A")
        purge()
        pn_b = g.build_property(SCR, cls, [(pid_b, False)], (900, 1450))[0]["uid"]
        purge()
        R.wire_checked(SCR, "Function", tmsc, R.T_CAST_OUT, "Property", pn_b, "reference", tag="[SCR] TMSC->PN_B")
        pn_a_uid = g.build_property(SCR, "VI Server:GObject", [(R.P_UID, False)], (1300, 1250))[0]["uid"]
        purge()
        R.wire_checked(SCR, "Property", pn_a, short_a, "Property", pn_a_uid, "reference", tag="[SCR] A->UID")
        pn_b_uid = g.build_property(SCR, "VI Server:GObject", [(R.P_UID, False)], (1300, 1450))[0]["uid"]
        purge()
        R.wire_checked(SCR, "Property", pn_b, short_b, "Property", pn_b_uid, "reference", tag="[SCR] B->UID")
        pn_b_cw = g.build_property(SCR, "VI Server:Terminal", [(R.P_CONN_WIRE, False)], (1300, 1650))[0]["uid"]
        purge()
        R.wire_checked(SCR, "Property", pn_b, short_b, "Property", pn_b_cw, "reference", tag="[SCR] B->ConnWire")
        pn_b_cwu = g.build_property(SCR, "VI Server:GObject", [(R.P_UID, False)], (1700, 1650))[0]["uid"]
        purge()
        R.wire_checked(SCR, "Property", pn_b_cw, "Wire", "Property", pn_b_cwu, "reference",
                       tag="[SCR] ConnWire->UID")
        for k, u in enumerate(consumers):
            ucls = next((c for c in ("Property", "Function", "SubVI", "Node") if u in g.uids(SCR, c)), None)
            g.wire(SCR, "Property", R.cidx(SCR, "Property", pn_a), short_a,
                   ucls, R.cidx(SCR, ucls, u), "reference", branch=True)
            print(f"   back-half sink #{u} ({ucls}) re-fed from {short_a} ({k + 1}/{len(consumers)})", flush=True)
        purge()
        es = g.exec_state(SCR)
        RES["created_uids"] = {"pn_a": pn_a, "pn_b": pn_b, "pn_a_uid": pn_a_uid, "pn_b_uid": pn_b_uid,
                               "pn_b_cw": pn_b_cw, "pn_b_cwu": pn_b_cwu, "seed": seed, "tmsc": tmsc,
                               "consumers": consumers}
        print(f"   recipe-created uids on the scratch: {json.dumps(RES['created_uids'], default=str)}", flush=True)
        must("P4c the scratch reproduced the failing state (ExecState 0 after the back half is re-fed)", es == 0,
             f"ExecState {es}")
        read_targets("at_b4")
    except Exception as e:
        print(f"\n   *** the run raised: {type(e).__name__}: {str(e)[:400]}", flush=True)
        RES["exception"] = f"{type(e).__name__}: {str(e)[:400]}"
        rc = 3
    finally:
        try:
            g.close_panel(SCR)      # NOT saved: closing an unsaved panel discards every edit (gscript.py:1202)
        except Exception as e:
            print(f"   close_panel: {str(e)[:120]}", flush=True)
        time.sleep(0.5)
        gone = None
        try:
            if os.path.exists(SCR):
                os.remove(SCR)
            gone = not os.path.exists(SCR)
        except Exception as e:
            gone = f"ERR {str(e)[:120]}"
        must("P0b the scratch VI was created and DELETED in the same run", gone is True, f"{SCR} -> {gone}")
        handles("at the end")
        after_md5 = snapshot("after")
        same = all(RES["md5"]["before"][k] == after_md5[k] for k in after_md5)
        must("P0a every original + the donor is byte-identical before and after", same,
             json.dumps(after_md5)[:300])
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, ensure_ascii=False, default=str)
        print(f"\n   -> {OUT}", flush=True)
        bad = [x["label"] for x in RES["gates"] if not x["ok"]]
        print(f"\nGATES {len(RES['gates']) - len(bad)}/{len(RES['gates'])} pass" +
              (f"; failing: {bad}" if bad else ""), flush=True)
        rc = rc or (0 if not bad else 3)
    return rc


if __name__ == "__main__":
    sys.exit(main())
