"""test_opshiftregs_v1.py - FUNCTIONAL acceptance of OpShiftRegs_v1 (gscript.shift_reg_left) on the frame loop.

Prediction contract (peer archive/peer/2026-09-14-opshiftregs-v0-elements-are-right-registers.md):
  T1 registers 0..13 of WhileLoop index 1 (uid 637): no errors; the right-side columns equal v0's
     (tools/bench/main_vi_shiftregs.json); every register has >= 1 left register.
  T2 every left element's class is 'LeftShiftRegister'; each left has exactly one inside terminal, Is Source? TRUE
     (source into the body); its outside terminal Is Source? FALSE (initial value; wire 0 = uninitialised).
  T3 stacked lefts: for registers with > 1 left, every left is read (index3 sweep) and their inside wires differ.
  T4 handle audit: 20 runs flat within +-100 (post-idle).
Output tools/bench/main_vi_shiftregs_v1.json for the stitch (tools/bench/stitch_shiftregs_left.py).
  py tools/bgrun.py --max-min 25 --log tools/bench/test_opshiftregs_v1.log -- py -u tools/bench/test_opshiftregs_v1.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))["vi"]
V0 = json.load(open(os.path.join(HERE, "main_vi_shiftregs.json"), encoding="utf-8"))["registers"]
LOOP, LOOP_UID = 1, 637
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def main():
    g._lv = None
    rows = []; errs = 0; same_right = True; classes = set(); n_in_ok = True; src_ok = True; stacked = []
    t0 = time.time()
    for k in range(len(V0)):
        r = g.shift_reg_left(MAIN, LOOP, k, 0)
        errs += bool(r["errors"])
        same_right &= (r["uid"] == V0[k]["uid"] and r["inside"] == V0[k]["inside"] and r["out"] == V0[k]["out"])
        lefts = [r["left"]]
        for j in range(1, len(r["left_uids"])):
            lefts.append(g.shift_reg_left(MAIN, LOOP, k, j)["left"])
        if len(r["left_uids"]) > 1:
            stacked.append((k, len(r["left_uids"]), [l["inside"][0]["wire"] if l["inside"] else 0 for l in lefts]))
        for l in lefts:
            classes.add(l["class"]); n_in_ok &= len(l["inside"]) == 1
            src_ok &= all(t["is_source"] for t in l["inside"]) and not l["out"]["is_source"]
        rows.append({**r, "lefts": lefts})
        print(f"   reg {k:2d} {r['inside'][0]['name'] if r['inside'] else '':28s} lefts {r['left_uids']} -> "
              f"{[(l['class'], l['out']['wire'], [(t['name'], t['is_source'], t['wire']) for t in l['inside']]) for l in lefts]} {r['errors'] or ''}", flush=True)
    print(f"   {time.time() - t0:.1f} s", flush=True)
    check("T1 no errors", errs == 0, str(errs))
    check("T1 right side == v0", same_right)
    check("T1 every register has >= 1 left", all(r["left_uids"] for r in rows))
    check("T2 all lefts LeftShiftRegister", classes == {"LeftShiftRegister"}, str(sorted(classes)))
    check("T2 one inside terminal per left", n_in_ok)
    check("T2 left inside source / outside sink", src_ok)
    print(f"   stacked registers: {stacked}", flush=True)
    check("T3 stacked lefts have distinct inside wires", all(len(set(ws)) == n for _k, n, ws in stacked), str(stacked))
    n_init = sum(1 for r in rows if r["left"]["out"]["wire"])
    print(f"   initialised (left outside wired): {n_init}/{len(rows)}", flush=True)
    json.dump({"vi": MAIN, "loop_uid": LOOP_UID, "registers": rows},
              open(os.path.join(HERE, "main_vi_shiftregs_v1.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for _ in range(3):
        g.shift_reg_left(MAIN, LOOP, 0, 0)
    h0 = handles()
    for _ in range(20):
        g.shift_reg_left(MAIN, LOOP, 0, 0)
    h1 = handles(); time.sleep(20); h2 = handles()
    check("T4 handles flat (+-100 post-idle)", abs(h2 - h0) <= 100, f"{h0} -> {h1} -> idle {h2}")
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
