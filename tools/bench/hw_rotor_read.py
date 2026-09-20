"""hw_rotor_read.py - HARDWARE, NO MOTION: read the rotor's current position through the Autonics driver.
User 2026-09-14 20:1x: "직접 움직여보자" (hardware acceptance approved; rig disassembled, rotor free). This step only
QUERIES: Configure copy (VISA Open + init write) on alias 'Rotor' (ASRL5::INSTR), then SetCommand Ring 2 (Get Position,
measured) on (a) claudeDev\SetCommand_signed.vi and (b) a scratch copy of the instr.lib original, Baseline 0 so
Pos_degree = 0.72 deg/pulse * raw. Prints the raw reply too. Auto error handling is switched off IN MEMORY on the
copies (nothing saved); the instr.lib originals are never touched.
  py tools/bgrun.py --max-min 5 --log tools/bench/hw_rotor_read.log -- py -u tools/bench/hw_rotor_read.py [resource]
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

RES = sys.argv[1] if len(sys.argv) > 1 else "Rotor"
D = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor"
SIGNED = os.path.join(g.CLAUDEDEV, "SetCommand_signed.vi")
CFG = os.path.join(g.CLAUDEDEV, f"SCRATCH_autonics_cfg_{os.getpid()}.vi")
ORIG = os.path.join(g.CLAUDEDEV, f"SCRATCH_setcommand_orig_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 60.0)


def read(vi, tag):
    vi.SetControlValue("VISA resource name", (RES, 0)); vi.SetControlValue("Ring", 2)
    vi.SetControlValue("Baseline Startpoint", 0.0); vi.SetControlValue("Numeric", 0.0)
    t0 = time.time()
    try:
        g._run(vi)
    except RuntimeError as e:
        print(f"   {tag}: run raised {str(e)[:120]}", flush=True)
    err = vi.GetControlValue("error out"); pos = vi.GetControlValue("Pos_degree")
    raw = vi.GetControlValue("read buffer"); sub = vi.GetControlValue("read buffer 2")
    print(f"   {tag}: Pos_degree {pos!r} deg (= {pos / 0.72 if isinstance(pos, float) else '?'} pulses), raw {raw!r}, hex {sub!r}, "
          f"error {err!r} ({time.time() - t0:.1f} s)", flush=True)
    return pos, sub, err


def main():
    g._lv = None
    shutil.copyfile(os.path.join(D, "Configure.vi"), CFG); shutil.copyfile(os.path.join(D, "SetCommand.vi"), ORIG); time.sleep(0.3)
    try:
        for p in (CFG, ORIG, SIGNED):
            g.set_auto_error_handling(p, False)
        cfg = g.op(CFG); cfg.SetControlValue("VISA resource name", (RES, 0))
        try:
            g._run(cfg)
            print(f"Configure on {RES!r}: ok, resource out {cfg.GetControlValue('VISA resource name out')!r}", flush=True)
        except RuntimeError as e:
            print(f"Configure on {RES!r}: raised {str(e)[:160]}", flush=True)
        # run 1 (20:17): the FIRST read after Configure timed out and the next call got the reply -> order swapped and a
        # third read added: the first call is expected to be the slow/empty one whichever VI makes it.
        order = [("original", ORIG), ("signed  ", SIGNED), ("signed  ", SIGNED), ("original", ORIG)]
        res = [read(g.op(p), tag) for tag, p in order]
        hexes = [r[1] for r in res]
        print(f"replies in order: {hexes}", flush=True)
        if len({h for h in hexes if h}) == 1:
            print(f"AGREE: every non-empty reply is {[h for h in hexes if h][0]}; positions {[r[0] for r in res]}", flush=True)
    finally:
        for p in (CFG, ORIG):
            try:
                g.close_panel(p)
            except Exception:
                pass
        for p in (CFG, ORIG):
            try:
                os.remove(p)
            except OSError as e:
                print(f"   leftover {p}: {e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
