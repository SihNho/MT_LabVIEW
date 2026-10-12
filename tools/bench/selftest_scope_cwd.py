# ---
# labview: none
# hardware: none
# ---
"""Self-test: scope-cwd-fix-20261012 (card chat-X11; Claude + GPT agreed in tools/bench/debate/scope-cwd-fix/relay
round_06_claude.md / round_06_gpt.md; user 2026-10-12 "동의 받고 고쳐").

Prediction contract (every line below is one gate):
  A. cwd = ROOT (the main tree): the representative ordinary command `py tools/debate_gdoc.py say ...` keeps today's
     verdict (allowed without a timeout), also with a differently spelled ROOT (slashes / case / trailing separator).
  B. cwd = ROOT, no timeout exemption when the command changes folder (cd / Set-Location / pushd / Push-Location, also
     inside a nested powershell -Command) or mixes an unconfirmed tools/ launch (a missing file) or a script outside
     the cwd's tools/ - refused, and WITHOUT the absolute-path hint.
  C. cwd = a fake bench cell (a temp folder with its own tools/): a relative `py tools/x.py` (labview none) is refused
     WITH the absolute-path hint; the drive-absolute path is allowed (plain, nested powershell, bgrun child with an
     absolute child); a relative bgrun child is refused with the hint.
  D. cwd = cell: a labview build script (absolute) is refused without the hint; a script outside the cell's tools/
     (the main tree's, or another tools/ folder below the cell) is refused; a dishonest `labview: none` header (imports
     gscript) is a scope_gate refusal ("not honest"), absolute or relative.
  E. no cwd in the payload: today's verdicts exactly - the say passes, the say mixed with a missing tools/ file still
     passes (the old rule), a cell-relative script is not seen.
  F. guardcore R4 (labview_launches) sees a cell's labview build script through the cwd; without cwd it does not.
Feeds tools/hooks/guard_bash.py real PreToolUse JSON in a subprocess (as tools/bench/selftest_guard_bash_codex.py does);
the cell lives in %TEMP% and is removed at the end."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
HOOK = os.path.join(ROOT, "tools", "hooks", "guard_bash.py")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
SAY = 'py tools/debate_gdoc.py say --dir tools/bench/debate/x/relay "hi"'
HDR = "# ---\n# labview: %s\n# hardware: none\n# ---\n"


def make_cell():
    cell = tempfile.mkdtemp(prefix="x11_cell_")
    os.makedirs(os.path.join(cell, "tools"))
    os.makedirs(os.path.join(cell, "sub", "tools"))
    files = {
        ("tools", "none_ok.py"): HDR % "none" + "print('ok')\n",
        ("tools", "lv_build.py"): HDR % "build" + "print('lv')\n",
        ("tools", "liar.py"): HDR % "none" + "import gscript\nprint('x')\n",
        ("tools", "bgrun.py"): HDR % "none" + "print('stub bgrun, never run')\n",
        ("sub", "tools", "none2.py"): HDR % "none" + "print('ok2')\n",
    }
    for parts, body in files.items():
        with open(os.path.join(cell, *parts), "w", encoding="utf-8") as f:
            f.write(body)
    return cell


def hook(cmd, cwd="__none__", ti_extra=None):
    ev = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": dict({"command": cmd}, **(ti_extra or {}))}
    if cwd != "__none__":
        ev["cwd"] = cwd
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(ev), capture_output=True, text=True, encoding="utf-8",
                       timeout=90)
    return p.returncode, (p.stderr or "").strip().replace("\n", " ")


def main():
    cell = make_cell()
    t = os.path.join(cell, "tools")
    q = lambda p: '"%s"' % p                                       # noqa: E731
    ok_abs, lv_abs, liar_abs = (os.path.join(t, n) for n in ("none_ok.py", "lv_build.py", "liar.py"))
    bg_abs = os.path.join(t, "bgrun.py")
    root_alt = ROOT.replace("\\", "/").lower() + "/"
    # (name, cmd, cwd, expect: "allow" | "block" | "hint" | "honest")
    cases = [
        ("A1 root say", SAY, ROOT, "allow"),
        ("A2 root say, ROOT spelled /, lower, trailing", SAY, root_alt, "allow"),
        ("A3 root say in nested powershell", 'powershell.exe -NoProfile -Command "%s"' % SAY.replace('"', '\\"'), ROOT,
         "allow"),
        ("B1 root cd then say", "cd tools && " + SAY, ROOT, "block"),
        ("B2 root Set-Location then say", "Set-Location tools; " + SAY, ROOT, "block"),
        ("B3 root pushd then say", "pushd tools && " + SAY, ROOT, "block"),
        ("B4 root Push-Location then say", "Push-Location x; " + SAY, ROOT, "block"),
        ("B5 root nested powershell cd", 'powershell -Command "cd tools; py tools/debate_gdoc.py say x"', ROOT, "block"),
        ("B6 root say + missing tools/ file", SAY + " ; py tools/no_such_x11_file.py", ROOT, "block"),
        ("B7 root say + script outside ROOT tools/", SAY + " ; py " + q(os.path.join(cell, "sub", "tools", "none2.py")),
         ROOT, "block"),
        ("C1 cell relative none", "py tools/none_ok.py", cell, "hint"),
        ("C2 cell absolute none", "py " + q(ok_abs), cell, "allow"),
        ("C3 cell absolute none, nested powershell", "powershell -Command \"py '%s'\"" % ok_abs, cell, "allow"),
        ("C4 cell bgrun abs + abs child", "py %s --max-min 1 --log x.log -- py -u %s" % (q(bg_abs), q(ok_abs)), cell,
         "allow"),
        ("C5 cell bgrun abs + relative child", "py %s --max-min 1 --log x.log -- py -u tools/none_ok.py" % q(bg_abs),
         cell, "hint"),
        ("C6 cell relative none, nested powershell", 'powershell -Command "py tools/none_ok.py"', cell, "hint"),
        ("D1 cell absolute labview build", "py " + q(lv_abs), cell, "block"),
        ("D2 cell absolute main-tree script", 'py "%s" say --dir x "hi"' % os.path.join(ROOT, "tools", "debate_gdoc.py"),
         cell, "block"),
        ("D3 cell absolute sub/tools script", "py " + q(os.path.join(cell, "sub", "tools", "none2.py")), cell, "block"),
        ("D4 cell abs none + cd", "cd tools; py " + q(ok_abs), cell, "block"),
        ("D5 cell absolute dishonest header", "py " + q(liar_abs), cell, "honest"),
        ("D6 cell relative dishonest header", "py tools/liar.py", cell, "honest"),
        ("E1 no cwd say", SAY, "__none__", "allow"),
        ("E2 no cwd say + missing tools/ file (old rule)", SAY + " ; py tools/no_such_x11_file.py", "__none__", "allow"),
        ("E3 no cwd cell-relative script (not seen)", "py tools/none_ok.py", "__none__", "block"),
    ]
    fails = 0
    try:
        for name, cmd, cwd, exp in cases:
            rc, err = hook(cmd, cwd)
            hinted = "ABSOLUTE path" in err
            if exp == "allow":
                good = rc == 0
            elif exp == "block":
                good = rc == 2 and "2b" in err and not hinted
            elif exp == "hint":
                good = rc == 2 and "2b" in err and hinted
            else:
                good = rc == 2 and "not honest" in err
            fails += not good
            print("%s  %-46s rc=%d %s" % ("PASS" if good else "FAIL", name, rc, "" if good else err[:300]), flush=True)
        import guardcore                                             # noqa: E402
        cmd = "py tools/lv_build.py"
        with_cwd, without = guardcore.labview_launches(cmd, cell), guardcore.labview_launches(cmd)
        good = len(with_cwd) == 1 and with_cwd[0][1] == "build" and without == []
        fails += not good
        print("%s  %-46s with=%s without=%s" % ("PASS" if good else "FAIL", "F1 guardcore R4 reads the cell via cwd",
                                                with_cwd, without), flush=True)
        total = len(cases) + 1
    finally:
        shutil.rmtree(cell, ignore_errors=True)
    print("RESULT %s" % json.dumps({"schema": "result-line/1", "status": "PASS" if not fails else "FAIL",
                                    "gates": {"pass": total - fails, "fail": fails}}), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
