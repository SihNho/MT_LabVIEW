# ---
# labview: none
# hardware: none
# evidence: tools/stage_prerun.py:17
# ---
r"""lb_setup - livebench harness, OFFLINE half (card chat-B7, user 2026-10-06). Builds the per-arm bench worktrees and
checks them; it never opens LabVIEW and never moves a motor (the real arm run is lb_run.py).

  snapshot            freeze the START STATE (from the main working tree, once): STATUS.md, next.json and the runner's
                      state files -> livebench/start_state/ + manifest.json (md5s). Every arm starts from these bytes.
  setup <arm>         git worktree add -b bench/<arm> <bench_root>/<arm> <commit>; then, in the worktree only:
                      start state applied (STATUS STOP markers neutralised, arm banner added), stale motor_session.json
                      removed, .claude/settings*.json hook paths re-pointed to the worktree, PATCHES (CLAUDEDEV_OUT: the
                      arm's claudeDev\bench\<arm> write root), Karpathy section (extras), the write fence
                      .livebench/sitecustomize.py; committed as "livebench setup"; record livebench/setup_<arm>.json.
  contain-dry <arm>   stage_prerun.dry of the cycle-1 stage recipe in the worktree with the arm env; records EVERY write
                      path the recipe attempts (stage_prerun._outside_temp) and every save/copy call; PASS when all
                      claudeDev writes resolve under claudeDev\bench\<arm> and nothing targets the main project. With
                      --counterfactual the same dry on the MAIN tree (unpatched) shows where the writes would go.
  stub <arm>          the whole runner for --cycles 2 in a throwaway worktree _stub_<arm>, sessions replaced by
                      stub_claude.py, fake claudeDev root in %TEMP%, then lb_collect -> livebench/stub_<arm>.json, then
                      teardown (unless --keep).
  teardown <name>     git worktree remove --force + branch -D bench/<name>.
Each run ends with a C6 RESULT line."""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
MAIN = os.path.dirname(TOOLS)
ARMS = json.load(open(os.path.join(HERE, "arms.json"), encoding="utf-8"))
STATE_DIR = os.path.join(HERE, "start_state")
STATE_FILES = ["STATUS.md", "tools/bench/next.json", "tools/bench/cycle_runner.log", "tools/bench/judge_ladder.json",
               "tools/bench/cycle_runner_retro_seen.json", "tools/bench/heartbeat_latest.md"]
STATE_ABSENT = ["tools/bench/motor_session.json"]     # absent in the main working tree (no motor session open)
CD_ROOT = ARMS["claudedev_root"]
MAIN_DIR = ARMS["main_project"]
RECIPE = "tools/recipes/stage_d1_ring_p4_s03v18_scratch.py"
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("GATE %s: %s%s" % (label, "PASS" if ok else "FAIL", ("  (%s)" % detail) if detail else ""), flush=True)
    return ok


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def git(*args, cwd=MAIN, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()[:300]))
    return r.stdout.strip()


def out_dir(arm):
    return os.path.join(CD_ROOT, "bench", arm)


def wt_path(name):
    return os.path.join(ARMS["bench_root"], name)


# ------------------------------------------------------------------ the patches (worktree only, anchor-checked)
def patches(main_parent):
    q = r'"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"'
    get_out = 'getattr(g, "CLAUDEDEV_OUT", CLAUDEDEV)'
    return [
        ("tools/gscript.py", "G1 CLAUDEDEV_OUT", "CLAUDEDEV = r%s\n" % q,
         "CLAUDEDEV = r%s\nCLAUDEDEV_OUT = os.environ.get(\"LIVEBENCH_CLAUDEDEV\") or CLAUDEDEV   # livebench (card chat-B7): "
         "the arm's ONLY write root\n" % q, 1),
        ("tools/gscript.py", "G2 PROJECT = the worktree", 'PROJECT = r"%s"\n' % MAIN_DIR,
         "PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # livebench: this worktree\n", 1),
        ("tools/gscript.py", "G3 ORIGINAL stays the main original",
         'os.path.join(os.path.dirname(PROJECT), "Min_Track N beads V6_ParallelLoop.vi")',
         'os.path.join(r"%s", "Min_Track N beads V6_ParallelLoop.vi")' % main_parent, 1),
        ("tools/gscript.py", "G4 save/gui_save fenced to the arm folder",
         "if (os.path.normcase(CLAUDEDEV) not in os.path.normcase(target)",
         "if (os.path.normcase(CLAUDEDEV_OUT) not in os.path.normcase(target)", 2),
        ("tools/gscript.py", "G5 hygiene scratch dir", "sd = scratch_dir or CLAUDEDEV\n", "sd = scratch_dir or CLAUDEDEV_OUT\n", 1),
        ("tools/stagekit.py", "K1 Stage work_dir", "work_dir=CLAUDEDEV,", "work_dir=%s," % get_out, 1),
        ("tools/stagekit.py", "K2 Stage.scratch", 'p = os.path.join(CLAUDEDEV, "{0}_{1}_{2}.vi"',
         'p = os.path.join(%s, "{0}_{1}_{2}.vi"' % get_out, 1),
        ("tools/stagekit.py", "K3 H6 listing", 'glob.glob(os.path.join(CLAUDEDEV, "*.vi"))',
         'glob.glob(os.path.join(%s, "*.vi"))' % get_out, 2),
        ("tools/stagexec.py", "X1 adopt root", "def _claudedev():\n    import gscript as g\n    return g.CLAUDEDEV\n",
         "def _claudedev():\n    import gscript as g\n    return getattr(g, \"CLAUDEDEV_OUT\", g.CLAUDEDEV)\n", 1),
        ("tools/stagexec.py", "X2 bare reference name: arm folder first",
         "reference = (os.path.join(K.CLAUDEDEV, reference[0]), reference[1])",
         "reference = ((lambda _o: _o if os.path.exists(_o) else os.path.join(K.CLAUDEDEV, reference[0]))("
         "os.path.join(getattr(K.g, \"CLAUDEDEV_OUT\", K.CLAUDEDEV), reference[0])), reference[1])", 1),
        ("tools/errorlist_check.py", "E1 beds in the arm folder", "CLAUDEDEV = r%s" % q,
         "CLAUDEDEV = os.environ.get(\"LIVEBENCH_CLAUDEDEV\") or r%s" % q, 1),
        ("tools/errorlist_check.py", "E2 Error List scratch", 'os.path.join(g.CLAUDEDEV, "_elc_',
         'os.path.join(getattr(g, "CLAUDEDEV_OUT", g.CLAUDEDEV), "_elc_', 1),
        ("tools/stage_prerun.py", "P1 launch gate: work copy in the arm folder",
         'if os.path.basename(os.path.dirname(str(w))).lower() != "claudedev":',
         'if ((norm(os.path.dirname(str(w))) != norm(os.environ["LIVEBENCH_CLAUDEDEV"])) if os.environ.get('
         '"LIVEBENCH_CLAUDEDEV") else (os.path.basename(os.path.dirname(str(w))).lower() != "claudedev")):', 1),
        ("tools/wiki_build.py", "W1 wiki scratch", 'os.path.join(g.CLAUDEDEV, "wikipane_',
         'os.path.join(getattr(g, "CLAUDEDEV_OUT", g.CLAUDEDEV), "wikipane_', 1),
        # R1 (first live launch 2026-10-06 12:07, lb_run_A.log: "BGRUN REAP marked KILLED: cycle_runner_main_20261003_1055.log
        # pid=23836, wait_runner_event.log pid=25492"): the worktree carries the MAIN repo's bgrun logs as committed at the
        # base commit, some at START without END; the arm's reaper must never mark or edit them.
        ("tools/bgrun_reap.py", "R1 reaper skips the logs inherited from the main repo",
         '        if os.path.normcase(os.path.abspath(p)) in excl:\n            continue\n',
         '        if os.path.normcase(os.path.abspath(p)) in excl:\n            continue\n'
         '        if os.path.basename(p) in _livebench_inherited():   # livebench (card chat-B7): main-repo logs, never reaped\n'
         '            continue\n', 1),
        ("tools/bgrun_reap.py", "R2 inherited-log list", 'BENCH = os.path.join(PROJECT, "tools", "bench")\n',
         'BENCH = os.path.join(PROJECT, "tools", "bench")\n\n\ndef _livebench_inherited():\n'
         '    """livebench (card chat-B7): basenames of the bgrun logs this worktree inherited from the main repo."""\n'
         '    try:\n        import json as _j\n'
         '        return set(_j.load(open(os.path.join(PROJECT, ".livebench", "inherited_logs.json"), encoding="utf-8")))\n'
         '    except (OSError, ValueError):\n        return set()\n', 1),
    ]


