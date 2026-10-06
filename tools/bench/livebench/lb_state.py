# ---
# labview: none
# hardware: none
# ---
r"""lb_state - livebench RESUME record and STOP SAFETY (card chat-B7; user 2026-10-06 11:5x: the user's tweezers
experiment runs on this PC from ~14:00, so the bench must stop and later continue where it left off).
Pure file reads (+ tasklist); lb_run imports it. CLI:
  status <arm> [--not-after HH:MM]   print the arm's state (cycles finished, last accepted VI, worktree HEAD) and whether
                                      a cycle may start now; writes nothing
  selftest                            temp STATUS / runner-log fixtures: 7 cases
RESUME  livebench/<arm>_state.json (livebench-state/1): cycles_finished counts the arm's OWN runner-log CYCLE lines after
        the start state's last cycle (143), so a crash or a stop between cycles resumes at the next unfinished cycle.
SAFETY  before EVERY cycle: main and arm STATUS `rig-state:` must be 조립 (실험중 / 분해 / unknown refuse), no
        LabVIEW.exe, and with --not-after now + cycle length <= cutoff (cycle length = the longest measured cycle of the
        arm, never less than 90 min: cycles 142/143 ran 87/88 min). A cycle in progress is never killed."""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ARMS = json.load(open(os.path.join(HERE, "arms.json"), encoding="utf-8"))
MAIN_DIR = ARMS["main_project"]
CYCLE_LINE_RE = re.compile(r"^CYCLE (\d+) \| (\S+ \S+) \| (\S+ \S+) \| exit (-?\d+)", re.M)
RIG_RE = re.compile(r"^rig-state:\s*(\S+)", re.M)
DEFAULT_CYCLE_MIN = 90.0


def git(*args, cwd=MAIN_DIR):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout


def labview_running():
    out = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    return "labview.exe" in out.lower()


def rig_state(status_path):
    try:
        m = RIG_RE.search(open(status_path, encoding="utf-8", errors="replace").read())
    except OSError:
        return "unknown"
    return m.group(1) if m else "unknown"


def start_last_cycle():
    txt = open(os.path.join(HERE, "start_state", "tools__bench__cycle_runner.log"), encoding="utf-8", errors="replace").read()
    return max([int(m.group(1)) for m in CYCLE_LINE_RE.finditer(txt)] or [0])


def arm_cycles(wt, start_last):
    try:
        txt = open(os.path.join(wt, "tools", "bench", "cycle_runner.log"), encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    seen = {}
    for m in CYCLE_LINE_RE.finditer(txt):
        if int(m.group(1)) > start_last:
            seen[int(m.group(1))] = (int(m.group(1)), m.group(2), m.group(3), int(m.group(4)))
    return [seen[k] for k in sorted(seen)]


def state(arm, S, st, start_last=None, write=True):
    """RESUME record: cycles finished, the last accepted VI (adopt/1 after the arm's first start), the worktree HEAD."""
    wt = S["worktree"]
    cyc = arm_cycles(wt, start_last_cycle() if start_last is None else start_last)
    last = None
    adl = os.path.join(wt, "tools", "bench", "adopted_scratch.jsonl")
    for ln in (open(adl, encoding="utf-8").read().splitlines() if os.path.exists(adl) else []):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if st.get("t0") and float(r.get("t") or 0) >= st["t0"]:
            last = {"path": (r.get("artefact") or {}).get("path"), "md5": (r.get("artefact") or {}).get("md5"),
                    "stage": r.get("stage"), "iso": r.get("iso")}
    st.update({"schema": "livebench-state/1", "arm": arm, "cycles_target": ARMS["cycles"], "cycles_finished": len(cyc),
               "cycles": [{"n": c[0], "start": c[1], "end": c[2], "exit": c[3]} for c in cyc],
               "next_cycle": (len(cyc) + 1) if len(cyc) < ARMS["cycles"] else None,
               "last_accepted_vi": last, "worktree_head": git("rev-parse", "HEAD", cwd=wt).strip(),
               "updated": time.strftime("%Y-%m-%d %H:%M:%S")})
    if write:
        with open(os.path.join(HERE, "%s_state.json" % arm), "w", encoding="utf-8") as f:
            json.dump(st, f, indent=1)
    return st


def cycle_minutes(st):
    ds = []
    for c in st.get("cycles") or []:
        try:
            ds.append((time.mktime(time.strptime(c["end"], "%Y-%m-%d %H:%M:%S"))
                       - time.mktime(time.strptime(c["start"], "%Y-%m-%d %H:%M:%S"))) / 60.0)
        except (ValueError, KeyError):
            pass
    return max(ds + [DEFAULT_CYCLE_MIN])


def may_start_cycle(S, st, not_after, main_status=None, now=None, lv_running=None):
    """(reason or None) - checked before EVERY cycle; a refusal is a clean, resumable stop."""
    for name, p in (("main", main_status or os.path.join(MAIN_DIR, "STATUS.md")),
                    ("arm", os.path.join(S["worktree"], "STATUS.md"))):
        rs = rig_state(p)
        if rs != "조립":
            return "%s STATUS rig-state is %s (only 조립 runs an arm; 실험중 = the user's experiment)" % (name, rs)
    if (labview_running() if lv_running is None else lv_running):
        return "LabVIEW.exe is running (the user's, or a cycle that did not close it)"
    if not_after:
        t = time.time() if now is None else now
        hh, mm = [int(x) for x in not_after.split(":")]
        lt = time.localtime(t)
        cut = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hh, mm, 0, 0, 0, -1))
        need = cycle_minutes(st)
        if t + need * 60.0 > cut:
            return "--not-after %s: a cycle needs ~%.0f min and would end after the cutoff" % (not_after, need)
    return None


