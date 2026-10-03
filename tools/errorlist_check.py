r"""errorlist_check - the cycle-start LabVIEW Error List check (user decision 5, 2026-09-24):
"사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시 확인해야할듯. GUI로 에러 내용 확인하고 각 에러 더블클릭하면 에러
위치로 이동해서 보여주거든. (블락 다이어그램 켜진 상태에서)".

WHAT ALREADY EXISTS (checked first): `tools/lv_errorlist.py` reads every Error List row by capture+OCR, count-checked
against the window's own "N errors and warnings" (docs/toolkit-capabilities.md:313; test tools/bench/diag_errorlist_v0.py).
This file REUSES it unchanged except for one optional per-item hook (`on_item`), and adds: a byte-identical SCRATCH copy
(the bed itself is never opened), Ctrl+E so the block diagram is up, a double-click per item with a capture of the
block diagram before/after, a zero-item path for a runnable VI, the expected-errors comparison, and the cleanup proofs.
The selected object's UID is NOT read: `TopLevelDiagram.Selection List[]` 0x6349400 exists (NI API ref) but the fleet
has no op that reads it (`grep "Selection" tools/gscript.py` -> 0), and branching `Open VI Reference.vi reference`
into a VI-class property node is a MEASURED failure (docs/toolkit-capabilities.md:666). Recorded per item as uid=None.

PREDICTION CONTRACT: Ctrl+E opens '<scratch> Block Diagram'; Ctrl+L opens a new 'Error list' window; items read ==
the window's own N (0 for a runnable VI); each double-click fronts the block diagram and changes its capture; the
Error List is closed with Esc; the scratch is closed and deleted; the bed md5 is unchanged; no VI is run or saved.
Every GUI act goes through lv_gui.ps1 with -Exception Approved -Evidence EVID (logged to tools/gui_actions.log).

  py tools/errorlist_check.py [--vi <bed.vi>] [--expected <file.json>]      rc 0 OK / 1 MISMATCH / 2 FAIL
  expected file: {"expected": [{"match": "<substring of the row text>", "count": n}, ...]}  (default: none = [])
Last stdout line: `ERRORLIST-VERDICT: OK|MISMATCH|FAIL <json path>`.
"""
import argparse, glob, hashlib, json, os, re, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "bench"))
# LAZY LabVIEW IMPORTS (card 81-1, 2026-09-25): the offline re-verdict (`find_reusable` / `reverdict`, used by
# cycle_runner.errorlist_hook when the bed md5 is unchanged) must import nothing LabVIEW-side, so gscript /
# lv_errorlist / bench_prep are bound only by `_lv_imports()`, which main() calls first. Same modules, same order.
g = E = labview_handles = None
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"   # == gscript.CLAUDEDEV

EVID = "user 2026-09-24 error-list check at cycle start"


def _lv_imports():
    global g, E, labview_handles
    if g is None:
        import gscript as _g
        import lv_errorlist as _E
        from bench_prep import labview_handles as _lh
        g, E, labview_handles = _g, _E, _lh
        E.EVIDENCE = EVID


BENCH = os.path.join(HERE, "bench")
# 2026-09-24 card chat-C2: external search (WebSearch, "LabVIEW scripting read selected objects block diagram
# Selection List") found no route other than a VI Server property node on TopLevelDiagram.Selection List[]; the
# ActiveX VirtualInstrument interface has no diagram access (toolkit-capabilities.md:666), and building an op VI is
# outside a labview=read card. So the uid is not read here; the after-capture of the diagram is the record.
UID_ROUTE = "none: needs a Selection List[] 6349400 op (unbuilt; card labview=read) - screenshot recorded"
COUNT_RE = re.compile(r"(\d+)\s*errors?\s*and\s*warnings?", re.I)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# HANDLE BASELINE (card chat-D, 2026-09-24): since the runner closes LabVIEW at every cycle end, this check usually
# starts with NO LabVIEW, and `handles_before` read 0 (tools/bench/errorlist_D1_l7_1_20260924_060431_20260924_192431.json:
# 0 -> 31,287; ..._191838.json: 0 -> 34,643) - a gate on that delta would be meaningless. So LabVIEW is started and
# allowed to SETTLE first; `handles_before` is read only then. HANDLE_TOL: the one warm measurement is +25 over a
# whole check (..._180737.json 42,764 -> 42,789), but a check on a freshly started LabVIEW LOADS the bed's hierarchy
# (fresh baseline ~31,500 per CLAUDE.md; ..._191838.json ended at 34,643, i.e. up to ~+3,100).
# HANDLES ARE A RECORD, NOT A GATE (card chat-E2, judgement 2026-09-25): cycle 80 read 22/22 items and FAILed only
# on handles_flat (37,239 -> 31,287, a DROP of 5,952 after the hierarchy unloaded; errorlist_check_cycle80.log).
# handles_before / handles_after / handles_delta are recorded in the JSON and log; HANDLE_TOL only sets the
# advisory flag `handles_advisory` ("within" / "outside"), which never touches the verdict.
HANDLE_TOL = 5000
LV_UP_S = 60.0
SETTLE_BAND = 300
SETTLE_S = 60.0
VI_READY_S = 60.0
# COM NOT READY (card chat-E1, 2026-09-25): the runner restart at 01:02 stopped in 22 s because LabVIEW answered
# `Application.Version` (lv_up_s 21.5) and its handles settled, but the FIRST GetVIReference then raised
# com_error -2147221231 "ClassFactory cannot supply requested class" (tools/bench/errorlist_check_cycle74.log;
# errorlist_D1_s4_loop17_20260925_010221.json). The app object comes up before the VirtualInstrument class does, so
# readiness is now proven with the call the check actually needs (vi_ready), retried until it answers.
NOT_READY = ("-2147221231", "ClassFactory")
# _APP_PIN (card chat-E1, run r1 errorlist_check_cold_20260925.log 01:05; CORRECTED card chat-E2 per the review
# archive/peer/2026-09-25-chat-E1r-pointer-release.md): with the vi_ready poll the ClassFactory error cleared on
# try 2 (20.4 s, ExecState 1 - ~16 s for a call that takes 1.3 s warm), then the NEXT call failed: the
# GetVIReference inside open_panel's vi_ref (ref_counts opened 1 / closed 1, errorlist_D1_s4_loop17_20260925_010538
# .json), com_error with inner scode 0x80010007 RPC_E_SERVER_DIED - not OpenFrontPanel and not 0x80010107. Two
# explanations fit and both predict that one held pointer works: (a) a COM-launched LabVIEW exits when its last
# Application pointer is released (this file dropped it, `g._lv = None`, before each retry); (b) the SECOND
# Dispatch during a cold launch reached a second or tearing-down instance. The A/B test
# tools/bench/com_pointer_ab.py (log com_pointer_ab_20260925.log) separates them. Either way ONE Application
# pointer is held for the whole run and there is no second Dispatch; LabVIEW closes when the process exits.
_APP_PIN = None


