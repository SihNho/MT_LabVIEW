r"""diag_delete_matrix.py - is the silent delete no-op just a TARGET NOT FULLY LOADED? One A/B answers it.

THE HYPOTHESIS, and it was written in our own code on 2026-08-28. `gscript.open_panel`'s docstring, tools/gscript.py:1042-1048:

    "Open the target's front panel - REQUIRED before wire() AND before drop_subvi(). Wiring a target loaded only
     via GetVIReference is SILENTLY DECLINED (count unchanged, no error): the diagram is not fully in memory.
     OpenFrontPanel forces the full load. Discovered 2026-08-28 after three silent failures."

Silently declined; count unchanged; no error. That is, word for word, what delete_object does - and
`delete_object` never calls open_panel().

TWO INDEPENDENT ROUTES REACHED THE SAME PLACE, which is why this is worth one run rather than one more argument:
  * codex, archive/peer/2026-09-16-delete-silent-noop2.md: NI documents Generic.Delete with "Loads the block
    diagram into memory: No", so the method will not promote a merely-referenced VI into a diagram-editing state;
    and "Generic.Delete has no semantic return value at all - its contract is the side effect", so a clean error
    cluster was never evidence of anything.
  * the prior-art review, archive/peer/2026-09-16-priorart-priorart-cycle11-delete.md finding 12: delete has
    demonstrably WORKED (six nodes of an FPTARGET copy; 1,403 junk Invokes purged in one net_map) - so a global
    "the tool is broken" reading was always wrong. Those successes ran against targets other operations had
    already forced into memory.

WHAT THIS REPLACES. Today's cycle opened by trying to REBUILD the op (tools/recipes/build_opdelete_v1.py). That
premise is withdrawn: the op may be perfectly good and simply called wrong.

PREDICTION CONTRACT
  Part A - READ the op, no mutation, with the creator-free readers the prior-art review named.
    A1 node_terms finds exactly one terminal named `error out` with is_source TRUE on the Invoke node.
    A2 MEASUREMENT: that terminal's connected-wire uid. 0 => keystone-op-spec.md:281 ("the Delete node's error out
       is unwired") was right and today's "already wired" conclusion was wrong.
    A3 The Invoke node's terminal list tells us which method is selected WITHOUT a new reader: an UNTYPED Invoke
       reports terminals literally named 'Method' (gscript.py net_map s33 heuristic), while Generic.Delete takes
       no parameters, so a correctly configured node shows exactly reference / reference out / error in / error
       out. Terminals named 'Method' would mean the method never attached - codex's alternative explanation.
    A4 OpDelete_v1 is IDENTICAL to v0 => today's wire_indicators call silently no-op'd, exactly as the prior-art
       review's finding 5 predicts (it needs an already-wired SOURCE).

  Part B - THE A/B. Same target, same class, same op, same index: only open_panel() differs.
    B1 WITHOUT open_panel: 0 objects removed   (reproduce the regression)
    B2 WITH    open_panel: exactly 1 removed   (the hypothesis)
    If B1 and B2 agree, the load-state explanation is REFUTED and the fault is elsewhere; that is a real result
    and the run says so rather than retrying.

  Part C - only if B2 holds: sweep the classes WITH open_panel, to find any class-specific residue. The record
    names one (an lvlib-member subVI node hung 120 s, keystone-op-spec.md:527-529), so a clean sweep is not
    assumed.
    C1 No cell removes an object of a DIFFERENT class than asked for (the op's Traverse order agrees with
       report_all's). Nothing has ever checked this.

Scratch discipline: one scratch copy per cell, deleted in the same run. No original is opened; nothing is saved.

  py tools/bgrun.py --max-min 25 --log tools/bench/diag_delete_matrix.log -- py -u tools/bench/diag_delete_matrix.py
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
AB_TARGETS = ["OpWireSource_v5.vi", "OpFPLabels_v0.vi"]      # OpWireSource_v5 is where today's delete returned 0
AB_CLASS = "Property"
OUT = os.path.join(HERE, "diag_delete_matrix.json")
RESULT = {"partA": {}, "partB": [], "partC": [], "gates": []}


def gate(label, ok, detail=""):
    RESULT["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}" + (f"   {detail}" if detail else ""), flush=True)
    return bool(ok)


def census(target):
    out = {}
    for cls in CENSUS_CLASSES:
        try:
            out[cls] = sorted(g.uids(target, cls))
        except Exception as e:
            out[cls] = f"ERR {str(e)[:50]}"
    return out


# ------------------------------------------------------------------ Part A

def read_op(name):
    path = os.path.join(g.CLAUDEDEV, name)
    if not os.path.exists(path):
        print(f"  (missing {name})", flush=True)
        return None
    rec = {"exec_state": g.exec_state(path)}
    print(f"\n  --- {name}  (ExecState {rec['exec_state']}) ---", flush=True)
    try:
        rec["panel_wiring"] = g.panel_wiring(path)
        for r in rec["panel_wiring"]:
            print(f"     FP {str(r.get('label'))!r:<22} ind={r.get('indicator')}  uid={r.get('uid')}  "
                  f"is_source={r.get('is_source')}  wire={r.get('wire')}"
                  + ("   <== BARE" if not r.get("wire") else ""), flush=True)
    except Exception as e:
        rec["panel_wiring"] = f"ERR {str(e)[:120]}"
        print(f"     panel_wiring: {rec['panel_wiring']}", flush=True)

    rec["nodes"] = {}
    for n in range(8):
        try:
            uid, rows = g.node_terms_uid(path, 0, n)
        except Exception as e:
            print(f"     Nodes[{n}] -> ERR {str(e)[:90]}", flush=True)
            break
        if not rows and not uid:
            print(f"     Nodes[{n}] -> (out of range, stopping)", flush=True)
            break
        rec["nodes"][str(n)] = {"uid": uid, "terms": rows}
        print(f"     Nodes[{n}] uid {uid}", flush=True)
        for r in rows:
            print(f"        t{r.get('i')} {str(r.get('name'))!r:<26} is_source={r.get('is_source')}  "
                  f"wire={r.get('wire')}" + ("   <== BARE" if not r.get("wire") else ""), flush=True)
    return rec


def partA():
    print("=== PART A  read the delete op with the creator-free readers (no mutation) ===", flush=True)
    for name in ("OpDelete_v0.vi", "OpDelete_v1.vi"):
        RESULT["partA"][name] = read_op(name)

    v0 = RESULT["partA"].get("OpDelete_v0.vi") or {}
    all_terms = [(n, r) for n, nd in (v0.get("nodes") or {}).items() for r in nd["terms"]]
    errs = [(n, r) for n, r in all_terms if str(r.get("name")).strip() == "error out" and r.get("is_source")]
    gate("A1 exactly one `error out` SOURCE terminal on OpDelete_v0",
         len(errs) == 1, str([(n, r.get("i"), r.get("wire")) for n, r in errs]))
    if errs:
        w = errs[0][1].get("wire")
        RESULT["partA"]["error_out_wire"] = w
        gate("A2 (measurement) that `error out` terminal is WIRED", bool(w),
             f"wire={w}" + ("  -> BARE: keystone-op-spec.md:281 was right; today's conclusion was wrong"
                            if not w else ""))
    method_terms = [(n, r.get("i")) for n, r in all_terms if str(r.get("name")).strip() == "Method"]
    gate("A3 no terminal is literally named 'Method' (=> a real method IS attached to the Invoke node)",
         not method_terms, str(method_terms) or "none - method attached")

    v1 = RESULT["partA"].get("OpDelete_v1.vi") or {}
    same = (json.dumps(v0.get("nodes"), sort_keys=True, default=str)
            == json.dumps(v1.get("nodes"), sort_keys=True, default=str))
    gate("A4 OpDelete_v1 is IDENTICAL to v0 (=> today's wire_indicators silently no-op'd)", same,
         "identical" if same else "they differ - wire_indicators DID change something")


# ------------------------------------------------------------------ Part B / C

def cell(target_name, cls, open_first, tag):
    src = os.path.join(g.CLAUDEDEV, target_name)
    stem = os.path.splitext(target_name)[0][:12].replace(" ", "")
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchMat_{tag}_{stem}_{cls}.vi")
    row = {"target": target_name, "class": cls, "open_panel": open_first}
    try:
        if os.path.exists(scratch):
            os.remove(scratch)
        shutil.copy2(src, scratch)
        before = census(scratch)
        n0 = len(before.get(cls) or [])
        row["count_before"] = n0
        if n0 == 0:
            row["skipped"] = "none present"
            print(f"  [{tag} {target_name}/{cls} open={open_first}] skipped - none present", flush=True)
            return row
        if open_first:
            # THE VARIABLE UNDER TEST. gscript.py:1042-1048: OpenFrontPanel forces the full load; a target loaded
            # only via GetVIReference silently declines edits with no error and no change.
            g.open_panel(scratch)
        vi = g.op(g.OP_DELETE)
        vi.SetControlValue("vi path", scratch)
        vi.SetControlValue("Class Name", cls)
        vi.SetControlValue("index", 0)
        try:
            g._run(vi)
            row["run"] = "returned"
        except Exception as e:
            row["run"] = f"raised {str(e)[:80]}"
        try:
            row["error_out_raw"] = str(vi.GetControlValue("error out"))[:60]
        except Exception as e:
            row["error_out_raw"] = f"READ FAILED {str(e)[:40]}"
        after = census(scratch)
        row["count_after"] = len(after.get(cls) or [])
        moved = {}
        for c in CENSUS_CLASSES:
            b, a = before.get(c), after.get(c)
            if isinstance(b, list) and isinstance(a, list) and set(b) - set(a):
                moved[c] = sorted(set(b) - set(a))
        row["disappeared_anywhere"] = moved
        row["removed_one"] = row["count_after"] == n0 - 1
        print(f"  [{tag} {target_name}/{cls} open_panel={open_first}]  {n0} -> {row['count_after']}  "
              f"{'REMOVED ONE' if row['removed_one'] else 'NOTHING REMOVED'}  run={row['run'][:30]}  "
              f"err={row['error_out_raw']}  elsewhere={moved or 'none'}", flush=True)
    except Exception as e:
        row["cell_error"] = str(e)[:200]
        print(f"  [{tag} {target_name}/{cls}] CELL ERROR {str(e)[:150]}", flush=True)
    finally:
        try:
            if os.path.exists(scratch):
                os.remove(scratch)
        except OSError:
            pass
    return row


def partB():
    print("\n=== PART B  THE A/B: same op, same target, same class - only open_panel() differs ===", flush=True)
    for t in AB_TARGETS:
        if not os.path.exists(os.path.join(g.CLAUDEDEV, t)):
            print(f"  (missing {t})", flush=True)
            continue
        RESULT["partB"].append(cell(t, AB_CLASS, False, "B-without"))
        RESULT["partB"].append(cell(t, AB_CLASS, True, "B-with"))
    without = [r for r in RESULT["partB"] if not r["open_panel"] and r.get("count_before")]
    with_ = [r for r in RESULT["partB"] if r["open_panel"] and r.get("count_before")]
    gate("B1 WITHOUT open_panel, nothing is removed (regression reproduced)",
         bool(without) and not any(r.get("removed_one") for r in without),
         str([(r["target"], r.get("count_before"), r.get("count_after")) for r in without]))
    ok = bool(with_) and all(r.get("removed_one") for r in with_)
    gate("B2 WITH open_panel, exactly one object is removed (THE HYPOTHESIS)", ok,
         str([(r["target"], r.get("count_before"), r.get("count_after")) for r in with_]))
    return ok


def partC():
    print("\n=== PART C  with open_panel, sweep the classes for class-specific residue ===", flush=True)
    t = AB_TARGETS[0]
    for cls in CENSUS_CLASSES:
        RESULT["partC"].append(cell(t, cls, True, "C"))
    rows = [r for r in RESULT["partC"] if r.get("count_before")]
    wrong = [r for r in rows if not r.get("removed_one") and r.get("disappeared_anywhere")]
    gate("C1 no cell removed an object of a DIFFERENT class than asked for", not wrong,
         str([(r["class"], r["disappeared_anywhere"]) for r in wrong])[:200])
    RESULT["class_results"] = {r["class"]: ("removed one" if r.get("removed_one") else "NOTHING") for r in rows}
    print(f"\n  per-class with open_panel: {json.dumps(RESULT['class_results'])}", flush=True)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    try:
        fresh()
        partA()
        if partB():
            partC()
        else:
            print("\n  Part C skipped: B2 did not hold, so a class sweep would measure the wrong thing.",
                  flush=True)
        bad = [r["label"] for r in RESULT["gates"] if not r["ok"]]
        print(f"\n=== {len(RESULT['gates']) - len(bad)}/{len(RESULT['gates'])} gates as predicted ===", flush=True)
        if bad:
            print("NOT AS PREDICTED: " + " | ".join(bad), flush=True)
    finally:
        g._lv = None
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RESULT, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
