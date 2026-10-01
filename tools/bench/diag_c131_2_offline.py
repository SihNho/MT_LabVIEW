"""diag_c131_2_offline - card 131-2 P1: MEASURE the candidate guard_peer offline classification (tools/bench/c131_2_reach.py,
v2) against the current one (guard_peer.script_touches_labview, v1) BEFORE switching it on. Offline: imports guard_peer
and reads files; no LabVIEW, no COM, no hook payload is written anywhere.

Replay A - the RECORDED argvs of gate-fp fp-16/17/18/22/24 (tools/bench/gate_fp_queue.jsonl lines 16-18, 22, 24) through
this hook's own decision order up to RULE-OFFLINE-CMD (guard_peer.main(): RUNS_RE / RUNNER_RE / REMEDY_RE / waiter ->
is the blamed log counted by newest_failing_log's filters (age ignored) -> RULE-OFFLINE-CARD / RULE-OFFLINE-CMD with the
recorded card's flags.labview). fp-18's recorded cmd is a description; it is replayed as the literal md5sum+grep it names.
Replay B - every LabVIEW launch in tools/bench/stage_runs.jsonl (unique script; a .json plan replays as `stagexec.py run`):
under a labview:none card offline_command(cmd) must be False AND selftest_exempt(start line) must be False = still HELD.
Info C - every tools/bench + tools/recipes .py whose classification flips v1 -> v2 (counts; the flips listed).
PREDICTION: A v2 5/5 pass (v1: fp-22 and fp-24 held); B v2 held == number of launches (and v1 the same); C no
tools/recipes script flips to offline."""
import glob, json, os, re, sys, time                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, B)
import protocol as P                                                               # noqa: E402
import logclass                                                                    # noqa: E402
import guard_peer as gp                                                            # noqa: E402
import c131_2_reach as R2                                                          # noqa: E402

V1 = getattr(gp, "script_touches_labview_v1", gp.script_touches_labview)   # after switch-on v1 is kept under this name
HOOK = gp.script_touches_labview
res = []


def gate(name, ok, det=""):
    res.append(bool(ok))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:600]), flush=True)


def card_lv(cid):
    p = os.path.join(B, "cards", "task_%s.json" % cid)
    try:
        with open(p, encoding="utf-8") as f:
            return str((json.load(f).get("flags") or {}).get("labview") or "none")
    except (OSError, ValueError):
        return None


def log_counted(path):
    """newest_failing_log's per-file filters for ONE log, age ignored. (counted, why)."""
    if not os.path.isfile(path):
        return False, "log missing"
    if gp.is_jev_ledger(path) or logclass.is_review_log(path):
        return False, "ledger/review"
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read().lstrip("﻿")
    last = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
    first = (last.splitlines() or [""])[0]
    if gp.RUNNER_RE.search(first):
        return False, "runner/jev"
    if "BGRUN START" in text and not gp.in_prediction_scope(first):
        return False, "out of scope"
    if "BGRUN START" in text and gp.selftest_exempt(first):
        return False, "selftest_exempt"
    if not gp.log_failure(text, os.path.getmtime(path))[0]:
        return False, "not failing"
    if "BGRUN START" in text and gp.superseded_by_rerun(path, os.path.getmtime(path), "BGRUN START" + last):
        return False, "superseded"
    return True, "counted"


def gate_pass(cmd, cid, log):
    if not gp.RUNS_RE.search(cmd) or gp.RUNNER_RE.search(cmd):
        return True, "not a run"
    if gp.REMEDY_RE.search(cmd):
        return True, "remedy"
    if gp.report_waiter_only(cmd):
        return True, "report waiter"
    if log:
        c, why = log_counted(os.path.join(ROOT, log))
        if not c:
            return True, "blamed log not counted (%s)" % why
    lv = card_lv(cid)
    off = gp.offline_command(cmd)
    if lv == "none" and off:
        return True, "RULE-OFFLINE-CARD"
    if lv in ("read", "build") and off and not P.card_owns_log(cid, os.path.join(ROOT, log or "")):
        return True, "RULE-OFFLINE-CMD"
    return False, "HELD (card %s labview %s, offline_command %s)" % (cid, lv, off)


q = {}
with open(os.path.join(B, "gate_fp_queue.jsonl"), encoding="utf-8") as f:
    for ln in f:
        if ln.strip():
            d = json.loads(ln)
            q[d["id"]] = d
