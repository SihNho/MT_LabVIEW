r"""Card 125-1 regression: the existing self-tests named by the card + the P3a / P2b preruns, after the gate edits.
Each entry is first checked with protocol.check_command against card 125-1 itself (flags.labview none): an entry the
card refuses is REPORTED as refused and NOT run (this runner never launches what the card's hook would refuse).
Runs each as a child process, reads its RESULT line (pass/fail counts).

PREDICTION CONTRACT: every allowed entry exits 0 with RESULT status PASS (stage_prerun --prerun on plan_ring_p3a.json
and on stage_d1_ring_p3a.py: PASS with an X16 line); P2b plan prerun PASS (card 125-3: X16 exempts its 5 const_donor
creates); selftest_c125_1 PASS (E4-E6 added by card 125-3); no entry refused by the card.
Ends with a RESULT line.
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402

E = [
    ("launch_gate", ["tools/bench/selftest_launch_gate.py"]),
    ("stagexec selftest", ["tools/stagexec.py", "selftest"]),
    ("census hook-in c123", ["tools/bench/selftest_census_hookin_c123.py"]),
    ("case_frame c124", ["tools/bench/selftest_case_frame_c124.py"]),
    ("guard_peer ladder", ["tools/bench/selftest_guard_peer_ladder.py"]),
    ("guard_peer budget", ["tools/bench/selftest_guard_peer_budget.py"]),
    ("guard_peer failre", ["tools/bench/selftest_guard_peer_failre.py"]),
    ("guard_peer jev", ["tools/bench/selftest_guard_peer_jev.py"]),
    ("guard_peer samerow", ["tools/bench/selftest_guard_peer_samerow.py"]),
    ("guard_peer 77 measure", ["tools/bench/selftest_guard_peer_77_measure.py"]),
    ("guard_peer scan_tmp", ["tools/bench/selftest_guard_peer_scan_tmp.py"]),
    ("protocol", ["tools/bench/selftest_protocol.py"]),
    ("protocol wiring", ["tools/bench/selftest_protocol_wiring.py"]),
    ("chat_p1 (RULE-OFFLINE-CARD, gate_fp)", ["tools/bench/selftest_chat_p1.py"]),
    ("c125_1 (fp-10..13, X16 incl. 125-3 scope)", ["tools/bench/selftest_c125_1.py"]),
    ("prerun plan_ring_p3a.json", ["tools/stage_prerun.py", "--prerun", "tools/bench/plan_ring_p3a.json", "--no-record"]),
    ("prerun stage_d1_ring_p3a.py", ["tools/stage_prerun.py", "--prerun", "tools/recipes/stage_d1_ring_p3a.py",
                                     "--no-record"]),
]


def main():
    # card 125-3: the card whose flags vet each entry may be passed as argv[1] (default card 125-1)
    cpath = os.path.join(ROOT, sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "tools", "bench", "cards",
                                                                                   "task_125-1.json")
    print("CARD %s" % os.path.relpath(cpath, ROOT), flush=True)
    card = P.load_card(cpath, None)
    card["_md5"] = P._md5(cpath)
    p2b = [f for f in sorted(os.listdir(os.path.join(ROOT, "tools", "bench"))) if re.match(r"plan_ring_p2b.*\.json$", f)]
    for f in p2b:
        E.append(("prerun %s" % f, ["tools/stage_prerun.py", "--prerun", "tools/bench/" + f, "--no-record"]))
        try:
            d = json.load(open(os.path.join(ROOT, "tools", "bench", f), encoding="utf-8"))
            n = sum(1 for a in d.get("actions") or [] if a.get("op") == "create" and a.get("prim"))
            nt = sum(1 for a in d.get("actions") or [] if a.get("op") == "create" and isinstance(a.get("terminals"), list))
            print("P2B %s: create actions with prim=%d, with declared terminals=%d" % (f, n, nt), flush=True)
        except (OSError, ValueError) as e:
            print("P2B %s unreadable: %s" % (f, e), flush=True)
    res = []
    for label, argv in E:
        cmd = "py -u " + " ".join(argv)
        why = P.check_command(card, cmd)
        if why:
            res.append((label, False))
            print("  REFUSED-BY-CARD  %-40s %s" % (label, why[:160]), flush=True)
            continue
        t0 = time.time()
        p = subprocess.run([sys.executable, "-u"] + argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        rl = [ln for ln in p.stdout.splitlines() if ln.startswith("RESULT ")]
        st = None
        if rl:
            try:
                st = json.loads(rl[-1][len("RESULT "):])
            except ValueError:
                st = None
        x16 = [ln.strip() for ln in p.stdout.splitlines() if "X16" in ln][:1]
        ok = p.returncode == 0 and (st is None or st.get("status") == "PASS")
        res.append((label, ok))
        print("  %s  %-40s rc=%s %s %.0fs %s" % ("PASS" if ok else "BAD ", label, p.returncode,
              json.dumps((st or {}).get("gates")) if st else "(no RESULT line)", time.time() - t0,
              ("| " + x16[0][:120]) if x16 else ""), flush=True)
        if not ok:
            print("    first_fail: %s | tail: %s" % ((st or {}).get("first_fail"),
                  (p.stdout[-400:] + p.stderr[-400:]).replace("\n", " | ")), flush=True)
    npass = sum(1 for _l, ok in res if ok)
    print(P.result_line(P.make_result(npass, len(res) - npass, next((l for l, ok in res if not ok), None))), flush=True)
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
