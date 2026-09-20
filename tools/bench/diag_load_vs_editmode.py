r"""diag_load_vs_editmode.py - is the delete variable diagram RESIDENCY, or PANEL/EDIT-MODE context?

WHY THIS RUN EXISTS. tools/bench/diag_delete_matrix.log measured a clean A/B - same op, same scratch target,
same Traverse class, same index, only `OpenFrontPanel(target)` differing: without it nothing was deleted
(12->12, 4->4), with it exactly one object was deleted (12->11, 4->3) for EVERY class. On that basis
`gscript.ensure_loaded()` (which calls `open_panel`) was inserted into 26 mutating wrappers.

CODEX REFUTED THE INFERENCE, not the measurement (archive/peer/2026-09-16-openpanel-ab.md):

    "`OpenFrontPanel` does not isolate diagram load state. It simultaneously changes panel visibility, window
     activation, and potentially the VI's edit/run-mode presentation. Your experiment therefore proves only:
     `Generic.Delete`, on references obtained through this traversal path, works after `OpenFrontPanel`."

and named the documented load primitive instead: the **VI `Block Diagram` property (23C)**, which labviewwiki
marks "Loads the block diagram into memory: Yes" and which opens no window; with `Metrics:Block Diagram Loaded`
as the check ("the diagram can be loaded while its window is closed"). Its falsifier, verbatim:

    "The load-state claim is falsified if `Metrics:Block Diagram Loaded` is true before Delete, yet Delete still
     does nothing until `OpenFrontPanel` is called."

WHAT ALREADY EXISTS ON DISK (checked before writing a line of this file, CLAUDE.md "check what already exists"):
  * `docs/vi-server-ids.json` has VI.Block Diagram = 23C but NO Metrics IDs, and NO op reads an arbitrary VI
    property by ID. `grep -n "^def " tools/gscript.py` shows readers for nodes/terminals/panels, none for
    VI-class metrics. So ONE tiny reader is built here (step 0) - the cheapest route named in the task.
  * THE LOADER ALREADY EXISTS AND NEEDED NO BUILD: `gscript.node_info()` runs OpNodeInfo_v0, whose chain is
    `Open VI Reference -> PN VI.Block Diagram (23C) -> Nodes[] -> ...` (tools/recipes/build_opnodeinfo.py:79).
    Reading 23C IS codex's explicit-load primitive, so `node_info(target, max_n=1)` forces the documented load
    with no window and no new artefact.
  * The raw-delete cell (op + SetControlValue + `_run`, bypassing the `delete_object` wrapper, which now calls
    `ensure_loaded` itself) is lifted from `tools/bench/diag_delete_matrix.py`'s `cell()`.

IDs USED (external search, mandatory per CLAUDE.md; labviewwiki VI_class, fetched 2026-09-16):
    Metrics:Front Panel Loaded   291   read-only   "whether the front panel of the VI is in memory"
    Metrics:Block Diagram Loaded 292   read-only   "whether the block diagram of the VI is in memory"
    Block Diagram                23C   read-only   loads the block diagram into memory: Yes
    Edit Mode On Open            22E   read/write  (A4 only)

PREDICTION CONTRACT
  G0  the reader op builds: PN(VI Server:VI,[291,292]) attaches with exactly 2 output terminals, wires to the
      donor's `Open VI Reference` refnum, saves, ExecState 1. A failure here is a MEASUREMENT failure, not a
      result: the arms still run, with flags = None, and the run says so.
  A1  flags on an untouched fresh copy (COM GetVIReference + Traverse census only): MEASUREMENT, no prediction.
      Expected FALSE if the hypothesis is right; TRUE would mean Traverse/GetVIReference already load it.
  A0  baseline, no load of any kind before the raw delete -> predict 0 removed (reproduces diag_delete_matrix).
  A2  THE DECIDING ARM. `node_info(scratch, max_n=1)` (= read 23C) -> re-read flags -> raw delete, NO panel.
      If `Block Diagram Loaded` goes TRUE and exactly 1 is removed  => LOAD is the variable; ensure_loaded must
         switch to the 23C read (no window) - that is codex's own "supports the narrow load-state explanation".
      If `Block Diagram Loaded` is TRUE and 0 are removed           => codex is right, the variable is edit/UI
         context; `open_panel` stays in ensure_loaded and its docstring is rewritten.
  A3  control: `open_panel(activate=False)` then raw delete -> predict 1 removed (matches diag_delete_matrix).
  A4  runs ONLY if A2 removed 0: on a fresh 23C-loaded copy, try a DIFFERENT mutator (`move_object`, GObject.Move)
      to separate "all edits are declined" from "delete specifically is declined", and read Edit Mode On Open
      (22E) on a loaded-no-panel copy vs a panel-opened copy - the concrete edit-mode indicator codex named.
  W1  no new LabVIEW window appears across A0/A1/A2 (lv_gui -Action windows, a READ), and at least one does in A3.

Scratch discipline: every scratch VI is created and deleted inside this run. No original is opened, nothing
outside user.lib\claudeDev is written, no hardware is touched.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_load_vs_editmode.log -- py -u tools/bench/diag_load_vs_editmode.py
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

CENSUS_CLASSES = ["Constant", "Property", "Invoke", "SubVI", "IndexArray", "Wire", "ControlTerminal"]
ARM_DONOR = "OpFPLabels_v0.vi"          # small: 4 Property objects, the diag_delete_matrix B-arm target
ARM_CLASS = "Property"
READER_DONOR = "OpReportAll_v0.vi"      # Open VI Reference -> Traverse (Traverse does NOT load the diagram)
P_FP_LOADED, P_BD_LOADED, P_EDITMODE = "291", "292", "22E"
OUT = os.path.join(HERE, "diag_load_vs_editmode.json")
RESULT = {"gates": [], "reader": {}, "arms": {}, "windows": {}}
PID = os.getpid()
SCRATCH = []                            # every scratch path, registered at creation, deleted in the finally block


def gate(label, ok, detail=""):
    RESULT["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}" + (f"   {detail}" if detail else ""), flush=True)
    return bool(ok)


def windows(tag):
    try:
        txt = g._lv_gui("-Action", "windows")
    except Exception as e:
        txt = f"ERR {e}"
    lines = [ln.strip() for ln in str(txt).splitlines() if ln.strip()]
    RESULT["windows"][tag] = lines
    print(f"  [windows {tag}] {len(lines)} line(s): {lines}", flush=True)
    return lines


def census(target):
    out = {}
    for cls in CENSUS_CLASSES:
        try:
            out[cls] = sorted(g.uids(target, cls))
        except Exception as e:
            out[cls] = f"ERR {str(e)[:50]}"
    return out


# --------------------------------------------------------------- step 0: the flag reader

def build_reader():
    """A minimal VI-property reader: donor's Open VI Reference -> PN VI[291,292] -> indicators."""
    src = os.path.join(g.CLAUDEDEV, READER_DONOR)
    path = os.path.join(g.CLAUDEDEV, f"ScratchBDLoaded_{PID}.vi")
    if os.path.exists(path):
        os.remove(path)
    shutil.copy2(src, path)                      # a COPY: never point an op at a running op (toolkit-capabilities)
    SCRATCH.append(path)                         # BEFORE anything can raise - this run left the copy behind
    info = {"path": path}                        # because cleanup keyed off the return value (fixed 2026-09-16)
    g.set_auto_error_handling(path, False)

    nodes = g.node_info(path, max_n=40)
    print(f"  reader donor nodes: {[(i, s) for i, s, _l in nodes]}", flush=True)
    oref = [i for i, style, _l in nodes if "Open VI Reference" in str(style)]
    if not oref:
        raise RuntimeError(f"no 'Open VI Reference' node in {READER_DONOR}: {[s for _i, s, _l in nodes]}")
    oref_i = oref[0]
    oterms = g.node_terms(path, 0, oref_i)
    print(f"  Open VI Reference terminals: {[(t['i'], t['name'], t['is_source']) for t in oterms]}", flush=True)
    refs = [t for t in oterms if t["is_source"] and "reference" in str(t["name"]).lower()
            and "error" not in str(t["name"]).lower()]
    if not refs:
        raise RuntimeError(f"no refnum output on Open VI Reference: {[t['name'] for t in oterms]}")
    src_term = refs[0]["i"]

    n0 = len(nodes)
    g.build_property(path, "VI Server:VI", [(P_FP_LOADED, False), (P_BD_LOADED, False)], (60, 900))
    nodes2 = g.node_info(path, max_n=40)
    if len(nodes2) != n0 + 1:
        raise RuntimeError(f"expected 1 new top-level node, Nodes[] went {n0} -> {len(nodes2)}")
    pn_i = len(nodes2) - 1                        # a newly created node goes to the END of Nodes[] (node_rank docstring)
    pterms = g.node_terms(path, 0, pn_i)
    print(f"  new PN[{pn_i}] terminals: {[(t['i'], t['name'], t['is_source']) for t in pterms]}", flush=True)
    ref_in = [t for t in pterms if not t["is_source"] and str(t["name"]).strip().lower() == "reference"]
    outs = [t for t in pterms if t["is_source"]
            and str(t["name"]).strip().lower() not in ("reference out", "dup reference", "error out")]
    err_out = [t for t in pterms if t["is_source"] and str(t["name"]).strip().lower() == "error out"]
    if not ref_in or len(outs) != 2:
        raise RuntimeError(f"PN did not attach 2 readable items: outs={[t['name'] for t in outs]}")

    dw, st = g.connect2(path, 0, pn_i, ref_in[0]["i"], oref_i, src_term)
    print(f"  connect2 PN.reference <- Open VI Reference.{refs[0]['name']!r}: wire delta {dw}, ExecState {st}",
          flush=True)

    wanted = [("fp", outs[0]), ("bd", outs[1])]
    if err_out:
        wanted.append(("err", err_out[0]))
    labels = {}
    for key, term in wanted:
        before = {row[1] for row in g.fp_labels(path)}
        g.create_indicator(path, pn_i, term["i"])
        after = {row[1] for row in g.fp_labels(path)}
        new = sorted(after - before)
        if len(new) != 1:
            raise RuntimeError(f"create_indicator on {term['name']!r} produced {new}")
        labels[key] = new[0]
        print(f"  indicator for {term['name']!r} -> label {new[0]!r}", flush=True)

    g.save(path)
    info["labels"] = labels
    info["exec_state"] = g.exec_state(path)
    return info