def apply_patches(wt, only=None):
    done = []
    for rel, label, old, new, count in patches(os.path.dirname(MAIN_DIR)):
        if only and not label.startswith(tuple(only)):
            continue
        p = os.path.join(wt, rel)
        src = open(p, encoding="utf-8").read()
        n = src.count(old)
        if not gate("PATCH %s (%s): anchor found %d time(s), expected %d" % (label, rel, n, count), n == count):
            raise SystemExit("anchor drift in %s - the worktree commit differs from the one the patches were written "
                             "for; update lb_setup.patches()" % rel)
        src = src.replace(old, new)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        r = subprocess.run([sys.executable, "-m", "py_compile", p], capture_output=True, text=True)
        gate("PATCH %s compiles" % label, r.returncode == 0, r.stderr.strip()[:200])
        done.append({"file": rel, "label": label, "count": count})
    return done


# ------------------------------------------------------------------ setup steps
def repoint_settings(wt):
    out = []
    forms = [(MAIN_DIR.replace("\\", "\\\\"), wt.replace("\\", "\\\\")), (MAIN_DIR.replace("\\", "/"), wt.replace("\\", "/"))]
    for name in ("settings.json", "settings.local.json"):
        p = os.path.join(wt, ".claude", name)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        n = 0
        for a, b in forms:
            n += t.count(a)
            t = t.replace(a, b)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(t)
        json.loads(t)
        left = sum(t.count(a) for a, _b in forms)
        gate("SETTINGS %s: %d main path(s) re-pointed, %d left" % (name, n, left), left == 0)
        out.append({"file": ".claude/" + name, "repointed": n})
    hooks = json.load(open(os.path.join(wt, ".claude", "settings.json"), encoding="utf-8")).get("hooks") or {}
    cmds = [h.get("command", "") for v in hooks.values() for m in v for h in m.get("hooks") or []]
    gate("SETTINGS every hook command points into the worktree (%d hooks)" % len(cmds),
         cmds and all(wt.replace("\\", "/") in c.replace("\\\\", "/").replace("\\", "/") for c in cmds))
    return out


def apply_state(wt, arm):
    man = json.load(open(os.path.join(STATE_DIR, "manifest.json"), encoding="utf-8"))
    for rel in STATE_FILES:
        src = os.path.join(STATE_DIR, rel.replace("/", "__"))
        gate("STATE %s md5 == manifest" % rel, md5(src) == man["files"][rel])
        dst = os.path.join(wt, rel)
        if rel == "STATUS.md":
            lines = open(src, encoding="utf-8").read().split("\n")
            n_stop = 0
            for i in range(min(60, len(lines))):
                if re.match(r"^STOP\b", lines[i]) or re.match(r"^#{1,6}\s*STOP\b", lines[i]):
                    lines[i] = "(livebench: STOP marker neutralised for the bench arm) " + lines[i]
                    n_stop += 1
            fm_end = [i for i, ln in enumerate(lines[:12]) if ln.strip() == "---"]
            at = fm_end[1] + 1 if len(fm_end) >= 2 else 0
            lines.insert(at, "LIVEBENCH ARM %s (card chat-B7, user 2026-10-06): this is a BENCH worktree (%s, branch bench/%s), "
                             "not the main project. LabVIEW outputs of this arm go to %s (gscript.CLAUDEDEV_OUT, Stage work "
                             "copies, saves); a write anywhere else under claudeDev or into the main project (%s) is refused "
                             "by .livebench/sitecustomize.py. Op VIs and donors are still read from the claudeDev root."
                             % (arm, wt, arm, out_dir(arm), MAIN_DIR))
            with open(dst, "w", encoding="utf-8", newline="") as f:
                f.write("\n".join(lines))
            set_current_bed(dst)
            txt = open(dst, encoding="utf-8").read()
            head = "\n".join(txt.split("\n")[:60])
            gate("STATE STATUS: %d STOP marker(s) neutralised, none left in the head" % n_stop,
                 not re.search(r"^STOP\b", head, re.M) and not re.search(r"^#{1,6}\s*STOP\b", txt, re.M))
        else:
            shutil.copyfile(src, dst)
    for rel in STATE_ABSENT:
        p = os.path.join(wt, rel)
        if os.path.exists(p):
            os.remove(p)
        gate("STATE %s absent (as in the main tree)" % rel, not os.path.exists(p))
    return man


