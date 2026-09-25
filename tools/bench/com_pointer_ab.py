r"""com_pointer_ab - the A/B COM pointer test owed by archive/peer/2026-09-25-chat-E1r-pointer-release.md (card chat-E2).

Separates two explanations of the chat-E1 r1 cold-start failure (ClassFactory, then RPC_E_SERVER_DIED 0x80010007):
  (a) CLAIM: a LabVIEW launched by a COM Dispatch exits when its last Application pointer is released;
  (b) ALTERNATIVE: a SECOND Dispatch during a cold launch reaches a second or tearing-down instance.
ARM A: cold start, one Dispatch + Version, log processes; release the pointer (+gc), poll the LabVIEW PIDs every 1 s
       for 30 s; re-Dispatch + Version; log processes.   (a) predicts the PID vanishes and the re-Dispatch is a new PID.
ARM B: cold start, Dispatch P1 + Version, hold it; Dispatch P2 at once + Version; log processes; P1.Version again.
       (b) predicts an error or a second PID in B.
COM only: no VI opened, no GUI, no hardware. LabVIEW is killed before each arm and at the end (restart authority).
WHAT EXISTS: no prior script does this (`ls tools/bench | grep -i -E "com_|dispatch|pointer"` -> none);
bench_prep.restart_labview kills; gscript.lv() is the one-Dispatch pattern this test reproduces by hand.
PREDICTION CONTRACT (structural): both arms complete; every step logs PIDs + CreationDate; the verdict line names
which of (a)/(b) the observations support (both, neither, or one). The OUTCOME is not predicted - it is measured.
"""
import gc, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol                                                                    # noqa: E402
from win32com.client import dynamic                                                # noqa: E402

OUT = os.path.join(HERE, "com_pointer_ab_20260925.json")
R = {"arms": {}, "gates": {}}


def procs():
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='LabVIEW.exe'\" | ForEach-Object { "
          "'{0}|{1}|{2}' -f $_.ProcessId, $_.CreationDate.ToString('HH:mm:ss.fff'), $_.CommandLine }")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    out = []
    for ln in r.stdout.strip().splitlines():
        p = ln.split("|", 2)
        if len(p) == 3:
            out.append({"pid": int(p[0]), "start": p[1], "cmd": p[2].strip()[:160]})
    return out


def kill_all():
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
    t0 = time.time()
    while procs() and time.time() - t0 < 20:
        time.sleep(1)
    return not procs()


def log(arm, step, **kw):
    kw.update(step=step, t=time.strftime("%H:%M:%S"), procs=procs())
    R["arms"].setdefault(arm, []).append(kw)
    print("%s %-14s %s" % (arm, step, json.dumps(kw, default=str)), flush=True)
    return kw


def version(p):
    t0 = time.time()
    try:
        return str(p.Version), round(time.time() - t0, 1), None
    except Exception as e:                                                         # noqa: BLE001
        return None, round(time.time() - t0, 1), repr(e)[:200]


def dispatch_version(deadline=60):
    t0, tries, last = time.time(), 0, None
    while time.time() - t0 < deadline:
        tries += 1
        try:
            p = dynamic.Dispatch("LabVIEW.Application")
            v, _s, err = version(p)
            if v:
                return p, v, round(time.time() - t0, 1), tries, None
            last = err
        except Exception as e:                                                     # noqa: BLE001
            last = repr(e)[:200]
        time.sleep(2)
    return None, None, round(time.time() - t0, 1), tries, last


# ---- ARM A: release the only pointer, watch the PID, re-Dispatch
R["gates"]["A0_cold"] = kill_all()
p, v, s, n, err = dispatch_version()
a1 = log("A", "dispatch1", version=v, s=s, tries=n, err=err)
R["gates"]["A1_version"] = bool(v)
pid0 = {x["pid"] for x in a1["procs"]}
del p
gc.collect()
t0, gone_at, seen = time.time(), None, []
while time.time() - t0 < 30:
    cur = {x["pid"] for x in procs()}
    seen.append([round(time.time() - t0, 1), sorted(cur)])
    if gone_at is None and pid0 and not (pid0 & cur):
        gone_at = round(time.time() - t0, 1)
    time.sleep(1)
log("A", "after_release", gone_at_s=gone_at, poll=seen[::5])
R["gates"]["A2_polled_30s"] = len(seen) >= 20
p, v, s, n, err = dispatch_version()
a3 = log("A", "redispatch", version=v, s=s, tries=n, err=err)
R["gates"]["A3_redispatch_answered"] = bool(v)
pid1 = {x["pid"] for x in a3["procs"]}
R["A_pid_vanished_after_release"] = gone_at is not None
R["A_redispatch_new_pid"] = bool(pid1) and not (pid0 & pid1)
del p
gc.collect()

# ---- ARM B: hold P1, second Dispatch P2 during the cold launch
R["gates"]["B0_cold"] = kill_all()
p1, v1, s1, n1, e1 = dispatch_version()
b1 = log("B", "dispatch1", version=v1, s=s1, tries=n1, err=e1)
R["gates"]["B1_version"] = bool(v1)
t2 = time.time()
try:
    p2 = dynamic.Dispatch("LabVIEW.Application")
    e2 = None
except Exception as e:                                                             # noqa: BLE001
    p2, e2 = None, repr(e)[:200]
v2, s2, e2v = version(p2) if p2 is not None else (None, None, None)
b2 = log("B", "dispatch2_held", version=v2, s=round(time.time() - t2, 1), err=e2 or e2v)
time.sleep(5)
v1b, _s, e1b = version(p1) if p1 is not None else (None, None, "no p1")
b3 = log("B", "p1_again_+5s", version=v1b, err=e1b)
R["gates"]["B2_second_dispatch_ran"] = True
R["B_second_dispatch_error"] = bool(e2 or e2v)
R["B_second_pid"] = len({x["pid"] for x in b2["procs"] + b3["procs"]}) > 1
R["B_p1_still_answers"] = bool(v1b)
del p1, p2
gc.collect()
R["gates"]["Z_killed_at_end"] = kill_all()

a_sup = R["A_pid_vanished_after_release"]
b_sup = R["B_second_dispatch_error"] or R["B_second_pid"]
R["verdict"] = {"claim_a_exit_on_release": a_sup, "alt_b_second_dispatch": b_sup,
                "reading": ("a" if a_sup and not b_sup else "b" if b_sup and not a_sup else
                            "both" if a_sup and b_sup else "neither")}
print("VERDICT %s" % json.dumps(R["verdict"]), flush=True)
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
fails = [k for k, v in R["gates"].items() if not v]
import hashlib                                                                     # noqa: E402
print(protocol.result_line(protocol.make_result(
    len(R["gates"]) - len(fails), len(fails), fails[0] if fails else None,
    [{"path": protocol._rel(OUT), "md5": hashlib.md5(open(OUT, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if fails else 0)