def main_changes(before, after, git_fn=None):
    """Main-tree paths that changed between two lb_run snapshots: new/changed `git status --porcelain` lines plus the
    files of commits made in between. [(path, how)]."""
    git_fn = git_fn or (lambda *a: git(*a))
    out = []
    pb, pa = set(before.get("porcelain") or []), after.get("porcelain") or []
    for ln in pa:
        if ln not in pb:
            out.append((ln[3:].strip().strip('"'), "worktree-state " + ln[:2].strip()))
    if before.get("head") and after.get("head") and before["head"] != after["head"]:
        for p in git_fn("diff", "--name-only", before["head"], after["head"]).splitlines():
            if p.strip():
                out.append((p.strip(), "commit %s..%s" % (before["head"][:8], after["head"][:8])))
    return out


def arm_caused(changes, cycles, fence_paths=(), main_dir=None):
    """Split main-tree changes into (SUSPECT = could have been written by this arm, INFO = other writers). Suspect:
    a path a worktree fence logged (event shell/open, class main), a `livebench_runner` log, or a basename carrying one
    of the arm's cycle numbers (>= 144) as a whole number. Everything else - chat-F2's commits, the chat's STATUS /
    docs edits - is INFO (user-chat decision 2026-10-06 after lb_run_A.log's false POST FAIL)."""
    md = os.path.normcase(main_dir or MAIN_DIR)
    fp = set(os.path.normcase(os.path.relpath(p, md)) if os.path.isabs(p) else os.path.normcase(p) for p in fence_paths)
    nums = set(str(int(n)) for n in cycles)
    sus, info = [], []
    for p, how in changes:
        base = os.path.basename(p.replace("\\", "/"))
        hit = (os.path.normcase(p.replace("/", os.sep)) in fp or "livebench_runner" in base
               or any(n in nums for n in re.findall(r"(?<!\d)(\d{3})(?!\d)", base)))
        (sus if hit else info).append({"path": p, "how": how})
    return sus, info


