r"""diag_d0_trace_path.py - CYCLE 30 dispatch 2, run 2: WHERE the trace file is written and WHAT builds its name.

Run 1 (tools/bench/diag_d0_inventory.log) answered (a)(b)(c) and the offline half of (d), and left two
things unresolved that only the machine can settle:

  1. `base path/filename` on `save N xyz traces.vi` #6384 (diagram 19) is fed by wire 5104, whose only two
     terminals in the NODE census are both sinks (#6384 t11 and the frame loop #637 t17). Its SOURCE is a
     NON-node GObject (a control terminal, a constant or a tunnel), which no offline census covers.
  2. `main_vi_nodeterms.json` was censused on the WORKING COPY, which carries Claude's 2026-09-01 TIFF
     FIXTURE INSERTION (`IMAQ Write TIFF File 2` #22700, `Build Path` #23020 - pinned memory
     "tiff-writer-is-a-fixture-insertion-not-original"). So the `Build Path` / `Strip Path` rows run 1
     printed may belong to the FIXTURE, not to the original's trace path. That must not be reported as
     the original's behaviour without checking the D0 copy itself.

READ-ONLY. No VI is RUN (op VIs only), no motor, no camera, no GUI click. Original preloaded read-only,
md5 before and after; handle count before and after.

PRIOR ART REUSED, nothing new built: `gscript.report_all` (OpReportAll_v0) for uid->class membership;
`tools/bench/diag_tunnelsource_onehop.py:read_terminal/wire_terminals` (OpWireSource_v5, UID-addressed -
the `UID 2` caveat in docs/toolkit-capabilities.md:60 is honoured by that wrapper).

PREDICTION CONTRACT
  T1 report_all(D0 copy,'GObject') returns ~9996 objects (run 1 measured 9996 on this same copy).
  T2 DISCRIMINATOR for the fixture question: uids 22700 (IMAQ Write TIFF) and 23020 (Build Path) are
     ABSENT from the D0 copy if the pinned memory is right, PRESENT if it is wrong. Either answer is a
     measurement; nothing is inferred from absence alone because #6384/#376/#637 are checked in the same
     call as positive controls.
  T3 wire 5104 has exactly one terminal with Is Source? TRUE; its owner class and uid are printed.
  T4 wire 5303 (the `Track File Path` INDICATOR's terminal wire, is_source False in run 1) likewise.
  T5 node 26615's terminal list (offline) names it as a File-Dialog-shaped node.
  T6 md5 of the ORIGINAL identical before and after.

  py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_d0_trace_path.log -- py -u tools/bench/diag_d0_trace_path.py
"""
import hashlib
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import gscript as g                                   # noqa: E402
from bench_prep import labview_handles                # noqa: E402
import diag_tunnelsource_onehop as hop                # noqa: E402

ORIG = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
COPY = (r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
        r"\Track_D0_copy_20260918.vi")
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")
OUT = os.path.join(HERE, "d0_trace_path.json")

g._run.__defaults__ = (6.0, 420.0)

# positive controls (must be present) and fixture suspects (the actual question)
CONTROLS = {6384: "save N xyz traces.vi (diagram 19)", 376: "save trace.vi (diagram 43)",
            637: "the frame WhileLoop", 26615: "the 'prompt (Choose or enter file path)' node"}
SUSPECTS = {22700: "IMAQ Write TIFF File 2 (Claude fixture 2026-09-01?)",
            23020: "Build Path (Claude fixture 2026-09-01?)",
            23175: "Strip Path (Claude fixture 2026-09-01?)",
            22703: "Format Into String (Claude fixture 2026-09-01?)"}
WIRES = {5104: "base path/filename into save N xyz traces #6384",
         5303: "the 'Track File Path' panel object's terminal wire",
         3769: "the 'Cal File Path' panel object's terminal wire"}

PASS = []


