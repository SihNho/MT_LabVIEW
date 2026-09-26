r"""selftest_leg_guard.py - card 106-2 L7 offline self-test of L2-L4 (no LabVIEW, no VISA port, no GUI act).
FOUND FIRST: drive_legguard.py (this card), m8_dry.stub (the dry stubs of v5), diag_c104_abba.py --dry (executes the leg script).
PREDICTION CONTRACT (all must hold; negatives in brackets):
 C  py_compile drive_legguard / drive_original_copy_v5 / drive_m8 / diag_c104_abba
 V  visa_precheck on a FAKE dll: all 0 -> ok; [one nonzero -> refused]; [RM fail -> refused]; [raise -> refused]; bypass env -> ok+bypassed; dry -> ok
 S  leg_loop stub: A fails before pick 1 at slot 1 -> run_leg called once; [refused slot 1 -> once]; all good -> 4;
    B fails before pick 1 at slot 2 -> 4 (rule is A only); A fails AFTER picks (unregistered, tra) -> rerun once, continues -> 5; max_legs 1 -> 1
 M  v5.main (m8_dry stubs): run1 fails before pick 1 -> leg called ONCE, step 30 'NOT started'; [run1 fails after picks started -> run2 called];
    [precheck refused -> leg never called, motor gate never called]
 W  DialogWatch fake windows: new enabled LVDChild while panel disabled -> fired, shot+kill+ocr on THAT hwnd, max gap <= 0.5 s;
    [new non-modal window -> not fired]; [modal hwnd already in baseline -> not fired]; #32770 modal -> fired
 L  v5.leg with a firing watch -> False, step run1.L1d, GUARD killed, cleanup makes NO COM call; STOP_AT_L2 env -> L2x step + direct kill (fake)
 O  ocr_text on the real 105-2 dialog capture contains '0xBFFF0072' and 'VISA Open'
 D  diag_c104_abba.py --dry (json -> diag_c106b_abba_dry.json, M8_OUT_DIR -> diag_c106b_out/m8_dry) exits 0, 4 legs, every V1 gate True
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c106b_selftest.log -- py -u tools/bench/selftest_leg_guard.py"""
import json, os, py_compile, subprocess, sys, tempfile, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
G = {}
def gate(k, v, info=""):
    G[k] = bool(v); print("GATE %-70s %s %s" % (k, "PASS" if v else "FAIL", info), flush=True)
for f in ("drive_legguard.py", "drive_original_copy_v5.py", "drive_m8.py", "diag_c104_abba.py"):
    try: py_compile.compile(os.path.join(HERE, f), doraise=True); gate("C compile %s" % f, True)
    except Exception as e: gate("C compile %s" % f, False, repr(e)[:300])      # noqa: BLE001
import drive_legguard as LG                                                     # noqa: E402
# ---- V: precheck on a fake dll
class FakeVisa:
    def __init__(self, st, rm=0, boom=False): self.st, self.rm, self.boom, self.closed = dict(st), rm, boom, 0
    def viOpenDefaultRM(self, p):
        if self.boom: raise OSError("fake")
        return self.rm
    def viOpen(self, rm, name, a, t, pv): pv._obj.value = 7; return self.st[name.decode()]
    def viStatusDesc(self, rm, s, b): b.value = b"fake %d" % s.value; return 0
    def viClose(self, v): self.closed += 1; return 0
