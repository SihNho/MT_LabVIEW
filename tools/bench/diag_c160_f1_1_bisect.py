# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/brief_160-f1-1.md
# ---
r"""diag_c160_f1_1_bisect - card 160-f1-1, MEASURE only (PD390(g)). Bisects 421d6108..a9d0da22 for the first commit whose
tools/*.py make `stage_prerun --dry tools/recipes/stage_d1_ring_p3b2a.py --no-record` lose the four PB rows
2626|Terminal|array|0-3 (diag_c159_f1_2_facts.md:18-23). REUSES diag_c159_f1_2_t2 (Serve finder, src_bytes, md5b - the
same in-memory serving of every top-level tools/*.py from a git revision, __file__ = the real path; nothing imported from
the working tree's tools/*.py, nothing written to disk but this script's log/json). Adds: a wrapper on
vigraph.computation_diff_frame that prints the PB row keys, node 2626's rows / renames and (when vigraph has it) the
POSITION key of every node-2626 terminal in both graphs; and a fall-through check naming any tools/ module NOT served.
EXISTING checked: diag_c159_f1_2_t2.py (C6 421d6108 PASS / C7 a9d0da22 FAIL, its log:85,95); git bisect itself is not used
because it checks out the working tree (another card edits stagesim/stagexec there).
PREDICTION: 421d6108 PB PASS; a9d0da22 PB FAIL missing 2626|Terminal|array|0..3; exactly one first-parent boundary.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c160_f1_1_bisect.log -- py -u tools/bench/diag_c160_f1_1_bisect.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag_c159_f1_2_t2 as T2                                                       # noqa: E402
ROOT, TOOLS, RECIPE = T2.ROOT, T2.TOOLS, T2.RECIPE
GOOD, BAD = "421d6108", "a9d0da22"
SUSPECTS = ["36da0566", "771a39a1", "653d1b61", "1449ae07", "9dbd384b", "18c241ec", "676f874f"]
OUT = os.path.join(HERE, "diag_c160_f1_1_bisect.json")


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True, check=True).stdout


def child(rev):
    rev, _, swap = rev.partition("+")                                              # "<rev>+<module>@<rev2>": one module from rev2
    names = git("ls-tree", "--name-only", rev, "tools/").split()
    srcs = dict((os.path.basename(p)[:-3], T2.src_bytes("git:" + rev, os.path.basename(p)[:-3])) for p in names if p.endswith(".py") and p.count("/") == 1)
    if swap:
        m, r2 = swap.split("@")
        srcs[m] = T2.src_bytes("git:" + r2, m)
    print("SERVED " + json.dumps(dict((n, T2.md5b(srcs[n])[:8]) for n in ("stagekit", "stage_prerun", "stagexec", "stagesim", "vigraph", "addrcheck") if n in srcs)), flush=True)
    sp = srcs.pop("stage_prerun")
    finder = T2.Serve(srcs)
    sys.meta_path.insert(0, finder)
    sys.path[0] = TOOLS
    import vigraph as V                                                              # served bytes
    orig = V.computation_diff_frame

    def wrap(A, B):
        cd = orig(A, B)
        rk = sorted(str(y["sink"]) for y in cd["rows"])
        print("CDIFF rk " + json.dumps(rk), flush=True)
        print("CDIFF n2626 " + json.dumps([[y["sink"], y.get("before"), y.get("after")] for y in cd["rows"] if int(y["node"]) == 2626])[:1500], flush=True)
        print("CDIFF renames2626 " + json.dumps([r for r in cd.get("renames", []) if int(r["node"]) == 2626]), flush=True)
        if hasattr(V, "pos_keys"):
            for lab, G in (("S1", A), ("END", B)):
                pk = V.pos_keys(G)
                print("POS {0} ".format(lab) + json.dumps(sorted([k, list(v)] for k, v in pk.items() if str(v[0]) == "2626")), flush=True)
        return cd
    V.computation_diff_frame = wrap
    sys.argv = [os.path.join(TOOLS, "stage_prerun.py"), "--dry", RECIPE, "--no-record"]
    fn = os.path.join(TOOLS, "stage_prerun.py")
    try:
        exec(compile(sp, fn, "exec"), {"__name__": "__main__", "__file__": fn, "__builtins__": __builtins__})
    finally:
        tn = os.path.normcase(TOOLS)
        fall = sorted(n for n, m in list(sys.modules.items()) if getattr(m, "__file__", None) and os.path.normcase(os.path.dirname(os.path.abspath(m.__file__))) == tn
                      and getattr(getattr(m, "__spec__", None), "loader", None) is not finder and n != "__main__")
        print("FALLTHROUGH " + json.dumps(fall), flush=True)


def run(rev):
    t0 = time.time()
    p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--child", rev], cwd=ROOT, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
    L = p.stdout.splitlines()
    get = lambda pre: next((x[len(pre):] for x in L if x.startswith(pre)), None)   # noqa: E731
    pb = next((x.strip() for x in L if " PB " in x and ("PASS" in x[:12] or "FAIL" in x[:12])), "PB ?")
    dl = next((x for x in reversed(L) if x.startswith("=== DRY ")), "NO DRY LINE " + p.stderr[-300:].replace("\n", " | "))
    rk = json.loads(get("CDIFF rk ") or "null")
    row = {"rev": rev, "subject": git("log", "-1", "--format=%ad %s", "--date=format:%m-%d %H:%M", rev.partition("+")[0]).strip()[:120], "pb": "PASS" if pb.startswith("PASS") else "FAIL",
           "rk_n": None if rk is None else len(rk), "missing": sorted(set(PRED) - set(rk or [])), "extra": sorted(set(rk or []) - set(PRED)), "dry": dl[:200],
           "served": get("SERVED "), "fallthrough": get("FALLTHROUGH "), "n2626": get("CDIFF n2626 "), "renames2626": get("CDIFF renames2626 "),
           "pos_s1": get("POS S1 "), "pos_end": get("POS END "), "rk": rk, "sec": round(time.time() - t0)}
    print("ROW {0} PB {1} rk {2} missing {3} extra {4} ({5}s) | {6}".format(rev, row["pb"], row["rk_n"], row["missing"], row["extra"], row["sec"], row["subject"]), flush=True)
    print("     served {0} fallthrough {1}".format(row["served"], row["fallthrough"]), flush=True)
    return row


def main():
    sys.path.insert(0, TOOLS)                                                      # parent only: protocol.result_line
    import protocol as P                                                         # noqa: E402
    md0 = dict((n, T2.md5b(open(os.path.join(TOOLS, n + ".py"), "rb").read())[:8]) for n in ("stagekit", "stage_prerun", "stagesim", "stagexec", "vigraph"))
    print("MD5 BEFORE " + json.dumps(md0), flush=True)
    revs = [GOOD] + [r[:8] for r in git("rev-list", "--first-parent", "--reverse", GOOD + ".." + BAD, "--", "tools/*.py").split()]
    if revs[-1] != BAD[:8]:
        revs.append(BAD)
    print("FIRST-PARENT candidates {0}".format(len(revs)), flush=True)
    res = {}
    lo, hi = 0, len(revs) - 1
    res[revs[lo]], res[revs[hi]] = run(revs[lo]), run(revs[hi])
    while hi - lo > 1 and res[revs[lo]]["pb"] == "PASS" and res[revs[hi]]["pb"] == "FAIL":
        mid = (lo + hi) // 2
        res[revs[mid]] = run(revs[mid])
        lo, hi = (mid, hi) if res[revs[mid]]["pb"] == "PASS" else (lo, mid)
    first_bad = revs[hi]
    print("FIRST-PARENT first bad {0}, last good {1}".format(first_bad, revs[lo]), flush=True)
    for r in SUSPECTS:
        if r not in res:
            res[r] = run(r)
    md1 = dict((n, T2.md5b(open(os.path.join(TOOLS, n + ".py"), "rb").read())[:8]) for n in ("stagekit", "stage_prerun", "stagesim", "stagexec", "vigraph"))
    print("MD5 AFTER " + json.dumps(md1) + (" UNCHANGED" if md1 == md0 else " CHANGED " + json.dumps([n for n in md0 if md0[n] != md1[n]])), flush=True)
    json.dump({"first_parent_first_bad": first_bad, "last_good": revs[lo], "rows": list(res.values())}, open(OUT, "w", encoding="utf-8"), indent=1)
    ok = res[GOOD]["pb"] == "PASS" and res[revs[-1]]["pb"] == "FAIL" and hi - lo == 1
    clean = all(not json.loads(r["fallthrough"] or "[]") for r in res.values())
    print(P.result_line({"status": "PASS" if ok and clean else "FAIL", "gates": {"pass": int(ok) + int(clean), "fail": int(not ok) + int(not clean)},
                         "first_fail": None if ok and clean else ("bracket/boundary not as predicted" if not ok else "a tools/ module fell through to the working tree"),
                         "artefacts": [{"path": "tools/bench/diag_c160_f1_1_bisect.json", "md5": T2.md5b(open(OUT, "rb").read())}]}), flush=True)
    return 0 if ok and clean else 1


PRED = json.load(open(os.path.join(HERE, "plan_ring_p3b2a_pred.json"), encoding="utf-8"))["cdiff_rows"]
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--child":
        child(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "--swap":                            # second pass: single-module swaps, rows only
        sys.path.insert(0, TOOLS)
        import protocol as P0                                                      # noqa: E402
        rows = [run(s) for s in sys.argv[2:]]
        json.dump(rows, open(os.path.join(HERE, "diag_c160_f1_1_swap.json"), "w", encoding="utf-8"), indent=1)
        print(P0.result_line({"status": "PASS", "gates": {"pass": len(rows), "fail": 0}, "first_fail": None,
                              "artefacts": [{"path": "tools/bench/diag_c160_f1_1_swap.json", "md5": T2.md5b(open(os.path.join(HERE, "diag_c160_f1_1_swap.json"), "rb").read())}]}), flush=True)
    else:
        sys.exit(main())
