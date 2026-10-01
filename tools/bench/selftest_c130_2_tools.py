r"""selftest_c130_2_tools - card 130-2 items 2+3, OFFLINE (no LabVIEW, no model, nothing launched; hooks' functions called).
FOUND FIRST: selftest_card_clock.py (clock cases), selftest_guard_peer_samerow.py / selftest_c121_3_gatefp.py (guard_peer
function-call pattern), protocol.OFFLINE_SELFTESTS (fp-15).
PREDICTION CONTRACT
  R1-R7  guard_peer.RUNS_RE (fp-18): md5sum/grep naming tools/stagexec.py then a tools/bench/*.py do NOT match; a real
         py/python3/python.exe launch of a bench script or recipe and bare bgrun.py still match
  W1-W5  guard_peer.report_waiter_only (fp-17): the fp-17 waiter command -> True; + a recipe / a bench script / a bgrun of a
         bench script / a plain bgrun -> False
  S1-S6  guard_peer.superseded_by_rerun (fp-16), BENCH patched to a temp dir: same command, newer, rc=0, no FAIL -> True;
         other command / rc=1 / TIMEOUT / a FAIL line / OLDER -> False; S7 the real fp-16 pair -> True
  F1-F3  protocol.check_command under card 130-2 (labview none) (fp-15): bgrun -- py -u tools/stagexec.py selftest, with a
         `cd <root> &&` prefix -> allowed; F3 `... selftest 2>&1 | tail -3` reported (measured, not asserted)
  C1-C4  protocol validate on result/1 (item 3): OK card -> rc 0 + CLOCK OK; UNMEASURED -> rc 0 + WARN; MISMATCH -> rc 1;
         the real result_128-5.json -> rc 1 CLOCK-MISMATCH
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c130_2_tools.log -- py -u tools/bench/selftest_c130_2_tools.py
"""
import contextlib, datetime as dt, io, json, os, shutil, sys, tempfile, time    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
os.chdir(ROOT)
import protocol as P          # noqa: E402
import guard_peer as GP       # noqa: E402
G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-76s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:200]), flush=True)


# ---- fp-18 RUNS_RE ----
for lab, c, want in (("R1 md5sum stagexec.py + bench .py", "md5sum tools/stagexec.py tools/bench/selftest_c120_routes.py", False),
                     ("R2 grep stagexec.py + bench .py", "grep -n def tools/stagexec.py tools/bench/diag_x.py", False),
                     ("R3 py -u bench script", "py -u tools/bench/diag_x.py", True),
                     ("R4 python3 recipe", "python3 tools/recipes/stage_x.py", True),
                     ("R5 C:\\Python\\python.exe bench", "C:\\Python\\python.exe tools/bench/diag_x.py", True),
                     ("R6 bare bgrun.py", "py tools/bgrun.py --log x -- powershell -File y.ps1", True),
                     ("R7 cd root && py -u bench", 'cd "%s" && py -u tools/bench/x.py' % ROOT, True)):
    gate(bool(GP.RUNS_RE.search(c)) == want, lab + (" matches" if want else " does not match"))
# ---- fp-17 waiter ----
WCMD = "py tools/bgrun.py --max-min 35 --log tools/bench/wait_runner_event.log -- py -u tools/wait_runner_event.py --max-min 30"
for lab, c, want in (("W1 fp-17 waiter command", WCMD, True),
                     ("W2 waiter ; recipe", WCMD + " ; py -u tools/recipes/stage_d1_ring_p3a.py", False),
                     ("W3 waiter + bench script", WCMD + " && py -u tools/bench/selftest_card_clock.py", False),
                     ("W4 bgrun of a bench script", "py tools/bgrun.py --log x.log -- py -u tools/bench/selftest_card_clock.py", False),
                     ("W5 plain bgrun of a ps1", "py tools/bgrun.py --log x.log -- powershell -File tools/lv_gui.ps1", False)):
    gate(GP.report_waiter_only(c) == want, lab + " -> %s" % want)
# ---- fp-16 supersession ----
tmp = tempfile.mkdtemp(prefix="c130_2_")
real_bench = GP.BENCH
GP.BENCH = tmp
CMD = "py -u tools/bench/diag_fake_c130_2.py"


def wlog(name, cmd, body, end, age):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("BGRUN START 2026-10-02 03:00:00 limit 1.0 min: %s\nBGRUN PID 1\n%s\n%s\n" % (cmd, body, end))
    t = time.time() - age
    os.utime(p, (t, t))
    return p


RP = 'RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}'
RF = 'RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":0,"fail":1},"first_fail":"X2","artefacts":[]}'
fail = wlog("a_fail.log", CMD, "  FAIL  X1 something\n" + RF.replace("X2", "X1"), "BGRUN END rc=1 after 3s", 100)
gate(GP.log_failure(open(fail, encoding="utf-8").read(), os.stat(fail).st_mtime)[0], "S0 the synthetic failing log reads as failing")
cases = (("S1 same cmd newer rc=0 -> superseded", CMD, RP, "BGRUN END rc=0 after 3s", 50, True),
         ("S2 other command -> not", CMD + " --other", RP, "BGRUN END rc=0 after 3s", 50, False),
         ("S3 newer rc=1 -> not", CMD, RP, "BGRUN END rc=1 after 3s", 50, False),
         ("S4 newer TIMEOUT -> not", CMD, RP, "BGRUN TIMEOUT after 60s", 50, False),
         ("S5 newer with a FAIL RESULT line, rc=0 -> not", CMD, RF, "BGRUN END rc=0 after 3s", 50, False),
         ("S6 OLDER pass -> not", CMD, RP, "BGRUN END rc=0 after 3s", 200, False))