def not_ready(e):
    t = repr(e)
    return any(k in t for k in NOT_READY)


def labview_up(R):
    """Start (COM Dispatch launches it) / reach LabVIEW, then wait until two handle readings 5 s apart differ by
    less than SETTLE_BAND. Records the steps in R; returns the settled handle count or None."""
    t0 = time.time()
    R["lv_was_running"] = labview_handles() > 0
    tries = 0
    while True:
        tries += 1
        try:
            global _APP_PIN
            _APP_PIN = g.lv()                        # held for the whole run: see _APP_PIN below
            R["lv_version"] = str(_APP_PIN.Version)
            break
        except Exception as e:                                                     # noqa: BLE001
            g._lv = _APP_PIN = None
            if time.time() - t0 > LV_UP_S:
                R["errors"].append("LabVIEW did not answer COM within %.0f s: %s" % (LV_UP_S, str(e)[:120]))
                print("LV-UP: no Version answer after %d tries, %.1f s" % (tries, time.time() - t0), flush=True)
                return None
            time.sleep(4)
    R["lv_version_s"] = round(time.time() - t0, 1)
    print("LV-UP: was_running=%s Version %s answered after %d tries, %.1f s" % (
        R["lv_was_running"], R["lv_version"], tries, R["lv_version_s"]), flush=True)
    prev, t1 = labview_handles(), time.time()
    while True:
        time.sleep(5)
        cur = labview_handles()
        if prev > 0 and abs(cur - prev) < SETTLE_BAND:
            R["lv_up_s"] = round(time.time() - t0, 1)
            print("LV-UP: handles settled %d -> %d at %.1f s" % (prev, cur, R["lv_up_s"]), flush=True)
            return cur
        if time.time() - t1 > SETTLE_S:
            R["errors"].append("LabVIEW handle count did not settle in %.0f s (%d -> %d)" % (SETTLE_S, prev, cur))
            R["lv_up_s"] = round(time.time() - t0, 1)
            return cur if cur > 0 else None
        prev = cur


def vi_ready(target, R):
    """Poll a counted GetVIReference (+ ExecState) on `target` until it answers, up to VI_READY_S; only the
    COM-not-ready error (NOT_READY) is retried, anything else is raised. Returns the ExecState."""
    t0, tries = time.time(), 0
    while True:
        tries += 1
        try:
            es = g.exec_state(target)
            R["vi_ready_s"], R["vi_ready_tries"] = round(time.time() - t0, 1), tries
            print("VI-READY: GetVIReference answered after %d tries, %.1f s (ExecState %s)" % (
                tries, R["vi_ready_s"], es), flush=True)
            return es
        except Exception as e:                                                     # noqa: BLE001
            if not not_ready(e) or time.time() - t0 > VI_READY_S:
                R["vi_ready_s"], R["vi_ready_tries"] = round(time.time() - t0, 1), tries
                print("VI-READY: gave up after %d tries, %.1f s: %s" % (tries, R["vi_ready_s"], str(e)[:120]),
                      flush=True)
                raise
            time.sleep(4)


def current_bed(status_path):
    """`current-bed: <file.vi>` in STATUS wins; else the NEWEST-on-disk claudeDev D1_*.vi that STATUS names."""
    return current_bed_text(open(status_path, encoding="utf-8").read())