q = lambda s: None                                                              # noqa: E731
r = LG.visa_precheck(dll=FakeVisa({"Rotor": 0, "ASRL5::INSTR": 0}), log=q); gate("V all 0 -> ok", r["ok"] and len(r["trials"]) == 2)
r = LG.visa_precheck(dll=FakeVisa({"Rotor": 0, "ASRL5::INSTR": -1073807246}), log=q)
gate("V [ASRL5 0xBFFF0072 -> refused]", not r["ok"] and r["trials"][1]["hex"] == "0xBFFF0072")
r = LG.visa_precheck(dll=FakeVisa({}, rm=-1), log=q); gate("V [RM fail -> refused]", not r["ok"])
r = LG.visa_precheck(dll=FakeVisa({}, boom=True), log=q); gate("V [raise -> refused]", not r["ok"] and "raised" in r.get("why", ""))
os.environ[LG.BYPASS_ENV] = "1"; r = LG.visa_precheck(dll=FakeVisa({}, boom=True), log=q); del os.environ[LG.BYPASS_ENV]
gate("V bypass env -> ok, bypassed, nothing opened", r["ok"] and r["bypassed"] and not r["trials"])
r = LG.visa_precheck(dry=True, dll=FakeVisa({}, boom=True), log=q); gate("V dry -> ok, nothing opened", r["ok"] and r["dry"] and not r["trials"])
gate("V default bypass OFF", os.environ.get(LG.BYPASS_ENV) != "1" and os.environ.get(LG.STOP_L2_ENV) != "1")
# ---- S: leg_loop
ORD = [("A", "a", 0, 15), ("B", "b", 0, 15), ("B", "b", 0, 15), ("A", "a", 0, 15)]
GOOD = {"rc": 0, "registered_ok": True, "picks_clicked": 15, "picks_registered_tra": 15}
FAILPRE = {"rc": 1, "registered_ok": False, "picks_clicked": 0, "picks_registered_tra": None}
def loop(fn, **k):
    calls = []
    def rl(slot, arm, src, attempt, npk): calls.append((slot, arm, attempt)); return dict(fn(slot, arm, attempt))
    fin, stop = LG.leg_loop(ORD, rl, log=q, **k); return calls, stop
c, s = loop(lambda sl, a, at: FAILPRE if sl == 1 else GOOD); gate("S A fails before pick 1 at slot 1 -> 1 call, stop", c == [(1, "A", 1)] and s and s["slot"] == 1, str(c))
c, s = loop(lambda sl, a, at: {"refused": True, "rc": "REFUSED"}); gate("S [refused slot 1 -> 1 call, stop]", c == [(1, "A", 1)] and s and "refused" in s["reason"], str(c))
c, s = loop(lambda sl, a, at: GOOD); gate("S all good -> 4 calls, no stop", len(c) == 4 and s is None, str(c))
c, s = loop(lambda sl, a, at: FAILPRE if sl == 2 else GOOD); gate("S B fails before pick 1 at slot 2 -> 4 calls (A-only rule)", len(c) == 4 and s is None, str(c))
c, s = loop(lambda sl, a, at: {"rc": 0, "registered_ok": False, "picks_clicked": 15, "picks_registered_tra": 14} if (sl, at) == (1, 1) else GOOD)
gate("S A fails AFTER picks -> rerun once, continue (5 calls)", len(c) == 5 and c[1] == (1, "A", 2) and s is None, str(c))
c, s = loop(lambda sl, a, at: GOOD, max_legs=1); gate("S max_legs 1 -> 1 call", c == [(1, "A", 1)] and s and "max-legs" in s["reason"], str(c))
# ---- M / L: v5 with the m8_dry stubs
import drive_original_copy_v5 as v5, m8_dry                                    # noqa: E401,E402
d4, d0 = v5.d4, v5.d0
REAL_LEG = v5.leg                                                               # before m8_dry.stub replaces it
TMP = tempfile.mkdtemp(prefix="c106b_st_"); COPY = os.path.join(TMP, "fake_copy.vi"); open(COPY, "wb").write(b"x" * 100)
for m in (v5, d4, d0): m.COPY, m.RUN_DIR, m.SHOTS = COPY, os.path.join(TMP, "run"), os.path.join(TMP, "shots")
v5.EVID = os.path.join(TMP, "evid"); v5.D0_JSON = d0.D0_JSON = os.path.join(TMP, "d0.json"); v5.PROBE_JSON = os.path.join(TMP, "probe.json")
m8_dry.stub(v5, d4, d0)
def run_main(leg_fn, pre_ok=True):
    calls, mg = [], []
    v5._once.clear(); v5.GUARD.update(killed=None, picks_started={}); d0.STEPS.clear()
    v5.VISA_PRECHECK = lambda log=print: {"ok": pre_ok, "names": ["Rotor", "ASRL5::INSTR"], "trials": [], "why": "stub"}
    d4.motor_gate = lambda why: (mg.append(why), (0, "LIMITS TMN=0 TMX=39\nSESSION START OK (DRY)"))[1]
    def lg(tag, n, b, cw): calls.append(tag); return leg_fn(tag)
    v5.leg = lg; v5.main(); return calls, mg, [s["step"] + " " + s["detail"] for s in d0.STEPS]
