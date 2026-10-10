# ---
# labview: none
# hardware: none
# ---
r"""selftest_shellguard_cand - card chat-X9 (discussion structure-equal-02 round 10): isolated test of the CANDIDATE
shell-write refusal (tools/bench/candidates/cand-shellguard-01/files/tools/hooks/: protected_write.py new, guard_bash.py,
guardcore.py, guard_card.py changed; adapt_codex.py / adapt_claude.py unchanged copies = the entry points) and of the
bundle-bound tokens / hash-chained ledger in tools/rules_apply.py. OFFLINE: no LabVIEW, no hardware; no command under
test is ever EXECUTED - each is only JUDGED by the candidate hook (real PreToolUse JSON on stdin, one subprocess per call,
Claude format and the recorded Codex format tools/bench/guardcore_fake/codex_payloads.jsonl:1).
The active hooks are never imported: the candidate scripts are run from the candidate folder (or a byte copy in a temp
fake tree); unchanged sibling modules (guard_session, protocol, ...) resolve through PYTHONPATH as they will once installed.

PREDICTION CONTRACT (any false line fails the run):
  S1 every protected shell-write form (redirect, Set/Add-Content, Out-File, New/Remove/Copy/Move/Rename-Item, cp, mv, rm,
     tee, sed -i, git checkout/restore --, py -c, nested bash/powershell -c, absolute + backslash paths, ledger, agent
     definitions, settings.local.json, recursive directory delete) is DENIED by the candidate guard_bash for the Claude
     payload, for the Codex payload, and by the candidate adapt_codex (guardcore chain), each reason naming protected files;
  S2 the same verbs on unprotected paths, and reads of protected files, are ALLOWED on all three routes;
  A1 on a temp fake tree, `py tools/rules_apply.py apply <bundle-id>` of an agreed, tested, unused bundle is ALLOWED;
     DENIED: another executable path, a modified rules_apply.py, a missing bundle, an unagreed bundle, a bundle with a
     target outside the protected globs, extra arguments / a second segment / --root on the real tree, a used token;
  T1 rules_apply: token reuse refused (token-unused), changed manifest after agreement refused (bundle-hash), a change
     between check and write refused (prehash), nothing written in each case;
  L1-L6 audit: clean chain passes; an edited earlier line breaks the chain; a forged appended line without agreement, a
     line re-using a token, a changed relay file, an edited last line (bundle + committed-prefix) are all flagged;
  W1 .claude/settings.local.json: Write / Edit / MultiEdit / NotebookEdit (candidate guard_card and adapt_claude) and
     apply_patch (candidate adapt_codex) DENIED; a Write to an unprotected path ALLOWED;
  M1 md5 of every active tools/hooks, .codex, .claude (worktrees excluded) and protected file identical before and after.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_shellguard_cand.log -- py -u tools/bench/selftest_shellguard_cand.py
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
B = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(B)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import protocol as P                                                                    # noqa: E402
import rules_apply as RA                                                                # noqa: E402

CID = "cand-shellguard-01"
CH = os.path.join(RA.cand_dir(ROOT, CID), "files", "tools", "hooks")
CAND_FILES = ["protected_write.py", "guard_bash.py", "guardcore.py", "guard_card.py", "adapt_codex.py", "adapt_claude.py"]
TMPLOG = tempfile.mkdtemp(prefix="shellguard_logs_")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", JEV_ADVISORY_OFF="1",
           GUARDCORE_LOG=os.path.join(TMPLOG, "guardcore.log"),
           PYTHONPATH=os.pathsep.join([os.path.join(TOOLS, "hooks"), TOOLS]))
for k in ("CYCLE_SESSION", "LV_GUARD_OFF", "BENCH_CELL", "GUARDCORE_ASSUME_LABVIEW", "GUARDCORE_CODEX_RAW"):
    ENV.pop(k, None)
with open(os.path.join(B, "guardcore_fake", "codex_payloads.jsonl"), encoding="utf-8") as _f:
    CODEX_T = json.loads(_f.readline())
SID = "shellguard_%d" % int(time.time())
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det).replace("RESULT {", "result {")[:400]),
          flush=True)


def claude(tool, ti, cwd):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti, "session_id": SID, "cwd": cwd}


def codex(tool, ti, cwd):
    d = dict(CODEX_T)
    d.update(tool_name=tool, tool_input=ti, cwd=cwd, session_id=SID)
    return d


def hook(script, payload):
    """(denied, reason) of one candidate hook run as a subprocess on the payload."""
    p = subprocess.run([sys.executable, script], input=json.dumps(payload), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=ENV, timeout=240)
    out = (p.stdout or "").strip()
    if out.startswith("{"):
        try:
            h = json.loads(out).get("hookSpecificOutput") or {}
            if h.get("permissionDecision") == "deny":
                return True, h.get("permissionDecisionReason") or ""
        except ValueError:
            pass
    return p.returncode == 2, (p.stderr or "").strip()


def routes(hooks_dir, cmd, shell, cwd):
    """[(route, denied, reason)] for the three shell routes."""
    gb, ac = os.path.join(hooks_dir, "guard_bash.py"), os.path.join(hooks_dir, "adapt_codex.py")
    return [("claude:" + shell, *hook(gb, claude(shell, {"command": cmd, "timeout": 20000}, cwd))),
            ("codex:guard_bash", *hook(gb, codex("Bash", {"command": cmd}, cwd))),
            ("codex:guardcore", *hook(ac, codex("Bash", {"command": cmd}, cwd)))]


def expect(label, hooks_dir, cmd, shell, cwd, deny, word="protected"):
    r = routes(hooks_dir, cmd, shell, cwd)
    if deny:
        ok = all(d and word in why for _, d, why in r)
    else:
        ok = not any(d for _, d, _ in r)
    gate(label, ok, "%s | %s" % (cmd[:90], "; ".join("%s=%s %s" % (n, "DENY" if d else "allow", w[:110] if (d != deny or
                                                         not ok) else "") for n, d, w in r)))


def active_md5s():
    """{rel: md5} of every active hook / .codex / .claude file (worktrees excluded) and every protected file."""
    out = {}
    for top in ("tools/hooks", ".codex", ".claude"):
        for dp, dns, fns in os.walk(os.path.join(ROOT, top)):
            dns[:] = [d for d in dns if d not in ("worktrees", "__pycache__")]
            for fn in fns:
                rel = os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/")
                if not rel.endswith(".log"):
                    out[rel] = RA.md5_file(os.path.join(ROOT, rel))
    for rel in RA.protected_files(ROOT, RA.load_protected(ROOT)):
        out[rel] = RA.md5_file(os.path.join(ROOT, rel))
    return out


# ------------------------------------------------------------------ S1 / S2 on the real tree (judged only)
ABS = os.path.join(ROOT, "CLAUDE.md")
PROT = [
    ("redirect >", "echo x > CLAUDE.md", "Bash"),
    ("redirect >>", "echo x >> tools/hooks/guard_bash.py", "Bash"),
    ("redirect ps", "'x' > docs/rules/new.md", "PowerShell"),
    ("Set-Content", "Set-Content -Path CLAUDE.md -Value x", "PowerShell"),
    ("Add-Content", "Add-Content AGENTS.md 'x'", "PowerShell"),
    ("Out-File", "'x' | Out-File -FilePath docs/rules/a.md", "PowerShell"),
    ("New-Item", "New-Item -ItemType File -Path tools/hooks/new_guard.py -Force", "PowerShell"),
    ("Remove-Item", "Remove-Item tools/hooks/guard_card.py", "PowerShell"),
    ("Copy-Item", "Copy-Item tools/bench/selftest_x.py tools/hooks/guard_card.py", "PowerShell"),
    ("Move-Item", "Move-Item tools/hooks/guard_card.py tools/bench/x.py", "PowerShell"),
    ("Rename-Item", "Rename-Item -Path tools/hooks/guard_card.py -NewName old.py", "PowerShell"),
    ("cp", "cp /tmp/x tools/hooks/guard_bash.py", "Bash"),
    ("mv", "mv AGENTS.md AGENTS.bak", "Bash"),
    ("rm", "rm -f .codex/hooks.json", "Bash"),
    ("tee", "echo x | tee -a CLAUDE.md", "Bash"),
    ("sed -i", "sed -i 's/a/b/' CLAUDE.md", "Bash"),
    ("git checkout --", "git checkout -- tools/hooks/guard_bash.py", "Bash"),
    ("git restore", "git restore CLAUDE.md", "Bash"),
    ("git checkout rev --", "git checkout HEAD~1 -- docs/rules/reviews.md", "Bash"),
    ("py -c open w", "py -c \"open('CLAUDE.md','w').write('x')\"", "Bash"),
    ("python -c pathlib", "python -c \"import pathlib; pathlib.Path('tools/hooks/guardcore.py').write_text('x')\"", "Bash"),
    ("py heredoc", "py - <<'EOF'\nopen('AGENTS.md','a').write('x')\nEOF", "Bash"),
    ("bash -c nested", "bash -c 'echo x > CLAUDE.md'", "Bash"),
    ("powershell -Command nested", "powershell -NoProfile -Command \"Set-Content CLAUDE.md x\"", "PowerShell"),
    ("absolute path", "Set-Content -LiteralPath \"%s\" -Value x" % ABS, "PowerShell"),
    ("backslash path", "Remove-Item tools\\hooks\\guard_card.py", "PowerShell"),
    ("cd then write", "cd tools/hooks && echo x > guard_bash.py", "Bash"),
    ("ledger append", "echo {} >> tools/bench/rules_ledger.jsonl", "Bash"),
    ("agent definition", "Set-Content .claude/agents/material.md x", "PowerShell"),
    ("codex agent definition", "rm .codex/agents/bench-opus-high.toml", "Bash"),
    ("settings.local shell", "Set-Content .claude/settings.local.json '{}'", "PowerShell"),
    ("settings.local redirect", "echo {} > .claude/settings.local.json", "Bash"),
    ("rm -rf dir", "rm -rf tools/hooks", "Bash"),
    ("Remove-Item -Recurse dir", "Remove-Item -Recurse .claude", "PowerShell"),
    ("wildcard", "rm tools/hooks/*.py", "Bash"),
    ("rules_protected.json", "Set-Content tools/rules_protected.json '{}'", "PowerShell"),
    ("rules_apply --root real", "py tools/rules_apply.py --root . apply cand-shellguard-01@0123abcd", "Bash"),
    ("rules_apply copy", "py tools/bench/candidates/rules_apply.py apply cand-shellguard-01@0123abcd", "Bash"),
    ("rules_apply baseline", "py tools/rules_apply.py audit --baseline", "Bash"),
    ("git reset --hard", "git reset --hard HEAD", "Bash"),
    ("cp into protected dir", "cp tools/bench/selftest_x.py tools/hooks/", "Bash"),
]
FREE = "tools/bench/guardcore_fake"
CTRL = [
    ("redirect free", "echo x > %s/sg_marker.txt" % FREE, "Bash"),
    ("Set-Content free", "Set-Content -Path %s/sg_m.txt -Value x" % FREE, "PowerShell"),
    ("cp protected -> free", "cp CLAUDE.md %s/claude_copy.md" % FREE, "Bash"),
    ("Get-Content | Out-File free", "Get-Content CLAUDE.md | Out-File %s/c.txt" % FREE, "PowerShell"),
    ("cat protected", "cat tools/hooks/guard_bash.py", "Bash"),
    ("grep protected", "grep -n x CLAUDE.md 2>/dev/null", "Bash"),
    ("git diff protected", "git diff -- CLAUDE.md", "Bash"),
    ("py -c read", "py -c \"print(open('CLAUDE.md').read()[:10])\"", "Bash"),
    ("py -c write free", "py -c \"open(r'%s/marker_allowed.txt','w').write('ok')\"" % FREE, "Bash"),
    ("rm free", "rm -f %s/sg_marker.txt" % FREE, "Bash"),
    ("rm wildcard free", "rm tools/bench/*.tmp", "Bash"),
    ("rules_apply audit", "py tools/rules_apply.py audit", "Bash"),
    ("git status", "git status --short", "Bash"),
    ("cp hook -> candidate folder", "cp tools/hooks/guard_bash.py %s/files/tools/hooks/" % (RA.CAND_REL + "/" + CID),
     "Bash"),
]


def real_tree():
    for lab, cmd, sh in PROT:
        expect("S1 deny " + lab, CH, cmd, sh, ROOT, True)
    for lab, cmd, sh in CTRL:
        expect("S2 allow " + lab, CH, cmd, sh, ROOT, False)


# ------------------------------------------------------------------ fake tree: rules_apply exception, T, L
def write(root, rel, text):
    f = os.path.join(root, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def ra(root, *args):
    p = subprocess.run([sys.executable, os.path.join(root, "tools", "rules_apply.py"), "--root", root] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV, timeout=120)
    return p.returncode, p.stdout + p.stderr


def relay(root, deb, rnd, toks):
    st = {"agreed": list(toks), "open": [], "questions": [], "experiment": "", "user_needed": "", "check": "",
          "done": True}
    for side in ("claude", "gpt"):
        write(root, "%s/relay/round_%02d_%s.md" % (deb, rnd, side), "text\n\nSTATE " + json.dumps(st, ensure_ascii=False)
              + "\n")


def bundle(root, cid, rnd, changes, agree=True):
    """Stage + test + (optionally) agree a bundle in the fake tree. Returns the bundle id."""
    for rel, text in changes.items():
        write(root, "%s/%s/files/%s" % (RA.CAND_REL, cid, rel), text)
    rc, out = ra(root, "stage", cid, "--debate", "deb", "--round", str(rnd))
    assert rc == 0, out
    arts = [{"path": rel, "md5": RA.md5_file(os.path.join(RA.cand_dir(root, cid), "files", rel))} for rel in changes]
    log = os.path.join(root, "t_%s.log" % cid)
    with open(log, "w", encoding="utf-8") as fh:
        fh.write(P.result_line(P.make_result(3, 0, None, arts)) + "\n")
    rc, out = ra(root, "add-test", cid, "--command", "py -u t.py", "--log", log)
    assert rc == 0, out
    bid = RA.bundle_id(RA._load_manifest(root, cid))
    relay(root, "deb", rnd, [bid + " 동의"] if agree else ["something else"])
    return bid


def git(root, *a):
    return subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@invalid"] + list(a),
                          capture_output=True, text=True, timeout=60)


def fake_tree():
    t = tempfile.mkdtemp(prefix="shellguard_fake_")
    try:
        for f in (RA.PROTECTED_REL, RA.SELF_REL):      # protocol / debate_relay resolve via PYTHONPATH (schemas)
            os.makedirs(os.path.dirname(os.path.join(t, f)), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, f), os.path.join(t, f))
        fh = os.path.join(t, "tools", "hooks")
        os.makedirs(fh)
        for f in CAND_FILES:
            shutil.copyfile(os.path.join(CH, f), os.path.join(fh, f))
        gate("F0 fake-tree hooks are byte copies of the candidate", all(
            RA.md5_file(os.path.join(fh, f)) == RA.md5_file(os.path.join(CH, f)) for f in CAND_FILES))
        write(t, "CLAUDE.md", "core v0\n")
        write(t, "docs/rules/a.md", "rule a v0\n")
        write(t, "notes/free.md", "free\n")
        rc, out = ra(t, "audit", "--baseline")
        gate("F1 genesis baseline", rc == 0 and len(RA.ledger_lines(t)) == 1, "rc=%d" % rc)
        b1 = bundle(t, "ch-1", 1, {"docs/rules/a.md": "rule a v1\n"})
        ok_cmd = "py tools/rules_apply.py apply " + b1
        expect("A1 allow exact apply of an agreed bundle", fh, ok_cmd, "Bash", t, False)
        expect("A2 deny another executable path", fh, "py tools/bench/rules_apply.py apply " + b1, "Bash", t, True,
               "rules_apply")
        with open(os.path.join(t, RA.SELF_REL), "a", encoding="utf-8") as f:
            f.write("# modified\n")
        expect("A3 deny modified rules_apply.py", fh, ok_cmd, "Bash", t, True, "md5")
        shutil.copyfile(os.path.join(ROOT, RA.SELF_REL), os.path.join(t, RA.SELF_REL))
        expect("A4 deny missing bundle", fh, "py tools/rules_apply.py apply nochange@0123abcd", "Bash", t, True,
               "does not exist")
        b2 = bundle(t, "ch-2", 2, {"docs/rules/a.md": "rule a v2\n"}, agree=False)
        expect("A5 deny unagreed bundle", fh, "py tools/rules_apply.py apply " + b2, "Bash", t, True, "agreement")
        b3 = bundle(t, "ch-3", 3, {"notes/free.md": "changed\n"})
        expect("A6 deny bundle target outside protected globs", fh, "py tools/rules_apply.py apply " + b3, "Bash", t,
               True, "protected:notes/free.md")
        b4 = bundle(t, "ch-4", 4, {".claude/settings.local.json": "{}\n"})
        expect("A7 deny bundle targeting settings.local.json", fh, "py tools/rules_apply.py apply " + b4, "Bash", t,
               True, "protected:.claude/settings.local.json")
        expect("A8 deny extra argument", fh, ok_cmd + " CLAUDE.md", "Bash", t, True, "rules_apply")
        expect("A9 deny second segment", fh, ok_cmd + " ; Set-Content CLAUDE.md x", "PowerShell", t, True)
        expect("A10 deny --root on the real tree", fh, "py tools/rules_apply.py --root . apply " + b1, "Bash", t, True,
               "rules_apply")
        rc, out = ra(t, "apply", b1)
        gate("A11 real apply of b1 (rules_apply subprocess)", rc == 0, [l for l in out.splitlines() if "FAIL" in l])
        expect("A12 deny re-use of b1 (token used)", fh, ok_cmd, "Bash", t, True, "token-unused")
        # T1 token reuse with a no-op bundle (only the reuse gate can refuse the second apply)
        bn = bundle(t, "ch-noop", 5, {"CLAUDE.md": "core v0\n"})
        rc1, _ = ra(t, "apply", bn)
        n = len(RA.ledger_lines(t))
        rc2, out2 = ra(t, "apply", bn)
        fails = [l.split()[1] for l in out2.splitlines() if l.startswith("FAIL")]
        gate("T1 token reuse refused", rc1 == 0 and rc2 == 1 and fails == ["token-unused"] and
             len(RA.ledger_lines(t)) == n, "rc1=%d rc2=%d fails=%s" % (rc1, rc2, fails))
        # T2 manifest changed after agreement -> new id, old id refused
        b6 = bundle(t, "ch-6", 6, {"docs/rules/a.md": "rule a v6\n"})
        live = RA.md5_file(os.path.join(t, "docs/rules/a.md"))
        log = os.path.join(t, "t_extra.log")
        with open(log, "w", encoding="utf-8") as fh2:
            fh2.write(P.result_line(P.make_result(1, 0, None, [])) + "\n")
        ra(t, "add-test", "ch-6", "--command", "py extra.py", "--log", log)
        rc, out = ra(t, "apply", b6)
        gate("T2 staged hash changed after agreement refused", rc == 1 and "FAIL  bundle-hash" in out and
             RA.md5_file(os.path.join(t, "docs/rules/a.md")) == live, [l for l in out.splitlines() if "FAIL" in l][:3])
        # T3 change between check and write -> prehash refuses, nothing written
        b7 = bundle(t, "ch-7", 7, {"docs/rules/a.md": "rule a v7\n"})
        n = len(RA.ledger_lines(t))

        def tamper():
            write(t, "%s/ch-7/files/docs/rules/a.md" % RA.CAND_REL, "rule a v7 TAMPERED\n")
        with contextlib.redirect_stdout(io.StringIO()) as cap:
            rc = RA.cmd_apply(t, b7, _after_check=tamper)
        print("  T3 apply output: " + " | ".join(l for l in cap.getvalue().splitlines() if "REFUSED" in l or
                                                 "prehash:cand" in l).replace("FAIL", "fail")[:300])
        gate("T3 pre-apply re-hash refuses a change after check", rc == 1 and
             RA.md5_file(os.path.join(t, "docs/rules/a.md")) == live and len(RA.ledger_lines(t)) == n, "rc=%d" % rc)
        # L audit
        g = RA.audit_ledger(t)
        gate("L1 audit: chain + entries clean", all(ok for _, ok, _ in g), [n_ for n_, ok, _ in g if not ok])
        git(t, "init", "-q")
        git(t, "add", "-A")
        gate("L1b git commit of the fake tree", git(t, "commit", "-q", "-m", "c").returncode == 0)
        lp = os.path.join(t, RA.LEDGER_REL)
        with open(lp, "rb") as f:
            orig = f.read()
        lines = RA.ledger_lines(t)

        def put(ls):
            with open(lp, "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(x + "\n" for x in ls))

        def failing():
            return [n_ for n_, ok, _ in RA.audit_ledger(t) if not ok]
        e0 = json.loads(lines[0])
        e0["paths"][0]["md5"] = "f" * 32
        put([json.dumps(e0, ensure_ascii=False, separators=(",", ":"))] + lines[1:])
        fl = failing()
        gate("L2 edited earlier line breaks the chain", "chain:1" in fl, fl[:4])
        put(lines)
        fake = json.loads(lines[-1])
        fake.update(id="ch-x@0123abcd", prev=RA.line_hash(lines[-1]))
        fake["agreement"] = dict(fake["agreement"], token="ch-x@0123abcd 동의")
        put(lines + [json.dumps(fake, ensure_ascii=False, separators=(",", ":"))])
        fl = failing()
        i = len(lines)
        gate("L3 forged appended line without agreement flagged", "entry:%d agreement" % i in fl and
             "entry:%d bundle" % i in fl and not any(x.startswith("chain") for x in fl), fl[:5])
        dup = json.loads(lines[-1])
        dup["prev"] = RA.line_hash(lines[-1])
        put(lines + [json.dumps(dup, ensure_ascii=False, separators=(",", ":"))])
        fl = failing()
        gate("L4 appended line re-using an agreed token flagged", "entry:%d token" % i in fl, fl[:5])
        put(lines)
        rel1 = os.path.join(t, "deb", "relay", "round_01_gpt.md")
        with open(rel1, "a", encoding="utf-8") as f:
            f.write("edited later\n")
        fl = failing()
        gate("L5 changed relay file flagged", any(x.endswith("relay-files") for x in fl), fl[:4])
        git(t, "checkout", "--", "deb/relay/round_01_gpt.md")
        last = json.loads(lines[-1])
        last["paths"][0]["md5"] = "e" * 32
        put(lines[:-1] + [json.dumps(last, ensure_ascii=False, separators=(",", ":"))])
        fl = failing()
        gate("L6 edited last line flagged (bundle + committed prefix, chain cannot see it)",
             "entry:%d bundle" % (len(lines) - 1) in fl and "ledger-committed-prefix" in fl and
             not any(x.startswith("chain") for x in fl), fl[:5])
        with open(lp, "wb") as f:
            f.write(orig)
        gate("L7 restored ledger audits clean", not failing(), failing()[:3])
    finally:
        shutil.rmtree(t, ignore_errors=True)


# ------------------------------------------------------------------ W1 settings.local.json via write tools
def write_tools():
    sl = os.path.join(ROOT, ".claude", "settings.local.json")
    gc, acl, acx = (os.path.join(CH, f) for f in ("guard_card.py", "adapt_claude.py", "adapt_codex.py"))
    for tool, ti in (("Write", {"file_path": sl, "content": "{}"}),
                     ("Edit", {"file_path": sl, "old_string": "a", "new_string": "b"}),
                     ("MultiEdit", {"file_path": ".claude/settings.local.json", "edits": []}),
                     ("NotebookEdit", {"notebook_path": sl, "new_source": "x"})):
        for name, script in (("guard_card", gc), ("adapt_claude", acl)):
            d, why = hook(script, claude(tool, ti, ROOT))
            gate("W1 deny %s settings.local via %s" % (tool, name), d and "protected" in why, why[:160])
    patch = "*** Begin Patch\n*** Update File: .claude/settings.local.json\n@@\n-a\n+b\n*** End Patch"
    d, why = hook(acx, codex("apply_patch", {"command": patch}, ROOT))
    gate("W1 deny apply_patch settings.local via adapt_codex", d and "protected" in why, why[:160])
    patch2 = ("*** Begin Patch\n*** Update File: %s/codex_ok.txt\n*** Move to: .claude/settings.local.json\n@@\n-ok\n+x\n"
              "*** End Patch" % FREE)
    d, why = hook(acx, codex("apply_patch", {"command": patch2}, ROOT))
    gate("W1 deny apply_patch rename onto settings.local", d and "protected" in why, why[:160])
    d, why = hook(gc, claude("Write", {"file_path": os.path.join(ROOT, FREE, "sg_free.txt"), "content": "x"}, ROOT))
    gate("W1 allow Write to an unprotected path (guard_card)", not d, why[:160])


def main():
    before = active_md5s()
    gate("M0 active files listed", len(before) > 50, "%d files" % len(before))
    try:
        real_tree()
        fake_tree()
        write_tools()
    finally:
        after = active_md5s()
        diff = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        gate("M1 active hook/.codex/.claude/protected md5s unchanged", not diff, diff[:6])
        shutil.rmtree(TMPLOG, ignore_errors=True)
    fails = [n for n, ok in res if not ok]
    arts = [{"path": "tools/hooks/" + f, "md5": RA.md5_file(os.path.join(CH, f))} for f in CAND_FILES]
    print(P.result_line(P.make_result(len(res) - len(fails), len(fails), fails[0] if fails else None, arts)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