def current_bed_text(txt, claudedev=None):
    """current_bed() on STATUS text (pure; cycle_runner holds the text already)."""
    m = re.search(r"^current-bed:\s*(\S+\.vi)", txt, re.M)
    names = [m.group(1)] if m else sorted(set(re.findall(r"(D1_[\w\-]+\.vi)", txt)))
    paths = [os.path.join(claudedev or CLAUDEDEV, os.path.basename(n)) for n in names]
    paths = [p for p in paths if os.path.exists(p)]
    return max(paths, key=os.path.getmtime) if paths else None


# OFFLINE RE-VERDICT (card 81-1, retrospective-cycle80 device-failed, archive/peer/2026-09-25-retrospective-cycle80.md:266):
# the GUI read of an UNCHANGED bed returns the same items, so re-reading it every cycle only buys new chances to fail
# (cycles 74 and 80 stopped the runner on the READ, not on the bed). When the newest complete read of this bed was
# taken on the SAME md5, its saved raw items are re-judged with the CURRENT checker (expected file + plan licences +
# header rule) and no LabVIEW is started. A read qualifies only if its own JSON records bed_md5_before == after ==
# the bed's md5 now, every read gate it recorded is True (handles_flat excluded: a record, not a gate, since chat-E2),
# and its _raw.json sibling holds exactly n_reported items. Anything else -> the GUI read, unchanged.
REUSE_SKIP_GATES = ("handles_flat",)


def find_reusable(bed, bed_md5, bench=None):
    """(main_json, raw_json, None) for the newest qualifying read of `bed` at `bed_md5`, else (None, None, reason)."""
    bench = bench or BENCH
    stem = os.path.splitext(os.path.basename(bed))[0]
    cands = [p for p in glob.glob(os.path.join(bench, "errorlist_%s_*.json" % stem))
             if not re.search(r"_(raw|reuse)\.json$", p)]
    for p in sorted(cands, key=lambda q: os.path.basename(q), reverse=True):     # names end in the read's stamp
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                                          # noqa: BLE001
            continue
        if os.path.basename(str(d.get("bed") or "")).lower() != os.path.basename(bed).lower():
            continue
        raw = p[:-len(".json")] + "_raw.json"
        # the NEWEST read of this bed decides: if it does not qualify, the GUI reads again (no fallback to older)
        if not (d.get("bed_md5_before") == d.get("bed_md5_after") == bed_md5):
            return None, None, "newest read %s was taken on md5 %s, bed is %s" % (
                os.path.basename(p), d.get("bed_md5_before"), bed_md5)
        gates = {k: v for k, v in (d.get("gates") or {}).items() if k not in REUSE_SKIP_GATES}
        if not gates or not all(gates.values()):
            return None, None, "newest read %s is incomplete (gates %s)" % (
                os.path.basename(p), [k for k, v in gates.items() if not v] or "none")
        if not os.path.exists(raw):
            return None, None, "newest read %s has no _raw.json" % os.path.basename(p)
        r = json.load(open(raw, encoding="utf-8"))
        if len(r.get("items") or []) != d.get("n_reported"):
            return None, None, "raw %s holds %d items, read reported %s" % (
                os.path.basename(raw), len(r.get("items") or []), d.get("n_reported"))
        return p, raw, None
    return None, None, "no saved read of %s" % os.path.basename(bed)


def reverdict(bed, main_json, raw_json, bench=None, out_dir=None, expected_path=None):
    """Offline verdict of a saved read with the CURRENT checker. Writes errorlist_<stem>_<ts>_reuse.json; returns
    (verdict OK|MISMATCH, out_path). No LabVIEW, no GUI."""
    bench = bench or BENCH
    src = json.load(open(main_json, encoding="utf-8"))
    raw = json.load(open(raw_json, encoding="utf-8"))
    stem = os.path.splitext(os.path.basename(bed))[0]
    exp_path = expected_path or os.path.join(bench, "errorlist_expected_%s.json" % stem)
    expected = json.load(open(exp_path, encoding="utf-8")).get("expected", []) if os.path.exists(exp_path) else []
    sp, pp, plan = plan_for_bed(bed, bench)
    # PD195(b) (card 88-4): a bed with an EXPLICIT expected file gets NO plan-derived licences - the uncapped
    # wire_from_open_rows class would silently absorb a new fault of the same wording. Interpretation: all derived
    # licences are dropped, not only the uncapped one (archive/peer/2026-09-26-c88-reuse-stalepin.md:90).
    derived = derive_expected(plan) if plan and not os.path.exists(exp_path) else []
    items = [dict(i) for i in raw.get("items") or []]
    for i in items:
        i.pop("licensed_by", None)
    extra, missing, usage = compare(items, expected, derived)
    verdict = "OK" if not (extra or missing) else "MISMATCH"
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(out_dir or bench, "errorlist_%s_%s_reuse.json" % (stem, ts))
    R = {"mode": "REUSE", "bed": bed, "bed_md5": src.get("bed_md5_before"), "reused_from": main_json,
         "reused_raw": raw_json, "reused_raw_md5": hashlib.md5(open(raw_json, "rb").read()).hexdigest(),
         "source_stamp": src.get("stamp"), "source_verdict": src.get("verdict"), "stamp": ts,
         "expected_file": exp_path if os.path.exists(exp_path) else None, "stage_file": sp, "plan_file": pp,
         "open_rows": (plan or {}).get("open_rows"), "item_count": len(items), "n_reported": src.get("n_reported"),
         "items": items, "extra": extra, "missing": missing, "licence_usage": usage, "verdict": verdict,
         "no_labview": True}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False, default=str)
    return verdict, out


