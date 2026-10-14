# ---
# labview: read
# hardware: camera
# offline-args: --mock
# ---
r"""p64_abba - the P6-4 leg sequencer (plan sections 2-3; base: tools/bench/diag_c104_abba.py, which is NOT edited). Order of letters
A (original's copy) / B (product copy) / O (OBS copy, plan 6.2), e.g. `--order ABBAO` (90 Hz day) or `--order B --run-s 60` (smoke S0).
Slot loop = drive_legguard.leg_loop (rerun-once; a refused leg or an A leg failing before pick 1 ends the loop). Per leg:
  leg-start checks (any one -> the leg is REFUSED: row rc REFUSED + reasons, the leg script NOT launched, the loop ends):
    stop   tools/bench/lean_bench/STOP exists          session  tools/bench/motor_session.json missing
    rig    STATUS rig-state != 조립 (motor_gate.rig_state)   pin  md5(src) != the pinned md5
    (a)    a LabVIEW process exists (every arm; diag_c104_abba.py:122 only recorded it - here it refuses)
    (b)    O only: <obs dir>\getbuff_first.txt exists   (c) O only: the pick log (BOBS90's PickLog default path) exists
    VISA   drive_legguard.visa_precheck of Rotor + ASRL5 (as diag_c104_abba.py:123-133)
  launch `p64_leg.py` (the unchanged leg script in a child; M8_RUN_ROOT / M8_OUT_DIR as p6fix_legs.py:46)
  after  m8_legs.wait_lv_gone (wait, then taskkill; gate T6 "LabVIEW gone after", diag_c104_abba.py:147-149); md5 unchanged;
         m8_legs.keep_leg_files; O only: the wrapper file and the pick log are MOVED (never deleted) into THIS leg's folder, then
         p64_own.py's check runs on them (NOT RUN when the wrapper file does not hold exactly 1 line - never PASS).
  gates  the leg's own (p64_leg L*), T1 rc 0, T5 measured fps within 15 % of --hz, T6, P2 md5; O: OWN verdict == PASS.
End: p64_sum.abba_summary (lost = column-0 gaps, both arms; the 9.1 criterion as a FACT) -> <out root>\p64_abba.json.
    py -u tools/bench/lean_bench/p64_abba.py --a-src <vi> --a-md5 <m> --b-src <vi> --b-md5 <m> [--o-src <vi> --o-md5 <m>]
          --hz 90 --run-s 120 --order ABBAO [--fracs-json <beadmap json>] --live          (rig day only; bgrun --material)
    ... same without --live = --dry: pins read, the leg-start checks evaluated on TODAY's disk, nothing launched
    py tools/bench/lean_bench/p64_abba.py --mock      (stubs + TEMP stand-ins; section 1.4 of lean_report_p64p3.md)
    py tools/bench/lean_bench/p64_abba.py --move-stale --to <leg folder> [--obs-dir <d>] [--picklog <f>]   (explicit move, never delete)"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, drive_legguard as LG, m8_legs as M8L, motor_gate as MG, p64_sum as PS, p64_own as OWN   # noqa: E401,E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
REAL = {"obs_dir": os.path.join(CD, "bench", "lean", "obs"), "picklog": os.path.join(HERE, "out_latest2", "picklog_w100.txt"),
        "stop": os.path.join(HERE, "STOP"), "session": os.path.join(BENCH, "motor_session.json")}
GB_NAME = "getbuff_first.txt"
LEG_PY = os.path.join(HERE, "p64_leg.py")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def lines_of(p):
    return sum(1 for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()) if os.path.isfile(p) else None


def real_hooks(log):
    return {"lv": LG.lv_running, "kill": LG.kill_labview, "rig": lambda: MG.rig_state(MG.read_status()),
            "precheck": lambda: LG.visa_precheck(dry=False, log=lambda s: log("  " + s)), "launch": launch_leg, "wait_s": 90}


def launch_leg(argv, out, env):
    """The real leg: p64_leg.py in a child process (its own child runs diag_c104_leg.py). Returns rc."""
    r = subprocess.run([sys.executable, "-u", LEG_PY] + argv, capture_output=True, text=True, errors="replace", timeout=22 * 60, env=env)
    open(os.path.join(out, "p64_leg_stdout.log"), "w", encoding="utf-8").write((r.stdout or "") + (r.stderr or ""))
    for ln in (r.stdout or "").splitlines():
        if ln.startswith(("GATE ", "RESULT ", "FACTS ")):
            print("  " + ln[:600], flush=True)
    return r.returncode


def start_checks(cfg, arm, src, pin):
    """The leg-start refusals; returns the list of reasons (empty = the leg may start). Reads the disk, never changes it."""
    H, why = cfg["hooks"], []
    if os.path.exists(cfg["stop"]):
        why.append("stop: STOP file exists (%s)" % cfg["stop"])
    if not os.path.isfile(cfg["session"]):
        why.append("session: motor_session.json missing (%s)" % cfg["session"])
    rs = H["rig"]()
    if rs != "assembled":
        why.append("rig: rig-state is %r, not 조립" % rs)
    m = md5(src)
    if m != pin:
        why.append("pin: md5(%s) = %s != %s" % (os.path.basename(src), m, pin))
    if H["lv"]():
        why.append("(a) a LabVIEW process exists before the leg")
    if arm == "O":
        gb = os.path.join(cfg["obs_dir"], GB_NAME)
        if os.path.exists(gb):
            why.append("(b) %s exists (%s lines) - a stale start value would be read as this leg's" % (gb, lines_of(gb)))
        if os.path.exists(cfg["picklog"]):
            why.append("(c) the pick log %s exists (%s lines) - not moved aside into its own leg's folder" % (cfg["picklog"], lines_of(cfg["picklog"])))
    return why


_nx = os.path.join(HERE, "no_such_file_p64")                                             # self-check: LabVIEW listed + a pick log present
assert [w[:3] for w in start_checks({"stop": _nx, "session": __file__, "obs_dir": _nx, "picklog": __file__,
                                     "hooks": {"rig": lambda: "assembled", "lv": lambda: True}}, "O", __file__, md5(__file__))] == ["(a)", "(c)"]


def move_obs_files(cfg, out):
    """After an O leg: move the wrapper file and the pick log into the leg's folder (never delete). Returns {name: {from, lines, md5}}."""
    moved = {}
    for src, name in ((os.path.join(cfg["obs_dir"], GB_NAME), GB_NAME), (cfg["picklog"], "picklog.txt")):
        if os.path.exists(src):
            dst = os.path.join(out, name)
            assert not os.path.exists(dst), "refusing to overwrite %s" % dst
            m0, n0 = md5(src), lines_of(src)
            shutil.move(src, dst)
            moved[name] = {"from": src, "lines": n0, "md5": m0, "md5_after": md5(dst), "src_gone": not os.path.exists(src)}
    return moved