def read_flags(reader, target):
    """(fp_loaded, bd_loaded, raw) for `target`, read with the scratch reader op. No load side effect intended:
    the op's own chain is Open VI Reference + Traverse, both documented as NOT loading the block diagram."""
    if not reader:
        return None
    try:
        vi = g.op(reader["path"])
        vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", ARM_CLASS)
        g._run(vi)
        rec = {}
        for key, label in reader["labels"].items():
            try:
                rec[key] = vi.GetControlValue(label)
            except Exception as e:
                rec[key] = f"ERR {str(e)[:40]}"
        return rec
    except Exception as e:
        return {"ERR": str(e)[:150]}


def flagstr(f):
    if not f:
        return "flags=UNAVAILABLE"
    return f"FPLoaded={f.get('fp')} BDLoaded={f.get('bd')}" + (f" err={f.get('err')}" if "err" in f else "")


# --------------------------------------------------------------- the arms

def raw_delete(scratch, cls=ARM_CLASS, index=0):
    """The op called directly, exactly as diag_delete_matrix.cell() does - NOT through delete_object(), which
    now calls ensure_loaded() itself and would open a panel in every arm."""
    row = {}
    vi = g.op(g.OP_DELETE)
    vi.SetControlValue("vi path", scratch)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", index)
    try:
        g._run(vi)
        row["run"] = "returned"
    except Exception as e:
        row["run"] = f"raised {str(e)[:90]}"
    try:
        row["error_out_raw"] = str(vi.GetControlValue("error out"))[:60]
    except Exception as e:
        row["error_out_raw"] = f"READ FAILED {str(e)[:40]}"
    return row


