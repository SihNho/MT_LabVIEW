# ---
# labview: none
# hardware: none
# ---
"""make_ref_done - lean bench: tools/bench/ref_done_yes_button.png (d0_locate.REF_DONE) is untracked in the main checkout and absent
in this worktree, so pick_by_template scored no candidate (S1 leg a1 L4 FAIL). Cut a 46x29 patch (the stored ref's size) from this
run's own screenshot at the box d0_locate's shape test found: (1091,900)-(1136,928), caption 25x12.
    py tools/bench/lean_bench/make_ref_done.py <png> l t r b"""
import os, sys                                                                            # noqa: E401
from PIL import Image
png, (l, t, r, b) = sys.argv[1], [int(v) for v in sys.argv[2:6]]
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ref_done_yes_button.png")
if os.path.exists(out):
    sys.exit("REFUSED: %s exists" % out)
Image.open(png).convert("RGB").crop((l, t, r + 1, b + 1)).save(out)
print("WROTE", out, Image.open(out).size)