def run_abba(cfg, log=print):
    """The slot loop. cfg: order [(arm, src, pin)], hz, run_s, picks, fracs, out_root, obs_dir, picklog, stop, session, hooks.
    Returns (gates, rows, finals, loop_stop, summary)."""
    H, G, rows = cfg["hooks"], {}, []
    legdir = os.path.join(cfg["out_root"], "legs"); os.makedirs(legdir, exist_ok=True)   # noqa: E702
    os.environ["M8_RUN_ROOT"], os.environ["M8_OUT_DIR"] = os.path.join(cfg["out_root"], "run"), os.path.join(cfg["out_root"], "m8json")   # p6fix_legs.py:46
    env = dict(os.environ)
    pins = {(a, s): p for a, s, p in cfg["order"]}

    def run_leg(slot, arm, src, attempt, npick):
        tag = "leg%d %s%s" % (slot, arm, "" if attempt == 1 else " rerun")
        out = os.path.join(legdir, "leg%d_%s_a%d" % (slot, arm, attempt)); os.makedirs(out, exist_ok=True)   # noqa: E702
        why = start_checks(cfg, arm, src, pins[(arm, src)])
        pc = None
        if not why:
            pc = H["precheck"]()
            if not pc.get("ok"):
                why.append("VISA precheck refused: %s" % ([(t.get("name"), t.get("hex")) for t in pc.get("trials") or []] or pc.get("why")))
        G["Q %s leg-start checks clear" % tag] = not why
        if why:
            row = {"leg": tag, "arm": arm, "slot": slot, "attempt": attempt, "rc": "REFUSED", "refused": True, "reasons": why, "launched": False,
                   "registered_ok": False, "picks_clicked": 0, "picks_registered_tra": None, "dir": out}
            log("=== LEG %s REFUSED: %s; leg script NOT launched" % (tag, why))
            rows.append(row); return row                                                  # noqa: E702
        t0 = time.time()
        argv = ["--src", src, "--picks", str(npick), "--run-s", str(cfg["run_s"]), "--hz", str(cfg["hz"]), "--out", out]
        argv += ["--fracs-json", cfg["fracs"]] if cfg.get("fracs") else []
        log("=== LEG %s start (%s)" % (tag, os.path.basename(src)))
        rc = H["launch"](argv, out, env)
        G["T6 %s LabVIEW gone after" % tag] = M8L.wait_lv_gone(log, H["lv"], H["kill"], H["wait_s"])
        G["P2 %s md5 unchanged by the leg" % tag] = md5(src) == pins[(arm, src)]
        kept = M8L.keep_leg_files(out, npick, cfg["run_s"], t0, log)
        j = json.load(open(os.path.join(out, "p64_leg.json"), encoding="utf-8")) if os.path.isfile(os.path.join(out, "p64_leg.json")) else {}
        F, LGt = j.get("facts") or {}, j.get("gates") or {}
        row = {"leg": tag, "arm": arm, "slot": slot, "attempt": attempt, "rc": rc, "refused": False, "launched": True, "dir": out, "kept": kept,
               "secs": round(time.time() - t0), "picks_registered_tra": F.get("picks_registered_tra"), "picks_clicked": F.get("picks_clicked"),
               "registered_ok": F.get("picks_registered_tra") == npick, "lost_col0": F.get("lost_col0"), "lost_indicator": F.get("lost_indicator"),
               "rows": F.get("rows"), "measured_hz": F.get("measured_hz"), "frame_at_stop": F.get("frame_at_stop"), "run_dir": F.get("run_dir"),
               "leg_gates": LGt}
        G["T1 %s rc 0" % tag] = rc == 0
        G["L %s leg gates (p64_leg) all pass" % tag] = bool(LGt) and all(LGt.values())
        G["T5 %s fps within 15%% of %s Hz" % (tag, cfg["hz"])] = isinstance(row["measured_hz"], (int, float)) and abs(row["measured_hz"] - cfg["hz"]) <= 0.15 * cfg["hz"]
        if arm == "O":
            row["moved"] = mv = move_obs_files(cfg, out)
            G["O %s wrapper file + pick log moved into the leg folder" % tag] = all(v["src_gone"] and v["md5"] == v["md5_after"] for v in mv.values()) \
                and not os.path.exists(os.path.join(cfg["obs_dir"], GB_NAME)) and not os.path.exists(cfg["picklog"])
            if row["run_dir"]:
                own = OWN.run(os.path.join(out, GB_NAME), os.path.join(out, "picklog.txt"), row["run_dir"], os.path.join(out, "leg.json"))
            else:
                own = {"verdict": "NOT RUN", "why": "no run dir from the leg"}
            row["own"] = {k: own.get(k) for k in ("verdict", "why", "wrapper_lines", "S", "R", "R_minus_S", "step2", "step3", "step4", "end_lag")}
            json.dump(own, open(os.path.join(out, "p64_own.json"), "w", encoding="utf-8"), indent=1, default=str)
            G["OWN %s acceptance #1 live half (plan 6.3): %s" % (tag, own["verdict"])] = own["verdict"] == "PASS"
        log("ROW " + json.dumps({k: v for k, v in row.items() if k not in ("leg_gates", "kept")}, default=str)[:1500])
        rows.append(row)
        return row

    order = [(a, s, False, cfg["picks"]) for a, s, _ in cfg["order"]]
    finals, stop = LG.leg_loop(order, run_leg, log=log)
    if stop and finals and finals[-1][3].get("reasons"):                                  # leg_loop words every refusal as VISA's
        stop["reason"] = "leg refused: %s" % "; ".join(finals[-1][3]["reasons"])
    for slot, arm, npk, row in finals:
        G["T12 slot%d %s registered == %d (<= 1 rerun)" % (slot, arm, npk)] = bool(row.get("registered_ok"))
    if stop:
        G["T17 leg loop ran every slot (stopped: %s)" % stop["reason"]] = False
    summ = PS.abba_summary([r for _, _, _, r in finals])
    return G, rows, finals, stop, summ