for lab, c, body, end, age, want in cases:
    q = wlog("b_rerun.log", c, body, end, age)
    txt = open(fail, encoding="utf-8").read()
    got = GP.superseded_by_rerun(fail, os.stat(fail).st_mtime, "BGRUN START" + txt.rsplit("BGRUN START", 1)[-1])
    gate(got == want, lab, got)
    os.remove(q)
GP.BENCH = real_bench
shutil.rmtree(tmp, ignore_errors=True)
rf = os.path.join(real_bench, "c125_1_offline_measure_c127_2.log")
if os.path.isfile(rf):
    t = open(rf, encoding="utf-8", errors="replace").read()
    gate(GP.superseded_by_rerun(rf, os.stat(rf).st_mtime, "BGRUN START" + t.rsplit("BGRUN START", 1)[-1]),
         "S7 real fp-16 pair: c127_2.log superseded by c127_2b.log")
else:
    gate(False, "S7 real fp-16 log present", rf)
# ---- fp-15 stagexec selftest under a labview-none card ----
card = dict(P.load_card(os.path.join(ROOT, "tools", "bench", "cards", "task_130-2.json"), None))
card.pop("requires", None)           # the requires ledger is the bind-time check, not what fp-15 is about
BG = "py tools/bgrun.py --material --max-min 8 --log tools/bench/x.log -- "
for lab, c, must in (("F1 bgrun -- py -u tools/stagexec.py selftest", BG + "py -u tools/stagexec.py selftest", True),
                     ("F2 cd root && bgrun ... selftest", 'cd "%s" && %spy -u tools/stagexec.py selftest' % (ROOT.replace("\\", "/"), BG), True),
                     ("F3 bgrun ... selftest 2>&1 | tail -3", BG + "py -u tools/stagexec.py selftest 2>&1 | tail -3", True),
                     ("F4 ... selftest > x.txt", BG + "py -u tools/stagexec.py selftest > tools/bench/x.txt", True),
                     ("F5 NEGATIVE ... selftest --live (another argument)", BG + "py -u tools/stagexec.py selftest --live", False),
                     ("F6 NEGATIVE ... run <plan>", BG + "py -u tools/stagexec.py run tools/bench/plan_x.json", False)):
    why = P.check_command(card, c)
    if must is None:
        print("INFO %s -> %s" % (lab, why or "allowed"), flush=True)
    else:
        gate((why is None) == must, lab + (" -> allowed" if must else " -> refused"), why)
# ---- item 3: validate + clock ----
td = tempfile.mkdtemp(prefix="c130_2_clk_")
now = dt.datetime.now().replace(microsecond=0)
binds = {"t-ok": now - dt.timedelta(minutes=10), "t-mm": now - dt.timedelta(minutes=8)}
with open(os.path.join(td, "guard_card.log"), "w", encoding="utf-8") as f:
    for cid, t in binds.items():
        f.write("%s | ALLOW material a1 | BOUND agent a1 (material) -> tools\\bench\\cards\\task_%s.json (id %s)\n"
                % (t.strftime("%Y-%m-%d %H:%M:%S"), cid, cid))


def res(cid, minutes, first_fail=None):
    r = {"schema": "result/1", "id": cid, "status": "FAIL" if first_fail else "PASS", "gates": {"pass": 1, "fail": 1 if first_fail else 0},
         "first_fail": first_fail, "blocked_by": None, "artefacts": [], "facts": ["x (a.py:1)"], "open": [],
         "cost": {"usd": None, "minutes": minutes, "labview_runs": 0}, "note": ""}
    p = os.path.join(td, "result_%s.json" % cid)
    json.dump(r, open(p, "w", encoding="utf-8"))
    json.dump({"budget": {"minutes": 50}}, open(os.path.join(td, "task_%s.json" % cid), "w", encoding="utf-8"))
    ts = time.mktime(now.timetuple())
    os.utime(p, (ts, ts))
    return p


def validate(p, extra=()):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = P.main(["validate", p, "--no-goalmap"] + list(extra))
    return rc, buf.getvalue()


for lab, p, want_rc, want_txt in (
        ("C1 OK card", res("t-ok", 10), 0, "verdict=OK"),
        ("C2 UNMEASURED (no bind line)", res("t-un", 12), 0, "WARN"),
        ("C3 MISMATCH (8 measured, 45 claimed, budget cited)", res("t-mm", 45, "budget: 50-min card budget spent"), 1, "CLOCK-MISMATCH")):
    rc, out = validate(p, ["--clock-log", os.path.join(td, "guard_card.log"), "--clock-cards", td])
    gate(rc == want_rc and want_txt in out, lab + " -> rc %d + %s" % (want_rc, want_txt), out.replace("\n", " | ")[:200])
shutil.rmtree(td, ignore_errors=True)
r1285 = os.path.join(ROOT, "tools", "bench", "cards", "result_128-5.json")
rc, out = validate(r1285)
gate(rc == 1 and "CLOCK-MISMATCH" in out, "C4 real result_128-5.json -> rc 1 CLOCK-MISMATCH", out.replace("\n", " | ")[:200])
rc, out = validate(r1285, ["--no-clock"])
gate(rc == 0, "C5 --no-clock keeps the schema-only answer for result_128-5.json", out.strip()[:120])
n = sum(1 for ok, _l in G if ok)
print("=== GATES: %d pass / %d fail" % (n, len(G) - n))
print(P.result_line(P.make_result(n, len(G) - n, next((l for ok, l in G if not ok), None))), flush=True)
sys.exit(0 if n == len(G) else 1)
