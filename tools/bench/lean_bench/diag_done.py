# ---
# labview: none
# hardware: none
# ---
"""diag_done - offline: why d0_locate.pick_by_template found no Done `Yes` button on a leg screenshot.
    py tools/bench/lean_bench/diag_done.py <png> [l t r b]"""
import os, sys                                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import d0_locate as D                                                                     # noqa: E402
png = sys.argv[1]
rect = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else (-6, 51, 1930, 1107)
w, why, cands = D.pick_by_template(png, rect)
print("WINNER", w and w.get("centre"), why)
for c in cands:
    cx, cy = c["caption_centre"]
    if "button_box" in c or (1000 < cx < 1250 and 850 < cy < 960):
        print(c["caption_centre"], c["caption_size"], c.get("button_box"), c.get("face"), c.get("template_score"), c.get("reject"))