def move_stale(obs_dir, picklog, to):
    """Explicit rig-day step: move a stale wrapper file / pick log into `to` (their own leg's folder). Never deletes."""
    os.makedirs(to, exist_ok=True)
    return move_obs_files({"obs_dir": obs_dir, "picklog": picklog}, to)


# ------------------------------------------------------------------ mock (no LabVIEW, no port, no camera, TEMP stand-ins only)
REC = {"A": os.path.join(HERE, "out_p6close", "run", "replay_s1_20261014_043654"), "B": os.path.join(HERE, "out_p6close", "run", "replay_s1_20261014_040041"),
       "O": OWN.OBS_RUN}


def mock_cfg(tmp, order="O", hz=90.0):
    sd = {k: os.path.join(tmp, "standin_" + k) for k in ("obs_dir", "picklog", "stop", "session")}
    sd["picklog"] += ".txt"
    os.makedirs(sd["obs_dir"], exist_ok=True)
    open(sd["session"], "w").write("{}")
    for k, v in sd.items():
        assert os.path.normcase(os.path.abspath(v)) != os.path.normcase(REAL[k]), "mock must never use the real %s" % k
    vis = {}
    for a in "ABO":
        p = os.path.join(tmp, "vi_%s.vi" % a); open(p, "wb").write(("stub VI %s" % a).encode()); vis[a] = (p, md5(p))   # noqa: E702
    calls = {"launch": 0, "kill": 0}
    st = {"lv": False, "lv_after_leg": False}

    def launch(argv, out, env):
        calls["launch"] += 1
        arm = os.path.basename(out).split("_")[1]
        rs = PS.run_sum(REC[arm], 15)
        fd = int(hz * float(argv[argv.index("--run-s") + 1]))
        facts = {"run_dir": REC[arm], "lost_col0": rs["lost"], "rows": rs["rows"], "lost_indicator": "0", "frames_delta": fd, "measured_hz": round(fd / float(argv[argv.index("--run-s") + 1]), 2),
                 "picks_registered_tra": 15.0, "picks_clicked": 15, "frame_at_stop": 23439 if arm == "O" else None}
        json.dump({"gates": {"L stub": True}, "facts": facts}, open(os.path.join(out, "p64_leg.json"), "w"), indent=1)
        if arm == "O":                                                                    # what BOBS90 writes during its leg
            shutil.copyfile(OWN.OBS_LEG, os.path.join(out, "leg.json"))
            open(os.path.join(sd["obs_dir"], GB_NAME), "w").write("20896\t20896\t142998000\n")
            shutil.copyfile(OWN.OBS_LOG, sd["picklog"])
        st["lv"] = st["lv_after_leg"]
        return 0

    def kill(wait_s=20.0):
        calls["kill"] += 1; st["lv"] = False                                              # noqa: E702
        return True, 0.0
    hooks = {"lv": lambda: st["lv"], "kill": kill, "rig": lambda: "assembled", "precheck": lambda: {"ok": True, "dry": True},
             "launch": launch, "wait_s": 0}
    cfg = dict(sd, hooks=hooks, hz=hz, run_s=120, picks=15, fracs=None, out_root=os.path.join(tmp, "out"),
               order=[(a, vis[a][0], vis[a][1]) for a in order])
    return cfg, calls, st