def windows_named(sub):
    return [(h, t) for h, t, _c, _r in E.top_windows(E.lv_pid()) if sub.lower() in (t or "").lower()]


def open_diagram(scratch, R):
    name = os.path.basename(scratch)
    bd = "%s Block Diagram" % name
    if windows_named(bd):
        return True
    title, fg = E._focus_vi_window(scratch, R["gui_acts_outer"])
    if not title:
        R["errors"].append("could not front the scratch: %s" % fg)
        return False
    E.shot("before_ctrl_e", R["gui_acts_outer"])
    E.send_keys("^e", R["gui_acts_outer"], "open block diagram", wait_ms=1500)
    t0 = time.time()
    while time.time() - t0 < 15 and not windows_named(bd):
        time.sleep(0.5)
    ok = bool(windows_named(bd))
    E.shot("after_ctrl_e", R["gui_acts_outer"])
    R["gui_acts_outer"].append({"act": "confirm", "tag": "ctrl+e opened the block diagram", "confirmed": ok})
    return ok


def make_on_item(scratch, R):
    bd = "%s Block Diagram" % os.path.basename(scratch)

    def shot_bd(tag):
        p = os.path.join(E.SHOTS, "bd_%s_%s.png" % (time.strftime("%H%M%S"), tag))
        g._lv_gui("-Action", "shotwin", "-Title", '"%s"' % bd, "-Out", p)
        return (p, md5(p)) if os.path.exists(p) else (None, None)

    def on_item(rec, acts):
        import win32gui
        b_path, b_md5 = shot_bd("before%d" % rec["index"])            # capture
        x0, y0, x1, y1 = rec["screen_rect"]                              # locate: the row on the live capture
        x, y = x0 + (x1 - x0) // 4, (y0 + y1) // 2
        g._lv_gui("-Action", "dclick", "-X", str(x), "-Y", str(y), "-Exception", "Approved", "-Evidence", EVID)
        acts.append({"act": "dclick", "tag": "item %d" % rec["index"], "screen_xy": [x, y]})
        time.sleep(1.5)
        fg = win32gui.GetWindowText(win32gui.GetForegroundWindow())       # act -> capture -> confirm
        a_path, a_md5 = shot_bd("after%d" % rec["index"])
        still = bool(windows_named("error list"))
        rec["show_error"] = {"fg_after": fg, "bd_before": b_path, "bd_after": a_path,
                             "bd_changed": bool(a_md5 and a_md5 != b_md5), "diagram_fronted": bd in fg,
                             "error_list_still_open": still, "uid": None, "class": None,
                             "uid_route": UID_ROUTE, "screenshot": a_path}
        acts.append({"act": "confirm", "tag": "item %d diagram fronted + changed" % rec["index"],
                     "confirmed": bd in fg and rec["show_error"]["bd_changed"]})
        if not still:
            raise RuntimeError("the Error List closed after the double-click")
    return on_item


def count_zero(R):
    """A runnable VI has no highlighted row, so lv_errorlist never reads N: OCR the last dialog capture whole."""
    caps = [a["path"] for a in R.get("gui_acts", []) if a.get("act") == "shotwin" and a.get("path")]
    caps += sorted(glob.glob(os.path.join(E.SHOTS, "errwin_*.png")), key=os.path.getmtime)[-1:]
    for p in caps[:1] + caps[-1:]:
        from PIL import Image
        for t, _c, _a, _b, _x in E.ocr_lines(Image.open(p).convert("RGB"), scale=2):
            m = COUNT_RE.search(t)
            if m:
                return int(m.group(1)), t, p
    return None, None, caps[-1] if caps else None


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


# card 127-2 (PD255(a) carry; review archive/peer/2026-10-01-c126-4-elocr.md:73): OCR reads 'SubVI' as 'subvl' and
# 'anything' as 'anvthing'. ADD-ONLY: norm() is unchanged (expected files store its keys); norm_ocr() is the alias-folded
# form, applied to BOTH sides only where a caller opts in (_hit's fallback, class_counts(ocr=True)).
OCR_ALIASES = (("vl", "vi"), ("v", "y"))


def ocr_fold(k):
    for a, b in OCR_ALIASES:
        k = k.replace(a, b)
    return k


def norm_ocr(s):
    return ocr_fold(norm(s))


