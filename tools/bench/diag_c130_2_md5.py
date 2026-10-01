"""diag_c130_2_md5 - card 130-2: md5 of the card's changed files (read-only). Prediction: every file exists."""
import hashlib, os, sys                                                             # noqa: E401
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as PR                                                               # noqa: E402
FS = ["tools/hooks/guard_bash.py", "tools/hooks/guard_peer.py", "tools/protocol.py", "tools/peer.ps1",
      "docs/ring-buffer-design.md", "tools/bench/gate_fp_queue.jsonl", "tools/bench/selftest_stoprecord_c130_2.py",
      "tools/bench/selftest_c130_2_tools.py", "tools/bench/selftest_c130_2_peerfact.py", "tools/bench/diag_c130_2_suite.py",
      "tools/bench/diag_c130_2_suite_all.log"]
ok = 0
for p in FS:
    fp = os.path.join(R, p)
    if os.path.isfile(fp):
        ok += 1
        print(hashlib.md5(open(fp, "rb").read()).hexdigest(), p, flush=True)
    else:
        print("MISSING", p, flush=True)
print(PR.result_line(PR.make_result(ok, len(FS) - ok)), flush=True)
