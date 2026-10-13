# ---
# labview: none
# hardware: none
# ---
"""lean_md5 - md5 of the lean-bench inputs (task.md "md5s of the inputs at the end (must equal the start)").
    py tools/bench/lean_bench/lean_md5.py <tag>     -> prints one line per file, writes tools/bench/lean_bench/md5_<tag>.json
    py tools/bench/lean_bench/lean_md5.py --diff a b -> compares two snapshots"""
import hashlib, json, os, sys                                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FILES = [os.path.join(CD, p) for p in (
    "D1_ring_p6_20261012_212645.vi", "D1_ring_p5_20261010_172913.vi", "D1_ring_p5s01_20261009_124542.vi", "D1_s1_copy.vi",
    "RingPickSlot_v0.vi", "RingSeqCheck_v0.vi",
    r"replay\D1_s1_replay_20260925_075422.vi", r"replay\replay_get_buff_image.vi", r"replay\replay_get_image_cal.vi",
    r"replay\replay_imaqdx_get_image_buf.vi", r"replay\replay_imaqdx_get_image_buf_paced60.vi",
    r"replay\replay_get_buff_image_paced60.vi",
    r"bench\lean\D1_ring_p6_replay_20261013_135743.vi")] + [                     # P6-3 (2026-10-13): the P6 replay copy, read-only input
    os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi"),
    r"G:\m8_replay_frames\frames_manifest.json",
    os.path.join(BENCH, "p6_replay_frames_manifest.txt"), os.path.join(BENCH, "motor_limits.json"),
    os.path.join(ROOT, "tools", "motor_gate.py"), os.path.join(BENCH, "plans", "plan_replay_swap_170.json")]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


if __name__ == "__main__":
    if sys.argv[1] == "--diff":
        a, b = (json.load(open(os.path.join(HERE, "md5_%s.json" % t))) for t in sys.argv[2:4])
        bad = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        for k in bad:
            print("DIFF %s %s -> %s" % (k, a.get(k), b.get(k)))
        print("EQUAL %d / %d" % (len(set(a) | set(b)) - len(bad), len(set(a) | set(b))))
        sys.exit(1 if bad else 0)
    r = dict((p, md5(p)) for p in FILES)
    for p, m in r.items():
        print("%s  %s" % (m, p))
    json.dump(r, open(os.path.join(HERE, "md5_%s.json" % sys.argv[1]), "w"), indent=1)