# EXPECTED ERRORS FROM THE PLAN (card chat-E2): a staged bed is broken BY DESIGN - its plan
# (tools/bench/plan_<stage>*.json, schema stageplan/1) declares `open_rows` [{node, term, why}] left for a later
# stage. Each open row licenses the Error List items LabVIEW raises for it, derived per node class from the plan's
# base graph (`base.path` objs[].class): a SubVI -> "... '<term>' is not wired" (only REQUIRED inputs are listed,
# so the licence is not required to appear); any other node -> one "Contains unwired or bad terminal"; and the
# half-wires an open row leaves -> the wire classes in WIRE_CLASSES. Their COUNT is not derivable from open_rows
# (one deleted sink can leave loose ends on several branches), so the wire licence is class-level and uncapped;
# the JSON records how many items it absorbed. Anything no licence covers is `extra` -> MISMATCH.
WIRE_CLASSES = ("wirehaslooseends", "hasnosource", "outputlooptunneltoaninput", "twoterminalsofdifferenttypes")
# REVERTED by docs/d1-loop12-17-split-plan.md Pre-decided 195(b) (cycle 88): cycle 87's uncapped additions
# "isnotconnectedtoanything" and "zerosources" are removed - an uncapped class licence hides a real fault of the same
# wording (archive/peer/2026-09-26-c87-errorlist-extras.md:118). The L2-A1 bed's items are licensed instead by an
# explicit, exact-count file: tools/bench/errorlist_expected_D1_l2_a1_20260925_235224.json.


def plan_for_bed(bed, bench=None):
    """stage_d1_<s>.json whose `work` is this bed -> the stageplan plan_<s>*.json carrying open_rows."""
    BENCH_ = bench or BENCH
    name = os.path.basename(bed).lower()
    for sp in sorted(glob.glob(os.path.join(BENCH_, "stage_d1_*.json"))):
        try:
            if os.path.basename(str(json.load(open(sp, encoding="utf-8")).get("work") or "")).lower() != name:
                continue
        except Exception:                                                          # noqa: BLE001
            continue
        stage = os.path.basename(sp)[len("stage_d1_"):-len(".json")]
        # cycle-87 firefighter: a simulated stage (docs/stage-simulator-plan.md) keeps its finalized plan under
        # tools/bench/sim/<stage>/ (plan_<stage>.json, stageplan_<stage>.json), not in tools/bench/; without this
        # the L2-A1 bed derived 0 licences and every one of its 35 by-design items was `extra` (cycle 87 MISMATCH).
        cands = sorted(glob.glob(os.path.join(BENCH_, "plan_%s*.json" % stage)))
        cands += sorted(glob.glob(os.path.join(BENCH_, "sim", stage, "plan_%s*.json" % stage)))
        cands += sorted(glob.glob(os.path.join(BENCH_, "sim", stage, "stageplan_%s*.json" % stage)))
        for pp in cands:
            try:
                p = json.load(open(pp, encoding="utf-8"))
            except Exception:                                                      # noqa: BLE001
                continue
            if p.get("schema") == "stageplan/1" and "open_rows" in p:
                return sp, pp, p
    return None, None, None


def derive_expected(plan):
    base = (plan.get("base") or {}).get("path")
    cls = {}
    if base and os.path.exists(os.path.join(ROOT, base)):
        for o in json.load(open(os.path.join(ROOT, base), encoding="utf-8")).get("objs") or []:
            cls[o.get("uid")] = o.get("class")
    rules, seen_nodes = [], set()
    for r in plan.get("open_rows") or []:
        n, t = int(r["node"]), r["term"]
        c = cls.get(n)
        if c == "SubVI":
            rules.append({"norm_all": [norm(t), "isnotwired"], "count": 1, "required": False,
                          "kind": "subvi_input_not_wired", "from": [n, t, c]})
        elif n not in seen_nodes:
            rules.append({"norm_all": ["containsunwiredorbadterminal"], "count": 1, "required": False,
                          "kind": "node_unwired", "from": [n, t, c]})
        seen_nodes.add(n)
    if plan.get("open_rows"):
        rules.append({"norm_any": list(WIRE_CLASSES), "count": None, "required": False,
                      "kind": "wire_from_open_rows", "from": "all open rows"})
    return rules


def _hit(rule, txt):
    if "match" in rule:
        return rule["match"].lower() in txt.lower()
    n = norm(txt)
    if "norm_all" in rule:
        if all(k in n for k in rule["norm_all"]):
            return True
        n2 = ocr_fold(n)                                   # card 127-2: OCR-alias fallback (only adds matches)
        return all(ocr_fold(k) in n2 for k in rule["norm_all"])
    if any(k in n for k in rule.get("norm_any") or []):
        return True
    n2 = ocr_fold(n)
    return any(ocr_fold(k) in n2 for k in rule.get("norm_any") or [])


def compare(items, expected, derived=()):
    """Explicit expected entries (file) are REQUIRED; plan-derived licences are not. Returns extra raws, missing
    explicit matches, and per-rule usage."""
    left = [dict(e, count=int(e.get("count", 1)), required=True, kind="explicit") for e in expected]
    left += [dict(d) for d in derived]
    used = [0] * len(left)
    extra = []
    for it in items:
        txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
        k = next((i for i, e in enumerate(left) if (e["count"] is None or e["count"] > 0) and _hit(e, txt)), None)
        if k is None:
            extra.append(it.get("raw"))
            continue
        used[k] += 1
        it["licensed_by"] = left[k]["kind"]
        if left[k]["count"] is not None:
            left[k]["count"] -= 1
    missing = [e.get("match") for e in left if e["required"] for _ in range(e["count"])]
    usage = [{"kind": e["kind"], "from": e.get("from") or e.get("match"), "used": u} for e, u in zip(left, used)]
    heads = license_headers(items)
    for pos in heads:                                   # remove exactly the licensed empty headers from `extra`
        extra.remove(items[pos].get("raw"))
    usage.append({"kind": "header_of_next", "from": "PD179(d): empty-raw tree header before a licensed item",
                  "used": len(heads)})
    return extra, missing, usage