def gate(label, ok, detail=""):
    PASS.append((label, bool(ok)))
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"   {'PASS' if ok else 'FAIL'} {label}{(' - ' + detail) if detail else ''}", flush=True)
    return ok


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def offline_node(uid):
    """Every terminal of `uid` as the node census recorded it (working copy, 2026-09-14)."""
    with open(NODETERMS, encoding="utf-8") as f:
        nt = json.load(f)
    for dk, dv in nt.get("diagrams", {}).items():
        for n in dv.get("nodes", []):
            if n.get("uid") == uid:
                return dk, dv.get("owner", ""), n.get("terms", [])
    return None, None, None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {}
    out["md5_orig_before"] = md5(ORIG)
    out["handles_before"] = labview_handles()
    print(f"md5 ORIGINAL BEFORE {out['md5_orig_before']}", flush=True)
    print(f"LabVIEW handles BEFORE {out['handles_before']}", flush=True)

    print("\n=== T5 the File-Dialog-shaped node #26615, offline ===", flush=True)
    dk, owner, terms = offline_node(26615)
    out["node_26615"] = {"diagram": dk, "owner": owner, "terms": terms}
    if terms:
        print(f"   diagram {dk} (owner {owner}), {len(terms)} terminals:", flush=True)
        for t in terms:
            print(f"      t[{t.get('i')}] {str(t.get('name'))!r:<44} "
                  f"{'SRC' if t.get('is_source') else 'sink'} wire {t.get('wire')}", flush=True)
    gate("T5 node 26615 terminals read offline", bool(terms), f"{len(terms or [])} terminals")

    try:
        app = g.lv()
        vi_orig = app.GetVIReference(ORIG, "", False, 0)
        print(f"\n   original resident, ExecState {int(vi_orig.ExecState)}", flush=True)
        vi_copy = app.GetVIReference(COPY, "", False, 0)
        print(f"   D0 copy loaded, ExecState {int(vi_copy.ExecState)}", flush=True)

        print("\n=== T1/T2 which of these objects EXIST in the D0 copy (a plain copy of the ORIGINAL) ===",
              flush=True)
        objs = g.report_all(COPY, "GObject")
        by_uid = {o["uid"]: o for o in objs}
        gate("T1 report_all('GObject') ~9996", abs(len(objs) - 9996) <= 50, f"{len(objs)} objects")
        out["gobject_total"] = len(objs)
        out["present"] = {}
        for title, table in (("POSITIVE CONTROLS (must be present)", CONTROLS),
                             ("FIXTURE SUSPECTS (the question)", SUSPECTS)):
            print(f"\n   -- {title}", flush=True)
            for uid, what in table.items():
                o = by_uid.get(uid)
                out["present"][uid] = {"what": what, "present": bool(o),
                                       "class": o.get("class") if o else None,
                                       "pos": o.get("pos") if o else None,
                                       "owner": o.get("owner") if o else None}
                print(f"      uid {uid:<7} {'PRESENT' if o else 'ABSENT '}  class "
                      f"{str(o.get('class')) if o else '-':<22.22} pos {str(o.get('pos')) if o else '-':<16} "
                      f"owner {str(o.get('owner')) if o else '-':<14.14} {what}", flush=True)
        gate("T2a all 4 positive controls present in the D0 copy",
             all(out["present"][u]["present"] for u in CONTROLS),
             ", ".join(str(u) for u in CONTROLS if not out["present"][u]["present"]) or "all present")
        absent = [u for u in SUSPECTS if not out["present"][u]["present"]]
        print(f"\n   => fixture suspects ABSENT from the D0 copy: {absent or 'none'}", flush=True)
        print("      (ABSENT confirms the pinned memory: those nodes are Claude's 2026-09-01 TIFF fixture in the "
              "WORKING COPY, not the original's trace path. PRESENT would refute it.)", flush=True)
        out["fixture_absent"] = absent

        print("\n=== T3/T4 who SOURCES the path wires (OpWireSource_v5, UID-addressed, on the D0 copy) ===",
              flush=True)
        out["wires"] = {}
        for w, what in WIRES.items():
            print(f"\n   -- wire {w}: {what}", flush=True)
            try:
                src, rows = hop.wire_source(COPY, w)
            except Exception as e:
                print(f"      FAILED {str(e)[:140]}", flush=True)
                out["wires"][w] = {"what": what, "error": str(e)[:200]}
                continue
            out["wires"][w] = {"what": what, "rows": rows,
                               "source": {"owner_class": src["owner_class"], "owner_uid": src["owner_uid"]}
                               if src else None}
            if src:
                oc, ou = src["owner_class"], src["owner_uid"]
                extra = by_uid.get(ou, {})
                print(f"      SOURCE = {oc!r} uid {ou}   (report_all class {extra.get('class')!r}, "
                      f"pos {extra.get('pos')}, owner {extra.get('owner')!r})", flush=True)
            else:
                print("      no single source terminal resolved on this wire", flush=True)
        gate("T3 wire 5104 resolved to one source",
             bool(out["wires"].get(5104, {}).get("source")),
             str(out["wires"].get(5104, {}).get("source")))
        gate("T4 wire 5303 resolved to one source",
             bool(out["wires"].get(5303, {}).get("source")),
             str(out["wires"].get(5303, {}).get("source")))
    except Exception:
        traceback.print_exc()
        gate("T9 no exception", False)
    finally:
        try:
            g.reset()
        except Exception:
            pass
        out["handles_after"] = labview_handles()
        out["md5_orig_after"] = md5(ORIG)
        gate("T6 ORIGINAL md5 unchanged", out["md5_orig_after"] == out["md5_orig_before"],
             f"{out['md5_orig_before']} -> {out['md5_orig_after']}")
        print(f"\nmd5 ORIGINAL AFTER  {out['md5_orig_after']}", flush=True)
        print(f"LabVIEW handles AFTER {out['handles_after']} (before {out['handles_before']})", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    npass = sum(1 for _, ok in PASS if ok)
    print(f"\n=== GATES {npass} pass / {len(PASS) - npass} fail ===", flush=True)
    for lab, ok in PASS:
        if not ok:
            print(f"    FAILING: {lab}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