def mock():
    G, res = {}, {}
    quiet = lambda s: None                                                                # noqa: E731

    def case(name, order, prep=None, want_refused=None, check=None):
        tmp = tempfile.mkdtemp(prefix="p64abba_mock_")
        try:
            cfg, calls, st = mock_cfg(tmp, order)
            planted = prep(cfg, st) if prep else []
            g, rows, finals, stop, summ = run_abba(cfg, log=quiet)
            ref = [r for r in rows if r.get("refused")]
            res[name] = {"launches": calls["launch"], "kills": calls["kill"], "refused": [(r["leg"], r["reasons"]) for r in ref],
                         "summary": summ, "own": [r.get("own", {}).get("verdict") for r in rows if r["arm"] == "O" and not r.get("refused")],
                         "moved": [{k: (v["lines"], v["src_gone"]) for k, v in (r.get("moved") or {}).items()} for r in rows if r.get("moved") is not None],
                         "planted_still_there": [os.path.exists(p) for p in planted], "gates_failing": [k for k, v in g.items() if not v]}
            print("CASE %-34s %s" % (name, json.dumps(res[name], default=str)[:900]), flush=True)
            ok = True
            if want_refused is not None:
                ok &= calls["launch"] == 0 and len(ref) == 1 and any(r.startswith(want_refused) for r in ref[0]["reasons"]) and all(res[name]["planted_still_there"])
            if check:
                ok &= check(res[name], g, rows)
            G["M %s" % name] = bool(ok)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def plant(path_key, text):
        def f(cfg, st):
            p = os.path.join(cfg["obs_dir"], GB_NAME) if path_key == "gb" else cfg[path_key]
            open(p, "w").write(text); return [p]                                          # noqa: E702
        return f
    clean = lambda r, g, rows: (r["launches"] == 1 and not r["refused"] and r["own"] == ["PASS"] and r["moved"] == [{GB_NAME: (1, True), "picklog.txt": (1475, True)}]
                                and not r["gates_failing"])
    case("clean OBS leg", "O", check=clean)
    case("(a) LabVIEW present before O", "O", prep=lambda cfg, st: st.update(lv=True) or [], want_refused="(a)")
    case("(a) LabVIEW present before A", "A", prep=lambda cfg, st: st.update(lv=True) or [], want_refused="(a)")
    case("(b) planted getbuff_first.txt", "O", prep=plant("gb", "8217\t8217\t1\n"), want_refused="(b)")
    case("(c) planted stale pick log", "O", prep=plant("picklog", "20896\t1\n"), want_refused="(c)")
    case("STOP file present", "A", prep=plant("stop", "stop"), want_refused="stop")
    case("session file missing", "B", prep=lambda cfg, st: os.remove(cfg["session"]) or [], want_refused="session")
    case("LabVIEW listed after the leg -> kill", "A", prep=lambda cfg, st: st.update(lv_after_leg=True) or [],
         check=lambda r, g, rows: r["kills"] == 1 and all(v for k, v in g.items() if k.startswith("T6 ")) and not r["gates_failing"])
    case("full A B B A O", "ABBAO", check=lambda r, g, rows: (r["launches"] == 5 and not r["refused"] and r["summary"]["lost_by_arm"] == {"A": [1068, 1068], "B": [0, 0]}
                                                               and r["summary"]["met"] is True and r["own"] == ["PASS"] and not r["gates_failing"]))
    tmp = tempfile.mkdtemp(prefix="p64abba_mock_")
    try:
        cfg, _c, _s = mock_cfg(tmp)
        gb, pl = os.path.join(cfg["obs_dir"], GB_NAME), cfg["picklog"]
        open(gb, "w").write("1\t1\t1\n"); shutil.copyfile(OWN.OBS_LOG, pl)                  # noqa: E702
        m0 = (md5(gb), md5(pl))
        mv = move_stale(cfg["obs_dir"], pl, os.path.join(tmp, "W100OBS_a1"))
        res["move-stale"] = mv
        print("CASE %-34s %s" % ("--move-stale on stand-ins", json.dumps(mv)[:600]), flush=True)
        G["M --move-stale: both moved, md5 equal, sources gone"] = (mv[GB_NAME]["md5_after"] == m0[0] and mv["picklog.txt"]["md5_after"] == m0[1]
                                                                    and mv[GB_NAME]["src_gone"] and mv["picklog.txt"]["src_gone"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    G["M real paths untouched: obs dir has no %s" % GB_NAME] = not os.path.exists(os.path.join(REAL["obs_dir"], GB_NAME))
    return G, res


def main(av):
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    if "--mock" in av:
        G, res = mock()
        jp = None
    elif "--move-stale" in av:
        mv = move_stale(arg("--obs-dir", REAL["obs_dir"]), arg("--picklog", REAL["picklog"]), arg("--to"))
        print(json.dumps(mv, indent=1))
        G = {"S moved %s" % k: v["src_gone"] and v["md5"] == v["md5_after"] for k, v in mv.items()} or {"S nothing to move": True}
        jp = None
    else:
        hz, run_s, live = float(arg("--hz", 90)), float(arg("--run-s", 120)), "--live" in av
        src = {"A": (arg("--a-src"), arg("--a-md5")), "B": (arg("--b-src"), arg("--b-md5")), "O": (arg("--o-src"), arg("--o-md5"))}
        order = [(a, os.path.normpath(src[a][0]), src[a][1]) for a in arg("--order", "ABBAO")]
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_root = arg("--out-root", os.path.join(HERE, "out_p64", "abba_%d_%s%s" % (int(hz), ts, "" if live else "_dry")))
        log = lambda s: print(s, flush=True)                                              # noqa: E731
        cfg = dict(REAL, hooks=real_hooks(log), hz=hz, run_s=run_s, picks=int(arg("--picks", 15)), fracs=arg("--fracs-json"),
                   out_root=out_root, order=order)
        if not live:                                                                      # --dry: read the disk, launch nothing
            G = {}
            for slot, (a, s, p) in enumerate(order, 1):
                why = start_checks(cfg, a, s, p)
                print("DRY slot %d %s %s md5=%s pin=%s -> %s" % (slot, a, os.path.basename(s), md5(s), p, "WOULD BE REFUSED: %s" % why if why else "would start"), flush=True)
                G["D slot%d %s pin read" % (slot, a)] = md5(s) is not None
            print("DRY nothing launched; real paths: %s" % json.dumps(REAL), flush=True)
            jp = None
        else:
            G, rows, finals, stop, summ = run_abba(cfg, log)
            os.makedirs(out_root, exist_ok=True)
            jp = os.path.join(out_root, "p64_abba.json")
            json.dump({"schema": "p64-abba/1", "hz": hz, "run_s": run_s, "order": order, "rows": rows, "gates": G, "loop_stop": stop,
                       "summary": summ, "lv_running_at_end": LG.lv_running()}, open(jp, "w", encoding="utf-8"), indent=1, default=str)
            print("SUMMARY %s" % json.dumps(summ), flush=True)
    for k, v in G.items():
        print("GATE %-80s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}] if jp else [])), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