def selftest():
    import protocol
    res = []
    tmp = tempfile.mkdtemp(prefix="lbstate_")
    wt = os.path.join(tmp, "wt")
    os.makedirs(os.path.join(wt, "tools", "bench"))
    S = {"worktree": wt}
    ok_status = os.path.join(tmp, "main_ok.md")
    open(ok_status, "w", encoding="utf-8").write("x\nrig-state: 조립   <!-- c -->\n")
    exp_status = os.path.join(tmp, "main_exp.md")
    open(exp_status, "w", encoding="utf-8").write("rig-state: 실험중\n")
    open(os.path.join(wt, "STATUS.md"), "w", encoding="utf-8").write("rig-state: 조립\n")
    log = os.path.join(wt, "tools", "bench", "cycle_runner.log")
    open(log, "w", encoding="utf-8").write("CYCLE 143 | 2026-10-03 10:47:54 | 2026-10-03 12:15:27 | exit 0 | $35 | x\n")
    noon = time.mktime((2026, 10, 7, 12, 0, 0, 0, 0, -1))

    def case(label, ok):
        res.append((label, bool(ok)))
        print("CASE %s: %s" % (label, "PASS" if ok else "FAIL"), flush=True)
    st = state("T", S, {}, start_last=143, write=False)
    case("S1 fresh arm: 0 finished, next 1", st["cycles_finished"] == 0 and st["next_cycle"] == 1)
    case("S2 조립, no LabVIEW, no cutoff -> may start",
         may_start_cycle(S, st, None, ok_status, noon, False) is None)
    case("S3 main rig-state 실험중 -> refused", "실험중" in (may_start_cycle(S, st, None, exp_status, noon, False) or ""))
    case("S4 LabVIEW running -> refused", "LabVIEW" in (may_start_cycle(S, st, None, ok_status, noon, True) or ""))
    case("S5 12:00 + 90 min > 13:00 cutoff -> refused; <= 14:00 -> may start",
         "not-after" in (may_start_cycle(S, st, "13:00", ok_status, noon, False) or "")
         and may_start_cycle(S, st, "14:00", ok_status, noon, False) is None)
    open(log, "a", encoding="utf-8").write("CYCLE 144 | 2026-10-07 09:00:00 | 2026-10-07 10:52:00 | exit 0 | $40 | y\n")
    st = state("T", S, st, start_last=143, write=False)
    case("S6 resume after one cycle: 1 finished, next 2, cycle length = the measured 112 min",
         st["cycles_finished"] == 1 and st["next_cycle"] == 2 and abs(cycle_minutes(st) - 112) < 0.1
         and "not-after" in (may_start_cycle(S, st, "13:45", ok_status, noon, False) or ""))
    open(log, "a", encoding="utf-8").write("CYCLE 145 | 2026-10-07 11:00:00 | 2026-10-07 12:20:00 | exit 0 | $30 | z\n")
    st = state("T", S, st, start_last=143, write=False)
    case("S7 two cycles finished: next None (collect only)", st["cycles_finished"] == 2 and st["next_cycle"] is None)
    b = {"head": "a" * 40, "porcelain": [" M STATUS.md", " M docs/chat-handoff.md"]}
    other = {"head": "b" * 40, "porcelain": [" M STATUS.md", " M docs/chat-handoff.md", " M tools/bench/heartbeat_latest.md",
                                             "?? tools/bench/cards/result_chat-F2.json"]}
    fake_git = lambda *a: "tools/gscript.py\ndocs/toolkit-capabilities.md\n"                       # noqa: E731
    ch = main_changes(b, other, fake_git)
    sus, info = arm_caused(ch, [144, 145], (), main_dir=tmp)
    case("S8 other writers only (chat-F2 commit, chat STATUS/handoff edits, a chat-F2 card): 0 suspect, all INFO",
         not sus and len(info) == 4)
    arm_w = dict(other, porcelain=other["porcelain"] + ["?? tools/bench/cycle_144_assign_1.log",
                                                       "?? tools/bench/livebench_runner.log", "?? tools/bench/x_fenced.txt"])
    ch = main_changes(b, arm_w, fake_git)
    sus, info = arm_caused(ch, [144, 145], [os.path.join(tmp, "tools", "bench", "x_fenced.txt")], main_dir=tmp)
    case("S9 arm-made main paths (cycle_144 log, livebench_runner log, a fence-logged path) are SUSPECT, others INFO",
         sorted(os.path.basename(s["path"]) for s in sus) == ["cycle_144_assign_1.log", "livebench_runner.log",
                                                               "x_fenced.txt"] and len(info) == 4)
    case("S10 a 4-digit number or a chat card id is not mistaken for a cycle",
         not arm_caused([("tools/bench/run_1440.log", "x"), ("tools/bench/cards/task_chat-B7.json", "x")], [144], (),
                        main_dir=tmp)[0])
    n_ok = sum(1 for _l, ok in res if ok)
    first = next((lab for lab, ok in res if not ok), None)
    print(protocol.result_line(protocol.make_result(n_ok, len(res) - n_ok, first)), flush=True)
    return 0 if first is None else 1


def main(argv=None):
    import argparse
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("status", "selftest"))
    ap.add_argument("arm", nargs="?")
    ap.add_argument("--not-after", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    S = json.load(open(os.path.join(HERE, "setup_%s.json" % a.arm), encoding="utf-8"))
    sp = os.path.join(HERE, "%s_state.json" % a.arm)
    st = state(a.arm, S, json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}, write=False)
    print(json.dumps({k: st[k] for k in ("arm", "cycles_finished", "cycles_target", "next_cycle", "last_accepted_vi",
                                         "worktree_head")}, ensure_ascii=False), flush=True)
    print("MAY-START: %s" % (may_start_cycle(S, st, a.not_after) or "yes"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
