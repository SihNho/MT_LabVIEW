"""diag_c111b_shots - card 111-2 A3 capture match, OFFLINE (no LabVIEW): crop the post-double-click block-diagram captures of
card 111-1 (tools/bench/errorlist_shots/bd_*_after<N>.png, paths from errorlist_..._c111.json) for the items whose object has
no uid, enlarged x2, into tools/bench/errorlist_shots/c111b_item<N>_<region>.png, and print where LabVIEW's selection colour
(#0078E5-ish blue dashes, lv_errorlist.py docstring) sits on each capture.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c111b_shots.log -- py -u tools/bench/diag_c111b_shots.py"""
import json, os, sys                                                                 # noqa: E401
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol                                                                      # noqa: E402
EL = json.load(open(os.path.join(HERE, "errorlist_D1_l2_b1_20260927_193100_c111.json"), encoding="utf-8"))["items"]
ITEMS = [6, 9, 16, 23, 24, 28, 44, 46, 47, 48, 49, 50]
OUTD = os.path.join(HERE, "errorlist_shots")
n_ok = 0
for it in EL:
    if it["index"] not in ITEMS:
        continue
    p = (it.get("show_error") or {}).get("screenshot")
    if not p or not os.path.exists(p):
        print("ITEM %d no capture" % it["index"], flush=True)
        continue
    im = Image.open(p).convert("RGB")
    W, H = im.size
    px = im.load()
    blue = [(x, y) for y in range(80, H - 30, 1) for x in range(10, W - 30, 1)
            if px[x, y][2] > 200 and px[x, y][0] < 60 and 90 < px[x, y][1] < 150]
    if blue:
        xs, ys = [b[0] for b in blue], [b[1] for b in blue]
        box = (max(0, min(xs) - 120), max(0, min(ys) - 90), min(W, max(xs) + 120), min(H, max(ys) + 90))
    else:
        box = (0, 0, W, H)
    out = os.path.join(OUTD, "c111b_item%d_sel.png" % it["index"])
    c = im.crop(box)
    c.resize((c.size[0] * 2, c.size[1] * 2)).save(out)
    n_ok += 1
    print("ITEM %d | %s | selection-blue px %d bbox %s -> %s" % (it["index"], it["raw"][:70], len(blue), box, os.path.basename(out)), flush=True)
print(protocol.result_line(protocol.make_result(n_ok, len(ITEMS) - n_ok, None if n_ok == len(ITEMS) else "missing capture", [])))