# TREE-HEADER ROWS (card 80-4, plan PD179(d), 2026-09-25): the Error List shows a subVI's required-input error as a
# tree - a header row whose OCR text can come back EMPTY, then the item row. cycle 80 read item 0 raw='' with the
# detail of item 1 (#5058 'Image In' is not wired, licensed by an open row) and called it extra. An empty-raw row is
# licensed ONLY when (a) the NEXT item is itself licensed and non-empty, and (b) the header's detail text (the error
# class description) equals that item's detail after norm(). It consumes no licence count. Anything else stays extra.

def license_headers(items):
    """Mark `licensed_by = 'header-of <n>'` on qualifying empty-raw rows; return their positions in `items`."""
    out = []
    for pos, it in enumerate(items):
        if it.get("licensed_by") or norm(it.get("raw")) or pos + 1 >= len(items):
            continue
        nxt = items[pos + 1]
        det = norm(it.get("detail"))
        if not (nxt.get("licensed_by") and not str(nxt["licensed_by"]).startswith("header-of")
                and norm(nxt.get("raw")) and det and det == norm(nxt.get("detail"))):
            continue
        it["licensed_by"] = "header-of %s" % nxt.get("index", pos + 1)
        out.append(pos)
    return out


# COUNT-ONLY SCRATCH READ (card chat-P2 item 3, user 2026-09-28 "1~4번 적용"): a stage that reads the Error List of a
# SCRATCH copy and then of the saved FINAL file paid two full reads (pool stage: scratch 664 s + final 665 s). The
# expensive part of a full read is the per-item double-click (make_on_item: two block-diagram captures + 1.5 s each).
# `--count-only --role scratch` walks the list WITHOUT the double-clicks (rows and details are still OCR'd, so every
# item's text and the per-class counts are read) and compares the per-class counts with the expected file; if they
# differ (any extra, any missing, or items != the window's own N) the FULL read runs at once on the same scratch,
# exactly as before. `--role final` (the default) ALWAYS gets the full read: --count-only is refused for it and said so.
def class_counts(items, ocr=False):
    """{norm(raw): n} over the read items - the per-class counts a count-only read is judged by. card 127-2: ocr=True
    keys by norm_ocr (OCR aliases folded, e.g. subvi/subvl one class); the default is unchanged."""
    out = {}
    for it in items or []:
        k = norm_ocr(it.get("raw")) if ocr else norm(it.get("raw"))
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def count_only_differs(items, n_reported, expected, derived):
    """(differs: bool, why: str) - a count-only read is accepted only when it matches the expectation exactly."""
    import copy
    ex, mi, _u = compare(copy.deepcopy(items or []), expected, [dict(d) for d in derived])
    why = []
    if n_reported is None or len(items or []) != n_reported:
        why.append("items %s != window N %s" % (len(items or []), n_reported))
    if ex:
        why.append("%d extra" % len(ex))
    if mi:
        why.append("%d missing" % len(mi))
    return bool(why), "; ".join(why)


def read_mode(count_only, role):
    """'count' only for a scratch copy; the final saved file is always 'full'."""
    return "count" if (count_only and role == "scratch") else "full"


