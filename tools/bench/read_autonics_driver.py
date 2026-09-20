"""read_autonics_driver.py - the Autonics rotor driver's terminals and saved defaults, all three VIs.

The rotor is an Autonics motor on COM5 (NI-VISA alias `Rotor`, an FTDI USB-serial port). Its driver is
`instr.lib\\Autonics Motor\\`, which contains exactly Configure.vi, SetCommand.vi and Close.vi - and those are
the three subVIs the main VI calls, which is how the rotor was identified.

The MODEL is still unknown. The user has said it is NOT the PMC-4B model, and the FTDI chip (VID_0403/PID_6001)
is generic, so the USB ids identify nothing. `Configure.vi` is the next place a model-specific setting would
show: baud, data bits, termination, an axis count, a pulses-per-revolution figure.

READ ONLY. These are vendor driver VIs under `instr.lib` - opened, read, never saved (CLAUDE.md rule 1).

  py tools/bench/read_autonics_driver.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor"
VIS = ["Configure.vi", "SetCommand.vi", "Close.vi"]
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    for nm in VIS:
        path = os.path.join(LIB, nm)
        print(f"\n--- {nm}  (READ ONLY, never saved) ---", flush=True)
        try:
            rows = g.fp_labels(path, max_n=40)
        except Exception as e:
            print(f"   fp_labels EXC {str(e)[:200]}", flush=True)
            continue
        try:
            ref = g.lv().GetVIReference(path, "", False, 0)
        except Exception as e:
            print(f"   GetVIReference EXC {str(e)[:160]}", flush=True)
            ref = None
        for i, lab, ind in rows:
            val = "<no ref>"
            if ref is not None and lab:
                try:
                    val = repr(ref.GetControlValue(lab))
                except Exception as e:
                    val = f"<unreadable: {str(e)[:50]}>"
            print(f"   {i:2d} {'IND' if ind else 'CTL'} {lab!r:30} = {val}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
