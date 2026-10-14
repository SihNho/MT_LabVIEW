# ---
# labview: none
# hardware: none
# ---
r"""fr150_md5 - read-only md5 pins for lean task fr150 (fr90_md5.py not edited). Reads files only; writes only
out_p64/fr150/md5_<start|end>.json and keeps its printed output in out_p64/fr150/md5_<start|end>.log (review fr90 c2 :18).
The three new Auto-Reset copies are added from fr150_state.json once fr150_build.py has pinned them.
    py tools/bench/lean_bench/fr150_md5.py start
    py tools/bench/lean_bench/fr150_md5.py end        (then the diff start vs end over the files present at both)"""
import hashlib, json, os, sys, time                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_p64", "fr150")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
L = os.path.join(CD, "bench", "lean")
FILES = {   # id: (path, pin)
    "A150": (os.path.join(L, "D1_s1_p64A150_20261015_015820.vi"), "65b409a8c44f9140b26f70135fb89b99"),
    "B150": (os.path.join(L, "D1_ring_p64B150_20261015_015820.vi"), "d3953cd6e96cc225ac0ed3f8ec3eaca0"),
    "BOBS150": (os.path.join(L, "D1_ring_p64Bobs150_20261015_015820.vi"), "35e7e973c93d1aa56bd6344fab1db8c1"),
    "rate wrapper": (os.path.join(L, "ConfigureGrab_rate150_20261015_015820.vi"), "1419d4c679bd2e68d4962e0ff3ad39d1"),
    "GetBuffFirst": (os.path.join(L, "GetBuffFirst_20261014_114246.vi"), "4cd87cb4fbe1a9a46675896397ec7a5f"),
    "camera file .icd": (r"C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (#000014FB0067A270).icd",
                         "2ea8512c57d734e76b02e91ced996d08"),
    "A90r": (os.path.join(L, "D1_s1_fr90A_20261015_034347.vi"), "7ca7d861557fcb331387b8df72a9a975"),
    "B90r": (os.path.join(L, "D1_ring_fr90B_20261015_034347.vi"), "b96b91e2f93989f915ff9a19f40ca965"),
    "BOBS90r": (os.path.join(L, "D1_ring_fr90Bobs_20261015_034347.vi"), "71ed7b871228660941d24b3c91715df7"),
    "original main VI": (os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "Min_Track N beads V6_ParallelLoop.vi")),
                         "2a78e17c449cacdaf5da389818526859"),
}
ABSENT = {"obs getbuff_first.txt": os.path.join(L, "obs", "getbuff_first.txt"),
          "obs configgrab_rate150.txt": os.path.join(L, "obs", "configgrab_rate150.txt"),
          "BOBS150 pick-log default path": os.path.join(HERE, "out_latest2", "picklog_w100.txt")}
STATE = os.path.join(HERE, "fr150_state.json")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def files():
    f = dict(FILES)
    if os.path.isfile(STATE):
        for k, v in (json.load(open(STATE, encoding="utf-8")).get("copies") or {}).items():
            f[k] = (v["path"], v["md5"])
    return f


def main(av):
    which = av[0] if av else "start"
    assert which in ("start", "end")
    os.makedirs(OUT, exist_ok=True)
    out = []
    say = lambda s: (print(s, flush=True), out.append(s))                                  # noqa: E731
    say("fr150_md5 %s %s" % (which, time.strftime("%Y-%m-%d %H:%M:%S")))
    d = {}
    for k, (p, pin) in files().items():
        m = md5(p)
        d[k] = {"path": p, "md5": m, "pin": pin, "pin_ok": m == pin}
        say("%-30s %s %s %s  %s" % (k, m, "==" if m == pin else "!=", pin, p))
    for k, p in ABSENT.items():
        d[k] = {"path": p, "exists": os.path.exists(p)}
        say("%-30s exists=%s  %s" % (k, os.path.exists(p), p))
    bad = [k for k, v in d.items() if v.get("pin_ok") is False]
    present = [k for k in ABSENT if d[k]["exists"]]
    say("PINS %s (%d / %d)" % ("ALL MATCH" if not bad else "MISMATCH %s" % bad, sum(1 for v in d.values() if v.get("pin_ok")),
                               sum(1 for v in d.values() if "pin_ok" in v)))
    say("ABSENT FILES %s" % ("all absent" if not present else "PRESENT %s" % present))
    rc = 1 if bad else 0
    if which == "end":
        a = json.load(open(os.path.join(OUT, "md5_start.json"), encoding="utf-8"))["files"]
        both = [k for k in d if k in a and "md5" in d[k]]
        diff = [k for k in both if a[k]["md5"] != d[k]["md5"]]
        say("DIFF start vs end (files pinned at both): %s" % ("EQUAL %d / %d" % (len(both), len(both)) if not diff else "CHANGED %s" % diff))
        say("added at end (new copies): %s" % [k for k in d if k not in a])
        rc = 1 if (bad or diff) else 0
    json.dump({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "files": d}, open(os.path.join(OUT, "md5_%s.json" % which), "w", encoding="utf-8"), indent=1)
    open(os.path.join(OUT, "md5_%s.log" % which), "w", encoding="utf-8").write("\n".join(out) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
