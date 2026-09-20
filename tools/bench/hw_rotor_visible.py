"""hw_rotor_visible.py - VISIBLE rotor test at the user's request (2026-09-14 20:3x: "-방향으로 3바퀴 돌려보고 5초 있다가
원점복귀"): counter stays 0 (user: "고치자 0으로"). PIC -1500 (= -3 turns at 500 pulses/turn) -> poll POS until stable
-> wait 5 s -> PAB 0 (absolute origin return; fallback PIC +1500 if the controller ignores PAB 0) -> poll -> POS 0.
Reads through SetCommand_signed.vi (Ring 2, Baseline 0); commands through RAWCMD_rotor.vi.
  py tools/bgrun.py --max-min 5 --log tools/bench/hw_rotor_visible.log -- py -u tools/bench/hw_rotor_visible.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

RES = "Rotor"
SIGNED = os.path.join(g.CLAUDEDEV, "SetCommand_signed.vi")
RAW = os.path.join(g.CLAUDEDEV, "RAWCMD_rotor.vi")
CMD = json.load(open(os.path.join(HERE, "rawcmd_labels.json"), encoding="utf-8"))["cmd"]
TURNS, PPT = 3, 500
g._run.__defaults__ = (6.0, 60.0)


def send(cmd):
    vi = g.op(RAW); vi.SetControlValue("VISA resource name", (RES, 0)); vi.SetControlValue(CMD, cmd + "\r")
    g._run(vi); print(f"   SEND {cmd!r} at t={time.time() - T0:.1f} s", flush=True)


def read():
    vi = g.op(SIGNED)
    vi.SetControlValue("VISA resource name", (RES, 0)); vi.SetControlValue("Ring", 2)
    vi.SetControlValue("Baseline Startpoint", 0.0); vi.SetControlValue("Numeric", 0.0)
    try:
        g._run(vi)
    except RuntimeError as e:
        print(f"      read raised {str(e)[:80]}", flush=True)
    return float(vi.GetControlValue("Pos_degree")), str(vi.GetControlValue("read buffer 2"))


def settle(label, max_s=90.0, gap=0.5):
    t = time.time(); last = None; n = 0
    while time.time() - t < max_s:
        p, h = read(); n += 1
        if h and h == last:
            print(f"   {label}: stable {h} = {p:.1f} deg after {time.time() - t:.1f} s ({n} polls)", flush=True)
            return p, h
        if h:
            print(f"      {label}: {h} = {p:.1f} deg  t={time.time() - T0:.1f} s", flush=True)
        last = h; time.sleep(gap)
    print(f"   {label}: NOT stable within {max_s} s (last {last})", flush=True)
    return read()


def main():
    global T0
    g._lv = None
    for p in (SIGNED, RAW):
        g.set_auto_error_handling(p, False)
    T0 = time.time()
    p0, h0 = read()
    if not h0:
        p0, h0 = read()
    print(f"   start: {h0} = {p0:.1f} deg", flush=True)
    if h0 != "00000000":
        print("STOP: counter is not 0 - not moving.", flush=True); return 2
    send(f"PIC -{TURNS * PPT}"); t_move = time.time()
    p1, h1 = settle("after -3 turns")
    print(f"   motion took about {time.time() - t_move:.1f} s (incl. polling); expected {-TURNS * 360:.0f} deg -> got {p1:.1f} deg ({h1})", flush=True)
    print("   waiting 5 s ...", flush=True); time.sleep(5.0)
    send("PAB 0"); t_back = time.time()
    p2, h2 = settle("after PAB 0")
    if h2 != "00000000":
        print("   PAB 0 did not return to 0 - fallback PIC +1500", flush=True)
        send(f"PIC {TURNS * PPT}"); p2, h2 = settle("after PIC +1500")
    print(f"   return took about {time.time() - t_back:.1f} s; final {h2} = {p2:.1f} deg", flush=True)
    ok = abs(p1 - (-TURNS * 360)) < 1e-6 and h2 == "00000000"
    print(f"\nSUMMARY: -3 turns read {p1:.1f} deg ({'PASS' if abs(p1 + TURNS * 360) < 1e-6 else 'FAIL'}); origin return {'PASS' if h2 == '00000000' else 'FAIL'}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
