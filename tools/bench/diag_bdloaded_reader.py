r"""diag_bdloaded_reader.py - attempt 2 at the Metrics flag reader, and the falsifier test it enables.

WHAT RUN 1 SETTLED (tools/bench/diag_load_vs_editmode.log, 2026-09-16, BGRUN END rc=0 after 112s):
    A0  no load at all      -> 4 -> 4   NOTHING removed
    A2  VI.Block Diagram 23C read (node_info), NO panel -> 4 -> 4   NOTHING removed
    A3  OpenFrontPanel(activate=False)                  -> 4 -> 3   removed uid 115
    A4  GObject.Move on the same 23C-loaded panel-less copy: (853,300) -> (853,300)  DID NOT MOVE
  so the decline is GENERAL (not delete-specific) and the 23C read is NOT sufficient. The action is already
  decided by those counts: `ensure_loaded` keeps `open_panel`.

WHAT IS STILL UNMEASURED, and it is exactly codex's falsifier (archive/peer/2026-09-16-openpanel-ab.md):
    "The load-state claim is falsified if `Metrics:Block Diagram Loaded` is TRUE before Delete, yet Delete still
     does nothing until `OpenFrontPanel` is called."
  Run 1 could not read that flag: the reader VI came out BROKEN (ExecState 0) after `connect2`, so `save()`
  refused it (correctly) and every arm ran with flags=None. Without the flag two readings survive:
    (i)  BDLoaded TRUE after the 23C read  => falsifier MET: the variable is panel/EDIT-MODE context.
    (ii) BDLoaded FALSE after the 23C read => the loader never loaded; load state is still a live explanation
         and `node_info` is simply the wrong primitive (its diagram ref is closed again inside the op).

WHY RUN 1's READER BROKE - measured here rather than guessed (CLAUDE.md "when a diagnosis is GUESSED twice,
build the reader"): run 1 printed only `wire delta 0, ExecState 0` AFTER connect2 and never sampled ExecState
between the steps, so "the branch broke it" and "build_property broke it" are indistinguishable. This run
samples ExecState after EVERY step and prints the PN's own terminal wiring, and it moves the node to (2400,60)
- far from the donor's For Loop, since a node created at (60,900) may have landed inside that structure while
owned by diagram 0.

PREDICTION CONTRACT
  R1 ExecState is 1 after the copy and after set_auto_error_handling.
  R2 after build_property the VI is BROKEN (a Property Node with a bare `reference` is a broken node) - this is
     expected, not a failure; R3 is what must clear it.
  R3 after connect2 the PN's terminal 0 (`reference`) carries a wire uid != 0 AND ExecState returns to 1.
     If terminal 0 is still bare -> connect2 declined; if it is wired and ExecState is still 0 -> the wire is
     broken (type), and remove_bad_wires + a re-read says which.
  F1 on an untouched fresh copy: Metrics:Block Diagram Loaded == FALSE  (this is the claim the whole patch rests
     on; TRUE would mean Traverse/GetVIReference already load it and the 26-wrapper story needs rewriting).
  F2 after node_info (VI.Block Diagram 23C): Block Diagram Loaded == TRUE  -> codex's falsifier is MET, because
     run 1 already showed Delete and Move both fail in exactly that state. FALSE => reading (ii) above.
  F3 after open_panel: Block Diagram Loaded == TRUE and Delete removes exactly one (repeat of A3, as the paired
     positive control read through the same instrument).

Scratch discipline: reader op and every arm copy are created and deleted in this run. No original opened.

  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_bdloaded_reader.log -- py -u tools/bench/diag_bdloaded_reader.py
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

ARM_DONOR = "OpFPLabels_v0.vi"
ARM_CLASS = "Property"
READER_DONOR = "OpReportAll_v0.vi"
OUT = os.path.join(HERE, "diag_bdloaded_reader.json")
RESULT = {"gates": [], "steps": [], "flags": {}}
PID = os.getpid()
SCRATCH = []                 # every scratch path, registered at creation, deleted in the finally block


def gate(label, ok, detail=""):
    RESULT["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}" + (f"   {detail}" if detail else ""), flush=True)
    return bool(ok)


def step(path, tag):
    st = g.exec_state(path)
    RESULT["steps"].append({"tag": tag, "exec_state": st})
    print(f"  [{tag}] ExecState {st}", flush=True)
    return st


def build_reader():
    src = os.path.join(g.CLAUDEDEV, READER_DONOR)
    path = os.path.join(g.CLAUDEDEV, f"ScratchBDL2_{PID}.vi")
    if os.path.exists(path):
        os.remove(path)
    shutil.copy2(src, path)
    SCRATCH.append(path)     # registered BEFORE anything can raise: run 1 and run 2 both left the copy on disk
    info = {"path": path}    # because cleanup keyed off the return value of this function (fixed 2026-09-16)
    step(path, "after copy")
    g.set_auto_error_handling(path, False)
    gate("R1 ExecState 1 after copy + set_auto_error_handling", step(path, "after AEH off") == 1)

    nodes = g.node_info(path, max_n=40)
    oref_i = [i for i, s, _l in nodes if "Open VI Reference" in str(s)][0]
    src_term = [t["i"] for t in g.node_terms(path, 0, oref_i)
                if t["is_source"] and str(t["name"]).strip() == "vi reference"][0]
    n0 = len(nodes)
    g.build_property(path, "VI Server:VI", [("291", False), ("292", False)], (2400, 60))
    st_pn = step(path, "after build_property")
    gate("R2 the VI is broken while the new PN's `reference` is bare (expected)", st_pn == 0, f"ExecState {st_pn}")
    nodes2 = g.node_info(path, max_n=40)
    if len(nodes2) != n0 + 1:
        raise RuntimeError(f"Nodes[] went {n0} -> {len(nodes2)}")
    pn_i = len(nodes2) - 1
    pterms = g.node_terms(path, 0, pn_i)
    print(f"  PN[{pn_i}] terminals: {[(t['i'], t['name'], t['is_source'], t['wire']) for t in pterms]}", flush=True)
    ref_in = [t for t in pterms if not t["is_source"] and str(t["name"]).strip() == "reference"][0]

    dw, st = g.connect2(path, 0, pn_i, ref_in["i"], oref_i, src_term)
    pterms2 = g.node_terms(path, 0, pn_i)
    wired = [t for t in pterms2 if t["i"] == ref_in["i"]][0]["wire"]
    print(f"  connect2 -> wire delta {dw}, ExecState {st}, PN.reference wire uid {wired}", flush=True)
    print(f"  PN[{pn_i}] terminals now: {[(t['i'], t['name'], t['wire']) for t in pterms2]}", flush=True)
    if st != 1:
        g.remove_bad_wires_scripted(path)
        st = step(path, "after remove_bad_wires")
        pterms3 = g.node_terms(path, 0, pn_i)
        wired = [t for t in pterms3 if t["i"] == ref_in["i"]][0]["wire"]
        print(f"  after RBW: PN.reference wire uid {wired}", flush=True)
    gate("R3 PN.reference is wired AND the VI is whole again", bool(wired) and st == 1,
         f"wire={wired} ExecState={st}")
    if st != 1:
        raise RuntimeError(f"reader still broken (ExecState {st}, reference wire {wired})")

    labels = {}
    for key, term in (("fp", 0), ("bd", 1)):
        outs = [t for t in g.node_terms(path, 0, pn_i) if t["is_source"]
                and str(t["name"]).strip().lower() not in ("reference out", "dup reference", "error out")]
        before = {row[1] for row in g.fp_labels(path)}
        g.create_indicator(path, pn_i, outs[term]["i"])
        new = sorted({row[1] for row in g.fp_labels(path)} - before)
        if len(new) != 1:
            raise RuntimeError(f"create_indicator on {outs[term]['name']!r} produced {new}")
        labels[key] = new[0]
        print(f"  indicator {outs[term]['name']!r} -> {new[0]!r}", flush=True)
    g.save(path)
    info["labels"] = labels
    info["exec_state"] = step(path, "after save")
    return info


def read_flags(reader, target):
    vi = g.op(reader["path"])
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", ARM_CLASS)
    g._run(vi)
    return {k: vi.GetControlValue(lbl) for k, lbl in reader["labels"].items()}


def raw_delete(scratch):
    vi = g.op(g.OP_DELETE)
    vi.SetControlValue("vi path", scratch)
    vi.SetControlValue("Class Name", ARM_CLASS)
    vi.SetControlValue("index", 0)
    try:
        g._run(vi)
        return "returned"
    except Exception as e:
        return f"raised {str(e)[:80]}"


def arm(reader, tag, load):
    src = os.path.join(g.CLAUDEDEV, ARM_DONOR)
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchBD_{PID}_{tag}.vi")
    row = {"tag": tag, "load": load}
    try:
        if os.path.exists(scratch):
            os.remove(scratch)
        shutil.copy2(src, scratch)
        n0 = len(g.uids(scratch, ARM_CLASS))
        row["flags_before"] = read_flags(reader, scratch)
        if load == "23C":
            g.node_info(scratch, max_n=1)
        elif load == "panel":
            g.open_panel(scratch)
        row["flags_after"] = read_flags(reader, scratch) if load else row["flags_before"]
        row["run"] = raw_delete(scratch)
        n1 = len(g.uids(scratch, ARM_CLASS))
        row["count"] = f"{n0} -> {n1}"
        row["removed_one"] = n1 == n0 - 1
        print(f"  [{tag} load={load}] before {row['flags_before']}  after {row['flags_after']}  "
              f"{row['count']}  {'REMOVED ONE' if row['removed_one'] else 'NOTHING REMOVED'}", flush=True)
    except Exception as e:
        row["arm_error"] = str(e)[:200]
        print(f"  [{tag}] ARM ERROR {str(e)[:180]}", flush=True)
    finally:
        try:
            if load == "panel":
                g.close_panel(scratch)
        except Exception:
            pass
        try:
            if os.path.exists(scratch):
                os.remove(scratch)
        except OSError:
            pass
    RESULT["flags"][tag] = row
    return row


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    reader = None
    try:
        fresh()
        print("=== build the Metrics reader (attempt 2, PN at (2400,60)) ===", flush=True)
        reader = build_reader()
        gate("R4 reader saved, ExecState 1", reader.get("exec_state") == 1, str(reader.get("labels")))

        print("\n=== the falsifier test, read through that instrument ===", flush=True)
        f1 = arm(reader, "F1_untouched", None)
        gate("F1 Block Diagram Loaded is FALSE on an untouched copy (GetVIReference + Traverse only)",
             (f1.get("flags_before") or {}).get("bd") is False, str(f1.get("flags_before")))
        f2 = arm(reader, "F2_23C", "23C")
        gate("F2 the 23C read turns Block Diagram Loaded TRUE",
             bool((f2.get("flags_after") or {}).get("bd")), str(f2.get("flags_after")))
        f3 = arm(reader, "F3_panel", "panel")
        gate("F3 control: with the panel open, Loaded is TRUE and one object is removed",
             bool((f3.get("flags_after") or {}).get("bd")) and bool(f3.get("removed_one")),
             f"{f3.get('flags_after')} {f3.get('count')}")

        print("\n=== VERDICT ===", flush=True)
        bd23 = (f2.get("flags_after") or {}).get("bd")
        if bd23 and not f2.get("removed_one"):
            print("  Block Diagram Loaded == TRUE and the delete STILL did nothing without a panel.\n"
                  "  => CODEX'S FALSIFIER IS MET: diagram residency is NOT the variable; the panel/edit-mode "
                  "context is.", flush=True)
        elif not bd23:
            print("  The 23C read did NOT leave the diagram loaded, so run 1's A2 never tested the hypothesis: "
                  "load state remains live and a loader that KEEPS the diagram ref is needed.", flush=True)
        else:
            print("  Loaded TRUE and the delete worked without a panel - LOAD is the variable after all.",
                  flush=True)
        bad = [r["label"] for r in RESULT["gates"] if not r["ok"]]
        print(f"\n=== {len(RESULT['gates']) - len(bad)}/{len(RESULT['gates'])} gates as predicted ===", flush=True)
        if bad:
            print("NOT AS PREDICTED: " + " | ".join(bad), flush=True)
    finally:
        for p in SCRATCH:
            try:
                if os.path.exists(p):
                    try:
                        g.close_panel(p)
                    except Exception:
                        pass
                    os.remove(p)
                    print(f"  removed scratch {os.path.basename(p)}", flush=True)
            except Exception as e:
                print(f"  (could not remove {os.path.basename(p)}: {str(e)[:100]})", flush=True)
        g._lv = None
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RESULT, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
