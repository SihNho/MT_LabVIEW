"""diag_c92c_capread_selftest.py - offline check of diag_c92c_leg.read_capture (a READ, no LabVIEW, no GUI act):
C1 a present window ("Program Manager") resolves to an hwnd with GetGUIThreadInfo ok; C2 a missing title gives no hwnd, no raise."""
import ctypes as C, ctypes.wintypes as W, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
import protocol as P                                                            # noqa: E402
src = open(os.path.join(HERE, "diag_c92c_leg.py")).read()
U32 = C.windll.user32


class d0: COPY_TITLE = "Program Manager"                                        # noqa: E701


exec(src[src.index("class GTI"):src.index("real_probe = ")])
a = read_capture("c1"); d0.COPY_TITLE = "zzz_no_such_window_c92c"; b = read_capture("c2")
g = {"C1 present window read ok": bool(a.get("panel_hwnd")) and a.get("ok") is True and "err" not in a,
     "C2 missing window: no hwnd, no raise": b.get("panel_hwnd") is None and "err" not in b}
for k, v in g.items(): print("GATE %s %s" % (k, "PASS" if v else "FAIL"))
bad = [k for k, v in g.items() if not v]
print(P.result_line(P.make_result(len(g) - len(bad), len(bad), bad[0] if bad else None)))
