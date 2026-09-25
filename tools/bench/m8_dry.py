"""m8_dry.py - the P0 dry mode of drive_m8.py (card 74-1): COM, GUI, motor gate, process list and the leg itself
are replaced, so the wrapper's whole path (retarget, v5.main gates G0-G5, cleanup, report, M-gates, json) runs with
nothing reaching LabVIEW, a window or a serial port. The fake leg writes a cal + tra file shaped like the real ones
(header text from tools/bench/d0_out/v5_20260918_180813/tra001-000)."""
import os


class FakeCom:
    def call(self, kind, *args, timeout=None):
        return {"state": 1, "get": 0}.get(kind, "DRY %s ok" % kind)


def stub(v5, d4, d0):
    d0.com = FakeCom()
    d0.gui = lambda *a, **k: "left=0 top=0 right=1920 bottom=1080\nVERDICT: CLEAR"
    d4.motor_gate = lambda why: (0, "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nSESSION START OK (DRY)")
    d4.record_panel = lambda tag: (60, 0, {})
    v5.labview_running = lambda: False
    v5.labview_handles = lambda: 0

    def fake_leg(tag, n, base_path, cal_wait):
        os.makedirs(v5.RUN_DIR, exist_ok=True)
        open(base_path, "wb").write(b"\x00" * 1000)
        open(os.path.join(v5.RUN_DIR, "tra001-000"), "wb").write(
            b"Raw data file of N bead xyz trace\nactual data points/nominal: 2968/2000000\n" + b"\x00" * 800)
        for i in (7, 8, 9, 10, 13):
            v5.rec("%d %s.L%d dry" % (n + i, tag, i), "DRY", True, "dry")
        last = 100 + int(90 * v5.RUN_S)     # card 89-4 review: sized from v5.RUN_S so a --run-s plumbing regression fails T5
        v5.rec("%d %s.L11 dry" % (n + 11, tag), "DRY", True, "current image number over %.0fs: 100 .. %d (lost=0)" % (v5.RUN_S, last))
        print("DRY RUN_S=%s" % v5.RUN_S, flush=True)
        v5.FACTS["frames_%s" % tag] = [100, last]
        v5.FACTS["stop_%s" % tag] = {"mechanism": "VI SERVER SetControlValue (DRY)", "latency_s": 1.0}
        return True
    v5.leg = fake_leg
