r"""build_opconstvalue_v1.py - OpConstValue_v1.vi: READ a diagram constant's VALUE by script (Constant.Value 634AC00),
the reader the fleet never had (toolkit-capabilities.md: "unexercised, blocked on a To More Specific Class donor").
Now unblocked twice over: (1) copy_by_index (row 39) copies ANY node by reference, and (2) NI's example
`Finding and Modifying Objects\Navigating Nodes and Wires.vi` diagram 3 holds exactly the chain we need -
`To More Specific Class` -> Property Node uid 284 reading `Value` (tools/bench/census_constant_seed.log).

WHY NOW: the original's reseed Case #5540 compares against four CONSTANTS (Less?.y, Or.y, And.y, Equal?.y) whose
values are invisible to the fleet; rule 1a forbids guessing them (docs/stage2-assembly-step-e.md).

BUILD (each gate fatal; nothing saved on a miss):
  D  donor = OpReport_v3.vi (Open VI Reference -> Traverse(Class Name) -> refs[] -> Index Array(index)); copy -> OP.
     Delete its report tail is NOT needed: the IA.element output is simply branched into the new chain.
  C1 copy_by_index(example, 'Property', index of uid 284, OP, expect_uid=284, finish=F1) where F1 makes the VI runnable:
     create_control on the copied PN's 'reference' -> a CONSTANT-TYPED refnum control (the seed)      [top level]
  C2 copy_by_index(example, 'Function', index of the TMSC feeding 284, OP, expect_uid=<tmsc>, finish=F2):
     F2: delete the seed control's wire; wire seed -> TMSC 'target class'; IA.element -> TMSC 'reference';
         TMSC 'specific class reference' -> PN 'reference'; create_indicator on PN 'Value' (a Variant indicator)
  S  auto error handling OFF; ExecState 1 -> save; labels json.
TEST (functional, the point of the whole op): a scratch = copy of EMPTY_v0 + three constants? - the fleet cannot
  create constants either, so the oracle is the MAIN VI itself: read-only, Traverse class 'Constant' on the main VI
  and report (index, uid, value) for the constants near the reseed nodes; the gate is "values come back as numbers
  or strings for >= 1 constant, no error" plus the known one: docs/NAMES.md records the VISA literal constant on
  startup frame 10 as a STRING - if its value reads as a COM-port string, the reader is functional.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opconstvalue_v1.log -- py -u tools/recipes/build_opconstvalue_v1.py
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
import build_track_v6_core as B  # noqa: E402  (must, walk, term)

EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects", "Navigating Nodes and Wires.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi")
MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstvalue_labels.json")
PN_UID = 284
must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)


def lv_pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return out or None


def com_preflight(tries=15, gap=4.0):
    """Run 4 (04:13): fresh() + 8 s + reset() was NOT enough - the first call on the relaunched instance died with
    0x800706BA and the instance was gone afterwards (peer ...-opconstvalue-run4-rpc-after-restart-no-labview).
    Same discipline as build_opaddshiftreg_v0.com_preflight: two spaced round-trips agreeing against an unchanged pid."""
    probe = os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi")
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
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) { Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    g.reset()          # run 1 (04:00): `_lv = None` alone left cached op proxies on the dead instance -> RPC unavailable
    com_preflight()    # run 4 (04:13): readiness is measured, never assumed
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def cls_idx(target, cls, uid):
    return [o["uid"] for o in g.report(target, cls)].index(uid)


def main():
    labels = {}
    if "--test-only" in sys.argv:
        # run 4 (04:13) built and saved the op with every build gate PASSED; only the test phase died (RPC after the
        # restart). The build is not rerun - the saved op + its labels json are the batch's product.
        must("S OpConstValue_v1.vi and its labels exist from the passed build", os.path.exists(OP) and os.path.exists(MAP_OUT))
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        print(f"   --test-only: labels {labels}", flush=True)
        return test(labels)
    fresh()
    # the TMSC feeding PN 284 on the example's diagram 3
    labels_ex = {r["uid"]: r["label"] for r in g.node_labels(EX, 3)}
    rows_by = {}
    for n in range(80):
        u, rows = g.node_terms_uid(EX, 3, n)
        if not u:
            break
        rows_by[u] = rows
    w_ref = term(rows_by[PN_UID], "reference", False)["wire"]
    tmsc = next(u for u, rows in rows_by.items() if any(r["is_source"] and r["wire"] == w_ref for r in rows))
    must("D the example's PN 284 is fed by a To More Specific Class", labels_ex.get(tmsc) == "To More Specific Class", f"{tmsc} {labels_ex.get(tmsc)!r}")
    i_pn = cls_idx(EX, "Property", PN_UID); i_tmsc = cls_idx(EX, "Function", tmsc)
    print(f"   example: PN 284 = Property[{i_pn}], TMSC {tmsc} = Function[{i_tmsc}]", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3)

    state = {}

    def F1(dst):
        # review (...-opconstvalue-v1-recipe): identify the copied PN by ADDED uid, not by "a PN with a Value output"
        w = walk(dst, 0)
        new_pns = [u for u, v in w.items() if v[1] == "Property Node" and u not in state["pn_before"]]
        must("C1 exactly one new Property node", len(new_pns) == 1, str(new_pns))
        pn = new_pns[0]
        must("C1 its data terminal is 'Value'", [r["name"] for r in w[pn][2] if r["i"] >= 4] == ["Value"], str([r["name"] for r in w[pn][2]]))
        state["pn"] = pn
        # review ...-fail2 step 2: the copied node's wires BEFORE the seed - any non-zero uid here is a stub (H3)
        stubs = [(r["name"], r["wire"]) for r in w[pn][2] if r["wire"]]
        print(f"   C1 diag: copied PN wires before the seed: {stubs}; ExecState {g.exec_state(dst)}", flush=True)
        must("C1 the copied node arrived with NO wires", not stubs, str(stubs))
        n = w[pn][0]; t = term(w[pn][2], "reference", False)["i"]
        b0 = {l for _i, l, ind in g.fp_labels(dst) if not ind}
        g.create_control(dst, n, t)
        new = [l for _i, l, ind in g.fp_labels(dst) if not ind and l not in b0]
        must("C1 exactly one new control (the seed)", len(new) == 1, str(new)); labels["seed"] = new[0]
        # Run 3 (04:1x): the copied node is a WRITE property (its 'Value' terminal is a SINK, wire 0) -> a required
        # unwired input keeps the VI broken. The seed control (Constant-typed) is what we needed from it: cut its
        # wire, delete the write node (+RBW) so the Target is runnable for the COM save; the READ node is built fresh
        # in F2 with build_property (Constant.Value 634AC00 is public).
        is_write = term(w[pn][2], "Value", False) is not None
        print(f"   F1: seed control {labels['seed']!r} on PN {pn}; 'Value' is {'a SINK (write node)' if is_write else 'a source'}", flush=True)
        pw = {r["label"]: r for r in g.panel_wiring(dst)}
        ws = [o["uid"] for o in g.report_all(dst, "Wire")]
        g.delete_object(dst, "Wire", ws.index(pw[labels["seed"]]["wire"]), verify=False)
        g.delete_object(dst, "Property", [o["uid"] for o in g.report_all(dst, "Property")].index(pn), verify=False)
        g.remove_bad_wires_scripted(dst)
        pw = {r["label"]: r for r in g.panel_wiring(dst)}
        must("F1 the seed control survives, unwired, after deleting the write node", labels["seed"] in pw and pw[labels["seed"]]["wire"] == 0)
        es = g.exec_state(dst)
        print(f"   F1: ExecState {es} with the seed free and the write node gone", flush=True)
        if es != 1:
            # run 2 (04:03): ExecState 0 here, unlocalised. DIAGNOSTIC (review ...-fail2-broken-after-seed): the PN's
            # terminals with wires, the panel wiring, and a Remove-Bad-Wires delta (a vanishing wire = a broken one)
            w = walk(dst, 0)
            print(f"   F1 diag: PN {pn} terminals {[(r['i'], r['name'], r['is_source'], r['wire']) for r in w[pn][2]]}", flush=True)
            print(f"   F1 diag: panel {[(r['label'], r['uid'], r['wire']) for r in g.panel_wiring(dst)]}", flush=True)
            before_w = g.uids(dst, "Wire"); g.remove_bad_wires_scripted(dst)
            print(f"   F1 diag: Remove Bad Wires removed {sorted(before_w - g.uids(dst, 'Wire'))}; ExecState now {g.exec_state(dst)}", flush=True)
    fresh()
    must("D the donor copy (OpReport_v3) is runnable before anything is copied", g.exec_state(OP) == 1)   # H4 gate
    state["pn_before"] = {u for u, v in walk(OP, 0).items() if v[1] == "Property Node"}
    ex_md5 = hashlib.md5(open(EX, "rb").read()).hexdigest()
    g.copy_by_index(EX, "Property", i_pn, OP, expect_uid=PN_UID, finish=F1)

    def F2(dst):
        w = walk(dst, 0)
        new_fn = [u for u, v in w.items() if u not in state["fn_before"] and term(v[2], "specific class reference", True)]
        must("C2 exactly one new To More Specific Class (by added uid)", len(new_fn) == 1, str(new_fn))
        tm = new_fn[0]
        ia = next(u for u, v in w.items() if v[1] == "Index Array")
        # the READ node, built fresh (the copied example node was a write; public member 634AC00 attaches directly)
        pn = g.build_property(dst, "VI Server:Constant", [("634AC00", False)], (1500, 700))[-1]["uid"]
        w = walk(dst, 0)
        must("C2 read PN built with a 'Value' SOURCE terminal", term(w[pn][2], "Value", True) is not None, str([(r['name'], r['is_source']) for r in w[pn][2]]))
        pw = {r["label"]: r for r in g.panel_wiring(dst)}
        must("C2 the seed control is free (wire 0) before wiring it", pw[labels["seed"]]["wire"] == 0)
        fi = lambda cls, u: [o["uid"] for o in g.report_all(dst, cls)].index(u)
        g.wire_control(dst, [labels["seed"]], "Function", fi("Function", tm), ["target class"])
        g.wire(dst, "IndexArray", fi("IndexArray", ia), "element", "Function", fi("Function", tm), "reference", branch=True)
        g.wire(dst, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", pn), "reference")
        w = walk(dst, 0); pw = {r["label"]: r for r in g.panel_wiring(dst)}
        must("F2 seed -> TMSC.'target class' on both ends", pw[labels["seed"]]["wire"] and pw[labels["seed"]]["wire"] == term(w[tm][2], "target class", False)["wire"])
        must("F2 IA.element -> TMSC.reference on both ends", term(w[ia][2], "element", True)["wire"] and term(w[ia][2], "element", True)["wire"] == term(w[tm][2], "reference", False)["wire"])
        a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[pn][2], "reference", False)["wire"]
        must("F2 TMSC -> PN.reference on both ends", a and a == b, f"{a}/{b}")
        n = w[pn][0]; t = term(w[pn][2], "Value", True)["i"]
        b0 = {l for _i, l, ind in g.fp_labels(dst) if ind}; g.create_indicator(dst, n, t)
        labels["value"] = [l for _i, l, ind in g.fp_labels(dst) if ind and l not in b0][-1]
        g.set_auto_error_handling(dst, False)
        print(f"   F2: value indicator {labels['value']!r}; ExecState {g.exec_state(dst)}", flush=True)
    fresh()
    state["fn_before"] = set(walk(OP, 0).keys())
    g.copy_by_index(EX, "Function", i_tmsc, OP, expect_uid=tmsc, finish=F2)
    must("S op saved runnable", g.exec_state(OP) == 1)
    must("S the NI example file is unchanged", hashlib.md5(open(EX, "rb").read()).hexdigest() == ex_md5)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}; donor md5 unchanged {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    # TEST (review ...-opconstvalue-v1-recipe: a run that does not throw proves nothing) - typed oracles on the main VI,
    # reference-only: StringConstant values must be str and one must be the VISA resource literal of startup frame 10
    # (NAMES.md: 'COM'/'ASRL'); DigitalNumericConstant values must be numbers and NOT all identical. A wrong-class seed
    # (e.g. Control.Value) would fail the cast (1055/1057) instead of returning these.
    return test(labels)


def test(labels):
    fresh()
    vi = g.op(OP)

    has_err = "error out" in [l for _i, l, ind in g.fp_labels(OP) if ind]   # once, not per read (run 5: ~12 s/read)

    def read_all(cls, limit):
        n = len(g.report(MAIN, cls)); out = []
        for i in range(min(n, limit)):
            vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
            try:
                g._run(vi); err = (g._err(vi, "error out") if has_err else None) or ""   # run 5: None[:20] lost all reads
                row = (i, vi.GetControlValue(labels["value"]), err)
            except Exception as e:
                row = (i, None, f"EXC {str(e)[:60]}")
            out.append(row)
            print(f"   {cls}[{i}/{n}] -> {row[1]!r:.40} {row[2][:40]}", flush=True)   # incremental: a later crash keeps the data
        return n, out
    n_s, strs = read_all("StringConstant", 22)
    n_n, nums = read_all("DigitalNumericConstant", 12)
    svals = [v for _i, v, e in strs if isinstance(v, str) and not e]
    nvals = [v for _i, v, e in nums if isinstance(v, (int, float)) and not isinstance(v, bool) and not e]
    must("T string constants read as str", len(svals) >= 1, str(len(svals)))
    # run 6 (04:41): the VISA literal sits on sequence FRAME 10, and the op traverses the TOP diagram only - oracle
    # replaced by two top-diagram strings documented by other routes: docs/fixture-recording.md ('img%05d.tif', read
    # from the Edit Format String dialog) and docs/GLOSSARY.md ('Bead # %d').
    must("T the documented top-diagram strings 'img%05d.tif' and 'Bead # %d' are read back exactly",
         "img%05d.tif" in svals and "Bead # %d" in svals, str(svals[:22]))
    must("T numeric constants read as numbers, not all identical", len(nvals) >= 2 and len(set(nvals)) >= 2, str(nvals[:10]))
    n_ok = sum(1 for _n, p in B.PASS if p)
    print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
    return 0 if B.PASS and n_ok == len(B.PASS) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
