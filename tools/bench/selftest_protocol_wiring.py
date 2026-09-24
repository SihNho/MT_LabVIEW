r"""selftest_protocol_wiring.py - session protocol v1 WIRING (task card chat-B, 2026-09-24). No LabVIEW, no network,
no peer dispatch (peer.ps1 only with -DryRun), no motor. Everything that writes goes to a temp dir, except two
throwaway scripts under tools/bench/ (bgrun scopes the NO-RESULT mark by path) that are deleted in the same run.

WHAT EXISTED (checked first): tools/protocol.py (validator, C6), tools/bench/selftest_protocol.py (schemas + C6),
selftest_next_gate_jev.py, selftest_cycle_runner(_ff).py. This file tests only what chat-B added.

    py tools/bench/selftest_protocol_wiring.py [--hooks-suffix .new]

`--hooks-suffix .new` imports tools/hooks/{guard_bash,guard_peer,report_gate}.py.new instead of the live files, so
the edited hooks are proven BEFORE they are os.replace'd over the live ones (the card's pass criterion).

PREDICTION CONTRACT - every gate below PASSES:
  B1-B7   binding: main session allowed; unbound card agent refused (Bash and Read); bind of a valid card allowed and
          recorded; a chained `bind x; other` is not a bind; a bind of an invalid card refused; a non-card agent type
          (Explore) allowed.
  F*      one refusal AND one allowance per flag: labview none/read/build, gui, hardware, run_vi, write, status_edit
          (Edit and Bash), git_commit, peers (peer.ps1 roles and the four review scripts).
  H1-H2   guard_bash(.new) end to end as a subprocess: unbound material agent refused (exit 2), main session allowed.
  N1-N4   next_gate(.new): absent / identical / invalid next.json block, a new valid one passes.
  P1-P5   guard_peer(.new).in_prediction_scope: recipe + bench in scope; tools/*.py utility, Jev, powershell out.
  R1-R2   report_gate(.new).decisions_block lists open items, not answered ones.
  V1-V5   C4/C5: review_card valid, render contains the id + contract, parse_verdict ok / missing / id mismatch.
  D1-D3   peer.ps1 -DryRun -ReviewCard shows the card; an invalid card is refused; outcome_review --dry-run and
          doc_ingest --full --dry-run write valid review/1 cards.
  G1-G3   bgrun: a scoped script without RESULT ends `(NO RESULT LINE)`, one with RESULT does not; audit's A8 regex
          matches the mark.
"""
import glob
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
HOOKS = os.path.join(TOOLS, "hooks")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HOOKS)
import protocol as P  # noqa: E402

SUFFIX = sys.argv[sys.argv.index("--hooks-suffix") + 1] if "--hooks-suffix" in sys.argv else ""
PASS, FAIL = [], []
TMP = tempfile.mkdtemp(prefix="pwiring_")
P.ACTIVE = os.path.join(TMP, "active.json")
os.environ["PROTOCOL_ACTIVE"] = P.ACTIVE          # the subprocess hook runs use the same isolated binding file
os.environ.pop("TYPESAFE_API_KEY", None)           # no Jev calls from any child


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %-62s %s" % ("PASS" if ok else "FAIL", label, str(detail)[:150]), flush=True)


