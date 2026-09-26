r"""diag_c106b_live.py - card 106-2 L5/L6/L7: the patched ABBA entry (diag_c104_abba.py) run for real, twice, each capped at ONE leg.
FOUND FIRST: diag_c104_abba.py (the entry 104-5 used; patched this card), drive_legguard.py (precheck, dialog watch, leg loop),
selftest_leg_guard.py (offline L2-L4, run before this). Child output is echoed with a '  | ' prefix so bgrun collects only
THIS file's RESULT line (the ABBA's own RESULT is FAIL by design in both runs: it produces no numbers).
SAFETY: step S runs the precheck stand-alone first; if ASRL5 now OPENS, L5/L6 are NOT run (the ABBA would run for real).
Both ABBA runs get --max-legs 1 and LEGGUARD_TEST_STOP_AT_L2=1 (a leg that got past a missing dialog is killed at L2, no pick).
PREDICTION CONTRACT:
 S   stand-alone precheck: ASRL5::INSTR status != 0 (0xBFFF0072 expected, as 106-1)      P0 LabVIEW absent, S1 md5 3e3d23ce
 L5a ABBA real, no bypass: 1 row, refused, ASRL5 status != 0   L5b loop stop reason 'refused'   L5c labview.exe never seen
     (tasklist every 0.5 s for the whole run)   L5d no leg.json written (leg script never launched)
 L6a ABBA real, LEGGUARD_TEST_BYPASS_VISA=1: v5 dialog_watch_run1.modal present   L6b shotwin rc 0, png exists
 L6c OCR text logged (non-empty)   L6d killed <= 15 s after detection, gone   L6e ONE leg: rows == 1, stop 'A leg failed before
     pick 1'   L6f picks_clicked 0   L6g v5 step 30 'NOT started'   L6h precheck bypassed recorded (ABBA row + v5)
 L7a LabVIEW gone after L6   L7b S1 md5 unchanged   L7c env flags default off in this process after the runs
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c106b_live.log -- py -u tools/bench/diag_c106b_live.py"""
import hashlib, json, os, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
import drive_legguard as LG                                                     # noqa: E402
S1 = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"; S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
OUT = os.path.join(HERE, "diag_c106b_out"); os.makedirs(OUT, exist_ok=True)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
G, F = {}, {}
def gate(k, v, info=""):
    G[k] = bool(v); print("GATE %-66s %s %s" % (k, "PASS" if v else "FAIL", str(info)[:400]), flush=True)