def by_design(R, expected, plan, record=True):
    """card chat-S5 (PD337(c), the user's "S1" item 3): a MISMATCH whose only difference is extra session-boundary items
    (unwired Local read, While conditional terminal) that the FIXED rule (tools/elrule.py) re-derives from the bed's own plan
    -> ('log', rule, detail) and one gate_soft_log.jsonl line; anything else ('stop', why, detail). Pure, offline: it reads
    R['extra'] / R['missing'] / R['items'] and the plan's step files only."""
    import elrule as ELR
    import gateclass as _GC
    base_total = sum(int(e.get("count", 1)) for e in expected or [])
    measured = len(R.get("items") or []) if R.get("items") is not None else R.get("n_reported")
    texts = []
    for raw in R.get("extra") or []:
        it = next((i for i in R.get("items") or [] if i.get("raw") == raw), {})
        texts.append("%s %s" % (raw or "", it.get("detail") or ""))
    bv, brule, bdet = ELR.by_design_verdict(texts, R.get("missing"), measured, base_total, plan=plan)
    if bv == "log" and record:
        _GC.soft_record("EL-BYDESIGN " + os.path.basename(str(R.get("bed") or "")), "ErrorList", base_total, measured, brule)
    return bv, brule, bdet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vi", default="")
    ap.add_argument("--expected", default="")
    ap.add_argument("--status", default=os.path.join(ROOT, "STATUS.md"))
    ap.add_argument("--count-only", action="store_true",
                    help="card chat-P2: walk the list without the per-item double-click; full read follows at once "
                         "if the per-class counts differ from the expected file. Honoured only with --role scratch.")
    ap.add_argument("--role", choices=["scratch", "final"], default="final",
                    help="what --vi is: a scratch copy (count-only allowed) or the saved final file (always full)")
    a = ap.parse_args()
    mode = read_mode(a.count_only, a.role)
    if a.count_only and mode != "count":
        print("COUNT-ONLY REFUSED: --role %s - the final saved file always gets the FULL read (card chat-P2)" % a.role,
              flush=True)
    _lv_imports()
    t0, ts = time.time(), time.strftime("%Y%m%d_%H%M%S")
    bed = a.vi or current_bed(a.status)
    R = {"bed": bed, "stamp": ts, "errors": [], "gui_acts_outer": [], "no_vi_was_run": True, "evidence": EVID,
         "role": a.role, "read_mode": mode, "count_only_refused": bool(a.count_only and mode != "count")}
    out = os.path.join(BENCH, "errorlist_%s_%s.json" % (os.path.splitext(os.path.basename(bed or "none"))[0], ts))
    verdict = "FAIL"
    if not bed or not os.path.exists(bed):
        R["errors"].append("no bed: %r" % bed)
    else:
        R["bed_md5_before"] = md5(bed)
        R["handles_before"] = labview_up(R)          # LabVIEW started and settled FIRST, then the baseline
        exp_path = a.expected or os.path.join(BENCH, "errorlist_expected_%s.json" %
                                              os.path.splitext(os.path.basename(bed))[0])
        expected = json.load(open(exp_path, encoding="utf-8")).get("expected", []) if os.path.exists(exp_path) else []
        R["expected_file"] = exp_path if os.path.exists(exp_path) else None
        R["stage_file"], R["plan_file"], plan = plan_for_bed(bed)
        derived = derive_expected(plan) if plan and not os.path.exists(exp_path) else []   # PD195(b), card 88-4
        R["open_rows"] = (plan or {}).get("open_rows")
        print("plan %s open_rows %s -> %d derived licences" % (R["plan_file"], len(R["open_rows"] or []),
                                                                len(derived)), flush=True)
        scratch = os.path.join(g.CLAUDEDEV, "_elc_%s_%s.vi" % (os.path.splitext(os.path.basename(bed))[0][:40], ts))
        shutil.copyfile(bed, scratch)
        R["scratch"], R["scratch_identical"] = scratch, md5(scratch) == R["bed_md5_before"]
        print("bed %s md5 %s -> scratch %s identical=%s" % (bed, R["bed_md5_before"], scratch,
                                                              R["scratch_identical"]), flush=True)
        try:
            vi_ready(scratch, R)                     # COM-not-ready guard (card chat-E1)
            g.open_panel(scratch)
            time.sleep(1.0)
            R["exec_state"] = g.exec_state(scratch)
            R["block_diagram_open"] = open_diagram(scratch, R)
            t_read = time.time()
            r = E.read(scratch, out.replace(".json", "_raw.json"), log=lambda s: print(s, flush=True),
                       on_item=None if mode == "count" else make_on_item(scratch, R))
            R.update({k: r.get(k) for k in ("method", "n_reported", "n_reported_from", "items", "categories",
                                            "gui_acts", "closed_with_esc", "window", "ocr_engine")})
            R["errors"] += r.get("errors") or []
            R["read_seconds"] = [round(time.time() - t_read, 1)]
            if mode == "count":
                R["class_counts"] = class_counts(R.get("items"))
                differs, why = count_only_differs(R.get("items"), R.get("n_reported"), expected, derived)
                print("COUNT-ONLY read: %d items, window N %s, %d classes, %.1f s -> %s" % (
                    len(R.get("items") or []), R.get("n_reported"), len(R["class_counts"]), R["read_seconds"][0],
                    ("counts DIFFER (%s): FULL read of the scratch follows" % why) if differs else "counts match"),
                    flush=True)
                if differs:
                    R["read_mode"] = "count->full"
                    R["count_only_first"] = {"items": len(R.get("items") or []), "n_reported": R.get("n_reported"),
                                             "why": why, "class_counts": R["class_counts"]}
                    t_read = time.time()
                    r = E.read(scratch, out.replace(".json", "_raw_full.json"), log=lambda s: print(s, flush=True),
                               on_item=make_on_item(scratch, R))
                    R.update({k: r.get(k) for k in ("method", "n_reported", "n_reported_from", "items", "categories",
                                                    "gui_acts", "closed_with_esc", "window", "ocr_engine")})
                    R["errors"] += r.get("errors") or []
                    R["read_seconds"].append(round(time.time() - t_read, 1))
            if not R["items"]:
                n0, line, cap = count_zero(R)
                R["n_reported"], R["n_reported_from"], R["zero_capture"] = (
                    R["n_reported"] if R["n_reported"] is not None else n0), line, cap
                R["errors"] = [e for e in R["errors"] if "errors band" not in e and "highlighted row" not in e]
        except Exception as e:                                                     # noqa: BLE001
            R["errors"].append("%s: %s" % (type(e).__name__, str(e)[:240]))
        try:
            g.close_panel(scratch)
        except Exception as e:                                                     # noqa: BLE001
            R["errors"].append("close_panel: %s" % str(e)[:160])
        for _ in range(6):
            try:
                os.remove(scratch)
                break
            except OSError:
                time.sleep(2.0)
        R["scratch_deleted"] = not os.path.exists(scratch)
        R["bed_md5_after"] = md5(bed)
        R["handles_after"] = labview_handles()
        R["ref_counts"] = g.ref_counts()
        items = R.get("items") or []
        R["item_count"] = len(items)
        R["show_error_ok"] = sum(1 for i in items if (i.get("show_error") or {}).get("diagram_fronted"))
        R["dclicked"] = sum(1 for i in items if i.get("show_error"))
        R["extra"], R["missing"], R["licence_usage"] = compare(items, expected, derived)
        for i in items:
            if str(i.get("licensed_by") or "").startswith("header-of"):
                print("LICENCE item %s: %s (empty-raw tree header, PD179(d))" % (i.get("index"), i["licensed_by"]),
                      flush=True)
        R["gates"] = {
            "window_opened": bool(R.get("window")),
            "count_read": R.get("n_reported") is not None,
            "all_items_read": R.get("n_reported") is not None and R["item_count"] == R["n_reported"],
            # a count-only scratch read skips the double-clicks BY DESIGN (card chat-P2); every other read keeps the gate
            "every_item_dclicked": R["dclicked"] == R["item_count"] if R.get("read_mode") != "count" else True,
            "closed_with_esc": bool(R.get("closed_with_esc")),
            "scratch_identical": bool(R.get("scratch_identical")),
            "scratch_deleted": R["scratch_deleted"],
            "bed_md5_unchanged": R["bed_md5_after"] == R["bed_md5_before"],
            "block_diagram_open": bool(R.get("block_diagram_open")),
            "refs_balanced": (R["ref_counts"] or {}).get("live", 0) == 0,
            "handles_baseline_up": bool(R.get("handles_before"))}
        R["handles_delta"] = ((R["handles_after"] - R["handles_before"])
                              if R.get("handles_before") and R.get("handles_after") else None)
        R["handles_advisory"] = (None if R["handles_delta"] is None else
                                 "within" if abs(R["handles_delta"]) <= HANDLE_TOL else "outside")   # record only
        print("HANDLES (record, not a gate): before %s after %s delta %s advisory %s (tol %d)" % (
            R.get("handles_before"), R.get("handles_after"), R["handles_delta"], R["handles_advisory"],
            HANDLE_TOL), flush=True)
        read_ok = all(R["gates"].values())
        verdict = ("OK" if not (R["extra"] or R["missing"]) else "MISMATCH") if read_ok else "FAIL"
        if verdict == "MISMATCH":
            # card chat-S2 (PD327, user 2026-10-03): per-class exactness stays STOP for every class EXCEPT loose ends; a
            # mismatch made only of loose-end items within max(5, 25 %) is LOG-only (gate_soft_log.jsonl), verdict OK
            import gateclass as _GC
            ev, erule = _GC.errorlist_verdict(R["extra"], R["missing"])
            if ev == "log":
                R["soft"] = erule
                _GC.soft_record("EL-LOOSE " + os.path.basename(bed), "LooseEnds", R["missing"], R["extra"], erule)
                print("SOFT  Error List loose-end mismatch is LOG-only: %s" % erule, flush=True)
                verdict = "OK"
            else:
                bv, brule, bdet = by_design(R, expected, plan)
                R["by_design"] = {"verdict": bv, "rule": brule, "detail": bdet}
                if bv == "log":
                    R["soft"] = brule
                    print("SOFT  Error List by-design difference, prediction re-derived: %s" % brule, flush=True)
                    verdict = "OK"
                else:
                    print("BY-DESIGN check: STOP - %s" % brule, flush=True)
    R["verdict"], R["seconds"] = verdict, round(time.time() - t0, 1)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False, default=str)
    print("items %s / window N %s ; show-error fronted %s ; extra %s ; missing %s ; errors %s ; handles %s -> %s ; "
          "bed md5 unchanged %s ; %.1f s" % (R.get("item_count"), R.get("n_reported"), R.get("show_error_ok"),
                                             len(R.get("extra") or []), len(R.get("missing") or []), R["errors"],
                                             R.get("handles_before"), R.get("handles_after"),
                                             R.get("bed_md5_after") == R.get("bed_md5_before"), R["seconds"]),
          flush=True)
    try:
        import protocol
        gates = R.get("gates") or {"bed_exists": False}
        fails = [k for k, v in gates.items() if not v]
        print(protocol.result_line(protocol.make_result(
            len(gates) - len(fails), len(fails), fails[0] if fails else None,
            [{"path": protocol._rel(out), "md5": md5(out)}],
            status="PASS" if verdict in ("OK", "MISMATCH") else "FAIL")), flush=True)
    except Exception as e:                                                         # noqa: BLE001
        print("RESULT-LINE ERROR %s: %s" % (type(e).__name__, e), flush=True)
    print("ERRORLIST-VERDICT: %s %s" % (verdict, out), flush=True)
    return {"OK": 0, "MISMATCH": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
