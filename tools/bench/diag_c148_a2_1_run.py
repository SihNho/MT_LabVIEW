# ---
# labview: none
# hardware: none
# ---
r"""diag_c148_a2_1_run - card 148-a2-1 driver: measure the fp-60 env leak on a THROWAWAY state copy, then run the census
self-tests with the assignment env (ASSIGN_STATE / CYCLE_ROLE / CYCLE_SESSION) stripped, so no child can reach a live
tools/bench/assign/state_*.json.

WHAT EXISTED: selftest_assign_flow.py / selftest_chat_p1.py / selftest_chat_p2.py / selftest_guard_session*.py (the
census); none runs itself with a stripped env, and this session inherits the assignment session's env, so a plain launch
would itself be the leak. This file only launches them.

Modes (argv[1]):
  measure        copy state_148_1.json -> diag_c148_a2_1_tmp/state_copy.json (sticky handback cleared, else the hook
                 short-circuits before any write), run selftest_chat_p1.py with CYCLE_SESSION=1 CYCLE_ROLE=assign
                 ASSIGN_STATE=<copy>; report what the copy gained.
                 PREDICTION: the copy gains handback c-outside-purpose naming card p1s-A (leak confirmed).
  suite <tag>    run the census self-tests (+ selftest_c148_guard_fp) with the three vars stripped; rc + SUMMARY/RESULT
                 per test -> diag_c148_a2_1_suite_<tag>.json. PREDICTION: rc 0 each (or the pre-fix counts).
  leak <tag> [-- args]  run selftest_c148_assign_leak.py (stripped env) with args; rc + RESULT.
  c147           run selftest_c147_b1_2.py (stripped env); PREDICTION 17 pass / 0 fail.
Every mode: live state_*.json md5 before == after, LabVIEW process count 0 before and after.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402

TMPD = os.path.join(HERE, "diag_c148_a2_1_tmp")
LEAKVARS = ("ASSIGN_STATE", "CYCLE_ROLE", "CYCLE_SESSION")
SUITE = ["selftest_assign_flow.py", "selftest_c148_guard_fp.py", "selftest_guard_session.py",
         "selftest_guard_session_pairing.py", "selftest_chat_p1.py", "selftest_chat_p2.py"]
NP = [0, 0]


def gate(label, ok, detail=""):
    NP[0 if ok else 1] += 1
    print("  %-4s %-62s %s" % ("ok" if ok else "BAD", label, str(detail)[:300]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def live_md5s():
    return dict((os.path.basename(p), md5(p)) for p in sorted(glob.glob(os.path.join(HERE, "assign", "state_*.json"))))


def lv_count():
    out = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    return sum(1 for ln in out.splitlines() if "labview" in ln.lower())


def stripped_env(extra=None):
    e = dict(os.environ)
    for k in LEAKVARS:
        e.pop(k, None)
    e.update(extra or {})
    return e


def run(script, env, args=(), timeout=1500):
    t = time.time()
    p = subprocess.run([sys.executable, "-u", os.path.join(HERE, script)] + list(args), cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    out = (p.stdout or "") + (p.stderr or "")
    summ = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("SUMMARY")]
    res = [ln.strip() for ln in out.splitlines() if ln.startswith("RESULT ")]
    bad = [ln.strip()[:160] for ln in out.splitlines() if ln.strip().startswith("BAD")]
    return {"script": script, "rc": p.returncode, "secs": round(time.time() - t, 1), "summary": summ[-1:] or None,
            "result": res[-1][7:] if res else None, "bad": bad[:8]}, out


def main(argv):
    mode = argv[0] if argv else "?"
    print("ENV this process: %s" % dict((k, os.environ.get(k)) for k in LEAKVARS + ("ASSIGN_CONFIG",)), flush=True)
    m0, lv0 = live_md5s(), lv_count()
    print("live state md5 before: %s" % m0, flush=True)
    gate("LabVIEW processes before == 0", lv0 == 0, lv0)
    if mode == "measure":
        os.makedirs(TMPD, exist_ok=True)
        src = os.path.join(HERE, "assign", "state_148_1.json")
        cp = os.path.join(TMPD, "state_copy.json")
        shutil.copyfile(src, cp)
        d = json.load(open(cp, encoding="utf-8"))
        print("copy of %s md5 %s; original handback trigger %s (cleared in the copy)" % (
            os.path.basename(src), md5(cp), (d.get("handback") or {}).get("trigger")), flush=True)
        d["handback"], d["refusals"] = None, []
        json.dump(d, open(cp, "w", encoding="utf-8"), indent=1)
        c0 = md5(cp)
        n_cards0 = len(d.get("cards") or [])
        env = stripped_env({"CYCLE_SESSION": "1", "CYCLE_ROLE": "assign", "ASSIGN_STATE": cp})
        r, out = run("selftest_chat_p1.py", env)
        open(os.path.join(TMPD, "measure_chat_p1.log"), "w", encoding="utf-8").write(out)
        d1 = json.load(open(cp, encoding="utf-8"))
        hb = d1.get("handback") or {}
        print("chat_p1 under the leaked env: %s" % json.dumps(r), flush=True)
        print("copy md5 %s -> %s; cards %d -> %d %s; refusals %s; handback %s" % (
            c0, md5(cp), n_cards0, len(d1.get("cards") or []), [c.get("id") for c in d1.get("cards") or []],
            d1.get("refusals"), json.dumps(hb)), flush=True)
        gate("M1 the copy gained a hand-back naming p1s-A (leak confirmed)", "p1s-A" in str(hb.get("detail")), hb.get("trigger"))
    elif mode == "suite":
        tag = argv[1]
        rows = []
        for s in SUITE:
            r, out = run(s, stripped_env())
            rows.append(r)
            print("SUITE %s %s" % (tag, json.dumps(r)), flush=True)
        json.dump(rows, open(os.path.join(HERE, "diag_c148_a2_1_suite_%s.json" % tag), "w", encoding="utf-8"), indent=1)
        gate("S all census self-tests rc 0 (%s)" % tag, all(r["rc"] == 0 for r in rows),
             [(r["script"], r["rc"]) for r in rows if r["rc"]])
    elif mode == "leak":
        tag = argv[1]
        r, out = run("selftest_c148_assign_leak.py", stripped_env(), args=argv[2:])
        open(os.path.join(TMPD, "leak_%s.log" % tag), "w", encoding="utf-8").write(out)
        print(out, flush=True)
        print("LEAK %s %s" % (tag, json.dumps(r)), flush=True)
        gate("L ran (%s) rc recorded" % tag, r["result"] is not None, r["rc"])
    elif mode == "c147":
        r, out = run("selftest_c147_b1_2.py", stripped_env())
        print("\n".join(ln for ln in out.splitlines() if re.match(r"\s*(ok|BAD|PASS|FAIL|SUMMARY|RESULT)", ln)), flush=True)
        print("C147 %s" % json.dumps(r), flush=True)
        gate("C rc 0", r["rc"] == 0, r["rc"])
    m1, lv1 = live_md5s(), lv_count()
    gate("live state_*.json md5 unchanged", m0 == m1, [k for k in m1 if m0.get(k) != m1[k]] + sorted(set(m0) - set(m1)))
    gate("LabVIEW processes after == 0", lv1 == 0, lv1)
    print(P.result_line(P.make_result(NP[0], NP[1], None if not NP[1] else "see BAD lines")), flush=True)
    return 1 if NP[1] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
