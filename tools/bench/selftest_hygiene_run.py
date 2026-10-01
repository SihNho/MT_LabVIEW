r"""selftest_hygiene_run - card 126-1 STEP 1: OFFLINE self-test of gscript.hygiene_run (no LabVIEW; COM pieces stubbed by monkeypatch:
ensure_loaded / close_panel replaced, counts injected, copies + record under %TEMP%).
PREDICTION: T1 recycle 5x4: live copies back to 0 after EVERY round, every round carries h_pre/h_post/h_closed (+gdi/user), PASS /
T2 a workload that RAISES once -> errors 1, FAIL / T3 a returned error string is counted / T4 h_closed drift 30/round x 5 -> dev 120 > 100,
FAIL / T5 a check problem -> FAIL / T6 one ensure_loaded + one close per round, no copy left on disk / T7 recycle=False -> one copy,
one close, PASS / T8 record file == returned record, schema op-hygiene/1, md5 == the op file's.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_hygiene_run.log -- py -u tools/bench/selftest_hygiene_run.py"""
import hashlib, json, os, sys, tempfile                                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g                                                                         # noqa: E402
import protocol as P                                                                        # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_hygrun_")
OPF, SRC = os.path.join(TMP, "OpFake_v0.vi"), os.path.join(TMP, "Src.vi")
for p, b in ((OPF, b"fake op bytes"), (SRC, b"fake source bytes")):
    open(p, "wb").write(b)
G, LOG = {}, {"load": [], "close": []}


def gate(label, ok, detail=""):
    G[label] = bool(ok)
    print("%s | %s | %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


g.ensure_loaded = lambda p: LOG["load"].append(p)


def _close(p):
    assert os.path.exists(p), "close of a copy that is not on disk"
    LOG["close"].append(p)


g.close_panel = _close


class Counts(object):
    def __init__(self, drift=0):
        self.n, self.drift, self.base = 0, drift, 31500

    def __call__(self):
        self.n += 1
        live = len(g._hyg_live)
        return {"handles": self.base + 40 * live + self.drift * (self.n // 3), "private": 10 ** 8, "gdi": 50 + live, "user": 40}


def run(name, workload, **kw):
    LOG["load"].clear(); LOG["close"].clear()                                              # noqa: E702
    rp = os.path.join(TMP, name + ".json")
    kw.setdefault("counts", Counts())
    r = g.hygiene_run(OPF, workload, SRC, scratch_dir=TMP, record_path=rp, card="selftest", say=lambda s: None, **kw)
    return r, rp


ok_wl = lambda c: ""                                                                        # noqa: E731
r, rp = run("t1", ok_wl, total=20, per_round=4)
gate("T1 recycle 5x4: PASS, 20 calls, 5 rounds", r["status"] == "PASS" and r["calls"] == 20 and r["rounds"] == 5, (r["status"], r["calls"], r["rounds"]))
gate("T1 live copies 0 after every round", r["live_after_close"] == [0] * 5, r["live_after_close"])
gate("T1 three handle series + gdi/user, one value per round", all(len(r[k]) == 5 and None not in r[k] for k in
     ("h_pre", "h_post", "h_closed", "gdi_pre", "gdi_post", "gdi_closed", "user_pre", "user_post", "user_closed")),
     {k: r[k] for k in ("h_pre", "h_post", "h_closed")})
gate("T1 pre/post read with the copy open, closed read without it", all(a > c for a, c in zip(r["h_pre"], r["h_closed"])), (r["h_pre"], r["h_closed"]))
gate("T6 one ensure_loaded + one close per round, distinct copies, none left on disk", len(LOG["load"]) == 5 and LOG["close"] == LOG["load"]
     and len(set(LOG["load"])) == 5 and not any(os.path.exists(p) for p in LOG["load"]), (len(LOG["load"]), len(LOG["close"])))
gate("T8 record file == returned record, schema op-hygiene/1, md5 of the op file", json.load(open(rp, encoding="utf-8")) == r
     and r["schema"] == "op-hygiene/1" and r["md5"] == hashlib.md5(open(OPF, "rb").read()).hexdigest(), r["md5"])

calls = {"n": 0}


def raiser(c):
    calls["n"] += 1
    if calls["n"] == 3:
        raise RuntimeError("boom")
    return ""


r, _ = run("t2", raiser, total=20, per_round=4)
gate("T2 a raising workload is counted as an error, FAIL, the run still completes", r["errors"] == 1 and r["status"] == "FAIL" and r["calls"] == 20
     and "boom" in r["error_samples"][0] and r["live_after_close"] == [0] * 5, (r["errors"], r["error_samples"]))
r, _ = run("t3", lambda c: "op error 1055", total=8, per_round=4)
gate("T3 a returned error string is counted (8 of 8), FAIL", r["errors"] == 8 and r["status"] == "FAIL", r["errors"])
r, _ = run("t4", ok_wl, total=20, per_round=4, counts=Counts(drift=30))
gate("T4 h_closed drift +30/round over 5 rounds -> max_dev 120 > 100 -> FAIL", r["status"] == "FAIL" and r["max_dev_closed"] == 120 and r["errors"] == 0,
     (r["h_closed"], r["max_dev_closed"]))
r, _ = run("t5", ok_wl, total=8, per_round=4, check=lambda c: ["frames 3 != 5"])
gate("T5 a check problem fails the record", r["status"] == "FAIL" and len(r["check_problems"]) == 2 and r["errors"] == 0, r["check_problems"])
r, _ = run("t7", ok_wl, total=12, per_round=4, recycle=False)
gate("T7 recycle=False: one copy, one close, 12 calls, PASS", r["status"] == "PASS" and r["calls"] == 12 and len(LOG["load"]) == 1
     and LOG["close"] == LOG["load"] and r["live_after_close"] == [0], (len(LOG["load"]), r["calls"], r["status"]))
w = {"n": 0}
r, _ = run("t9", ok_wl, total=8, per_round=4, warm=lambda c: w.__setitem__("n", w["n"] + 1))
gate("T9 warm runs once, not counted as a call", w["n"] == 1 and r["calls"] == 8, (w, r["calls"]))
gate("T10 the module's live-copy list is empty at the end", g._hyg_live == [], g._hyg_live)

bad = [k for k, v in G.items() if not v]
print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
