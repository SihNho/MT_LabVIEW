# ---
# labview: none
# hardware: none
# ---
"""p6close_copy - byte-copy the 4 test VIs of the final P6 (latest fail1 lineage) to fresh files under claudeDev\bench\lean\
(task p6close step 3). Each source is pinned before, each copy must hash equal to its source. Writes p6close_copies.json.
    py tools/bench/lean_bench/p6close_copy.py"""
import hashlib, json, os, shutil, sys, time                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
LEAN = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
SRC = {"replay": ("D1_ring_p6latest_replay_20261014_010104.vi", "d615e096075c74c5ac0c63c05a722217"),
       "gap": ("D1_ring_p6latest_replay_gap_20261014_010104.vi", "f656620329ffaf8c675fe050192ff9d3"),
       "w40": ("D1_ring_p6latest_replay_w40_20261014_010104.vi", "0eb42f736d6874e1af58781c82e81e37"),
       "w100": ("D1_ring_p6latest_replay_w100_20261014_010104.vi", "04e5400646af36b7afc3876d6fe3b6a7")}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


if __name__ == "__main__":
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = {"stamp": stamp, "copies": {}}
    for k, (name, pin) in SRC.items():
        src = os.path.join(LEAN, name)
        if md5(src) != pin:
            print("STOP source pin mismatch", k, src); sys.exit(2)
        dst = os.path.join(LEAN, "D1_ring_p6close_%s_%s.vi" % (k, stamp))
        if os.path.exists(dst):
            print("STOP target exists", dst); sys.exit(2)
        shutil.copyfile(src, dst)
        m = md5(dst)
        ok = m == pin and md5(src) == pin
        out["copies"][k] = {"src": src, "src_md5": pin, "path": dst, "md5": m, "equal": ok}
        print("%s %s %s -> %s %s" % ("OK  " if ok else "FAIL", k, pin, m, dst))
        if not ok:
            sys.exit(3)
    json.dump(out, open(os.path.join(HERE, "p6close_copies.json"), "w"), indent=1)
    print("COPIES 4/4 equal, stamp", stamp)