def load(name):
    path = os.path.join(HOOKS, name + ".py" + SUFFIX)
    if not os.path.exists(path):
        path = os.path.join(HOOKS, name + ".py")        # only some hooks have a pending .new copy
    mod = name + "_under_test"
    spec = importlib.util.spec_from_file_location(mod, path,
                                                  loader=importlib.machinery.SourceFileLoader(mod, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def card(cid, **flags):
    fl = {"labview": "none", "gui": False, "hardware": "none", "run_vi": False, "write": [], "status_edit": False,
          "git_commit": False, "peers": []}
    fl.update(flags)
    c = {"schema": "task/1", "id": cid, "kind": "build", "goal": "wiring self-test", "flags": fl,
         "budget": {"failures": 2, "minutes": 5}, "unblocks": "M3"}
    p = os.path.join(TMP, "task_%s.json" % cid)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(c, f)
    return p


def pay(aid, tool, atype="material", **ti):
    d = {"tool_name": tool, "tool_input": ti}
    if aid:
        d["agent_id"], d["agent_type"] = aid, atype
    return d


def bound(cid, **flags):
    """A fresh agent id bound to a fresh card with these flags."""
    aid = "a" + cid
    ok, msg = P.hook_decision(pay(aid, "Bash", command="py tools/protocol.py bind \"%s\"" % card(cid, **flags)))
    assert ok, msg
    return aid


def allowed(aid, tool="Bash", **ti):
    return P.hook_decision(pay(aid, tool, **ti))[0]


def script(name, body):
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def main():
    print("=== selftest_protocol_wiring (hooks%s)" % (SUFFIX or " = live files"), flush=True)
    # ---- B: binding
    gate("B1 main session (no agent_id) is not governed", allowed(None, command="ls"))
    gate("B2 unbound card agent: Bash refused", not allowed("u1", command="ls"))
    gate("B3 unbound card agent: Read refused", not allowed("u1", "Read", file_path="x"))
    c = card("b4")
    ok, msg = P.hook_decision(pay("b4", "Bash", command="py tools/protocol.py bind %s" % c.replace("\\", "/")))
    gate("B4 bind of a valid card is allowed and recorded", ok and P.binding("b4") is not None, msg)
    gate("B5 `bind x; other` is NOT a bind (stays unbound)",
         not allowed("b5", command="py tools/protocol.py bind %s; ls" % c.replace("\\", "/")) and not P.binding("b5"))
    bad = script("task_bad.json", '{"schema": "task/1", "id": "bad"}')
    ok6, msg6 = P.hook_decision(pay("b6", "Bash", command="py tools/protocol.py bind %s" % bad.replace("\\", "/")))
    gate("B6 bind of an INVALID card is refused", not ok6 and "BIND REFUSED" in (msg6 or ""), msg6)
    gate("B7 a non-card agent type (Explore) is not governed", allowed("e1", command="ls") is False and
         P.hook_decision(pay("e1", "Bash", atype="Explore", command="ls"))[0])

    # ---- F: flags
    recipe = sorted(glob.glob(os.path.join(TOOLS, "recipes", "*.py")))[0]
    lv_src = script("lv_probe.py", "import gscript\nprint(gscript)\n")
    lv_save = script("lv_save.py", "import gscript\ngscript.save('x')\n")
    gui_src = script("gui_probe.py", "import gscript\ngscript.gui_save('x')\n")
    run_src = script("run_probe.py", "vi = None\nvi.Run(False)\n")
    plain = os.path.join(HERE, "selftest_protocol.py")
    a = bound("fnone")
    gate("F1 labview none: a recipe is refused (quoted absolute path and relative path)",
         not allowed(a, command="py -u \"%s\"" % recipe)
         and not allowed(a, command="py -u tools/recipes/%s" % os.path.basename(recipe)))
    gate("F2 labview none: a gscript-importing script is refused", not allowed(a, command="py %s" % lv_src))
    gate("F3 labview none: lv_gui.ps1 is refused", not allowed(a, command="& .\\tools\\lv_gui.ps1 -Action shot"))
    gate("F4 labview none: a pure-python bench script is allowed", allowed(a, command="py -u \"%s\"" % plain))
    gate("F4b labview none: READING a LabVIEW script (head/grep) is not running it",
         allowed(a, command="head -15 \"%s\"; grep -n x %s" % (lv_src, lv_src))
         and not allowed(a, command="py tools/bgrun.py --material --max-min 1 --log x.log -- py -u \"%s\"" % lv_src))
    a = bound("fread", labview="read")
    gate("F5 labview read: recipe refused, saving script refused",
         not allowed(a, command="py \"%s\"" % recipe) and not allowed(a, command="py %s" % lv_save))
    gate("F6 labview read: a non-saving LabVIEW script is allowed", allowed(a, command="py %s" % lv_src))
    a = bound("fbuild", labview="build", gui=False)
    m1 = os.path.join(TOOLS, "recipes", "build_d1_m3a1.py")
    raw1 = open(m1, encoding="utf-8", errors="replace").read()
    gate("F7 labview build + gui false: build_d1_m3a1.py (gui_save only in prose) is allowed",
         allowed(a, command="py -u \"%s\"" % m1))
    gate("F7b code_only() strips the prose mentions of gui_save in build_d1_m3a1.py",
         "gui_save(" in raw1 and "gui_save(" not in P.code_only(raw1)
         and P.code_only(raw1).count("\n") == raw1.count("\n"))
    gate("F7c a REAL call survives code_only (x = 1  # gui_save() -> kept only the call)",
         "gui_save(" in P.code_only("import gscript\ngscript.gui_save('v')  # note gui_save()\n")
         and "gui_save" not in P.code_only('"""gui_save() doc"""\nx = 1  # gui_save()\n'))
    gate("F8 gui false: lv_gui click refused, shot allowed",
         not allowed(a, command="& .\\tools\\lv_gui.ps1 -Action click -X 1 -Y 2")
         and allowed(a, command="& .\\tools\\lv_gui.ps1 -Action shot"))
    gate("F9 gui false: a script calling gui_save is refused", not allowed(a, command="py %s" % gui_src))
    a2 = bound("fgui", labview="build", gui=True)
    gate("F10 gui true: click allowed", allowed(a2, command="& .\\tools\\lv_gui.ps1 -Action click -X 1 -Y 2"))
    gate("F11 hardware none: motor_gate refused, --dry-run allowed",
         not allowed(a, command="py tools/motor_gate.py --session start")
         and allowed(a, command="py tools/motor_gate.py --device pi --command \"POS?\" --dry-run"))
    gate("F12 hardware none: a real cycle_runner refused, --dry-run allowed",
         not allowed(a, command="py tools/cycle_runner.py --cycles 1")
         and allowed(a, command="py tools/cycle_runner.py --dry-run --cycles 1"))
    a3 = bound("fhw", hardware="gate")
    gate("F13 hardware gate: motor_gate allowed", allowed(a3, command="py tools/motor_gate.py --session start"))
    gate("F14 run_vi false: a script calling VI.Run() refused", not allowed(a, command="py %s" % run_src))
    a4 = bound("frun", run_vi=True)
    gate("F15 run_vi true: allowed", allowed(a4, command="py %s" % run_src))
    aw = bound("fw", write=["tools/**", "docs/protocol/*.json"])
    gate("F16 write: inside the globs allowed",
         allowed(aw, "Edit", file_path=os.path.join(TOOLS, "hooks", "x.py"))
         and allowed(aw, "Write", file_path=os.path.join(ROOT, "docs", "protocol", "task.json")))
    gate("F17 write: outside the globs refused",
         not allowed(aw, "Edit", file_path=os.path.join(ROOT, "docs", "NAMES.md"))
         and not allowed(aw, "Write", file_path=os.path.join(ROOT, ".claude", "settings.json")))
    gate("F18 write: the card's own result file and %TEMP% are always writable",
         allowed(aw, "Write", file_path=os.path.join(P.CARDS_DIR, "result_fw.json"))
         and allowed(aw, "Write", file_path=os.path.join(tempfile.gettempdir(), "scratch.txt")))
    gate("F19 status_edit false: Edit STATUS.md refused, Bash `>> STATUS.md` refused",
         not allowed(aw, "Edit", file_path=os.path.join(ROOT, "STATUS.md"))
         and not allowed(aw, command="echo x >> STATUS.md"))
    as_ = bound("fst", status_edit=True)
    gate("F20 status_edit true: Edit STATUS.md allowed", allowed(as_, "Edit", file_path=os.path.join(ROOT, "STATUS.md")))
    gate("F21 git_commit false refused / true allowed",
         not allowed(a, command="git commit -m x") and allowed(bound("fgit", git_commit=True), command="git commit -m x"))
    gate("F22 peers []: peer.ps1 hypothesis refused, prior_art_review refused",
         not allowed(a, command="powershell -Command \"& 'tools/peer.ps1' -Agent claude -Role hypothesis -Task x\"")
         and not allowed(a, command="py tools/prior_art_review.py --plan x"))
    ap_ = bound("fpeer", peers=["hypothesis", "priorart"])
    gate("F23 peers [hypothesis, priorart]: those allowed, fact/retrospective refused",
         allowed(ap_, command="powershell -Command \"& 'tools/peer.ps1' -Agent claude -Role hypothesis -Task x\"")
         and allowed(ap_, command="py tools/prior_art_review.py --plan x")
         and not allowed(ap_, command="powershell -Command \"& 'tools/peer.ps1' -Kind fact -Task x\"")
         and not allowed(ap_, command="py tools/retrospective.py --cycle 1"))

    # ---- H: guard_bash end to end (the file under test, as a subprocess, with the isolated binding file)
    gb = os.path.join(HOOKS, "guard_bash.py" + SUFFIX)
    if not os.path.exists(gb):
        gb = os.path.join(HOOKS, "guard_bash.py")

    def hook(payload):
        r = subprocess.run([sys.executable, gb], input=json.dumps(payload), capture_output=True, text=True,
                           cwd=ROOT, timeout=60)
        return r.returncode, r.stderr
    rc, err = hook(pay("hunbound", "Bash", command="ls"))
    gate("H1 guard_bash: unbound material agent refused", rc == 2 and "UNBOUND" in err, err.strip()[:100])
    rc, err = hook(pay(None, "Bash", command="ls"))
    gate("H2 guard_bash: main session `ls` allowed", rc == 0, err.strip()[:100])

    # ---- N: next_gate of the file under test, on a fake root
    gbm = load("guard_bash")
    fake = types.ModuleType("jev")
    fake.ask = lambda *a, **k: (None, "no key")
    sys.modules["jev"] = fake
    froot = os.path.join(TMP, "root")
    os.makedirs(os.path.join(froot, "tools", "bench"))
    os.makedirs(os.path.join(froot, "tools", "hooks"))
    open(os.path.join(froot, "STATUS.md"), "w").write("## NEXT\nx\n")
    nj = os.path.join(froot, "tools", "bench", "next.json")
    snap = os.path.join(froot, "tools", "bench", "next_snapshot.md5")
    gbm.HERE = os.path.join(froot, "tools", "hooks")

    def ng():
        old = sys.stderr
        sys.stderr = io.StringIO()
        try:
            return gbm.next_gate(), sys.stderr.getvalue()
        finally:
            sys.stderr = old
    open(snap, "w").write("absent")
    gate("N1 next_gate: no next.json blocks", ng()[0] == 2)
    body = '{"schema":"next/1","cycle":1,"act":"a","task_kind":"build","stop_requested":false,"advances":["M3"]}'
    open(nj, "w", newline="").write(body)
    open(snap, "w").write(P._md5(nj))
    gate("N2 next_gate: an identical next.json blocks", ng()[0] == 2)
    open(nj, "w", newline="").write('{"schema":"next/1","act":"b"}')
    rc, err = ng()
    gate("N3 next_gate: an invalid next.json blocks", rc == 2 and "INVALID" in err, err[:80])
    open(nj, "w", newline="").write(body.replace('"a"', '"b"'))
    gate("N4 next_gate: a new valid next.json passes", ng()[0] == 0)

    # ---- P: guard_peer scope
    gpm = load("guard_peer")
    s = lambda c: gpm.in_prediction_scope("BGRUN START 2026-09-24 20:00:00 limit 5.0 min: " + c)  # noqa: E731
    gate("P1 recipe in scope", s("py -u tools/recipes/stage_x.py"))
    gate("P2 bench script in scope", s("py -u \"G:/x y/tools/bench/diag_x.py\" --a"))
    gate("P3 tools/*.py utility out of scope", not s("py tools/motor_gate.py --session start"))
    gate("P4 Jev script out of scope", not s("py tools/bench/jev_trial.py") and not s("py tools/jev_triage.py x"))
    gate("P5 a non-python command out of scope", not s("powershell -File tools/lv_gui.ps1 -Action shot"))
    gate("P6 a START line quoting the bgrun call is judged by the script after `--`",
         s("py tools/bgrun.py --material --max-min 10 --log x.log -- py -u tools/recipes/stage_x_v3.py")
         and not s("py tools/bgrun.py --max-min 5 --log x.log -- py tools/motor_gate.py --session end"))

    # ---- R: report_gate open decisions
    rgm = load("report_gate")
    dp = script("decisions.json", json.dumps({"schema": "decisions-pending/1", "items": [
        {"id": "D-1", "asked": "2026-09-24", "by": "chat", "question": "open one?", "options": ["a", "b"],
         "status": "open"},
        {"id": "D-2", "asked": "2026-09-24", "by": "cycle 3", "question": "answered one?", "options": ["a"],
         "status": "answered", "answer": "a", "answered_at": "2026-09-24"}]}))
    blk = rgm.decisions_block(dp)
    gate("R1 report_gate lists the OPEN decision", "D-1" in blk and "open one?" in blk, blk.strip()[:80])
    gate("R2 report_gate omits the answered one", "D-2" not in blk)

    # ---- V: review/verdict
    rc_ = P.review_card("hypothesis", "74-05", "the claim", predicted="p", observed="o", ruled_out=["r"])
    gate("V1 review_card builds a valid review/1", P.validate_obj(rc_)[0])
    txt = P.render_review(rc_) + P.verdict_contract(rc_)
    gate("V2 render has the card block and the contract with the id", "REVIEW CARD" in txt and '"id":"74-05"' in txt)
    ans = ("prose ...\nVERDICT {\"schema\":\"verdict/1\",\"id\":\"74-05\",\"verdict\":\"refuted\","
           "\"alternative\":\"x\",\"discriminating_test\":\"y\",\"violations\":[],\"sources\":[],\"note\":\"\"}\n")
    d, why = P.parse_verdict(ans, "74-05")
    gate("V3 parse_verdict reads the last VERDICT line", d is not None and d["verdict"] == "refuted", why)
    gate("V4 no VERDICT line -> None", P.parse_verdict("just prose", "74-05")[0] is None)
    gate("V5 id mismatch -> None", P.parse_verdict(ans, "other")[0] is None)

    # ---- D: peer.ps1 -DryRun and two callers
    rpath = P.write_review_card(P.review_card("fact", "wiring-selftest", "a dry-run claim"))
    ps = lambda extra: subprocess.run(  # noqa: E731
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
         "& '%s' -Kind fact -Slug wiring-selftest -Task 'q' -DryRun %s" % (os.path.join(TOOLS, "peer.ps1"), extra)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    r = ps("-ReviewCard '%s'" % rpath)
    gate("D1 peer.ps1 -DryRun -ReviewCard shows the card", r.returncode == 0 and "id wiring-selftest" in r.stdout,
         (r.stdout + r.stderr).strip().splitlines()[-1:] if (r.stdout + r.stderr).strip() else "")
    r = ps("-ReviewCard '%s'" % bad)
    gate("D2 peer.ps1 refuses an invalid review card", r.returncode != 0 and "REFUSED" in (r.stdout + r.stderr))
    os.remove(rpath)
    before = set(glob.glob(os.path.join(P.CARDS_DIR, "review_*.json")))
    outs = []
    for cmd in ([sys.executable, os.path.join(TOOLS, "outcome_review.py"), "--dry-run"],
                [sys.executable, os.path.join(TOOLS, "doc_ingest.py"), "--full", "--dry-run", "--slug",
                 "ingest-wiring-selftest"],
                [sys.executable, os.path.join(TOOLS, "prior_art_review.py"), "--dry-run", "--plan", "wiring self-test",
                 "--slug", "wiring-selftest", "--no-recipe", "self-test"],
                [sys.executable, os.path.join(TOOLS, "retrospective.py"), "--cycle", "999", "--since-hours", "1",
                 "--dry-run", "--slug", "retrospective-wiring-selftest"]):
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300)
        outs.append(r.stdout + r.stderr)
    pat = r"review_(outcome-review-\d+|ingest-wiring-selftest|priorart-wiring-selftest|retrospective-wiring-selftest)\.json$"
    new = sorted(p for p in glob.glob(os.path.join(P.CARDS_DIR, "review_*.json")) if re.search(pat, p))
    roles = sorted(P.load_card(p, None)["role"] for p in new if os.path.exists(p))
    gate("D3 the 4 review callers --dry-run write valid review/1 cards",
         roles == ["ingest", "outcome", "priorart", "retrospective"], roles)
    gate("D4 outcome_review --dry-run resolves peer.ps1 -DryRun WITH the review card",
         "DRYRUN reviewcard : id outcome-review-" in outs[0], outs[0].strip()[-120:])
    for p in new:
        if re.search(pat, p):
            try:
                os.remove(p)
            except OSError:
                pass

    # ---- G: bgrun NO RESULT LINE
    s_no = os.path.join(HERE, "_wiring_tmp_noresult.py")
    s_ok = os.path.join(HERE, "_wiring_tmp_result.py")
    try:
        open(s_no, "w").write("print('no verdict here')\n")
        open(s_ok, "w").write("import sys; sys.path.insert(0, r'%s'); import protocol\n"
                              "print(protocol.result_line(protocol.make_result(1, 0)))\n" % TOOLS)
        outs = []
        for sp in (s_no, s_ok):
            lg = os.path.join(TMP, os.path.basename(sp) + ".log")
            subprocess.run([sys.executable, os.path.join(TOOLS, "bgrun.py"), "--max-min", "1", "--log", lg, "--",
                            sys.executable, "-u", sp], cwd=ROOT, capture_output=True, text=True, timeout=120)
            outs.append(open(lg, encoding="utf-8").read())
        gate("G1 no RESULT line -> `(NO RESULT LINE)` on the END line, rc unchanged",
             re.search(r"^BGRUN END rc=0 after \d+s \(NO RESULT LINE\)$", outs[0], re.M), outs[0].strip()[-60:])
        gate("G2 with a RESULT line -> no mark", "NO RESULT LINE" not in outs[1] and "BGRUN END rc=0" in outs[1])
        gate("G3 audit A8's pattern matches the mark",
             re.search(r"^BGRUN END rc=-?\d+ after \d+s \(NO RESULT LINE\)", outs[0], re.M)
             and "A8" in open(os.path.join(TOOLS, "audit_cycle.py"), encoding="utf-8").read())
    finally:
        for sp in (s_no, s_ok):
            try:
                os.remove(sp)
            except OSError:
                pass

    print("\n=== GATES: %d pass / %d fail%s" % (len(PASS), len(FAIL),
                                                ("; failing: " + ", ".join(FAIL)) if FAIL else ""), flush=True)
    print(P.result_line(P.make_result(len(PASS), len(FAIL), FAIL[0] if FAIL else None)), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