REPLAY = [(i, q[i]["cmd"], q[i]["card"], q[i].get("log")) for i in ("fp-16", "fp-17", "fp-22", "fp-24")]
REPLAY.insert(2, ("fp-18", "md5sum tools/stagexec.py tools/bench/selftest_errorlist_reuse_81_c127.py; "
                           "grep -n ROUTE_CENSUS tools/stagexec.py", "127-2", "tools/bench/selftest_errorlist_reuse_81_c127.log"))

out = {}
for tag, fn in (("v1", V1), ("v2", R2.script_touches_labview)):
    gp.script_touches_labview = fn
    t0 = time.time()
    a = []
    for i, cmd, cid, log in REPLAY:
        ok, why = gate_pass(cmd, cid, log)
        a.append(ok)
        print("A %s %-6s %-5s %s" % (tag, i, "pass" if ok else "HELD", why), flush=True)
    # B
    seen, held, nb, missing = set(), 0, 0, 0
    with open(os.path.join(B, "stage_runs.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(x) for x in f if x.strip()]
    nrec = len(rows)
    leaks = []
    for r in rows:
        s = r["script"]
        if s in seen:
            continue
        seen.add(s)
        nb += 1
        if not os.path.isfile(os.path.join(ROOT, s)):
            missing += 1
        run = ("py -u tools/stagexec.py run %s" % s) if s.endswith(".json") else ("py -u %s" % s)
        cmd = "py tools/bgrun.py --material --max-min 30 --log tools/bench/x.log -- " + run
        h = (not gp.offline_command(cmd)) and (not gp.selftest_exempt("BGRUN START x limit 30.0 min: " + run))
        held += h
        if not h:
            leaks.append(s)
    print("B %s unique launches %d (records %d, scripts missing on disk %d): held %d, leaks %s" % (
        tag, nb, nrec, missing, held, leaks), flush=True)
    out[tag] = dict(a=a, held=held, nb=nb, leaks=leaks, sec=time.time() - t0)
gp.script_touches_labview = HOOK

gate("A v2: fp-16/17/18/22/24 recorded argvs all pass", all(out["v2"]["a"]), "%d/5 (v1 %d/5)" % (
    sum(out["v2"]["a"]), sum(out["v1"]["a"])))
gate("B v2: every stage_runs.jsonl LabVIEW launch still held", out["v2"]["held"] == out["v2"]["nb"],
     "%d/%d (v1 %d/%d) leaks %s" % (out["v2"]["held"], out["v2"]["nb"], out["v1"]["held"], out["v1"]["nb"], out["v2"]["leaks"]))

# C - flips over every bench / recipe script
flips_off, flips_on, n, hook_diff = [], [], 0, []
t0 = time.time()
for p in sorted(glob.glob(os.path.join(ROOT, "tools", "bench", "*.py")) + glob.glob(os.path.join(ROOT, "tools", "recipes", "*.py"))):
    n += 1
    a, b = V1(p), R2.script_touches_labview(p)
    if HOOK is not V1 and HOOK(p) != b:
        hook_diff.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    if a and not b:
        flips_off.append(os.path.relpath(p, ROOT).replace("\\", "/"))
    elif b and not a:
        flips_on.append(os.path.relpath(p, ROOT).replace("\\", "/"))
rec_off = [x for x in flips_off if x.startswith("tools/recipes/")]
print("C scripts %d (%.1fs): v1 LV -> v2 offline %d; v1 offline -> v2 LV %d" % (n, time.time() - t0, len(flips_off), len(flips_on)))
print("C to-offline: %s" % flips_off)
print("C to-LV: %s" % flips_on)
gate("C no tools/recipes script flips to offline", not rec_off, rec_off)
if HOOK is not V1:
    gate("E switched-on hook v2 == measured candidate on every script", not hook_diff, "%d differ %s" % (
        len(hook_diff), hook_diff[:10]))
t0 = time.time()
R2._MODINFO.clear()
R2.script_touches_labview(os.path.join(B, "selftest_x10_c130_1.py"))
gate("D cold v2 classification of selftest_x10_c130_1 within the hook budget (10 s)", time.time() - t0 < 5.0,
     "%.2fs" % (time.time() - t0))
print(P.result_line(P.make_result(sum(res), len(res) - sum(res), None if all(res) else "see FAIL lines")), flush=True)
