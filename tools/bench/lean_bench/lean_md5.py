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
    r"bench\lean\D1_ring_p6_replay_20261013_135743.vi",                           # P6-3 (2026-10-13): the P6 replay copy, read-only input
    r"bench\lean\gap_get_buff_image_paced60_20261013_161639.vi",                  # p6fix (2026-10-13): P6-3 test files reused read-only
    r"bench\lean\RingSeqCheck_w40_20261013_161639.vi", r"bench\lean\RingSeqCheck_w100_20261013_161639.vi",
    r"bench\lean\D1_ring_p6fix_20261013_231910.vi", r"bench\lean\D1_ring_p6fix_replay_20261013_231910.vi",   # latest (2026-10-14): p6fix files, read-only
    r"bench\lean\D1_ring_p6fix_replay_gap_20261013_231910.vi", r"bench\lean\D1_ring_p6fix_replay_w40_20261013_231910.vi",
    r"bench\lean\D1_ring_p6fix_replay_w100_20261013_231910.vi",
    r"bench\lean\RingPickSlot_latest_20261014_010104.vi", r"bench\lean\D1_ring_p6latest_20261014_010104.vi",   # latest retry (2026-10-14): fail1's 6 files
    r"bench\lean\D1_ring_p6latest_replay_20261014_010104.vi", r"bench\lean\D1_ring_p6latest_replay_gap_20261014_010104.vi",
    r"bench\lean\D1_ring_p6latest_replay_w40_20261014_010104.vi", r"bench\lean\D1_ring_p6latest_replay_w100_20261014_010104.vi",
    r"bench\lean\PickLog_latestobs_20261014_025316.vi", r"bench\lean\RingPickSlot_latestobs_20261014_025316.vi",   # latest retry 2: retry 1's 3 saved files
    r"bench\lean\D1_ring_p6latestobs_replay_w100_20261014_025316.vi",
    r"bench\lean\D1_ring_p6close_replay_20261014_035857.vi", r"bench\lean\D1_ring_p6close_gap_20261014_035857.vi",   # p6close (2026-10-14): fresh byte copies of the 4 test VIs
    r"bench\lean\D1_ring_p6close_w40_20261014_035857.vi", r"bench\lean\D1_ring_p6close_w100_20261014_035857.vi",
    r"background VIs_COPY\get buff image-lost frames.vi", "EMPTY_v0.vi", "DonorCase_v0.vi",   # p64p1 (2026-10-14): wrapper inputs
    r"bench\lean\D1_ring_p64Bobs_20261014_114246.vi", r"bench\lean\GetBuffFirst_20261014_114246.vi",   # p64p1 outputs (BOBS90 + wrapper)
    r"bench\lean\GetBuffLog_20261014_114246.vi", r"bench\lean\GetBuffFirst_test_paced_20261014_114246.vi",
    r"bench\lean\GetBuffFirst_test_gap_20261014_114246.vi", r"bench\lean\GetBuffFirst_harness_paced_20261014_114246.vi",
    r"bench\lean\GetBuffFirst_harness_gap_20261014_114246.vi")] + [
    os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928", f) for f in ("cal001", "tra001-000")] + [
    os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi"),
    r"G:\m8_replay_frames\frames_manifest.json",
    os.path.join(BENCH, "p6_replay_frames_manifest.txt"), os.path.join(BENCH, "motor_limits.json"),
    os.path.join(ROOT, "tools", "motor_gate.py"), os.path.join(BENCH, "plans", "plan_replay_swap_170.json")]
# latest retry (2026-10-14, review line 13/18): every file of `zz_LabView VI\background VIs\` (a superset of the background subVIs
# the W100 copy loads; the loaded subset is listed by latestobs_build.py from the cold load)
BG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(ROOT))), "background VIs")
FILES += sorted(os.path.join(dp, f) for dp, _dn, fs in os.walk(BG) for f in fs)
# p64p2 (2026-10-14): the vi.lib library holding `IMAQdx Configure Grab.vi` (an original) and the camera file (.icd, must not change)
FILES += [r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Configure Grab.vi",   # .llb is a folder here
          r"C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (#000014FB0067A270).icd"]
# p64p2 outputs: only with --outputs (so `--diff p64p2_start p64p2_end` compares inputs only)
if "--outputs" in sys.argv:
    import glob
    FILES += sorted(glob.glob(os.path.join(CD, "bench", "lean", "*_p64p2_*.vi")) + glob.glob(os.path.join(CD, "bench", "lean", "*rate150*.vi"))
                    + glob.glob(os.path.join(CD, "bench", "lean", "*p64*150_*.vi")) + glob.glob(os.path.join(CD, "bench", "lean", r"D1_s1_p64A_*.vi")))
    sys.argv.remove("--outputs")
# p64p2 retry 1 (2026-10-15, tags p64p2r1_start / p64p2r1_end): with --r1 also the failed cycle's outputs (kept, never re-saved)
# and vi.lib `Merge Errors.vi` (an original the new wrapper calls); --r1new lists ONLY the retry's new outputs (pinned at the end)
if "--r1" in sys.argv:
    FILES += [os.path.join(CD, "bench", "lean", f) for f in (
        "ConfigureGrab_rate150_20261014_140059.vi", "D1_s1_p64A_20261014_140059.vi", "D1_s1_p64A150_20261014_140059.vi",
        "D1_ring_p64B150_20261014_140059.vi", "D1_ring_p64Bobs150_20261014_140059.vi", "Rate150Harness_p64p2_20261014_140059.vi")]
    FILES += [os.path.join(HERE, "out_p64", "p64p2", f) for f in sorted(os.listdir(os.path.join(HERE, "out_p64", "p64p2")))]
    FILES += [r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb\Merge Errors.vi",
              r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Write Delimited Spreadsheet (string).vi",
              r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Read Attributes From String.vi"]
    sys.argv.remove("--r1")
if "--r1new" in sys.argv:
    import glob
    _ts = json.load(open(os.path.join(HERE, "p64p2r1_state.json"), encoding="utf-8"))["ts"]   # the retry's <newts>
    FILES = sorted(glob.glob(os.path.join(CD, "bench", "lean", "*_%s.vi" % _ts)) + glob.glob(os.path.join(HERE, "out_p64", "p64p2_r1", "*")))
    sys.argv.remove("--r1new")


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
