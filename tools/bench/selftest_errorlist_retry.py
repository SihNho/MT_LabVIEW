r"""selftest_errorlist_retry - card chat-E1: cycle_runner.errorlist_hook retries a COM-not-ready FAIL exactly once.

No LabVIEW: subprocess.run is replaced by a fake that writes a scripted log, time.sleep by a counter.
Existing tests checked first: selftest_cycle_runner(_ff).py run the hook only under --dry-run (SKIP path); nothing
exercised the FAIL/retry branch, so this file does.

PREDICTION CONTRACT (4 cases):
  A  OK first                     -> 1 run, verdict OK, no sleep
  B  ClassFactory FAIL then OK    -> 2 runs, verdict OK, one 20 s sleep, retry log used
  C  ClassFactory FAIL twice      -> 2 runs, verdict FAIL
  D  other FAIL (no COM text)     -> 1 run, verdict FAIL, no sleep
"""
import os, sys, tempfile, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import cycle_runner as C                                                            # noqa: E402
import protocol                                                                     # noqa: E402

CF = "errors [\"com_error: (-2147221231, 'ClassFactory ...', None, None)\"]\n"


def case(seq):
    tmp = tempfile.mkdtemp(prefix="elretry_")
    calls, sleeps = [], []

    def fake_run(cmd, **kw):
        log = cmd[cmd.index("--log") + 1]
        kind = seq[len(calls)]
        calls.append(log)
        js = os.path.join(tmp, "x%d.json" % len(calls))
        body = {"ok": "ERRORLIST-VERDICT: OK %s\n" % js,
                "cf": CF + "ERRORLIST-VERDICT: FAIL %s\n" % js,
                "other": "errors ['no bed']\nERRORLIST-VERDICT: FAIL %s\n" % js}[kind]
        with open(log, "w", encoding="utf-8") as f:
            f.write(body + "BGRUN END rc=0 after 1s\n")
        return types.SimpleNamespace(stdout="", returncode=0)

    orig_run, orig_sleep = C.subprocess.run, C.time.sleep
    C.subprocess.run, C.time.sleep = fake_run, lambda s: sleeps.append(s)
    try:
        a = types.SimpleNamespace(dry_run=False, dry_cmd=None, no_errorlist_hook=False)
        v, js, why = C.errorlist_hook(99, a, tmp, os.path.join(tmp, "runner.log"), "rig: disassembled\n")
    finally:
        C.subprocess.run, C.time.sleep = orig_run, orig_sleep
    return v, calls, sleeps


def main():
    exp = {"A": (["ok"], "OK", 1, []), "B": (["cf", "ok"], "OK", 2, [20]),
           "C": (["cf", "cf"], "FAIL", 2, [20]), "D": (["other"], "FAIL", 1, [])}
    npass = nfail = 0
    first = None
    for k, (seq, v_exp, n_exp, sl_exp) in exp.items():
        v, calls, sleeps = case(seq)
        ok = v == v_exp and len(calls) == n_exp and sleeps == sl_exp and \
            (n_exp < 2 or calls[1].endswith("_retry.log"))
        print("%s case %s: verdict %s runs %d sleeps %s" % ("PASS" if ok else "FAIL", k, v, len(calls), sleeps))
        npass += ok
        nfail += not ok
        if not ok and first is None:
            first = "case " + k
    print("%d/%d PASS" % (npass, npass + nfail))
    print(protocol.result_line(protocol.make_result(npass, nfail, first, [],
                                                    status="PASS" if not nfail else "FAIL")))
    return 0 if not nfail else 1


if __name__ == "__main__":
    sys.exit(main())
