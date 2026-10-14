r"""fr90_md5 - read-only md5 of every file task fr90 pins (sources, leg copies, the original, the moved pick log). No LabVIEW.
    py tools/bench/lean_bench/fr90_md5.py"""
import hashlib, os                                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
LEAN = os.path.join(CD, "bench", "lean")
PINS = [("S1 copy (A source)", os.path.join(CD, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"),
        ("final VI (B source)", os.path.join(LEAN, "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f"),
        ("BOBS90 (OBS source)", os.path.join(LEAN, "D1_ring_p64Bobs_20261014_114246.vi"), "257fb8522d557305ab6fe2aa11a04b61"),
        ("A90r", os.path.join(LEAN, "D1_s1_fr90A_20261015_034347.vi"), "7ca7d861557fcb331387b8df72a9a975"),
        ("B90r", os.path.join(LEAN, "D1_ring_fr90B_20261015_034347.vi"), "b96b91e2f93989f915ff9a19f40ca965"),
        ("BOBS90r", os.path.join(LEAN, "D1_ring_fr90Bobs_20261015_034347.vi"), "71ed7b871228660941d24b3c91715df7"),
        ("original main VI", os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "Min_Track N beads V6_ParallelLoop.vi")), "2a78e17c449cacdaf5da389818526859"),
        ("moved pick log", os.path.join(HERE, "out_latest2", "legs", "W100OBS_a1", "picklog.txt"), "9a6cc2e3491afa481fcf5e0936f42945")]
bad = 0
for name, p, want in PINS:
    got = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None
    bad += got != want
    print("%-22s %s %s %s" % (name, got, "==" if got == want else "!=", want))
print("PINS %s (%d / %d)" % ("ALL MATCH" if not bad else "MISMATCH", len(PINS) - bad, len(PINS)))
