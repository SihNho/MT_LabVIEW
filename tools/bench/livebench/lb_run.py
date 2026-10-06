# ---
# labview: build
# hardware: motor
# ---
r"""lb_run - livebench driver, LIVE half (card chat-B7, user 2026-10-06). Runs ONE arm for real and collects its metrics.
NOT run by card chat-B7 (build and stub-test only). Arms run ONE AT A TIME (one LabVIEW), in arms.json "order".

  run <arm>      preflight -> prepare -> before-snapshots -> the arm's runner -> after-snapshots -> lb_collect
  collect <arm>  re-collect from a finished run (livebench/<arm>_run.json)

preflight  setup_<arm>.json exists (lb_setup setup), the worktree HEAD descends from its setup commit, no LabVIEW.exe,
           no other arm marked running (livebench/RUNNING.json), the MAIN STATUS still carries its STOP line (the main
           runner stays stopped - this driver never touches the main tree, STATUS or runner).
prepare    claudeDev\bench\<arm>\ created; the start VI byte-copied there from the claudeDev root and md5-checked
           (arms.json start_vi); the main project's Claude memory copied to the worktree's project key
           (~/.claude/projects/<mangled worktree>/memory) unless --no-memory, so the arm sessions see the same memory.
runner     `py tools/bgrun.py --max-min <N> --log tools/bench/livebench_runner.log -- py -u tools/cycle_runner.py --cycles 2
           --flow <purpose|legacy>` with cwd = the worktree and the arm env (PYTHONPATH = .livebench write fence,
           LIVEBENCH_CLAUDEDEV = the arm folder). No supervisor. Motor-limit, Error List and LabVIEW-close hooks stay ON
           (cycle_runner's defaults; rig assembled, motor grant in force).
snapshots  claudeDev root listing (name, size, mtime; bench\ excluded) and the main tree (HEAD, STATUS md5, `git status
           --porcelain` md5) before and after -> livebench/<arm>_snapshots.json (the containment evidence).
collect    lb_collect.py -> livebench/<arm>.json (livebench/1; plan_progress first)."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ARMS = json.load(open(os.path.join(HERE, "arms.json"), encoding="utf-8"))
CD_ROOT, MAIN_DIR = ARMS["claudedev_root"], ARMS["main_project"]
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("GATE %s: %s%s" % (label, "PASS" if ok else "FAIL", ("  (%s)" % detail) if detail else ""), flush=True)
    return ok


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def git(*args, cwd=MAIN_DIR):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout


def mangle(path):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def labview_running():
    out = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    return "labview.exe" in out.lower()


def snap():
    cd = {}
    for dp, dns, fns in os.walk(CD_ROOT):
        if os.path.normcase(dp) == os.path.normcase(CD_ROOT):
            dns[:] = [d for d in dns if d.lower() != "bench"]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            cd[os.path.relpath(p, CD_ROOT)] = [st.st_size, int(st.st_mtime)]
    porc = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=MAIN_DIR, capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout
    lines = porc.splitlines()
    for i, ln in enumerate(lines):          # a MODIFIED file that changes again keeps its porcelain line: add its mtime
        p = os.path.join(MAIN_DIR, ln[3:].strip().strip('"'))
        try:
            lines[i] = "%s\t%d" % (ln, int(os.path.getmtime(p)))
        except OSError:
            pass
    return {"claudedev": cd, "main": {"head": git("rev-parse", "HEAD").strip(), "porcelain": lines}}


def fence_paths(wt, t0):
    """Main-tree paths a worktree fence logged (Python open/copy or shell) since t0."""
    out = []
    p = os.path.join(wt, "tools", "bench", "livebench_writes.jsonl")
    for ln in (open(p, encoding="utf-8").read().splitlines() if os.path.exists(p) else []):
        try:
            r = json.loads(ln)
            if r.get("class") == "main" and time.mktime(time.strptime(r["t"], "%Y-%m-%d %H:%M:%S")) >= t0 - 1:
                out.append(r["path"])
        except (ValueError, KeyError):
            continue
    return out


def diff_snaps(a, b, cycles=(), fpaths=()):
    """claudeDev: any change outside bench\\ (fixture excepted) is the arm's (nobody else writes there while an arm
    runs). Main tree: only changes the ARM could have caused are SUSPECT (lb_state.arm_caused); concurrent work by
    other writers (chat-F2 commits, the chat's STATUS edits) is INFO."""
    ka, kb = set(a["claudedev"]), set(b["claudedev"])
    changed = sorted(k for k in ka & kb if a["claudedev"][k] != b["claudedev"][k])
    strip = lambda s: dict(s, porcelain=[ln.split("\t")[0] for ln in s["porcelain"]])   # noqa: E731
    ch = main_changes(dict(a["main"], porcelain=a["main"]["porcelain"]), dict(b["main"], porcelain=b["main"]["porcelain"]))
    ch = [(p.split("\t")[0], how) for p, how in ch]
    sus, info = arm_caused(ch, cycles, fpaths)
    return {"claudedev_added": sorted(kb - ka), "claudedev_removed": sorted(ka - kb), "claudedev_changed": changed,
            "main_suspect": sus, "main_info": info, "main_head": [a["main"]["head"], b["main"]["head"]],
            "main_porcelain_lines": [len(strip(a["main"])["porcelain"]), len(strip(b["main"])["porcelain"])]}


sys.path.insert(0, HERE)
from lb_state import may_start_cycle, state as write_state, main_changes, arm_caused   # noqa: E402  (selftest 10 cases)


def run(arm, max_min=300, no_memory=False, not_after=None):
    setup_p = os.path.join(HERE, "setup_%s.json" % arm)
    if not gate("PRE setup record %s" % os.path.basename(setup_p), os.path.exists(setup_p)):
        return
    S = json.load(open(setup_p, encoding="utf-8"))
    wt, out = S["worktree"], S["claudedev_out"]
    sp = os.path.join(HERE, "%s_state.json" % arm)
    st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {"segments": []}
    st = write_state(arm, S, st)
    if st["cycles_finished"] >= ARMS["cycles"]:
        print("RUN %s: already finished %d/%d cycles - collect only" % (arm, st["cycles_finished"], ARMS["cycles"]), flush=True)
        collect(arm)
        return
    gate("PRE worktree HEAD descends from the setup commit",
         subprocess.run(["git", "merge-base", "--is-ancestor", S["setup_commit"], "HEAD"], cwd=wt).returncode == 0)
    lock = os.path.join(HERE, "RUNNING.json")
    gate("PRE no other arm running", not os.path.exists(lock), open(lock).read() if os.path.exists(lock) else "")
    gate("PRE main STATUS still carries its STOP line (main runner stays stopped)",
         re.search(r"^STOP\b", open(os.path.join(MAIN_DIR, "STATUS.md"), encoding="utf-8").read(), re.M) is not None)
    if any(not ok for _l, ok in GATES):
        return
    why = may_start_cycle(S, st, not_after)
    if why:
        print("RUN-STOPPED %s (resumable, nothing started): %s" % (arm, why), flush=True)
        return
    os.makedirs(out, exist_ok=True)
    sv = ARMS["start_vi"]
    dst = os.path.join(out, sv["name"])
    if not (os.path.exists(dst) and md5(dst) == sv["md5"]):
        shutil.copyfile(os.path.join(CD_ROOT, sv["name"]), dst)
    gate("PREP start VI byte copy in the arm folder, md5 %s" % sv["md5"][:8], md5(dst) == sv["md5"])
    if not no_memory:
        src = os.path.join(os.path.expanduser("~"), ".claude", "projects", mangle(MAIN_DIR), "memory")
        mem = os.path.join(os.path.expanduser("~"), ".claude", "projects", mangle(wt), "memory")
        if os.path.isdir(src) and not os.path.exists(mem):
            shutil.copytree(src, mem)
        gate("PREP memory copied to the worktree's project key", os.path.isdir(mem))
    env = dict(os.environ)
    for k in ("CYCLE_SESSION", "CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_RESULT", "ASSIGN_CONFIG", "PURPOSE_PHASE",
              "HANDBACK_RECORD", "BENCH_CELL"):
        env.pop(k, None)
    env.update(S["env"])
    st.setdefault("t0", time.time())
    # ONE runner process per cycle (`--cycles 1`), so a stop between cycles is always clean and a later `run` resumes at
    # the next unfinished cycle. The runner's own state (judge ladder, next.json, cycle count) lives in files; only its
    # in-memory firefighter history is per process, and with 2 cycles the firefighter cannot fire anyway (it needs two
    # failing cycles BEFORE the one it changes). bgrun's deadline is the last resort, far above a cycle (~90 min).
    while st["cycles_finished"] < ARMS["cycles"]:
        why = may_start_cycle(S, st, not_after)
        if why:
            print("RUN-STOPPED %s after %d/%d cycle(s) (resumable): %s" % (arm, st["cycles_finished"], ARMS["cycles"], why),
                  flush=True)
            break
        # LINE ENDINGS BEFORE EVERY CYCLE (chat 2026-10-06): main-equal, arm-unchanged tracked files get main's working
        # bytes back (a git checkout/reset inside the arm may have rewritten them); the arm's own files are never touched.
        import lb_setup
        sb = lb_setup.sync_bytes_precycle(wt)
        st.setdefault("sync_bytes", []).append(dict(sb, t=time.strftime("%Y-%m-%d %H:%M:%S")))
        print("SYNC-BYTES before cycle %d: %d fixed, %d identical, %d arm-changed skipped, %d mismatches after %s"
              % (st["cycles_finished"] + 1, sb["fixed"], sb["identical"], sb["skipped_arm_changed"], sb["mismatches_after"],
                 sb["paths"][:5]), flush=True)
        gate("PRE cycle: sync_bytes left 0 mismatches", sb["mismatches_after"] == 0)
        with open(lock, "w", encoding="utf-8") as f:
            json.dump({"arm": arm, "since": time.strftime("%Y-%m-%d %H:%M:%S"), "pid": os.getpid()}, f)
        before = snap()
        t0 = time.time()
        cmd = [sys.executable, os.path.join("tools", "bgrun.py"), "--max-min", str(max_min), "--log",
               os.path.join("tools", "bench", "livebench_runner.log"), "--", "py", "-u",
               os.path.join("tools", "cycle_runner.py"), "--cycles", "1", "--flow", S["flow"]]
        print("RUN %s cycle %d/%d: %s (cwd %s)" % (arm, st["cycles_finished"] + 1, ARMS["cycles"], " ".join(cmd), wt),
              flush=True)
        try:
            rc = subprocess.run(cmd, cwd=wt, env=env).returncode
        finally:
            os.remove(lock)
        t1 = time.time()
        done_before = set(c["n"] for c in st.get("cycles") or [])
        st = write_state(arm, S, st)
        seg_cycles = sorted(set(c["n"] for c in st.get("cycles") or []) - done_before) or \
            [max([c["n"] for c in st.get("cycles") or []] + [143]) + 1]       # a cycle that stopped early has no CYCLE line
        d = diff_snaps(before, snap(), seg_cycles, fence_paths(wt, t0))
        st.setdefault("segments", []).append({"t0": t0, "t1": t1, "rc": rc, "cycles": seg_cycles, "snapshots": d})
        st["t1"] = t1
        st = write_state(arm, S, st)
        gate("POST cycle: nothing in the claudeDev root changed outside bench\\ (fixture excepted)",
             not [k for k in d["claudedev_added"] + d["claudedev_removed"] + d["claudedev_changed"]
                  if not k.lower().startswith("niscriptingexamples")], json.dumps(d)[:300])
        for x in d["main_info"][:20]:
            print("INFO main-tree change by another writer (not this arm): %s (%s)" % (x["path"], x["how"]), flush=True)
        gate("POST cycle: no main-tree change this arm could have caused (cycles %s, fence-logged paths, "
             "livebench_runner logs)" % seg_cycles, not d["main_suspect"], json.dumps(d["main_suspect"])[:300])
        gate("POST cycle: LabVIEW gone", not labview_running())
        if rc != 0:
            print("RUN %s: the runner exited %d - stopping here (resumable)" % (arm, rc), flush=True)
            break
    with open(os.path.join(HERE, "%s_snapshots.json" % arm), "w", encoding="utf-8") as f:
        json.dump([s["snapshots"] for s in st.get("segments") or []], f, indent=1)
    with open(os.path.join(HERE, "%s_run.json" % arm), "w", encoding="utf-8") as f:
        json.dump({"arm": arm, "t0": st["t0"], "t1": st.get("t1") or time.time(), "worktree": wt,
                   "cycles_finished": st["cycles_finished"], "segments": len(st.get("segments") or [])}, f, indent=1)
    if st.get("segments"):
        collect(arm)


def collect(arm):
    S = json.load(open(os.path.join(HERE, "setup_%s.json" % arm), encoding="utf-8"))
    R = json.load(open(os.path.join(HERE, "%s_run.json" % arm), encoding="utf-8"))
    out_json = os.path.join(HERE, "%s.json" % arm)
    c = subprocess.run([sys.executable, "-u", os.path.join(HERE, "lb_collect.py"), "--worktree", S["worktree"], "--arm", arm,
                        "--setup-commit", S["setup_commit"], "--t0", str(R["t0"]), "--t1", str(R["t1"]),
                        "--claudedev-out", S["claudedev_out"], "--writelog", S["env"]["LIVEBENCH_WRITELOG"],
                        "--snapshots", os.path.join(HERE, "%s_snapshots.json" % arm), "--flow", S["flow"],
                        "--extras", ",".join(S["extras"]), "--start-vi", json.dumps(ARMS["start_vi"]),
                        "--agent", ARMS["arms"][arm].get("agent", "claude-code"), "--out", out_json])
    gate("COLLECT %s" % os.path.basename(out_json), c.returncode == 0 and os.path.exists(out_json))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "collect"))
    ap.add_argument("arm")
    ap.add_argument("--max-min", type=float, default=300, help="bgrun last-resort deadline for ONE cycle")
    ap.add_argument("--no-memory", action="store_true")
    ap.add_argument("--not-after", default=None, metavar="HH:MM",
                    help="never START a cycle that could not end before this local time (cycle length = longest measured, "
                         "default 90 min)")
    a = ap.parse_args(argv)
    if a.not_after and not re.match(r"^\d{1,2}:\d\d$", a.not_after):
        ap.error("--not-after takes HH:MM")
    (run(a.arm, a.max_min, a.no_memory, a.not_after) if a.cmd == "run" else collect(a.arm))
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
    import protocol
    npass = sum(1 for _l, ok in GATES if ok)
    first = next((lab for lab, ok in GATES if not ok), None)
    print(protocol.result_line(protocol.make_result(npass, len(GATES) - npass, first)), flush=True)
    return 1 if first else 0


if __name__ == "__main__":
    sys.exit(main())