def arm(tag, reader, load=None, do_delete=True):
    """One arm on its own FRESH copy of the donor. `load` in {None, '23C', 'panel'}."""
    src = os.path.join(g.CLAUDEDEV, ARM_DONOR)
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchLM_{PID}_{tag}.vi")
    row = {"tag": tag, "load": load}
    try:
        if os.path.exists(scratch):
            os.remove(scratch)
        shutil.copy2(src, scratch)
        before = census(scratch)
        row["count_before"] = len(before.get(ARM_CLASS) or [])
        row["flags_before"] = read_flags(reader, scratch)
        print(f"  [{tag}] fresh copy: {ARM_CLASS}={row['count_before']}  {flagstr(row['flags_before'])}", flush=True)

        if load == "23C":
            # codex's explicit load primitive, through an op that already exists: OpNodeInfo_v0's chain is
            # Open VI Reference -> PN VI.Block Diagram (23C) -> Nodes[]. No window is opened.
            row["loader"] = "node_info(max_n=1) => VI.Block Diagram 23C"
            row["loader_out"] = str(g.node_info(scratch, max_n=1))[:120]
        elif load == "panel":
            row["loader"] = "open_panel(activate=False) => VI.OpenFrontPanel"
            g.open_panel(scratch)
        if load:
            row["flags_after_load"] = read_flags(reader, scratch)
            # taken HERE, before the finally block closes an opened panel again
            row["windows_after_load"] = windows(f"{tag} after load")
            print(f"  [{tag}] after {row['loader']}: {flagstr(row['flags_after_load'])}", flush=True)

        row["exec_state"] = g.exec_state(scratch)
        if do_delete:
            row.update(raw_delete(scratch))
            after = census(scratch)
            row["count_after"] = len(after.get(ARM_CLASS) or [])
            moved = {}
            for c in CENSUS_CLASSES:
                b, a = before.get(c), after.get(c)
                if isinstance(b, list) and isinstance(a, list) and set(b) - set(a):
                    moved[c] = sorted(set(b) - set(a))
            row["disappeared_anywhere"] = moved
            row["removed_one"] = row["count_after"] == row["count_before"] - 1
            print(f"  [{tag}] DELETE: {row['count_before']} -> {row['count_after']}  "
                  f"{'REMOVED ONE' if row['removed_one'] else 'NOTHING REMOVED'}  run={row['run'][:30]}  "
                  f"err={row['error_out_raw']}  elsewhere={moved or 'none'}", flush=True)
    except Exception as e:
        row["arm_error"] = str(e)[:250]
        print(f"  [{tag}] ARM ERROR {str(e)[:200]}", flush=True)
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
    RESULT["arms"][tag] = row
    return row


