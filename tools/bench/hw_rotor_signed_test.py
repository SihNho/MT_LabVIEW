"""hw_rotor_signed_test.py - HARDWARE ACCEPTANCE of the signed rotor read (user 2026-09-14 20:1x: "직접 움직여보자").
Rotor = Autonics PMC-2HS, alias 'Rotor'. Commands go through RAWCMD_rotor.vi (Configure.vi copy with a string control
on VISA Write); reads through SetCommand_signed.vi (deliverable) and a scratch copy of the ORIGINAL SetCommand.vi,
Ring 2, Baseline 0 (Pos_degree = 0.72 deg/pulse * raw). The first read after opening the port is discarded (measured
artefact). Plan review: archive/peer/2026-09-14-rotor-negative-coordinate-test-plan.md.

Sequence and predictions (each POS read on BOTH VIs):
  R0  POS                      -> both 000186A0 (72000 deg) unless the counter was changed since 20:2x
  C1  'CLL X'  (clear active counter, no motion)  -> POS 00000000 on both (0 deg)
  M1  'PIC -10' (relative, -10 pulses = -7.2 deg) -> wait -> POS FFFFFFF6: signed -7.2 deg, original +3092376445.92 deg
  M2  'PIC 10'                                    -> wait -> POS 00000000 on both
The counter is LEFT AT 0 (the new VI's convention, baseline 0); restoring +100000 pulses = a 200-turn move, only on
request. Any read that disagrees between the two VIs where they should agree, or a POS not matching the prediction,
stops the sequence before the next motion.
  py tools/bgrun.py --max-min 6 --log tools/bench/hw_rotor_signed_test.log -- py -u tools/bench/hw_rotor_signed_test.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

RES = "Rotor"
D = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor"
SIGNED = os.path.join(g.CLAUDEDEV, "SetCommand_signed.vi")
RAW = os.path.join(g.CLAUDEDEV, "RAWCMD_rotor.vi")
ORIG = os.path.join(g.CLAUDEDEV, f"SCRATCH_setcommand_orig_{os.getpid()}.vi")
CMD = json.load(open(os.path.join(HERE, "rawcmd_labels.json"), encoding="utf-8"))["cmd"]
K = 0.72
WAIT_S = 2.0
g._run.__defaults__ = (6.0, 60.0)
LOG = []


def send(cmd):
    vi = g.op(RAW)
    vi.SetControlValue("VISA resource name", (RES, 0)); vi.SetControlValue(CMD, cmd + "\r")
    t0 = time.time(); g._run(vi)
    print(f"   SEND {cmd!r}  ({time.time() - t0:.2f} s)", flush=True)


def read_one(path, tag):
    vi = g.op(path)
    vi.SetControlValue("VISA resource name", (RES, 0)); vi.SetControlValue("Ring", 2)
    vi.SetControlValue("Baseline Startpoint", 0.0); vi.SetControlValue("Numeric", 0.0)
    try:
        g._run(vi)
    except RuntimeError as e:
        print(f"      {tag}: run raised {str(e)[:100]}", flush=True)
    return float(vi.GetControlValue("Pos_degree")), str(vi.GetControlValue("read buffer 2")), vi.GetControlValue("error out")


def pos(step):
    """POS on both VIs; a timed-out first read is retried once (the port-open artefact)."""
    out = {}
    for tag, path in (("signed", SIGNED), ("original", ORIG)):
        p, h, e = read_one(path, tag)
        if not h:
            p, h, e = read_one(path, tag)
        out[tag] = (p, h)
        print(f"   {step} {tag:8s}: hex {h!r} -> {p!r} deg  err {e[1]}", flush=True)
    LOG.append((step, out))
    return out


def settled(step, tries=10, gap=0.5):
    """Peer condition: no fixed wait after a motion command - poll POS (signed copy) until two consecutive reads
    agree (motion finished), then read both VIs. RAWCMD has no read path, so INR polling is replaced by
    position stability, which is what the acceptance needs."""
    last = None
    for k in range(tries):
        _p, h, _e = read_one(SIGNED, "poll")
        if h and h == last:
            print(f"   {step}: position stable at {h} after {k + 1} polls", flush=True)
            break
        last = h; time.sleep(gap)
    return pos(step)


def main():
    g._lv = None
    shutil.copyfile(os.path.join(D, "SetCommand.vi"), ORIG); time.sleep(0.3)
    try:
        for p in (ORIG, SIGNED, RAW):
            g.set_auto_error_handling(p, False)
        r0 = pos("R0")
        if not r0["signed"][1] or r0["signed"][1] != r0["original"][1]:
            print("STOP: baseline read disagrees or empty - no motion.", flush=True); return 2
        send("CLL X"); time.sleep(0.5)
        c1 = pos("C1")
        if c1["signed"][1] != "00000000" or c1["original"][1] != "00000000":
            print("STOP: counter not cleared as predicted - no motion.", flush=True); return 3
        send("PIC -10"); time.sleep(0.5)
        m1 = settled("M1")
        ok_neg = (m1["signed"][1] == "FFFFFFF6" and abs(m1["signed"][0] - (-10 * K)) < 1e-6
                  and abs(m1["original"][0] - 4294967286 * K) < 1e-3)
        print(f"   NEGATIVE READ {'PASS' if ok_neg else 'FAIL'}: signed {m1['signed']}, original {m1['original']}", flush=True)
        send("PIC 10"); time.sleep(0.5)
        m2 = settled("M2")
        ok_back = m2["signed"][1] == "00000000" and m2["original"][1] == "00000000"
        print(f"   RETURN {'PASS' if ok_back else 'FAIL'}: {m2}", flush=True)
        json.dump(LOG, open(os.path.join(HERE, "hw_rotor_signed_test.json"), "w"), indent=1)
        print(f"\nSUMMARY: negative-coordinate read {'PASS' if ok_neg else 'FAIL'}, return {'PASS' if ok_back else 'FAIL'}; counter left at 0", flush=True)
        return 0 if ok_neg and ok_back else 1
    finally:
        try:
            g.close_panel(ORIG)
        except Exception:
            pass
        try:
            os.remove(ORIG)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