BED_RE = re.compile(r"^current-bed:\s*(\S+\.vi)", re.M)     # == errorlist_check.current_bed_text's regex


def set_current_bed(status_path):
    """The arm's STATUS names the START VI (its byte copy in claudeDev\\bench\\<arm>) as `current-bed:`, in the exact form
    errorlist_check.current_bed_text parses (first `^current-bed: <name>.vi` line; the name is joined with the
    LIVEBENCH_CLAUDEDEV-patched CLAUDEDEV). The start state's own line (D1_ring_p3b2b_..., main STATUS) is replaced."""
    name = ARMS["start_vi"]["name"]
    t = open(status_path, encoding="utf-8").read()
    line = ("current-bed: %s   <!-- livebench (card chat-B7): the arm's bed = the byte copy of the start VI in "
            "claudeDev\\bench\\<arm>, md5 %s; the Error List REUSE path reads errorlist_%s_*.json + "
            "errorlist_expected_%s.json -->" % (name, ARMS["start_vi"]["md5"], name[:-3], name[:-3]))
    if BED_RE.search(t):
        t = re.sub(r"^current-bed:.*$", lambda _m: line, t, count=1, flags=re.M)
    else:
        t = t.rstrip("\n") + "\n" + line + "\n"
    with open(status_path, "w", encoding="utf-8", newline="") as f:
        f.write(t)
    got = BED_RE.search(open(status_path, encoding="utf-8").read())
    gate("BED STATUS current-bed parses to %s" % name, got and got.group(1) == name)


def stage_start_vi(arm):
    """Byte copy of the start VI into claudeDev\\bench\\<arm> (no LabVIEW), md5-checked; the arm's first bed."""
    sv = ARMS["start_vi"]
    out = out_dir(arm)
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, sv["name"])
    if not (os.path.exists(dst) and md5(dst) == sv["md5"]):
        shutil.copyfile(os.path.join(CD_ROOT, sv["name"]), dst)
    return gate("BED start VI byte copy %s md5 %s" % (dst, sv["md5"][:8]), md5(dst) == sv["md5"])


def sync_errorlist(wt):
    """The main repo's saved Error List reads + expected file for the start VI's stem, byte-identical in the worktree
    (they are tracked at the base commit; re-copied if main's differ or a newer read exists)."""
    stem = ARMS["start_vi"]["name"][:-3]
    n = 0
    for src in glob.glob(os.path.join(MAIN, "tools", "bench", "errorlist_%s_*.json" % stem)) + \
            glob.glob(os.path.join(MAIN, "tools", "bench", "errorlist_expected_%s.json" % stem)):
        dst = os.path.join(wt, "tools", "bench", os.path.basename(src))
        if not (os.path.exists(dst) and md5(dst) == md5(src)):
            shutil.copyfile(src, dst)
        n += md5(dst) == md5(src)
    gate("BED %d Error List file(s) of %s byte-identical to main (read + raw + expected)" % (n, stem), n >= 3)


def record_inherited_logs(wt):
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(wt, "tools", "bench", "*.log")))
    with open(os.path.join(wt, ".livebench", "inherited_logs.json"), "w", encoding="utf-8") as f:
        json.dump(names, f, indent=0)
    gate("REAP %d inherited main-repo bgrun log(s) listed in .livebench/inherited_logs.json" % len(names), len(names) > 0)


def sync_ignored(wt):
    """Byte-copy the git-IGNORED start inputs (arms.json ignored_inputs) from the main tree into the worktree."""
    n, bad = 0, []
    for g_ in ARMS["ignored_inputs"]["globs"]:
        for src in glob.glob(os.path.join(MAIN, g_)):
            dst = os.path.join(wt, os.path.relpath(src, MAIN))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not (os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src) and md5(dst) == md5(src)):
                shutil.copyfile(src, dst)
            n += 1
            if md5(dst) != md5(src):
                bad.append(dst)
    gate("IGNORED inputs: %d file(s) byte-identical to the main tree" % n, n > 0 and not bad, str(bad[:3]))
    return n