def abba(tag, extra_env, max_min):
    jrel = os.path.join("tools", "bench", "diag_c106b_abba_%s.json" % tag); jp = os.path.join(ROOT, jrel)
    env = {k: v for k, v in os.environ.items() if k not in (LG.BYPASS_ENV, LG.STOP_L2_ENV)}
    env.update({LG.STOP_L2_ENV: "1", "M8_OUT_DIR": os.path.join(OUT, "m8_%s" % tag)}); env.update(extra_env)
    seen, stop = [], threading.Event()
    def mon():
        while not stop.is_set():
            if LG.lv_running(): seen.append(round(time.time() - t0, 1))
            time.sleep(0.5)
    t0 = time.time(); th = threading.Thread(target=mon, daemon=True); th.start()
    p = subprocess.Popen([sys.executable, "-u", os.path.join(HERE, "diag_c104_abba.py"), "--json", jrel, "--max-legs", "1"], cwd=ROOT, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for ln in p.stdout: print("  | " + ln.rstrip()[:700], flush=True)
    rc = p.wait(timeout=max_min * 60); stop.set(); th.join(2)
    j = json.load(open(jp)) if os.path.isfile(jp) and os.path.getmtime(jp) >= t0 else {}
    print("[c106b] ABBA %s rc=%s secs=%.0f labview_seen=%s" % (tag, rc, time.time() - t0, seen[:3]), flush=True)
    return rc, j, seen, jrel
F["lv_before"] = LG.lv_running(); F["s1_md5_before"] = md5(S1)
gate("P0 LabVIEW absent, S1 md5 3e3d23ce", not F["lv_before"] and F["s1_md5_before"] == S1_MD5, F["s1_md5_before"])
pc = LG.visa_precheck(log=lambda s: print("[c106b] " + s, flush=True)); F["standalone_precheck"] = pc
asrl = next((t for t in pc.get("trials") or [] if t["name"] == "ASRL5::INSTR"), {})
gate("S stand-alone precheck: ASRL5 status != 0", not pc["ok"] and asrl.get("status") not in (0, None), asrl.get("hex"))
if G["S stand-alone precheck: ASRL5 status != 0"] and G["P0 LabVIEW absent, S1 md5 3e3d23ce"]:
    rc, j, seen, jr5 = abba("l5", {}, 8); F["l5"] = {"rc": rc, "labview_seen": seen, "json": jr5, "stop": j.get("leg_loop_stop")}
    rows = j.get("rows") or []; r0 = rows[0] if rows else {}
    a5 = next((t for t in (r0.get("precheck") or {}).get("trials") or [] if t["name"] == "ASRL5::INSTR"), {})
    gate("L5a 1 row, refused, ASRL5 status != 0", len(rows) == 1 and r0.get("refused") and a5.get("status") not in (0, None), "%s %s" % (a5.get("hex"), a5.get("text")))
    gate("L5b leg loop stop = refused", "refused" in str((j.get("leg_loop_stop") or {}).get("reason")), j.get("leg_loop_stop"))
    gate("L5c labview.exe never seen during the L5 run", not seen, seen[:5])
    gate("L5d leg script never launched (no leg.json)", not os.path.isfile(os.path.join(ROOT, r0.get("dir") or "x", "leg.json")), r0.get("dir"))
    rc, j, seen, jr6 = abba("l6", {LG.BYPASS_ENV: "1"}, 13); F["l6"] = {"rc": rc, "json": jr6, "stop": j.get("leg_loop_stop")}
    rows = j.get("rows") or []; r0 = rows[0] if rows else {}
    vj = os.path.join(OUT, "m8_l6", "m8_v5_replay_s1_p15_r120.json"); v = json.load(open(vj)) if os.path.isfile(vj) else {}
    vf = v.get("facts") or {}; dw = vf.get("dialog_watch_run1") or {}; md = dw.get("modal") or {}
    F["l6"].update({"v5_json": os.path.relpath(vj, ROOT), "dialog_watch": {k: dw.get(k) for k in ("polls", "max_gap_s", "new_windows")}, "modal": md,
                    "steps_fail": [s["step"] for s in v.get("steps") or [] if not s["ok"]]})
    print("[c106b] L6 modal %s" % json.dumps(md, default=str)[:2500], flush=True)
    gate("L6a modal dialog seen by the watch (Run->L2)", bool(md), (md.get("win"), dw.get("max_gap_s"), dw.get("polls")))
    sw = md.get("shotwin") or {}
    gate("L6b shotwin -Hwnd rc 0, png exists", sw.get("rc") == 0 and os.path.isfile(sw.get("png") or "x"), sw.get("png"))
    tx = (md.get("ocr") or {}).get("text") or ""
    gate("L6c dialog text logged (OCR non-empty)", bool(tx.strip()), tx[:400])
    kl = md.get("kill") or {}
    gate("L6d LabVIEW killed <= 15 s after detection (no COM Abort)", kl.get("gone") and (md.get("kill_after_visible_s") or 99) <= 15.0, (md.get("kill_after_visible_s"), kl))
    gate("L6e ONE leg: rows == 1, stop 'A leg failed before pick 1'", len(rows) == 1 and "before pick 1" in str((j.get("leg_loop_stop") or {}).get("reason")), j.get("leg_loop_stop"))
    gate("L6f no pick clicked", r0.get("picks_clicked") == 0, r0.get("picks_clicked"))
    gate("L6g v5 run2 NOT started", any("30 run2" in s["step"] and "NOT started" in s["detail"] for s in v.get("steps") or []))
    gate("L6h precheck bypass recorded (ABBA row + v5)", ((r0.get("precheck") or {}).get("bypassed") is True) and ((vf.get("visa_precheck") or {}).get("bypassed") is True))
    F["lv_after"] = LG.lv_running(); gate("L7a LabVIEW gone after L6", not F["lv_after"])
F["s1_md5_after"] = md5(S1); gate("L7b S1 md5 unchanged", F["s1_md5_after"] == S1_MD5, F["s1_md5_after"])
gate("L7c test flags default off in this process", os.environ.get(LG.BYPASS_ENV) != "1" and os.environ.get(LG.STOP_L2_ENV) != "1")
jp = os.path.join(ROOT, "tools", "bench", "facts_c106b.json"); json.dump({"gates": G, "facts": F}, open(jp, "w"), indent=1, default=str)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
