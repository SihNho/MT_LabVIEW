r"""selftest_c133_1_gatefp_close - card 133-1 (PD276(d), PD282(b)): gate_fp.py `close` verb. Offline, a TEMP queue
(GATE_FP_QUEUE env, the self-test hook gate_fp.py:52). Prior art: drain (needs a fix + self-test), note (status unchanged).
PREDICTION:
  C1 close an open entry with a reason citing an existing path:line -> status 'closed', close_reason kept
  C2 a reason with no citation / a citation to a missing file -> REFUSED, entry stays open
  C3 closing an already-closed entry -> REFUSED; an unknown id -> REFUSED
  C4 `due` no longer counts the closed entry; the CLI form `close --id --reason` returns 0 / 2
    py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_c133_1_gatefp_close.log -- py -u tools/bench/selftest_c133_1_gatefp_close.py"""
import os, sys, tempfile                                                           # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(tempfile.mkdtemp(prefix="st_c133_1_fp_"), "q.jsonl")
os.environ["GATE_FP_QUEUE"] = Q
sys.path.insert(0, os.path.dirname(B))
import gate_fp as G, protocol as P                                                 # noqa: E401,E402
NP, NF = [0], [None]


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:300]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


assert G.QUEUE == Q
e1, _ = G.log_fp("checker:stage_prerun:X1", "cmd one", "tools/gate_fp.py:1 evidence", "t-1")
e2, _ = G.log_fp("guard_peer", "cmd two", "tools/gate_fp.py:2 evidence", "t-2")
c, why = G.close(e1["id"], "correct refusal per tools/gate_fp.py:123")
row = [r for r in G.read_queue() if r["id"] == e1["id"]][0]
gate("C1 close with a real citation -> closed", c is not None and row["status"] == "closed" and "gate_fp.py:123" in row["close_reason"], (why, row))
n1, w1 = G.close(e2["id"], "no citation here")
n2, w2 = G.close(e2["id"], "see tools/no_such_file.py:9")
row2 = [r for r in G.read_queue() if r["id"] == e2["id"]][0]
gate("C2 no citation / missing file -> REFUSED, still open", n1 is None and n2 is None and row2["status"] == "open", (w1, w2))
n3, w3 = G.close(e1["id"], "again tools/gate_fp.py:1")
n4, w4 = G.close("fp-999", "x tools/gate_fp.py:1")
gate("C3 already closed / unknown id -> REFUSED", n3 is None and "already closed" in w3 and n4 is None and "no entry" in w4, (w3, w4))
d, det = G.due(cycle=0)
rc_ok = G.main(["close", "--id", e2["id"], "--reason", "superseded, tools/gate_fp.py:147"])
rc_bad = G.main(["close", "--id", e2["id"], "--reason", "again tools/gate_fp.py:147"])
gate("C4 due counts 1 open (not the closed); CLI close rc 0 then 2", "1 open" in det and rc_ok == 0 and rc_bad == 2, (det, rc_ok, rc_bad))
print(P.result_line(P.make_result(NP[0], 4 - NP[0], NF[0])), flush=True)