def install_fence(wt):
    """The SHELL write fence (chat decision 2026-10-06): .livebench/guard_fence.py, registered FIRST in the worktree's
    PreToolUse Bash|PowerShell hooks (idempotent), then its self-test (refuse + allow cases) against the worktree's
    arm.json. Worktree only - the main repo's settings are never touched."""
    ov = os.path.join(wt, ".livebench")
    dst = os.path.join(ov, "guard_fence.py")
    shutil.copyfile(os.path.join(HERE, "overlay", "guard_fence.py"), dst)
    sp = os.path.join(wt, ".claude", "settings.json")
    s = json.load(open(sp, encoding="utf-8"))
    cmd = 'py "%s"' % dst.replace("\\", "/")
    blk = next((m for m in s["hooks"]["PreToolUse"] if m.get("matcher") == "Bash|PowerShell"), None)
    blk["hooks"] = [h for h in blk["hooks"] if "guard_fence.py" not in h.get("command", "")]
    blk["hooks"].insert(0, {"type": "command", "command": cmd, "timeout": 10,
                            "statusMessage": "livebench fence: no shell write into claudeDev outside this arm or into main"})
    with open(sp, "w", encoding="utf-8", newline="") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
    gate("FENCE hook registered first in %s" % sp, json.load(open(sp, encoding="utf-8"))["hooks"]["PreToolUse"]
         [s["hooks"]["PreToolUse"].index(blk)]["hooks"][0]["command"] == cmd)
    r = subprocess.run([sys.executable, dst, "--selftest"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    print(r.stdout.strip(), r.stderr.strip()[-300:], flush=True)
    m = re.search(r"FENCE-SELFTEST .*: (\d+) pass / (\d+) fail", r.stdout)
    gate("FENCE self-test in %s: %s" % (wt, m.group(0) if m else "no summary"), r.returncode == 0 and m and m.group(2) == "0")
    return {"file": ".livebench/guard_fence.py", "md5": md5(dst), "selftest": m.group(0) if m else None}


def fence(arm):
    """Install the shell fence into an EXISTING arm worktree, commit it there, and move setup_<arm>.json's baseline."""
    wt = wt_path(arm)
    sp = os.path.join(HERE, "setup_%s.json" % arm)
    rec = json.load(open(sp, encoding="utf-8"))
    f = install_fence(wt)
    git("add", "-A", cwd=wt)
    if git("status", "--porcelain", cwd=wt):
        git("commit", "-q", "-m", "livebench shell fence (card chat-B7): .livebench/guard_fence.py first in PreToolUse "
            "Bash|PowerShell", cwd=wt)
    rec["setup_commit"], rec["fence"] = git("rev-parse", "HEAD", cwd=wt), f
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    gate("FENCE committed in the worktree, setup baseline moved to %s" % rec["setup_commit"][:10],
         not git("status", "--porcelain", cwd=wt))


def restore_mtimes(wt):
    """`git worktree add` stamps every file with the checkout time, so every mtime-ordered check in the arm (outcome
    cadence, retro-debt, guard_peer's newest failing log) saw 4417 logs 'written today' (hooks_A.json: outcome '11
    retrospectives since', retro-debt '227 build logs, span 0.0 h' - main says 1/5 and ok). Every worktree file that is
    byte-identical to its main-repo file gets the main file's mtime back."""
    n = same = 0
    for rel in git("ls-files", "-z", cwd=wt).split("\0") + \
            [os.path.relpath(p, wt) for g_ in ARMS["ignored_inputs"]["globs"] for p in glob.glob(os.path.join(wt, g_))]:
        if not rel:
            continue
        w, m = os.path.join(wt, rel), os.path.join(MAIN, rel)
        try:
            if os.path.getsize(w) != os.path.getsize(m):
                continue
            if md5(w) != md5(m):
                continue
            st = os.stat(m)
            os.utime(w, (st.st_atime, st.st_mtime))
            same += 1
        except OSError:
            continue
        n += 1
    gate("MTIME %d worktree file(s) byte-identical to main got main's mtime back" % same, same > 1000)
    return same


DUE_NOTE = ("inherited from the main repo at the bench start; cleared identically in every arm (chat decision "
            "2026-10-06: the arms measure build progress, the main repo still owes it separately) - card chat-B7")


def clear_due(wt):
    """Clear the INHERITED due state, identically per arm, through each gate's OWN discharge record (no review is
    faked): violations -> a dated `DECISION: no-device` block per due slug in docs/violation-decisions.md (violations.py
    discharges a slug by a decision newer than its newest retrospective); gate-fp -> every open queue row
    status 'livebench-deferred' (gate_fp.due counts status == open). Outcome and retro-debt are mtime cadences:
    restore_mtimes() returns them to main's state. Returns the record for the manifest / setup json."""
    rec = {"mtimes_restored": restore_mtimes(wt), "violations": [], "gate_fp": [], "note": DUE_NOTE}
    r = subprocess.run([sys.executable, os.path.join("tools", "violations.py"), "--due"], cwd=wt, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    slugs = re.findall(r"^DUE ([a-z0-9-]+): (\d+) occurrences", r.stdout, re.M)
    if slugs:
        stamp = time.strftime("%Y-%m-%d %H:%M")
        blocks = "".join("\n\n## %s — %s (livebench start state, card chat-B7)\n\nDECISION: no-device — %s "
                         "(%s occurrences at the bench start).\n" % (s, stamp, DUE_NOTE, n) for s, n in slugs)
        p = os.path.join(wt, "docs", "violation-decisions.md")
        with open(p, "a", encoding="utf-8", newline="") as f:
            f.write(blocks)
        rec["violations"] = [{"slug": s, "occurrences": int(n), "decision": "no-device", "stamp": stamp} for s, n in slugs]
    q = os.path.join(wt, "tools", "bench", "gate_fp_queue.jsonl")
    if os.path.exists(q):
        rows = [json.loads(ln) for ln in open(q, encoding="utf-8") if ln.strip()]
        for row in rows:
            if row.get("status") == "open":
                row.update({"status": "livebench-deferred", "livebench_note": DUE_NOTE})
                rec["gate_fp"].append(row.get("id"))
        with open(q, "w", encoding="utf-8", newline="") as f:
            f.write("".join(json.dumps(row) + "\n" for row in rows))
    r2 = subprocess.run([sys.executable, os.path.join("tools", "violations.py"), "--due"], cwd=wt, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", timeout=120)
    gate("DUE cleared: violations %s, gate-fp %s; violations --due now lists none" % (
        [v["slug"] for v in rec["violations"]], rec["gate_fp"]), not re.search(r"^DUE ", r2.stdout, re.M), r2.stdout[:200])
    return rec


def record_cleared(arm, rec):
    mp = os.path.join(STATE_DIR, "manifest.json")
    man = json.load(open(mp, encoding="utf-8"))
    man.setdefault("cleared_due", {"rule": "lb_setup.clear_due at setup/clear-due, identical for every arm: " + DUE_NOTE,
                                   "arms": {}})
    man["cleared_due"]["arms"][arm] = {k: v for k, v in rec.items() if k != "note"}
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)


def clear_due_cmd(arm):
    wt = wt_path(arm)
    sp = os.path.join(HERE, "setup_%s.json" % arm)
    rec = json.load(open(sp, encoding="utf-8"))
    cd = clear_due(wt)
    git("add", "-A", cwd=wt)
    if git("status", "--porcelain", cwd=wt):
        git("commit", "-q", "-m", "livebench clear inherited due state (card chat-B7): violations decision blocks, "
            "gate-fp rows deferred; mtimes restored", cwd=wt)
    restore_mtimes(wt)                       # the commit does not touch mtimes; re-run is cheap insurance
    rec["setup_commit"], rec["cleared_due"] = git("rev-parse", "HEAD", cwd=wt), cd
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    record_cleared(arm, cd)
    gate("DUE committed in the worktree, setup baseline moved to %s" % rec["setup_commit"][:10],
         not git("status", "--porcelain", cwd=wt))


def repair(arm):
    """Fixes after the first live launch (2026-10-06 12:07, lb_run_A.log) for an EXISTING worktree: reset to the setup
    baseline (drops the failed launch's runner lines / cycle-144 files; git-ignored sim inputs stay), current-bed = the
    start VI, Error List reads synced, inherited-log list + reaper patches R1/R2, start VI staged; committed; baseline
    moved. The failed launch's main-side records go to livebench/failed_launch_<arm>_*/."""
    wt = wt_path(arm)
    sp = os.path.join(HERE, "setup_%s.json" % arm)
    rec = json.load(open(sp, encoding="utf-8"))
    git("reset", "-q", "--hard", rec["setup_commit"], cwd=wt)
    git("clean", "-fdq", cwd=wt)
    gate("REPAIR %s reset to the setup baseline %s, clean" % (arm, rec["setup_commit"][:10]),
         not git("status", "--porcelain", cwd=wt) and git("rev-parse", "HEAD", cwd=wt) == rec["setup_commit"])
    moved = []
    for nm in ("%s_state.json", "%s_run.json", "%s.json", "%s_snapshots.json", "lb_run_%s.log"):
        p = os.path.join(HERE, nm % arm)
        if os.path.exists(p):
            d = os.path.join(HERE, "failed_launch_%s_20261006_1207" % arm)
            os.makedirs(d, exist_ok=True)
            shutil.move(p, os.path.join(d, os.path.basename(p)))
            moved.append(os.path.basename(p))
    set_current_bed(os.path.join(wt, "STATUS.md"))
    sync_errorlist(wt)
    record_inherited_logs(wt)
    pat = apply_patches(wt, only=("R1", "R2"))
    stage_start_vi(arm)
    git("add", "-A", cwd=wt)
    git("commit", "-q", "-m", "livebench repair (card chat-B7): current-bed = start VI bench copy, Error List reads, "
        "reaper never touches inherited main-repo logs", cwd=wt)
    rec["setup_commit"] = git("rev-parse", "HEAD", cwd=wt)
    rec["patches"] = [p for p in rec["patches"] if not p["label"].startswith(("R1", "R2"))] + pat
    rec["repair"] = {"t": time.strftime("%Y-%m-%d %H:%M:%S"), "moved_failed_launch_records": moved}
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    gate("REPAIR committed, setup baseline moved to %s" % rec["setup_commit"][:10], not git("status", "--porcelain", cwd=wt))


def hooks_child(wt, json_out):
    """In the worktree, with the arm env: the runner's OWN errorlist_hook with subprocess.run made to raise (so the GUI
    read path cannot start LabVIEW: only the offline REUSE branch can return), then gates_due and the cycle card's bed."""
    sys.path.insert(0, os.path.join(wt, "tools"))
    import argparse as _ap
    import importlib
    import tempfile
    CR = importlib.import_module("cycle_runner")
    assert os.path.normcase(os.path.dirname(CR.__file__)) == os.path.normcase(os.path.join(wt, "tools")), CR.__file__
    out = {}
    tmp = tempfile.mkdtemp(prefix="lbhooks_")
    CR.ERRORLIST_REUSE_OUT = tmp
    real_run = CR.subprocess.run

    def no_run(*a, **k):
        raise RuntimeError("GUI-READ path reached (would start LabVIEW): %s" % (a[0] if a else k))
    CR.subprocess.run = no_run
    st_text = open(os.path.join(wt, "STATUS.md"), encoding="utf-8").read()
    rl = os.path.join(tmp, "runner.log")
    a = _ap.Namespace(dry_run=False, dry_cmd="", no_errorlist_hook=False)
    try:
        v, js, why = CR.errorlist_hook(999, a, os.path.join(wt, "tools", "bench"), rl, st_text)
        out["errorlist"] = {"verdict": v, "json": js, "why": why}
    except Exception as e:                                                         # noqa: BLE001
        out["errorlist"] = {"verdict": "RAISED", "why": "%s: %s" % (type(e).__name__, e)}
    CR.subprocess.run = real_run
    out["errorlist_log"] = open(rl, encoding="utf-8").read() if os.path.exists(rl) else ""
    import errorlist_check as EC
    out["bed"] = EC.current_bed_text(st_text)
    _m, card, _w = CR.next_json_reading(os.path.join(wt, "tools", "bench"))
    out["gates_due"] = CR.gates_due(os.path.join(wt, "tools", "bench"), os.path.join(wt, "archive", "peer"), card)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)


def hooks_check(arm):
    wt = wt_path(arm)
    env = dict(os.environ)
    env.update(arm_env(arm, wt))
    env["LIVEBENCH_CONTAIN"] = "enforce"
    env["LIVEBENCH_WRITELOG"] = os.path.join(os.environ.get("TEMP", "."), "lb_hooks_%s_writes.jsonl" % arm)
    jo = os.path.join(os.environ.get("TEMP", "."), "lb_hooks_%s.json" % arm)
    if os.path.exists(jo):
        os.remove(jo)
    before = git("status", "--porcelain", cwd=wt)
    r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "_hooks_child", "--wt", wt, "--json-out", jo],
                       cwd=wt, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    if not gate("HOOKS %s: child wrote its record (rc %d)" % (arm, r.returncode), os.path.exists(jo), (r.stderr or "")[-300:]):
        return
    d = json.load(open(jo, encoding="utf-8"))
    print("HOOKS %s: errorlist %s | bed %s | log %s" % (arm, d["errorlist"], d["bed"], d["errorlist_log"].strip()[:300]),
          flush=True)
    for g_ in d["gates_due"]:
        print("   gates_due %-40s due=%s %s" % (g_["gate"], g_["due"], str(g_["detail"])[:120]), flush=True)
    gate("HOOKS %s: the bed is the start VI's copy in the arm folder" % arm,
         os.path.normcase(str(d["bed"])) == os.path.normcase(os.path.join(out_dir(arm), ARMS["start_vi"]["name"])))
    gate("HOOKS %s: errorlist_hook verdict OK via the offline REUSE path (no GUI read, no LabVIEW)" % arm,
         d["errorlist"]["verdict"] == "OK" and "| REUSE |" in d["errorlist_log"], str(d["errorlist"])[:200])
    gate("HOOKS %s: gates_due ran every check without an error" % arm,
         d["gates_due"] and all(g_["due"] is not None for g_ in d["gates_due"]))
    gate("HOOKS %s: no inherited gate is due at the start (outcome / violations / retro-debt / gate-fp)" % arm,
         not [g_["gate"] for g_ in d["gates_due"] if g_["due"]], str([g_["gate"] for g_ in d["gates_due"] if g_["due"]]))
    with open(os.path.join(HERE, "hooks_%s.json" % arm), "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, default=str)
    gate("HOOKS %s: the check left the worktree unchanged" % arm, git("status", "--porcelain", cwd=wt) == before)


def apply_karpathy(wt):
    sec = open(os.path.join(HERE, "karpathy_principles.md"), encoding="utf-8").read()
    for rel in ARMS["karpathy_targets"]:
        p = os.path.join(wt, rel)
        t = open(p, encoding="utf-8").read()
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(t.rstrip("\n") + "\n\n" + sec)
        gate("KARPATHY section appended to %s" % rel, "## Karpathy coding principles" in open(p, encoding="utf-8").read())


def setup(arm, name=None, commit=None):
    cfg = ARMS["arms"][arm]
    commit = commit or cfg.get("commit")
    if not commit:
        raise SystemExit("arm %s has no commit yet (%s) - pass --commit" % (arm, cfg.get("commit_rule")))
    name = name or arm
    wt = wt_path(name)
    branch = "bench/%s" % name
    if not gate("SETUP %s: worktree path is free and outside the project" % name,
                not os.path.exists(wt) and not os.path.abspath(wt).lower().startswith(MAIN_DIR.lower() + os.sep)):
        raise SystemExit("worktree exists: %s" % wt)
    os.makedirs(ARMS["bench_root"], exist_ok=True)
    full = git("rev-parse", commit)
    git("worktree", "add", "-b", branch, wt, full)
    gate("SETUP worktree at %s on %s (%s)" % (wt, branch, full[:8]), git("rev-parse", "HEAD", cwd=wt) == full)
    man = apply_state(wt, arm)
    settings = repoint_settings(wt)
    pat = apply_patches(wt)
    n_ign = sync_ignored(wt)
    if "karpathy" in cfg.get("extras", []):
        apply_karpathy(wt)
    ov = os.path.join(wt, ".livebench")
    os.makedirs(ov, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "overlay", "sitecustomize.py"), os.path.join(ov, "sitecustomize.py"))
    env = arm_env(arm, wt)
    with open(os.path.join(ov, "arm.json"), "w", encoding="utf-8") as f:
        json.dump({"arm": arm, "name": name, "base_commit": full, "flow": cfg["flow"], "extras": cfg.get("extras", []),
                   "env": env, "card": "chat-B7"}, f, indent=1)
    fence_rec = install_fence(wt)
    record_inherited_logs(wt)
    sync_errorlist(wt)
    stage_start_vi(arm)
    cd_rec = clear_due(wt)
    git("add", "-A", cwd=wt)
    git("commit", "-q", "-m", "livebench setup arm %s (card chat-B7): start state, hooks re-pointed, CLAUDEDEV_OUT patches, "
        "write fence%s" % (arm, ", Karpathy section" if "karpathy" in cfg.get("extras", []) else ""), cwd=wt)
    setup_commit = git("rev-parse", "HEAD", cwd=wt)
    restore_mtimes(wt)
    if not name.startswith("_stub"):
        record_cleared(name, cd_rec)
    rec = {"schema": "livebench-setup/1", "arm": arm, "name": name, "worktree": wt, "branch": branch,
           "base_commit": full, "setup_commit": setup_commit, "flow": cfg["flow"], "extras": cfg.get("extras", []),
           "claudedev_out": out_dir(arm), "start_state_manifest": man, "settings": settings, "patches": pat,
           "ignored_inputs_copied": n_ign, "fence": fence_rec, "cleared_due": cd_rec,
           "overlay_md5": md5(os.path.join(ov, "sitecustomize.py")), "env": env,
           "next_json_md5": md5(os.path.join(wt, "tools", "bench", "next.json")),
           "t": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(HERE, "setup_%s.json" % name), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    gate("SETUP next.json == the fixed purpose", rec["next_json_md5"] == man["files"]["tools/bench/next.json"])
    print("SETUP-DONE %s %s setup_commit %s" % (name, wt, setup_commit[:10]), flush=True)
    return rec


def arm_env(arm, wt, root=None, out=None):
    return {"PYTHONPATH": os.path.join(wt, ".livebench"), "LIVEBENCH_ARM": arm,
            "LIVEBENCH_CLAUDEDEV": out or out_dir(arm), "LIVEBENCH_CLAUDEDEV_ROOT": root or CD_ROOT,
            "LIVEBENCH_MAIN": MAIN_DIR, "LIVEBENCH_WRITELOG": os.path.join(wt, "tools", "bench", "livebench_writes.jsonl"),
            "LIVEBENCH_CONTAIN": "enforce"}


def snapshot(force=False):
    if os.path.exists(os.path.join(STATE_DIR, "manifest.json")) and not force:
        raise SystemExit("start state already frozen (%s) - every arm must start from the same bytes" % STATE_DIR)
    os.makedirs(STATE_DIR, exist_ok=True)
    files = {}
    for rel in STATE_FILES:
        src = os.path.join(MAIN, rel)
        dst = os.path.join(STATE_DIR, rel.replace("/", "__"))
        shutil.copyfile(src, dst)
        files[rel] = md5(dst)
        gate("SNAPSHOT %s" % rel, md5(src) == files[rel])
    for rel in STATE_ABSENT:
        gate("SNAPSHOT %s absent in the main tree" % rel, not os.path.exists(os.path.join(MAIN, rel)))
    man = {"schema": "livebench-start/1", "from": MAIN, "head": git("rev-parse", "HEAD"), "files": files,
           "absent": STATE_ABSENT, "t": time.strftime("%Y-%m-%d %H:%M:%S"),
           "start_vi": ARMS["start_vi"], "purpose_act": json.load(open(os.path.join(MAIN, "tools", "bench", "next.json"),
                                                                       encoding="utf-8")).get("act")}
    with open(os.path.join(STATE_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)


# ------------------------------------------------------------------ containment dry run
def contain_child(wt, recipe, json_out):
    sys.path.insert(0, os.path.join(wt, "tools"))
    import importlib
    SP = importlib.import_module("stage_prerun")
    assert os.path.normcase(os.path.dirname(os.path.abspath(SP.__file__))) == os.path.normcase(os.path.join(wt, "tools")), SP.__file__
    rec = {"writes": [], "calls": []}
    orig_out, orig_stub = SP._outside_temp, SP._stub

    def outside(p):
        rec["writes"].append(str(p))
        return orig_out(p)

    def stub(name):
        f = orig_stub(name)
        if re.search(r"save|copy", name.split(".")[-1], re.I):
            def g(*a, **k):
                rec["calls"].append({"name": name, "args": [str(x)[:300] for x in a[:2]]})
                return f(*a, **k)
            g.__name__, g._dry = f.__name__, True
            return g
        return f
    SP._outside_temp, SP._stub = outside, stub
    tr = SP.dry(os.path.join(wt, recipe))
    out = {"status": tr.get("status"), "first_fail": tr.get("first_fail"), "works": tr.get("works"),
           "discards": tr.get("discards"), "saves": tr.get("saves"), "blocked": tr.get("blocked"),
           "input_vi": tr.get("input_vi"), "reached_end": tr.get("reached_end"), "coverage": tr.get("coverage"),
           "writes": rec["writes"], "save_copy_calls": rec["calls"],
           "claudedev_out_const": getattr(sys.modules.get("gscript"), "CLAUDEDEV_OUT", None)}
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)


def classify(p, out, root=CD_ROOT, main=MAIN_DIR):
    n = os.path.normcase(os.path.abspath(p))
    u = lambda d: n == os.path.normcase(d) or n.startswith(os.path.normcase(d).rstrip("\\/") + os.sep)  # noqa: E731
    if u(out):
        return "arm"
    if u(os.path.join(root, "NIScriptingExamples", "Moving Objects")):
        return "fixture"
    if u(root):
        return "outside"
    if u(main):
        return "main"
    return "other"


def contain_dry(arm, name=None, recipe=RECIPE, counterfactual=False):
    name = name or arm
    wt = wt_path(name)
    res = {}
    runs = [("arm", wt, arm_env(arm, wt))]
    if counterfactual:
        runs.append(("main-unpatched", MAIN, {"LIVEBENCH_CLAUDEDEV": out_dir(arm)}))
    for tag, cwd, extra in runs:
        env = dict(os.environ)
        env.update(extra)
        env["LIVEBENCH_CONTAIN"] = "log"
        env["LIVEBENCH_WRITELOG"] = os.path.join(os.environ.get("TEMP", "."), "lb_contain_%s_%s.jsonl" % (name, tag))
        jo = os.path.join(os.environ.get("TEMP", "."), "lb_contain_%s_%s.json" % (name, tag))
        if os.path.exists(jo):
            os.remove(jo)
        r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "_contain_child", "--wt", cwd, "--recipe", recipe,
                            "--json-out", jo], cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        if not gate("CONTAIN %s: dry child wrote its record (rc %d)" % (tag, r.returncode), os.path.exists(jo),
                    (r.stderr or r.stdout)[-300:]):
            continue
        d = json.load(open(jo, encoding="utf-8"))
        paths = list(d["writes"]) + [x for c in d["save_copy_calls"] for x in c["args"] if re.search(r"\.vi$", x, re.I)]
        cls = {}
        for p in paths:
            cls.setdefault(classify(p, out_dir(arm)), []).append(p)
        works = [classify(w, out_dir(arm)) for w in d.get("works") or []]
        d["by_class"] = {k: sorted(set(v)) for k, v in cls.items()}
        d["works_class"] = works
        res[tag] = d
        print("CONTAIN %s: dry %s (first_fail %s); works %s; classes %s" % (
            tag, d["status"], str(d["first_fail"])[:120], d.get("works"), {k: len(v) for k, v in d["by_class"].items()}),
            flush=True)
        for k in ("outside", "main", "arm"):
            for p in d["by_class"].get(k, [])[:6]:
                print("   %-8s %s" % (k, p), flush=True)
        saves = [x for c in d["save_copy_calls"] if re.search(r"save", c["name"], re.I) for x in c["args"]
                 if re.search(r"\.vi$", x, re.I)]
        print("CONTAIN %s: save calls %s" % (tag, saves), flush=True)
        if tag == "arm":
            gate("CONTAIN arm: the dry reached its end (status %s)" % d["status"], str(d["status"]).startswith("PASS"),
                 str(d["first_fail"])[:200])
            gate("CONTAIN arm: the dry's saves %s act on the Stage work copy (in the stub, Stage.save saves self.work)"
                 % d.get("saves"), bool(d.get("saves")) and works and all(w == "arm" for w in works)
                 and all(classify(x, out_dir(arm)) == "arm" for x in saves))
            gate("CONTAIN arm: gscript.CLAUDEDEV_OUT (the save/gui_save fence, patch G4) == the arm folder",
                 os.path.normcase(str(d.get("claudedev_out_const"))) == os.path.normcase(out_dir(arm)),
                 str(d.get("claudedev_out_const")))
            gate("CONTAIN arm: the dry reached a Stage work copy", bool(works))
            gate("CONTAIN arm: every Stage work copy is under %s" % out_dir(arm), works and all(w == "arm" for w in works))
            gate("CONTAIN arm: no write resolves under claudeDev outside the arm folder", not cls.get("outside"))
            gate("CONTAIN arm: no write resolves into the main project", not cls.get("main"))
        else:
            gate("CONTAIN counterfactual: the UNPATCHED main tree puts the work copy in the claudeDev root",
                 works and all(w == "outside" for w in works), str(d.get("works")))
    with open(os.path.join(HERE, "contain_%s.json" % name), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


# ------------------------------------------------------------------ stub dry run of the whole runner
def stub(arm, keep=False):
    name = "_stub_" + arm
    if os.path.exists(wt_path(name)):
        teardown(name)
    rec = setup(arm, name=name)
    wt = rec["worktree"]
    tmp = os.path.join(os.environ.get("TEMP", "."), "lbstub_%s" % time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(tmp)
    stubpy = os.path.join(tmp, "stub_claude.py")
    shutil.copyfile(os.path.join(HERE, "stub_claude.py"), stubpy)
    if not gate("STUB stand-in paths carry no space (cycle_runner whitespace-splits --dry-cmd)",
                " " not in sys.executable and " " not in stubpy, "%s | %s" % (sys.executable, stubpy)):
        raise SystemExit(1)
    root, out = os.path.join(tmp, "claudeDev"), os.path.join(tmp, "claudeDev", "bench", arm)
    os.makedirs(out)
    env = dict(os.environ)
    for k in ("CYCLE_SESSION", "CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_RESULT", "ASSIGN_CONFIG", "PURPOSE_PHASE",
              "HANDBACK_RECORD", "BENCH_CELL"):
        env.pop(k, None)
    env.update(arm_env(arm, wt, root=root, out=out))
    env["LIVEBENCH_STUB_TRANSCRIPTS"] = os.path.join(tmp, "transcripts")
    t0 = time.time()
    cmd = [sys.executable, "-u", os.path.join("tools", "cycle_runner.py"), "--cycles", "2", "--flow", rec["flow"],
           "--max-min", "5", "--dry-cmd", "%s %s judge" % (sys.executable, stubpy),
           "--assign-dry-cmd", "%s %s assign" % (sys.executable, stubpy)]
    r = subprocess.run(cmd, cwd=wt, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    t1 = time.time()
    with open(os.path.join(HERE, "stub_%s_runner.out" % arm), "w", encoding="utf-8") as f:
        f.write(r.stdout + "\n--- stderr ---\n" + r.stderr)
    rl = open(os.path.join(wt, "tools", "bench", "cycle_runner.log"), encoding="utf-8", errors="replace").read()
    new = rl[rl.rfind("JUDGE-LADDER | " + time.strftime("%Y-%m-%d", time.localtime(t0))):] if rl else ""
    gate("STUB runner exit 0 (rc %d)" % r.returncode, r.returncode == 0, r.stderr[-300:])
    gate("STUB runner ran 2 cycles", len(re.findall(r"^CYCLE \d+ \|", rl[-20000:], re.M)) >= 2 and "--cycles 2 exhausted" in rl)
    if rec["flow"] == "purpose":
        gate("STUB assignment rounds ended PURPOSE_MET in both cycles", rl.count("| PURPOSE_MET") >= 2)
    wl = os.path.join(wt, "tools", "bench", "livebench_writes.jsonl")
    fence = open(wl, encoding="utf-8").read() if os.path.exists(wl) else ""
    gate("STUB fence refused the write outside the arm folder", '"class": "outside", "refused": true' in fence)
    gate("STUB fence allowed + logged the arm-folder write", '"class": "arm"' in fence)
    out_json = os.path.join(HERE, "stub_%s.json" % arm)
    c = subprocess.run([sys.executable, "-u", os.path.join(HERE, "lb_collect.py"), "--worktree", wt, "--arm", arm,
                        "--setup-commit", rec["setup_commit"], "--t0", str(t0), "--t1", str(t1), "--claudedev-out", out,
                        "--transcripts", os.path.join(tmp, "transcripts"), "--writelog", wl, "--flow", rec["flow"],
                        "--extras", ",".join(rec["extras"]), "--start-vi", json.dumps(ARMS["start_vi"]), "--stub",
                        "--out", out_json], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(c.stdout.strip(), c.stderr.strip()[-400:], flush=True)
    if gate("STUB metrics JSON written", c.returncode == 0 and os.path.exists(out_json)):
        m = json.load(open(out_json, encoding="utf-8"))
        pp = m["plan_progress"]
        gate("STUB metrics: plan_progress first, 2 cycles, cards 3 (2 PASS 1 FAIL), early catches w1+g1 per cycle, "
             "P4 ops 78/190 sessions 3/6, 2 re-plans (M3->M8->M3), 1 LabVIEW stage run per cycle, 2 saved VIs, fence refusals 2",
             list(m)[:9][-2:] == ["plan_progress", "secondary"] and len(m["cycles"]) == 2 and m["cards"]["issued"] == 3
             and m["cards"]["by_status"] == {"PASS": 2, "FAIL": 1}
             and m["early_catches"]["guard_write"]["count"] == 2 and m["early_catches"]["launch_gates"]["count"] == 2
             and pp["m3_detail"]["p4_ops_adopted"] == 78 and pp["m3_detail"]["p4_sessions_adopted"] == 3
             and len(pp["replans"]) == 2 and m["labview_runs"]["count"] == 2 and len(m["saved_vis"]) == 2
             and len(m["containment"]["refused"]) == 2,
             json.dumps({"cards": m["cards"]["by_status"], "w": m["early_catches"]["guard_write"]["count"],
                         "g": m["early_catches"]["launch_gates"]["count"], "ops": pp["m3_detail"]["p4_ops_adopted"],
                         "sess": pp["m3_detail"]["p4_sessions_adopted"], "replans": pp["replans"],
                         "lv": m["labview_runs"]["count"], "vis": len(m["saved_vis"]),
                         "refused": len(m["containment"]["refused"])}))
    if not keep:
        teardown(name)
        os.remove(os.path.join(HERE, "setup_%s.json" % name))
    shutil.rmtree(tmp, ignore_errors=True)
    return new


def teardown(name):
    wt = wt_path(name)
    if os.path.exists(wt):
        git("worktree", "remove", "--force", wt, check=False)
        shutil.rmtree(wt, ignore_errors=True)
        git("worktree", "prune", check=False)
    git("branch", "-D", "bench/%s" % name, check=False)
    gate("TEARDOWN %s: worktree and branch gone" % name, not os.path.exists(wt) and
         not git("branch", "--list", "bench/%s" % name, check=False))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("snapshot", "setup", "sync-ignored", "fence", "repair", "clear-due", "hooks-check",
                                    "contain-dry",
                                    "stub", "teardown", "_contain_child", "_hooks_child"))
    ap.add_argument("arm", nargs="?")
    ap.add_argument("--commit")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--counterfactual", action="store_true")
    ap.add_argument("--recipe", default=RECIPE)
    ap.add_argument("--wt")
    ap.add_argument("--json-out")
    a = ap.parse_args(argv)
    if a.cmd == "_contain_child":
        contain_child(a.wt, a.recipe, a.json_out)
        return 0
    if a.cmd == "_hooks_child":
        hooks_child(a.wt, a.json_out)
        return 0
    if a.cmd == "snapshot":
        snapshot(a.force)
    elif a.cmd == "setup":
        setup(a.arm, commit=a.commit)
    elif a.cmd == "sync-ignored":
        n = sync_ignored(wt_path(a.arm))
        sp = os.path.join(HERE, "setup_%s.json" % a.arm)
        if os.path.exists(sp):
            rec = json.load(open(sp, encoding="utf-8"))
            rec["ignored_inputs_copied"] = n
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(rec, f, indent=1)
    elif a.cmd == "fence":
        fence(a.arm)
    elif a.cmd == "repair":
        repair(a.arm)
    elif a.cmd == "clear-due":
        clear_due_cmd(a.arm)
    elif a.cmd == "hooks-check":
        hooks_check(a.arm)
    elif a.cmd == "contain-dry":
        contain_dry(a.arm, recipe=a.recipe, counterfactual=a.counterfactual)
    elif a.cmd == "stub":
        stub(a.arm, a.keep)
    elif a.cmd == "teardown":
        teardown(a.arm)
    sys.path.insert(0, TOOLS)
    import protocol                      # the MAIN tree's protocol; never imported in the _contain_child (worktree) process
    npass = sum(1 for _l, ok in GATES if ok)
    nfail = len(GATES) - npass
    first = next((lab for lab, ok in GATES if not ok), None)
    print(protocol.result_line(protocol.make_result(npass, nfail, first)), flush=True)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
