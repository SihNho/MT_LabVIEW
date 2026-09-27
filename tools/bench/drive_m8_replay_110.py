r"""drive_m8_replay_110 - card 110-6 R3+R4 (PD210(c), PD217(f); m8 plan PD22(d)/PD23): the rule-1a replay of the display-loop VI.
Two legs, each in its OWN LabVIEW launch (PD17(b')), on the SAME recorded frames (the swapped stand-ins serve f(k mod 10044)):
  leg A = claudeDev\replay\D1_s1_replay_20260925_075422.vi (S1's swap copy, md5 126f8497..., REUSED as plan 95 did)
  leg B = the swap copy that stage_replay_swap.py --plan 110 saved (argv --disp <path>, md5 read from its stage json)
FOUND FIRST (nothing new is built): diag_c104_leg.py = the ABBA's 15-pick leg (drive_m8 --leg replay_s1 --src <vi>, pick-1
capture release, rerun-once rule) - reused as the leg runner; drive_legguard.visa_precheck before each leg (card 106-2);
m8b_replay_compare.main/tra = the cycle-78 comparer (INDEX row 47). 15 picks, 120 s (the ABBA load, PD203(c)).
PREDICTION: P1 both sources' md5 == pins before leg 1; per leg: V1 VISA precheck 0, T1 leg rc 0 (<= 1 rerun), T2 15 picks
registered in tra, T3 LabVIEW gone after; C = m8b_replay_compare G1/G2/G3 (G3 = X/Y/Z bit-identical over the common rows);
C4 col 0 / trans / rot rows that differ REPORTED (not gated); P2 md5 unchanged after; INDEX row appended. No judgement.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/drive_m8_replay_110.log -- py -u tools/bench/drive_m8_replay_110.py --disp <vi>"""
import hashlib, json, os, subprocess, sys, time                                          # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, drive_legguard as LG, m8b_replay_compare as CMP                  # noqa: E401,E402
RP = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\replay"
A_ = sys.argv[1:]; DISP = os.path.normpath(A_[A_.index("--disp") + 1])
SJ = json.load(open(os.path.join(HERE, "stage_replay_swap_110.json"), encoding="utf-8"))
PIN = {"S1replay": (os.path.join(RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8"),
       "dispreplay": (DISP, SJ["copies"]["disp"]["md5"])}
NPICK, RUN_S, TS = 15, 120, time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "c110f_replay_%s" % TS); os.makedirs(LEGDIR, exist_ok=True)
OUT = os.path.join(HERE, "m8b_replay_110.json")
G, rows = {}, []
lv = lambda: "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()   # noqa: E731


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def leg(tag, src):
    for att in (1, 2):
        out = os.path.join(LEGDIR, "%s_a%d" % (tag, att)); os.makedirs(out, exist_ok=True)
        pc = LG.visa_precheck(dry=False, log=lambda s: print("  " + s, flush=True))
        G["V1 %s a%d VISA precheck 0" % (tag, att)] = pc["ok"]
        if not pc["ok"]:
            return None
        t = time.time()
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "diag_c104_leg.py"), "--src", src, "--picks", str(NPICK),
                            "--run-s", str(RUN_S), "--out", out], capture_output=True, text=True, errors="replace", timeout=18 * 60)
        for ln in (r.stdout or "").splitlines():
            if ln.startswith(("GATE ", "RESULT ", "REGISTERED")):
                print("  " + ln[:500], flush=True)
        t2 = time.time()
        while lv() and time.time() - t2 < 90: time.sleep(5)
        if lv(): subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5); print("  taskkill LabVIEW", flush=True)
        G["T3 %s a%d LabVIEW gone after" % (tag, att)] = not lv()
        F = (json.load(open(os.path.join(out, "leg.json"))) if os.path.isfile(os.path.join(out, "leg.json")) else {}).get("facts") or {}
        reg = F.get("picks_registered_tra")
        row = {"leg": tag, "attempt": att, "rc": r.returncode, "secs": round(time.time() - t), "run_dir": F.get("run_dir"),
               "registered": reg, "lost": F.get("lost"), "src": src, "source_md5": F.get("source_md5"), "v5_failing": F.get("v5_failing"), "dir": out}
        rows.append(row); print("ROW " + json.dumps(row, default=str), flush=True)
        if row["run_dir"] and reg == NPICK:
            G["T1 %s rc 0" % tag] = r.returncode == 0; G["T2 %s %d picks registered" % (tag, NPICK)] = True
            return row["run_dir"]
    G["T2 %s %d picks registered" % (tag, NPICK)] = False
    return None