c, mg, st = run_main(lambda tag: False)
gate("M run1 fails before pick 1 -> leg called once, run2 NOT started", c == ["run1"] and any("30 run2" in x and "before pick 1" in x for x in st), str(c))
def after_picks(tag): v5.GUARD["picks_started"][tag] = True; return False
c, mg, st = run_main(after_picks); gate("M [run1 fails after picks started -> run2 called]", c == ["run1", "run2"], str(c))
c, mg, st = run_main(lambda tag: True); gate("M [run1 ok -> run2 called]", c == ["run1", "run2"], str(c))
c, mg, st = run_main(lambda tag: True, pre_ok=False)
gate("M [precheck refused -> no leg, no motor gate]", c == [] and mg == [] and any("0q LEG REFUSED" in x for x in st), str((c, mg)))
# ---- W: DialogWatch on fake window lists
PANEL = (100, "x.vi Front Panel", "LVDChild", True, True)
def seq_snap(seq):
    it = iter(seq); last = [None]
    def f():
        try: last[0] = next(it)
        except StopIteration: pass                                              # noqa: E701
        return last[0]
    return f
def watch(seq, secs=2.0):
    shots, kills, ocrs = [], [], []
    w = LG.DialogWatch("st", os.path.join(TMP, "dlg"), log=q, snap=seq_snap(seq),
                       shoot=lambda h, png: (shots.append(h), open(png, "wb").write(b"p"), {"rc": 0, "exists": True, "png": png})[2],
                       kill=lambda: (kills.append(1), (True, 0.1))[1], ocr=lambda png: (ocrs.append(png), {"text": "fake text"})[1])
    w.start(); time.sleep(secs); rec = w.stop(); return w, rec, shots, kills, ocrs
DIS = (100, "x.vi Front Panel", "LVDChild", True, False)
w, rec, sh, k, o = watch([[PANEL], [PANEL], [PANEL], [DIS, (555, "", "LVDChild", True, True)]])
gate("W modal LVDChild -> fired, shot+kill+ocr on hwnd 555, gap <= 0.5", w.fired and sh == [555] and k == [1] and o and rec["modal"]["ocr"]["text"] == "fake text"
     and rec["max_gap_s"] <= 0.5, "gap=%s polls=%s kill_after=%s" % (rec["max_gap_s"], rec["polls"], rec["modal"] and rec["modal"]["kill_after_visible_s"]))
w, rec, sh, k, o = watch([[PANEL], [PANEL, (556, "Configure.vi Front Panel", "LVDChild", True, True)]])
gate("W [new non-modal window -> not fired, logged]", not w.fired and not k and len(rec["new_windows"]) == 1)
w, rec, sh, k, o = watch([[PANEL, (557, "", "LVDChild", True, True)], [DIS, (557, "", "LVDChild", True, True)]])
gate("W [dialog hwnd already in baseline -> not fired]", not w.fired and not k)
w, rec, sh, k, o = watch([[PANEL], [DIS, (558, "Save", "#32770", True, True)]])
gate("W #32770 modal -> fired", w.fired and sh == [558])
# ---- L: v5.leg with a firing watch / STOP_AT_L2
class FakeCom:
    def __init__(self): self.n = 0
    def call(self, kind, *a, timeout=None): self.n += 1; return {"state": 2, "get": 0}.get(kind, "ok")
class FakeRun:
    def __init__(self, *a): self.returned = None
    def start(self): pass
class FireWatch:
    def __init__(self, tag, outdir, log=print, fire_after=0.3):
        self.fired, self.t = False, time.time(); self.rec = {"tag": tag, "modal": {"win": [9, "", "LVDChild", True, True], "shotwin": {"rc": 0, "png": "p"},
                                                                                  "kill": {"gone": True, "secs": 0.2}, "kill_after_visible_s": 1.6, "ocr": {"text": "Error -1073807246"}}}
        threading.Timer(fire_after, lambda: setattr(self, "fired", True)).start()
    def start(self): pass
    def stop(self, timeout=60.0): return self.rec if self.fired else dict(self.rec, modal=None)
