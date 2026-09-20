r"""build_opdelete_v1.py - give the delete op a LIVE error output, then prove it on controls and for real.

Plan: docs/cycle11-plan.md (stages 1 and 2). One runner, one bgrun, one notification.

THE PROBLEM, measured not assumed (tools/bench/diag_delete_error_control.log):
  `delete_object()` removes nothing and OpDelete_v0's front-panel `error out` reads (False, 0, '') even for inputs
  that CANNOT succeed - an index of 999999, an unknown class name. Both of those attempts raised
  "run blocked behind a modal dialog (dismissed by watchdog after ~9 s)". So the indicator is DEAD and the DIALOG
  is the only error signal there is; `gscript.delete_object` used to catch exactly that exception and carry on.

THE READING THIS RECIPE IS BUILT ON, stated so it can be refuted:
  gscript.wire's own docstring says "Unwired error INPUTS are harmless - only an unwired error OUT that receives an
  error raises a dialog." That explains every observation at once: the Generic.Delete Invoke Node's `error out` is
  UNWIRED, the method errors, Automatic Error Handling pops the dialog, the watchdog dismisses it, and the
  front-panel indicator - wired to something else, or to nothing - never moves.

METHOD. create_indicator() both TESTS and FIXES that reading in one call: it is documented to yield no control when
the terminal is already wired, so a new indicator appearing IS the proof that the terminal was unwired.

  ! NO net_map() ANYWHERE IN THIS RECIPE. net_map purges the junk Invoke nodes it drops (spec s33) with
    `delete_object(..., verify=False)` inside `except Exception: pass`. With delete broken it cannot clean up after
    itself and leaves the walked VI carrying junk and (its own comment) broken. Topology is read with node_info(),
    fp_labels() and report_all(), none of which run a creator.

PREDICTION CONTRACT
  P1 OpDelete_v0 holds exactly ONE Invoke node - no junk left behind by a past net_map walk.
  P2 create_indicator(invoke, terminal 3) adds exactly one ControlTerminal whose LABEL names `error out`.
     The label is the confirmation that terminal 3 really is error out; any other name means the index was wrong.
     If instead NOTHING is created, the terminal was already wired - the reading above is REFUTED and the recipe
     falls back to branching the existing indicator onto it with wire_indicators().
  P3 ExecState == 1 after the edit, and the save persists (re-read through a fresh VI reference).
  P4 On the rebuilt op, control A (Property[999999]) and control B (class 'NoSuchClassXYZ') drive the NEW
     indicator to a NON-ZERO status AND the run returns with NO modal dialog. Wiring the error out is what should
     remove the dialog.
  P5 A real delete of one Property, and of one Invoke, on a scratch copy either removes exactly one object with a
     clean error (delete works; the regression was only ever the reporting) or reports a SPECIFIC error code -
     the first time this project has had the reason in hand. BOTH outcomes are results; P5 is a measurement, not
     a gate.
  P6 The two control cases delete nothing (census unchanged).

Scratch discipline: every scratch VI is created and deleted in the same run. No original is opened; nothing outside
claudeDev is written.

  py tools/bgrun.py --max-min 25 --log tools/bench/build_opdelete_v1.log -- py -u tools/recipes/build_opdelete_v1.py
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

V0 = os.path.join(g.CLAUDEDEV, "OpDelete_v0.vi")
V1 = os.path.join(g.CLAUDEDEV, "OpDelete_v1.vi")
DONOR = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
SCRATCH = os.path.join(g.CLAUDEDEV, "ScratchDelV1_c11.vi")
OUT = os.path.join(ROOT, "tools", "bench", "build_opdelete_v1.json")

ERR_TERM = 3          # reference / reference out / error in (no error) / error out
RESULT = {"gates": [], "measurements": {}}


def must(label, ok, detail=""):
    RESULT["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}" + (f"   {detail}" if detail else ""), flush=True)
    return bool(ok)


def note(key, value):
    RESULT["measurements"][key] = value
    print(f"  .. {key}: {value}", flush=True)


# ---------------------------------------------------------------- stage 1: build

def stage1():
    print("=== STAGE 1  OpDelete_v1: wire the Invoke Node's error out to a live indicator ===", flush=True)
    if os.path.exists(V1):
        os.remove(V1)
    shutil.copy2(V0, V1)
    print(f"copied {os.path.basename(V0)} -> {os.path.basename(V1)}", flush=True)

    invokes = g.report_all(V1, "Invoke")
    note("invoke_count", len(invokes))
    note("invoke_uids", [o["uid"] for o in invokes])
    if not must("P1 exactly ONE Invoke node (no junk from a past net_map walk)", len(invokes) == 1,
                f"{len(invokes)} found"):
        return None

    nodes = g.node_info(V1, max_n=40)
    note("node_info", [(i, s, t) for i, s, t in nodes])
    inv_idx = [i for i, style, _ in nodes
               if "invoke" in (style or "").lower() or "method" in (style or "").lower()]
    note("invoke_nodes_index", inv_idx)
    if not must("Invoke node located in Nodes[] (creation order)", len(inv_idx) == 1,
                f"indices {inv_idx}; styles seen = {sorted({s for _, s, _ in nodes})}"):
        return None
    inv = inv_idx[0]

    fp_before = g.fp_labels(V1)
    note("fp_before", fp_before)
    before_ct = g.uids(V1, "ControlTerminal")

    print(f"  create_indicator(Nodes[{inv}], terminal {ERR_TERM}) ...", flush=True)
    new = g.create_indicator(V1, inv, ERR_TERM)
    fp_after = g.fp_labels(V1)
    added = [lab for _, lab, _ in fp_after if lab not in [x[1] for x in fp_before]]
    note("fp_added", added)
    note("controlterminal_delta", len(g.uids(V1, "ControlTerminal")) - len(before_ct))

    if new and added:
        label = added[0]
        if not must("P2 the new indicator's label names `error out` (terminal 3 confirmed)",
                    "error out" in label.lower(), f"label={label!r}"):
            return None
        RESULT["mode"] = "created"
    else:
        # The reading is REFUTED: the Invoke's error out was already wired. Fall back to branching the EXISTING
        # front-panel `error out` onto that wire - wire_indicators is documented to need an already-wired source.
        print("  create_indicator yielded nothing -> the terminal was ALREADY WIRED. Reading refuted; "
              "falling back to wire_indicators (branch the existing indicator onto the wire).", flush=True)
        RESULT["mode"] = "branched"
        existing = [lab for _, lab, is_ind in fp_before if is_ind and lab.strip().lower().startswith("error out")]
        note("existing_error_indicators", existing)
        if not must("an existing `error out` indicator to branch onto", bool(existing), existing):
            return None
        label = existing[0]
        # wire_indicators takes a TRAVERSE index (Class Name + index), not a Nodes[] index - and P1 has already
        # established there is exactly one Invoke on this VI, so its Traverse index is 0.
        g.wire_indicators(V1, 0, ["error out"], [label], node_class="Invoke")

    st = g.exec_state(V1)
    if not must("P3a ExecState == 1 after the edit", st == 1, f"ExecState={st}"):
        return None
    size = g.save(V1)
    note("saved_bytes", size)
    g.reset()
    if not must("P3b the save persisted (fresh reference, ExecState 1)", g.exec_state(V1) == 1):
        return None
    ct_after = g.uids(V1, "ControlTerminal")
    must("P3c the indicator survived the save", len(ct_after) - len(before_ct) == (1 if RESULT["mode"] == "created" else 0),
         f"ControlTerminal {len(before_ct)} -> {len(ct_after)}")
    note("error_indicator_name", label)
    return label


# ---------------------------------------------------------------- stage 2: prove

def attempt(vi, tag, cls, index):
    vi.SetControlValue("vi path", SCRATCH)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", index)
    ran, dialog = "returned", False
    try:
        g._run(vi)
    except Exception as e:
        ran = f"raised {str(e)[:120]}"
        dialog = "modal dialog" in str(e)
    row = {"tag": tag, "cls": cls, "index": index, "run": ran, "dialog": dialog}
    for name in (RESULT.get("error_name"), "error out"):
        if not name:
            continue
        try:
            row[f"raw[{name}]"] = str(vi.GetControlValue(name))[:120]
        except Exception as e:
            row[f"raw[{name}]"] = f"READ FAILED {str(e)[:60]}"
        row[f"decoded[{name}]"] = g._err(vi, name)
    print(f"  [{tag}] {cls}[{index}]  run={ran}  dialog={dialog}\n"
          f"        {json.dumps({k: v for k, v in row.items() if k.startswith(('raw', 'decoded'))}, default=str)}",
          flush=True)
    return row


def stage2(label):
    print("\n=== STAGE 2  prove OpDelete_v1: controls that cannot succeed, then real deletes ===", flush=True)
    RESULT["error_name"] = label
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(DONOR, SCRATCH)
    fresh()
    prop0 = g.uids(SCRATCH, "Property")
    inv0 = g.uids(SCRATCH, "Invoke")
    note("scratch_census_before", {"Property": len(prop0), "Invoke": len(inv0), "ExecState": g.exec_state(SCRATCH)})

    vi = g.op(V1)
    rows = [attempt(vi, "A out-of-range index", "Property", 999999),
            attempt(vi, "B unknown class", "NoSuchClassXYZ", 0)]
    RESULT["controls"] = rows

    live = any(r.get(f"decoded[{label}]") for r in rows)
    no_dialog = not any(r["dialog"] for r in rows)
    must("P4a the new indicator reports a NON-ZERO status for an impossible input", live,
         "; ".join(str(r.get(f"decoded[{label}]")) for r in rows))
    must("P4b no modal dialog on the control runs (the unwired error out was the dialog)", no_dialog,
         f"dialogs={[r['dialog'] for r in rows]}")
    must("P6 the control cases deleted nothing",
         g.uids(SCRATCH, "Property") == prop0 and g.uids(SCRATCH, "Invoke") == inv0)

    print("\n  --- P5 real deletes ---", flush=True)
    real = []
    for cls, pre in (("Property", prop0), ("Invoke", inv0)):
        if not pre:
            print(f"  (no {cls} object on the scratch - skipped)", flush=True)
            continue
        r = attempt(vi, f"REAL delete {cls}[0]", cls, 0)
        post = g.uids(SCRATCH, cls)
        r["removed"] = sorted(set(pre) - set(post))
        r["count"] = f"{len(pre)} -> {len(post)}"
        print(f"        {cls}: {r['count']}   removed={r['removed'] or 'NOTHING'}", flush=True)
        real.append(r)
    RESULT["real"] = real
    works = [r for r in real if len(r.get("removed") or []) == 1]
    note("P5_delete_works_for", [r["cls"] for r in works])
    note("P5_delete_fails_for", [r["cls"] for r in real if r not in works])
    note("P5_reported_reason", {r["cls"]: r.get(f"decoded[{label}]") for r in real if r not in works})
    # P5 is a MEASUREMENT, not a gate - both outcomes are results. Recorded as a gate row only so the
    # log shows at a glance which way it went.
    must("P5 (measurement, not a gate) every real delete removed exactly one object",
         bool(real) and len(works) == len(real),
         f"{len(works)}/{len(real)} worked")
    return True


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    rc = 1
    try:
        for p, what in ((V0, "OpDelete_v0"), (DONOR, "OpWireSource_v5 donor")):
            if not os.path.exists(p):
                print(f"STOP: {what} missing at {p}", flush=True)
                return 3
        fresh()
        label = stage1()
        if label:
            stage2(label)
        bad = [row["label"] for row in RESULT["gates"] if not row["ok"]]
        RESULT["failed_gates"] = bad
        print(f"\n=== {len(RESULT['gates']) - len(bad)}/{len(RESULT['gates'])} gates PASS ===", flush=True)
        if bad:
            print("FAILED: " + " | ".join(bad), flush=True)
        rc = 0 if not bad else 1
    finally:
        g._lv = None
        for p in (SCRATCH,):
            try:
                if os.path.exists(p):
                    os.remove(p)
                    print(f"  scratch removed: {os.path.basename(p)}", flush=True)
            except OSError as e:
                print(f"  could not remove {p}: {e}", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RESULT, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