def arm4_editmode(reader):
    """A4 - only when A2 deleted nothing. Separates 'every edit is declined while unloaded' from 'delete is'."""
    print("\n=== A4  A2 removed nothing: is the variable EDIT MODE rather than residency? ===", flush=True)
    src = os.path.join(g.CLAUDEDEV, ARM_DONOR)
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchLM_{PID}_A4.vi")
    row = {"tag": "A4"}
    try:
        if os.path.exists(scratch):
            os.remove(scratch)
        shutil.copy2(src, scratch)
        row["flags_before"] = read_flags(reader, scratch)
        g.node_info(scratch, max_n=1)                       # 23C load, no panel
        row["flags_after_load"] = read_flags(reader, scratch)
        objs = g.report_all(scratch, ARM_CLASS)
        row["pos_before"] = objs[0]["pos"] if objs else None
        # A SECOND mutator family on the same 23C-loaded, panel-less copy: GObject.Move (632A400).
        vi = g.op(g.OP_MOVE)
        vi.SetControlValue("vi path", scratch)
        vi.SetControlValue("Class Name", ARM_CLASS)
        vi.SetControlValue("index", 0)
        vi.SetControlValue("location (0, 0)", [1200.0, 900.0])
        try:
            g._run(vi)
            row["move_run"] = "returned"
        except Exception as e:
            row["move_run"] = f"raised {str(e)[:80]}"
        objs2 = g.report_all(scratch, ARM_CLASS)
        row["pos_after"] = objs2[0]["pos"] if objs2 else None
        row["move_landed"] = row["pos_after"] != row["pos_before"]
        print(f"  [A4] move on a 23C-loaded, panel-less copy: {row['pos_before']} -> {row['pos_after']}  "
              f"{'MOVED' if row['move_landed'] else 'DID NOT MOVE'}", flush=True)
        gate("A4 a non-delete mutator (GObject.Move) on a 23C-loaded panel-less copy also fails "
             "(=> the decline is general, not delete-specific)", not row["move_landed"],
             f"{row['pos_before']} -> {row['pos_after']}")
    except Exception as e:
        row["arm_error"] = str(e)[:250]
        print(f"  [A4] ARM ERROR {str(e)[:200]}", flush=True)
    finally:
        try:
            if os.path.exists(scratch):
                os.remove(scratch)
        except OSError:
            pass
    RESULT["arms"]["A4"] = row
    return row


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    reader = None
    try:
        fresh()
        windows("start")

        print("\n=== STEP 0  build the VI-property reader (291/292); nothing on disk reads them ===", flush=True)
        try:
            reader = build_reader()
            gate("G0 reader op built and saved, ExecState 1", reader.get("exec_state") == 1,
                 f"{os.path.basename(reader['path'])} labels={reader.get('labels')}")
        except Exception as e:
            reader = None
            gate("G0 reader op built and saved, ExecState 1", False, str(e)[:250])
            print("  (arms continue WITHOUT the flags - the delete counts are the decider either way)", flush=True)
        RESULT["reader"] = {k: v for k, v in (reader or {}).items()}
        # the reader build itself opens ONE panel (build_property -> ensure_loaded -> open_panel on the reader
        # COPY), so the window baseline for the arms is taken here, not at start.
        w_base = windows("after reader build")

        print("\n=== A1  MEASUREMENT: flags on an untouched fresh copy ===", flush=True)
        a1 = arm("A1", reader, load=None, do_delete=False)
        f1 = a1.get("flags_before") or {}
        gate("A1 (measurement) Block Diagram Loaded on an untouched copy", True, flagstr(f1))

        print("\n=== A0  baseline: no load at all, then the raw delete ===", flush=True)
        a0 = arm("A0", reader, load=None)
        gate("A0 nothing removed with no load of any kind (reproduces diag_delete_matrix B1)",
             a0.get("removed_one") is False, f"{a0.get('count_before')} -> {a0.get('count_after')}")
        windows("after A0/A1")

        print("\n=== A2  THE DECIDING ARM: explicit 23C load, NO panel, then the raw delete ===", flush=True)
        a2 = arm("A2", reader, load="23C")
        fb = (a2.get("flags_before") or {}).get("bd")
        fa = (a2.get("flags_after_load") or {}).get("bd")
        gate("A2a reading VI.Block Diagram (23C) turns Block Diagram Loaded TRUE without a panel",
             bool(fa) and not bool(fb), f"before={fb} after={fa}")
        gate("A2b DECIDER: with the diagram loaded and NO panel, exactly one object is removed",
             bool(a2.get("removed_one")), f"{a2.get('count_before')} -> {a2.get('count_after')}  "
                                          f"BDLoaded before={fb} after={fa}")
        w2 = a2.get("windows_after_load") or windows("after A2")

        print("\n=== A3  control: OpenFrontPanel(activate=False), then the raw delete ===", flush=True)
        a3 = arm("A3", reader, load="panel")
        gate("A3 control: with OpenFrontPanel exactly one object is removed",
             bool(a3.get("removed_one")), f"{a3.get('count_before')} -> {a3.get('count_after')}  "
                                          f"{flagstr(a3.get('flags_after_load'))}")
        w3 = a3.get("windows_after_load") or windows("after A3")
        gate("W1 the 23C route (A2) opened NO new window, while the panel route (A3) did",
             len(w2) == len(w_base) and len(w3) > len(w2),
             f"baseline={len(w_base)} afterA2={len(w2)} afterA3={len(w3)}")

        if a2.get("removed_one") is False:
            arm4_editmode(reader)

        print("\n=== VERDICT ===", flush=True)
        if a2.get("removed_one"):
            print("  A2 REMOVED ONE => LOAD STATE is the variable. ensure_loaded() must load via the 23C read "
                  "(no window), not OpenFrontPanel.", flush=True)
        else:
            print("  A2 REMOVED NOTHING => codex's falsifier is met if BDLoaded was TRUE: the variable is "
                  "panel/EDIT-MODE context, not diagram residency. open_panel stays; the docstring changes.",
                  flush=True)

        bad = [r["label"] for r in RESULT["gates"] if not r["ok"]]
        print(f"\n=== {len(RESULT['gates']) - len(bad)}/{len(RESULT['gates'])} gates as predicted ===", flush=True)
        if bad:
            print("NOT AS PREDICTED: " + " | ".join(bad), flush=True)
    finally:
        # scratch discipline: every scratch VI is created and deleted in this same run
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