real_watch, real_kill = v5.LG.DialogWatch, v5.LG.kill_labview
kills = []
v5.LG.kill_labview = lambda wait_s=20.0: (kills.append(1), (True, 0.1))[1]
fc = FakeCom(); d0.com, d0.RunThread = fc, FakeRun
real_leg = REAL_LEG
v5._once.clear(); v5.GUARD.update(killed=None, picks_started={}); d0.STEPS.clear(); v5.LG.DialogWatch = FireWatch
ok = real_leg("run1", 10, os.path.join(TMP, "cal001"), 1.0)
n_before = fc.n; v5.cleanup(); n_after = fc.n
gate("L v5.leg with a firing watch -> False, run1.L1d recorded, GUARD killed", ok is False and any("run1.L1d" in s["step"] for s in d0.STEPS) and v5.GUARD["killed"])
gate("L cleanup after a guard kill makes NO COM call", n_after == n_before and v5.FACTS.get("cleanup_skipped_com"), "com calls %d->%d" % (n_before, n_after))
class QuietWatch(FireWatch):
    def __init__(self, tag, outdir, log=print): super().__init__(tag, outdir, log, fire_after=9999)
v5._once.clear(); v5.GUARD.update(killed=None, picks_started={}); d0.STEPS.clear(); v5.LG.DialogWatch = QuietWatch; kills.clear()
os.environ[LG.STOP_L2_ENV] = "1"; ok = real_leg("run1", 10, os.path.join(TMP, "cal001"), 1.0); del os.environ[LG.STOP_L2_ENV]
gate("L STOP_AT_L2 -> False, run1.L2x recorded, direct kill, no pick", ok is False and kills == [1] and any("run1.L2x" in s["step"] for s in d0.STEPS)
     and not v5.GUARD["picks_started"])
v5.LG.DialogWatch, v5.LG.kill_labview = real_watch, real_kill
# ---- O: OCR on the real 105-2 capture
png = os.path.join(HERE, "diag_c105b_out", "pw", "c105b_20260927_055929_h1706538_birth_pw.png"); t = time.time(); o = LG.ocr_text(png)
tx = (o.get("text") or "").replace(" ", "").upper()
gate("O ocr_text on the 105-2 dialog capture has 0xBFFF0072 + VISA Open", "0XBFFF0072" in tx and "VISAOPEN" in tx, "%.1fs %s" % (time.time() - t, (o.get("text") or "")[:200]))
# ---- D: the ABBA dry run executes the patched chain (v5.main precheck stub in drive_m8 --dry)
env = dict(os.environ, M8_OUT_DIR=os.path.join(HERE, "diag_c106b_out", "m8_dry"))
jd = os.path.join("tools", "bench", "diag_c106b_abba_dry.json"); t = time.time()
p = subprocess.run([sys.executable, "-u", os.path.join(HERE, "diag_c104_abba.py"), "--dry", "--json", jd], capture_output=True, text=True, env=env, cwd=ROOT, timeout=1500)
for ln in (p.stdout or "").splitlines():
    if ln.startswith(("GATE ", "LEGLOOP", "=== LEG", "INDEX")) or "PRECHECK" in ln: print("   | " + ln[:300], flush=True)
dj = json.load(open(os.path.join(ROOT, jd))) if os.path.isfile(os.path.join(ROOT, jd)) else {}
v1 = [v for k, v in (dj.get("gates") or {}).items() if k.startswith("V1 ")]
gate("D ABBA --dry exits 0, 4 legs, every V1 precheck gate True, no loop stop", p.returncode == 0 and len(dj.get("rows") or []) == 4 and len(v1) == 4 and all(v1)
     and not dj.get("leg_loop_stop"), "rc=%s rows=%d v1=%s %.0fs; stderr %s" % (p.returncode, len(dj.get("rows") or []), v1, time.time() - t, (p.stderr or "")[-300:]))
bad = [k for k, v in G.items() if not v]
out = os.path.join(HERE, "diag_c106b_selftest.json"); json.dump({"gates": G}, open(out, "w"), indent=1)
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(out, ROOT), "md5": v5.d0.md5(out)}])), flush=True)
sys.stdout.flush(); os._exit(1 if bad else 0)