mb = {k: md5(p) for k, (p, _m) in PIN.items()}; print("MD5 BEFORE %s" % mb, flush=True)
G["P1 S1 replay copy + disp replay copy md5 == pins before leg 1"] = all(mb[k] == m for k, (_p, m) in PIN.items())
rdA = rdB = None
if G["P1 S1 replay copy + disp replay copy md5 == pins before leg 1"] and not lv():
    rdA = leg("A_S1replay", PIN["S1replay"][0])
    rdB = leg("B_dispreplay", DISP) if rdA else None
R = {}
if rdA and rdB:
    CMP.main(rdA, rdB, OUT); R = json.load(open(OUT))
    for k, v in R.get("gates", {}).items(): G["C " + k] = v
    (_i1, t1), (_i2, t2) = CMP.tra(rdA), CMP.tra(rdB); n = min(len(t1), len(t2))
    R["per_column_rows_differ"] = [int(np.sum(t1[:n, c].view("u8") != t2[:n, c].view("u8"))) for c in range(t1.shape[1])]
    R["max_abs_diff_per_column"] = [float(np.nanmax(np.abs(t1[:n, c] - t2[:n, c]))) for c in range(t1.shape[1])]
    R["cols_note"] = "col 0 time/frame, 1 trans, 2 rot, then 15 beads x (x,y,z)"
    print("C4 per-column rows differ %s" % R["per_column_rows_differ"], flush=True)
ma = {k: md5(p) for k, (p, _m) in PIN.items()}
G["P2 md5 after == before"] = ma == mb
G["H LabVIEW gone at end"] = not lv()
R.update({"card": "110-7", "legs": rows, "pins": {k: [p, m] for k, (p, m) in PIN.items()}, "md5_before": mb, "md5_after": ma,
          "wrapper_gates": G, "npicks": NPICK, "run_s": RUN_S, "legdir": os.path.relpath(LEGDIR, ROOT), "judgement_not_applied": "PD210(c)/217(f)"})
json.dump(R, open(OUT, "w"), indent=1, default=str)
if rdA and rdB:
    ix = os.path.join(ROOT, "archive", "benchmarks", "INDEX.md"); txt = open(ix, encoding="utf-8").read()
    n = int([ln for ln in txt.splitlines() if ln.startswith("| ")][-1].split("|")[1]) + 1
    line = ("| %d | %s | **Card 110-7 (110-6 route; PD210(c)/217(f)) rule-1a replay of the display-loop VI: same recorded frames through S1's swap copy "
            "(`replay\\D1_s1_replay_20260925_075422.vi`) and the disp swap copy (`%s`), 15 picks, %d s, own LabVIEW each.** "
            "`tools/bench/drive_m8_replay_110.py` -> diag_c104_leg.py -> m8b_replay_compare | env as row 47; picks 15 | rows A %s / B %s, common %s, "
            "X/Y/Z rows not bit-identical %s, max abs diff X/Y/Z %s, per-column rows differ %s. Level: FUNCTIONAL (replay), 2 runs | "
            "`tools/bench/m8b_replay_110.json`, legs `%s/` |" % (n, time.strftime("%Y-%m-%d"), os.path.basename(DISP), RUN_S, R.get("rows_s1"),
                                                             R.get("rows_s3"), R.get("common"), R.get("rows_xyz_not_bit_identical"),
                                                             R.get("max_abs_diff_xyz"), R.get("per_column_rows_differ"),
                                                             os.path.relpath(LEGDIR, ROOT).replace("\\", "/")))
    open(ix, "a", encoding="utf-8").write(("" if txt.endswith("\n") else "\n") + line + "\n")
    G["I INDEX row %d appended" % n] = line in open(ix, encoding="utf-8").read()
    json.dump(R, open(OUT, "w"), indent=1, default=str)
for k, v in G.items(): print("GATE %-60s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
sys.exit(1 if bad else 0)
