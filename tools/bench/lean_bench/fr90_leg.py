# ---
# labview: read
# hardware: camera
# ---
r"""fr90_leg - p64_leg.py (NOT edited) plus ONE read: the `# of Auto-Reset` indicator (and `Auto-Reset`, `Total Lost Frames`,
the frame counter) read by VI Server just BEFORE and just AFTER the leg's stop (v5.stop_with_fallback wrapped in the child; the
leg script's own stop hook, diag_c104_leg.py:137-147, wraps this one and still runs first). Reads only; nothing is written to
the VI. The reads go to <out>/fr90_autoreset.json; the parent adds gate
  L8 `# of Auto-Reset` == 0 at the end (after-stop read; before-stop read if the after read failed)
to <out>/p64_leg.json, so p64_abba's "leg gates all pass" includes it. A leg with a non-zero count is INVALID (task fr90 item 4).
Since S0 attempt 1 also: v5's display locator is fr90_locate.locate_image_display (the original first; a camera-shaped fallback
when the live field is brighter than the original's mid-grey band). Retry 1 (C2): that locator hands v5 a box only if every
side is within +-5 px of the recorded display rect (232,500)-(873,1013); otherwise None, so v5 ends the leg before any pick.
    py -u tools/bench/lean_bench/fr90_leg.py --src <vi> --picks 15 --run-s 120 --hz 90 --out <dir>"""
import json, os, sys, time                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p64_leg as PL                                                                      # noqa: E402
AR_IND, AR_CTL = "# of Auto-Reset", "Auto-Reset"
OUT_NAME = "fr90_autoreset.json"


def child(av):
    out = av[av.index("--out") + 1]
    import drive_original_copy_v5 as v5                                                   # the same module drive_m8 / the leg script import
    d0 = v5.d0
    real = v5.stop_with_fallback
    rec = {"reads": []}

    def read(tag):
        r = {"tag": tag, "t": round(time.time(), 2)}
        for lab in (AR_IND, AR_CTL, d0.I_LOST, v5.I_FRAME):
            try:
                r[lab] = d0.getv(lab, timeout=4.0)
            except Exception as e:                                                         # noqa: BLE001
                r[lab] = "ERR %r" % (e,)
        rec["reads"].append(r)
        json.dump(rec, open(os.path.join(out, OUT_NAME), "w", encoding="utf-8"), indent=1, default=str)
        print("[fr90 leg] AUTORESET %s" % json.dumps(r, default=str), flush=True)

    def hook(tag):
        read("before-stop %s" % tag)
        o = real(tag)
        read("after-stop %s" % tag)
        return o
    v5.stop_with_fallback = hook
    import fr90_locate                                                                     # S0 attempt 1: the live field is brighter than
    v5.L.locate_image_display = fr90_locate.locate_image_display                           # d0_locate's mid-grey band (fr90_locate.py doc)
    PL.child(av)


def count_at_end(out):
    p = os.path.join(out, OUT_NAME)
    if not os.path.isfile(p):
        return None, "no %s (the leg never reached its stop)" % OUT_NAME
    reads = json.load(open(p, encoding="utf-8")).get("reads") or []
    for want in ("after-stop", "before-stop"):
        for r in reversed(reads):
            v = r.get(AR_IND)
            if r["tag"].startswith(want) and isinstance(v, (int, float)):
                return v, "%s read %r (Auto-Reset control %r)" % (r["tag"], v, r.get(AR_CTL))
    return None, "no numeric read: %r" % (reads,)


def parent(av):
    PL.__file__ = os.path.abspath(__file__)                                               # p64_leg.parent launches "<__file__> --child": this file
    rc = PL.parent(av)
    out = av[av.index("--out") + 1]
    n, why = count_at_end(out)
    jp = os.path.join(out, "p64_leg.json")
    if os.path.isfile(jp):
        j = json.load(open(jp, encoding="utf-8"))
        j["facts"]["auto_reset_end"], j["facts"]["auto_reset_why"] = n, why
        j["gates"]["L8 # of Auto-Reset == 0 at the end"] = (n == 0)
        json.dump(j, open(jp, "w", encoding="utf-8"), indent=1, default=str)
    print("FACTS {\"auto_reset_end\": %s, \"auto_reset_why\": %s}" % (json.dumps(n), json.dumps(why)), flush=True)
    print("GATE %-60s %s" % ("L8 # of Auto-Reset == 0 at the end", "PASS" if n == 0 else "FAIL"), flush=True)
    return 1 if (rc or n != 0) else 0


if __name__ == "__main__":
    if "--child" in sys.argv:
        child(sys.argv[1:])
    else:
        sys.exit(parent(sys.argv[1:]))
