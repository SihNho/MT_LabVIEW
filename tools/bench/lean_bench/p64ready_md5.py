# ---
# labview: none
# hardware: none
# ---
r"""p64ready_md5 - read-only md5 pins for lean task p64ready (the 150 Hz offline dry). Reads files only; writes only under
out_p64/p64ready/.
    py tools/bench/lean_bench/p64ready_md5.py start      -> out_p64/p64ready/md5_start.json
    py tools/bench/lean_bench/p64ready_md5.py end        -> out_p64/p64ready/md5_end.json, then prints the diff start vs end"""
import hashlib, json, os, sys, time                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_p64", "p64ready")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
L = os.path.join(CD, "bench", "lean")
FILES = {   # id: (path, pin or None = start must equal end only)
    "wrapper": (os.path.join(L, "ConfigureGrab_rate150_20261015_015820.vi"), "1419d4c679bd2e68d4962e0ff3ad39d1"),
    "A150": (os.path.join(L, "D1_s1_p64A150_20261015_015820.vi"), "65b409a8c44f9140b26f70135fb89b99"),
    "B150": (os.path.join(L, "D1_ring_p64B150_20261015_015820.vi"), "d3953cd6e96cc225ac0ed3f8ec3eaca0"),
    "BOBS150": (os.path.join(L, "D1_ring_p64Bobs150_20261015_015820.vi"), "35e7e973c93d1aa56bd6344fab1db8c1"),
    "GetBuffFirst": (os.path.join(L, "GetBuffFirst_20261014_114246.vi"), "4cd87cb4fbe1a9a46675896397ec7a5f"),
    "p64_abba.py": (os.path.join(HERE, "p64_abba.py"), None),
    "p64_leg.py": (os.path.join(HERE, "p64_leg.py"), None),
    "p64_own.py": (os.path.join(HERE, "p64_own.py"), None),
    "p64_sum.py": (os.path.join(HERE, "p64_sum.py"), None),
    "drive_legguard.py": (os.path.join(os.path.dirname(HERE), "drive_legguard.py"), None),
    "picklog_w100": (os.path.join(HERE, "out_latest2", "picklog_w100.txt"), "9a6cc2e3491afa481fcf5e0936f42945"),
    "icd": (r"C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (#000014FB0067A270).icd",
            "2ea8512c57d734e76b02e91ced996d08"),
}
EXTRA = {"obs_getbuff_first": os.path.join(L, "obs", "getbuff_first.txt"), "obs_configgrab_rate150": os.path.join(L, "obs", "configgrab_rate150.txt")}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def snap():
    d = {k: {"path": p, "md5": md5(p), "pin": pin, "pin_ok": (md5(p) == pin) if pin else None} for k, (p, pin) in FILES.items()}
    d["picklog_w100"]["lines"] = sum(1 for _ in open(FILES["picklog_w100"][0], "rb")) if os.path.isfile(FILES["picklog_w100"][0]) else None
    for k, p in EXTRA.items():
        d[k] = {"path": p, "exists": os.path.exists(p)}
    return {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "files": d}


def main(av):
    which = av[0] if av else "start"
    assert which in ("start", "end")
    os.makedirs(OUT, exist_ok=True)
    s = snap()
    jp = os.path.join(OUT, "md5_%s.json" % which)
    json.dump(s, open(jp, "w", encoding="utf-8"), indent=1)
    for k, v in s["files"].items():
        print("%-24s %s" % (k, json.dumps({x: v[x] for x in v if x != "path"})))
    pins_bad = [k for k, v in s["files"].items() if v.get("pin_ok") is False]
    print("PINS %s" % ("ALL MATCH" if not pins_bad else "MISMATCH %s" % pins_bad))
    if which == "end":
        a = json.load(open(os.path.join(OUT, "md5_start.json"), encoding="utf-8"))["files"]
        diff = [k for k in s["files"] if a.get(k) != s["files"][k]]
        print("DIFF start vs end: %s" % ("EQUAL %d / %d" % (len(s["files"]), len(s["files"])) if not diff else "CHANGED %s" % diff))
        return 1 if diff or pins_bad else 0
    return 1 if pins_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
