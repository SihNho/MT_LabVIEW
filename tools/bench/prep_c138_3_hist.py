r"""prep_c138_3_hist - card 138-3, read-only git history of the two fixtures the red self-tests read: per commit, md5 and
finalized.base (provisional or not; does the base graph carry fs_frames). Answers: which commit last had the fixture the
test was written against (c133_1 expects input md5 98992a59 + a provisional base; c133_6 expects BASE['fs_frames']).
PREDICTION: prints one line per commit per fixture; RESULT line."""
import hashlib, json, os, subprocess, sys                                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(B))   # noqa: E702
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as P                                                                 # noqa: E402
git = lambda *a: subprocess.run(["git"] + list(a), cwd=R, capture_output=True)       # noqa: E731
for f in ("tools/bench/plan_ring_p3b2.json", "tools/bench/plan_ring_p3b2b.json"):
    for ln in git("log", "--format=%h %ci %s", "--", f).stdout.decode().splitlines():
        h = ln.split()[0]
        b = git("show", "%s:%s" % (h, f)).stdout
        try:
            p = json.loads(b.decode("utf-8"))
        except Exception as e:
            print(f, ln, "ERR", e); continue
        base = (p.get("finalized") or {}).get("base") or p.get("base") or {}
        bp = base.get("path") if isinstance(base, dict) else base
        hasfs = None
        if bp:
            bb = git("show", "%s:%s" % (h, bp)).stdout
            try:
                hasfs = "fs_frames" in json.loads(bb.decode("utf-8"))
            except Exception:
                hasfs = "unreadable@commit"
        print("%s | %s | md5 %s | final %s | base %s provisional=%s fs_frames=%s" % (
            f.split("/")[-1], ln[:60], hashlib.md5(b).hexdigest()[:8], p.get("final"), bp,
            base.get("provisional") if isinstance(base, dict) else None, hasfs))
for t in ("tools/bench/selftest_c134_2_regress.py", "tools/bench/selftest_c134_2_regress.log"):
    print(t, git("log", "-3", "--format=%h %ci", "--", t).stdout.decode().strip().replace("\n", " | "))
print(P.result_line(P.make_result(1, 0, None, [])))
