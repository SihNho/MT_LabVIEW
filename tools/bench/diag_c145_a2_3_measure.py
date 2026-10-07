# ---
# labview: read
# hardware: none
# ---
r"""diag_c145_a2_3_measure.py - card 145-a2-3 steps 3-5: READ the connector-pane wiring rule of every terminal of
claudeDev\RingPickSlot_v0.vi (6fcf153f) and RingSeqCheck_v0.vi (0295a8d3) with OpWiringRules_v0 (built and positive-controlled
by tools/bench/build_opwiringrules_v0.py; its hygiene record build_opwiringrules_v0_hygiene.json is checked here: PASS + md5 match),
VIs loaded by Open VI Reference only (no panel, never saved). Wired-at-drop from the s04 graph rows (diag_c145_a2_1_table.log ROW lines).
PREDICTION: every assigned input of both VIs reads a rule in {1,2,3}; no UNWIRED input at PS1/SQ1 reads 1 (Required) - else RETURN
naming it. After a PASS table: delete claudeDev\D1_ring_p4s04_20261007_212230.vi (abb76d41) and its resume record. Pinned md5s unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c145_a2_3_measure.log -- py -u tools/bench/diag_c145_a2_3_measure.py
"""
import hashlib, json, os, re, subprocess, sys, time, traceback                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)                 # noqa: E702
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
CD = g.CLAUDEDEV; OP = os.path.join(CD, "OpWiringRules_v0.vi")                           # noqa: E702
LAB = json.load(open(os.path.join(HERE, "build_opwiringrules_v0_labels.json")))["reader"]
HYG = json.load(open(os.path.join(HERE, "build_opwiringrules_v0_hygiene.json")))
VIS = {"RingPickSlot_v0": "6fcf153f", "RingSeqCheck_v0": "0295a8d3"}
PIN = {os.path.join(CD, k + ".vi"): v for k, v in VIS.items()}
PIN.update({os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff", os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca",
            os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877", os.path.join(HERE, "plan_ring_p4_s04v18.json"): "f349c39a",
            os.path.join(HERE, "plan_ring_p4_s04v18_pred.json"): "a2bbc8bf",
            os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s04v18.py"): "fe3f630c",
            os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s04v18_scratch.py"): "f5e4bdf8"})
DEL = [os.path.join(CD, "D1_ring_p4s04_20261007_212230.vi"), os.path.join(HERE, "resume", "resume_plan_ring_p4_s04v18_20261007_212913.json")]
FACTS = os.path.join(HERE, "diag_c145_a2_3_facts.md"); RULE = {0: "Invalid", 1: "Required", 2: "Recommended", 3: "Optional", 4: "Dynamic"}  # noqa: E702
G, ROWS, OUT = {}, [], {}
g._run.__defaults__ = (6.0, 120.0)


class Stop(Exception):
    pass


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d="", need=True):
    G[k] = bool(ok); print("  GATE %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:600]), flush=True)  # noqa: E702
    if need and not ok:
        raise Stop(k)


def rd(target, idx):
    with g.hygiene_probe(OP):            # the reader's PASS record is checked in main() (it sits outside op_hygiene/, card globs)
        vi = g.op(OP); vi.SetControlValue("vi path", target); vi.SetControlValue("index", int(idx))  # noqa: E702
        for k, v in (("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")):
            if k in LAB["controls"]:
                vi.SetControlValue(k, v)
        g._run(vi)
        return ([int(x) for x in (vi.GetControlValue(LAB["Rules"]) or ())], vi.GetControlValue("Text"),
                int(vi.GetControlValue("Number of Connection Terminals")), g._err(vi, LAB["RErr"]) or "")


def wired_map():                         # name -> (dir, wired) from the step-1 graph rows
    m = {}
    for ln in open(os.path.join(HERE, "diag_c145_a2_1_table.log"), encoding="utf-8"):
        x = re.match(r"ROW \| (\w+) \| ([^|]*) \| pane [^|]* \| (input|output) \| wired (True|False)", ln)
        if x and x.group(2).strip():
            m[(x.group(1), x.group(2).strip())] = (x.group(3), x.group(4) == "True")
    return m


def main():
    before = {p: md5(p) for p in PIN}
    gate("0 pinned md5s before", all(before[p].startswith(v) for p, v in PIN.items()), before)
    gate("0 reader hygiene record PASS and md5 == reader file", HYG.get("status") == "PASS" and HYG.get("md5") == md5(OP), (HYG.get("status"), HYG.get("md5")))
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    wm = wired_map()
    for vi in VIS:
        path = os.path.join(CD, vi + ".vi"); rules, _t, n, err = rd(path, 0)              # noqa: E702
        gate("R %s read: no error, len == %d terminals" % (vi, n), not err and len(rules) == n > 0, (rules, err))
        for i in range(n):
            name = rd(path, i)[1]; d, w = wm.get((vi, name), ("free" if not name else "?", None))  # noqa: E702
            ROWS.append((vi, i, name, rules[i], RULE.get(rules[i], "?"), d, w))
            print("ROW | %s | %d | %r | %d %s | %s | wired %s" % ROWS[-1], flush=True)
    bad = [r for r in ROWS if r[5] == "input" and r[6] is False and r[3] == 1]
    gate("T every unwired input at PS1/SQ1 is NOT Required", not bad, bad)
    gate("T every named terminal has a rule in 1..3", all(r[3] in (1, 2, 3) for r in ROWS if r[2]), [r for r in ROWS if r[2] and r[3] not in (1, 2, 3)])
    OUT["handles"] = (h0, bench_prep.labview_handles())


if __name__ == "__main__":
    ok_table = False
    try:
        main(); ok_table = all(G.values())                                                # noqa: E702
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)  # noqa: E702
    finally:
        g.reset(); subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)  # noqa: E702
        tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        gate("E LabVIEW gone (tasklist)", "labview.exe" not in tl, need=False)
        after = {p: md5(p) for p in PIN}
        gate("E pinned md5s unchanged", all(after[p].startswith(v) for p, v in PIN.items()), {os.path.basename(p): h[:8] for p, h in after.items()}, need=False)
        if ok_table:
            for p in DEL:
                os.path.exists(p) and os.remove(p)                                        # noqa: E702
            gate("H abb76d41 + its resume record deleted", not any(os.path.exists(p) for p in DEL), DEL, need=False)
        with open(FACTS, "w", encoding="utf-8") as f:
            f.write("---\ntype: facts\nstatus: current\ndate: %s\n---\n# Card 145-a2-3: connector-pane wiring rules READ (OpWiringRules_v0)\n\n"
                    "| VI | pane index | control | rule | meaning | dir | wired at PS1/SQ1 |\n|---|---|---|---|---|---|---|\n" % time.strftime("%Y-%m-%d"))
            for r in ROWS:
                f.write("| %s | %d | %s | %d | %s | %s | %s |\n" % r)
            f.write("\nSource log: tools/bench/diag_c145_a2_3_measure.log (ROW lines). Wired-at-drop: tools/bench/diag_c145_a2_1_table.log:16-31.\n"
                    "Handles (after restart, end): %s. Gates: %s\n" % (OUT.get("handles"), {k: v for k, v in G.items()}))
        bad = [k for k, v in G.items() if not v]
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": FACTS, "md5": md5(FACTS)}])), flush=True)
        sys.exit(1 if bad else 0)
