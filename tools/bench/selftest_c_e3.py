# ---
# labview: none
# hardware: none
# ---
"""Self-test of card chat-E3 (declared-scope headers, write-time and launch-time checks, WAITING, diff-only prior art).
OFFLINE: no LabVIEW, no peer, no network. Fixtures live in tools/bench/_e3tmp/ (deleted at the end) and %TEMP%; the
launch ledger / bindings / card folder are fixture files through PROTOCOL_LAUNCHES / PROTOCOL_ACTIVE / GUARD_WRITE_CARDS.
PREDICTION: every case PASS (count printed in the RESULT line); fp-36..39 are the regression cases FP36..FP39.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
os.chdir(ROOT)
TMP = os.path.join(HERE, "_e3tmp")
XT = tempfile.mkdtemp(prefix="e3st_")
os.makedirs(TMP, exist_ok=True)
LEDGER = os.path.join(XT, "launches.jsonl")
ACTIVE = os.path.join(XT, "active.json")
CARDS = os.path.join(XT, "cards")
os.makedirs(CARDS)
os.environ["PROTOCOL_LAUNCHES"] = LEDGER
os.environ["PROTOCOL_ACTIVE"] = ACTIVE
os.environ["GUARD_WRITE_CARDS"] = CARDS
for k in ("CARD_ID", "CARD_LABVIEW"):
    os.environ.pop(k, None)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import protocol as P          # noqa: E402
import scope_header as S      # noqa: E402
import stop_record as SR      # noqa: E402
import guard_peer as GP       # noqa: E402
import guard_cycle as GC      # noqa: E402
import guard_write as GW      # noqa: E402
import stage_prerun as SP     # noqa: E402
import priorart_diff as PD    # noqa: E402

R = []


def case(name, ok, detail=""):
    R.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, str(detail)[:300]), flush=True)


def put(name, text, mode="w"):
    p = os.path.join(TMP, name)
    with open(p, "wb") as f:
        f.write(text.encode("utf-8") if isinstance(text, str) else text)
    return p


HDR_NONE = "# ---\n# labview: none\n# hardware: none\n# ---\n"
HDR_BUILD = "# ---\n# labview: build\n# hardware: none\n# ---\n"
try:
    # ---------------------------------------------------------------- header parsing + canonical bytes
    p = put("h_top.py", HDR_NONE + '"""doc"""\nx = 1\n')
    case("H1 header at the top parses", S.read(p)[0] and S.read(p)[0]["labview"] == "none")
    p = put("h_tail.py", 'x = 1\n' + HDR_BUILD)
    case("H2 header at the tail parses", S.read(p)[0] and S.read(p)[0]["labview"] == "build")
    p = put("h_bad.py", "# ---\n# labview: none\n# hardware: none\n# colour: red\n# ---\nx=1\n")
    case("H3 unknown key -> invalid", S.read(p)[1] and "unknown header key" in S.read(p)[1], S.read(p)[1])
    p = put("h_lvbad.py", "# ---\n# labview: maybe\n# hardware: none\n# ---\nx=1\n")
    case("H4 bad labview value -> invalid", S.read(p)[1] is not None, S.read(p)[1])
    okc = True
    for orig in (b"a = 1\nb = 2\n", b"a = 1\nb = 2", b"a = 1\r\nb = 2\r\n", b"", b"#!/usr/bin/env py\nx=1"):
        nb = S.append_block(orig, S.render("read", "none"))
        okc = okc and S.canonical_bytes(nb) == orig and S.parse_bytes(nb)[0] is not None
    case("H5 append_block/canonical_bytes round-trip (LF, no final NL, CRLF, empty, shebang)", okc)
    p = put("h_canon.py", S.append_block(b"y = 2\n", S.render("none", "none")))
    case("H6 stop_record.sha256_of / stage_prerun.sha256 are header-blind",
         SR.sha256_of(p) == hashlib.sha256(b"y = 2\n").hexdigest() == SP.sha256(p))

    # ---------------------------------------------------------------- honesty + compile
    def hon(src, hdr=HDR_NONE, name="hon.py"):
        q = put(name, hdr + src)
        return S.honesty(q, S.read(q)[0])
    case("HON1 none + import gscript -> dishonest", hon("import gscript\n"))
    case("HON2 none + subprocess py recipe -> dishonest",
         hon("import subprocess, sys\nsubprocess.run([sys.executable, '-u', 'tools/recipes/stage_x.py'])\n"))
    case("HON3 none + recipe path as a git argument -> honest",
         not hon("import subprocess\nsubprocess.run(['git', 'show', 'HEAD:tools/recipes/x.py'])\n"))
    case("HON4 read + gui_save() -> dishonest", hon("def f(g):\n    g.gui_save(1)\n", "# ---\n# labview: read\n# hardware: none\n# ---\n"))
    case("HON5 none + runpy without evidence -> dishonest", hon("import runpy\nrunpy.run_path('a.py')\n"))
    case("HON6 none + subprocess motor_gate.py -> hardware dishonest",
         hon("import subprocess\nsubprocess.run(['py', 'tools/motor_gate.py', '--execute'])\n"))
    q = put("cmp_bad.py", HDR_NONE + "def f(:\n")
    case("C1 compile error found", S.compile_error(q))

    # ---------------------------------------------------------------- what a command RUNS
    L = lambda c: [os.path.basename(p) for p, _a in S.launches(c)]          # noqa: E731
    case("L1 git add of recipes runs nothing", L("git add tools/recipes/a.py tools/recipes/b.py && git commit -m x") == [])
    case("L2 py -m py_compile runs nothing", L("py -m py_compile tools/recipes/a.py") == [])
    case("L3 bgrun child is a run", L("py tools/bgrun.py --max-min 3 --log x.log -- py -u tools/stagexec.py adopt --script s.py")
         == ["bgrun.py", "stagexec.py"])
    case("L4 powershell -Command '& peer.ps1' is a run",
         L("powershell -Command \"& 'tools/peer.ps1' -Kind fact -Slug x\"") == ["peer.ps1"], L("powershell -Command \"& 'tools/peer.ps1' -Kind fact -Slug x\""))
    case("L5 grep of a recipe runs nothing", L('grep -n "import gscript" tools/recipes/a.py') == [])

    # ---------------------------------------------------------------- launch check against card flags
    card_none = {"id": "t-none", "flags": {"labview": "none", "hardware": "none", "write": [], "peers": []}}
    card_read = {"id": "t-read", "flags": {"labview": "read", "hardware": "none", "write": [], "peers": []}}
    nohdr = put("nohdr.py", "x = 1\n")
    rel_nohdr = os.path.relpath(nohdr, ROOT).replace("\\", "/")
    r = P.check_command(card_none, "py -u " + rel_nohdr)
    case("LC1 missing header -> refused", r and "scope header" in r, r)
    bld = put("bld.py", HDR_BUILD + "x = 1\n")
    r = P.check_command(card_none, "py -u " + os.path.relpath(bld, ROOT).replace("\\", "/"))
    case("LC2 declared build under labview none -> refused", r and "declares labview: build" in r, r)
    r = P.check_command(card_read, "py -u " + os.path.relpath(bld, ROOT).replace("\\", "/"))
    case("LC3 declared build under labview read -> refused", r and "declares labview: build" in r, r)
    cb = put("cmpfail.py", HDR_NONE + "def f(:\n")
    r = P.check_command(card_none, "py -u " + os.path.relpath(cb, ROOT).replace("\\", "/"))
    case("LC4 non-compiling script -> refused at launch", r and "does not compile" in r, r)
    r = P.check_command(card_none, 'grep -n "import gscript" tools/stagexec.py | head -3')
    case("LC5 grep naming 'import gscript' is not a LabVIEW command", r is None, r)
    mh = put("mot.py", "# ---\n# labview: none\n# hardware: motor\n# ---\nx=1\n")
    r = P.check_command(card_none, "py -u " + os.path.relpath(mh, ROOT).replace("\\", "/"))
    case("LC6 hardware motor under card hardware none -> refused", r and "hardware" in r, r)
    case("LC7 guard_bash.scope_gate refuses a headerless tools script for any session",
         __import__("guard_bash").scope_gate("py -u " + rel_nohdr) == 2)

    # ---------------------------------------------------------------- fp-36..39 regressions
    r = P.check_command(card_none, "py tools/bgrun.py --material --max-min 3 --log tools/bench/x_adopt.log -- py -u "
                                   "tools/stagexec.py adopt --script tools/recipes/s.py --log diag.log")
    case("FP39 stagexec adopt under labview none -> allowed", r is None, r)
    r = P.check_command(card_none, "py tools/bgrun.py --material --max-min 3 --log tools/bench/x_run.log -- py -u "
                                   "tools/stagexec.py run tools/bench/plan.json")
    case("FP39b stagexec run under labview none -> still refused", r and "labview" in r, r)
    seg = "py tools/bgrun.py --material --max-min 3 --log tools/bench/p.log -- py -u tools/stage_prerun.py " \
          "--scratch-required tools/recipes/stage_d1_ring_p4_s02v18.py"
    case("FP37 stage_prerun --scratch-required is an offline checker (stop_record + guard_cycle)",
         SR.offline_checker(seg) and GC.offline_only(seg) and SR.segment_class(seg) == "exempt")
    case("FP37b a recipe launch under bgrun is not offline",
         not SR.offline_checker("py tools/bgrun.py --max-min 3 --log l.log -- py -u tools/recipes/stage_x.py"))
    case("FP38 git add / commit of recipe paths are read-only for the launch gate",
         SR.segment_class("git add tools/recipes/stage_a.py tools/recipes/stage_b.py") == "readonly"
         and SR.segment_class("git commit -m 'x' tools/recipes/stage_a.py") == "readonly"
         and SR.segment_class("py -u tools/recipes/stage_a.py") == "build")
    r = P.check_command(card_none, "py tools/protocol.py validate docs/protocol/result.json")
    r2 = P.check_command(card_none, "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "
                                    "tools/bench/selftest_cycle_runner.py")
    case("FP40 protocol CLI and the stub-only runner self-test are offline under labview none", r is None and r2 is None, (r, r2))
    card_peer = {"id": "t-peer", "flags": {"labview": "none", "hardware": "none", "write": [], "peers": ["hypothesis"]}}
    r = P.check_command(card_peer, "powershell -Command \"& 'tools/peer.ps1' -Agent claude -Role hypothesis -Slug x "
                                   "-TaskFile t.md -TimeoutSec 780\"")
    case("FP40c a peer dispatch (peer.ps1 only NAMES LabVIEW in prompts) is offline under labview none", r is None, r)
    r = P.check_command(card_none, "py tools/cycle_runner.py --dry-run --cycles 1")
    r2 = P.check_command(card_none, "py tools/cycle_runner.py --cycles 1")
    case("FP40b cycle_runner --dry-run allowed, a real run refused with the offline hint", r is None and r2 and "use --dry-run" in r2,
         (r, r2))
    r = P.check_command(card_none, "py tools/stage_prerun.py --graph x.json tools/recipes/stage_x.py")
    case("FP37c stage_prerun outside its offline modes is still not offline", r and "stage_prerun" in r, r)
    with open(LEDGER, "w", encoding="utf-8") as f:
        f.write(json.dumps({"card": "142-P2", "log": "prep_c142_p2_q1.log", "t": "2026-10-03 10:00:00"}) + "\n")
        f.write(json.dumps({"card": "142-4", "log": "build_ringseqcheck_v0.log", "t": "2026-10-03 10:05:00"}) + "\n")
    with open(os.path.join(CARDS, "task_142-4.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "task/1", "id": "142-4", "flags": {"labview": "build"}}, f)
    with open(ACTIVE, "w", encoding="utf-8") as f:
        json.dump({"agent-lv": {"card": os.path.join(CARDS, "task_142-4.json"), "agent_type": "material"}}, f)
    logp = os.path.join(XT, "prep_c142_p2_q1.log")
    body = ("BGRUN START 2026-10-03 10:00:00 limit 5.0 min: py -u tools/bench/prep_c142_p2_q1.py\n"
            'RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":0,"fail":1},"first_fail":"x"}\n'
            "BGRUN END rc=1 after 3s\n")
    with open(logp, "w", encoding="utf-8") as f:
        f.write(body)
    case("FP36 failing log owner from the ledger", P.log_owner(logp) == "142-P2", P.log_owner(logp))
    oo = GP.other_card_log({"agent_id": "agent-lv"}, logp, body)
    case("FP36 an LV card is not held by another card's failing log (RULE-OTHER-CARD)", oo == ("142-4", "142-P2"), oo)
    own = os.path.join(XT, "build_ringseqcheck_v0.log")
    body_own = body.replace("10:00:00 limit", "10:05:00 limit")
    with open(own, "w", encoding="utf-8") as f:
        f.write(body_own)
    case("FP36b its OWN failing log still holds it", P.log_owner(own, body_own) == "142-4"
         and GP.other_card_log({"agent_id": "agent-lv"}, own, body_own) is None)
    with open(LEDGER, "a", encoding="utf-8") as f:     # a LATER non-launch row naming the same log (fp-36's own record)
        f.write(json.dumps({"card": "142-4", "log": "prep_c142_p2_q1.log", "t": "2026-10-03 10:09:26"}) + "\n")
    case("FP36e a ledger row written after the run started does not take it over", P.log_owner(logp, body) == "142-P2")
    case("FP36c the judgement session (no agent_id) is held by every failing log", GP.other_card_log({}, logp, body) is None)
    body2 = body.replace('"first_fail":"x"}', '"first_fail":"x","card":"143-9","labview":"none"}')
    case("FP36d the RESULT line's card field wins over the ledger", P.log_owner(logp, body2) == "143-9")
    os.environ["CARD_ID"], os.environ["CARD_LABVIEW"] = "143-9", "none"
    rl = P.result_line(P.make_result(1, 0))
    os.environ.pop("CARD_ID"), os.environ.pop("CARD_LABVIEW")
    case("RL1 result_line stamps card + labview from bgrun's env", '"card":"143-9"' in rl and '"labview":"none"' in rl, rl)

    # ---------------------------------------------------------------- WAITING
    w = {"schema": "result-line/1", "status": "WAITING", "gates": {"pass": 0, "fail": 0}, "first_fail": "WAITING: x"}
    case("W1 WAITING result line is valid and not a failure", P.validate_obj(w)[0] and not P.result_failed(w))
    case("W2 result/1 accepts WAITING", P.validate_obj({"schema": "result/1", "id": "143-P1", "status": "WAITING",
                                                         "gates": {"pass": 0, "fail": 0}})[0])
    seg_w = ("BGRUN START 2026-10-04 10:00:00 limit 3.0 min: x\n" + P.result_line(dict(w)) + "\nBGRUN END rc=0 after 2s\n")
    case("W3 a WAITING run log is not failing (guard_peer reads run_verdict)", not P.run_verdict(seg_w)["failed"])
    real = SP.provisional_dry_graph
    SP.provisional_dry_graph = lambda r: ("base_provisional.json", None)
    f143 = ["EXECUTOR-STOP tools/bench/plan_ring_p4_s03v18.json: executed 0 of 20 ops, stopped IN op {'k': None}: ExecStop: "
            "BASE: the scratch copy's graph differs from the plan's base graph: {'unbound': [-21, -19, -16, -15, -12, -11]}"]
    wr = SP.waiting_reason("r.py", {"status": "FAIL", "fails": f143})
    case("W4 143-P1's dry failure -> WAITING", wr and "-21" in wr, wr)
    case("W5 a real base difference is not WAITING", SP.waiting_reason("r.py", {"status": "FAIL", "fails": [
        f143[0].replace("{'unbound': [-21, -19, -16, -15, -12, -11]}", "{'only_sim_terms': [3]}")]}) is None)
    SP.provisional_dry_graph = lambda r: (None, None)
    case("W6 not a provisional base -> never WAITING", SP.waiting_reason("r.py", {"status": "FAIL", "fails": f143}) is None)
    SP.provisional_dry_graph = real
    g143 = [["X1 dry run PASS", False, "EXECUTOR-STOP"], ["X2 plan", True, ""], ["X5 wiring ops", False, "ops 0"],
            ["X10 predicted MB", False, "UNMEASURED: base is PROVISIONAL"]]
    case("W7 143-P1's prerun failures follow from the base -> WAITING", SP.waiting_prerun({"gates": g143}))
    case("W8 an X2 failure is not WAITING", not SP.waiting_prerun({"gates": g143 + [["X2 finalized", False, "no"]]}))

    # ---------------------------------------------------------------- write-time hook
    case("WR1 headerless tools script -> write problem", any("no scope header" in x for x in GW.decide(nohdr)))
    case("WR2 clean script -> no write problem", GW.decide(put("clean.py", HDR_NONE + "x = 1\n")) == [],
         GW.decide(os.path.join(TMP, "clean.py")))
    case("WR3 dishonest none -> write problem", any("dishonest" in x for x in GW.decide(put("dis.py", HDR_NONE + "import gscript\n"))))
    case("WR4 compile error -> write problem", any("compile" in x for x in GW.decide(cb)))
    plan = json.load(open(os.path.join(HERE, "plan_ring_p4_s03v18.json"), encoding="utf-8"))
    base_ok = P.validate_obj(plan)
    plan["actions"][0]["why"] = "x" * 545
    pj = put("plan_e3.json", json.dumps(plan))
    case("WR5a a 545-char PROSE why (143-5 failure 1) is no longer a problem (chat-S5 PD337(d))", GW.decide(pj) == [])
    plan["actions"][0]["id"] = "y" * 81
    pj = put("plan_e3.json", json.dumps(plan))
    pr = GW.decide(pj)
    case("WR5b a MACHINE field over its limit (id 81 > 80) -> write problem", base_ok[0] and pr and "schema" in pr[0],
         pr[:1] or base_ok)
    tgt = put("pinned.py", HDR_NONE + "x = 2\n")
    with open(os.path.join(CARDS, "task_P9.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "task/1", "id": "P9", "inputs": [{"path": os.path.relpath(tgt, ROOT), "md5": "0" * 32}]}, f)
    case("WR6 an open card pinning another md5 -> stale-pin problem (143-P1)", any("open card P9" in x for x in GW.decide(tgt)))
    open(os.path.join(CARDS, "result_P9.json"), "w").write("{}")
    case("WR7 a closed card's pin is not reported", not any("open card P9" in x for x in GW.decide(tgt)))
    tk = put("task_e3x.json", json.dumps({"schema": "task/1", "id": "e3x", "kind": "build", "goal": "g", "why": "w",
                                          "inputs": [{"path": os.path.relpath(tgt, ROOT), "md5": "1" * 32}],
                                          "pass": ["p"], "outputs": [], "flags": {}, "budget": {"failures": 1, "minutes": 5},
                                          "unblocks": "M4"}))
    case("WR8 task/1 with a stale input md5 -> problem", any("stale" in x for x in GW.decide(tk)), GW.decide(tk))
    rv = os.path.join(XT, "2026-10-04-priorart-e3x.md")
    with open(rv, "w", encoding="utf-8") as f:
        f.write("PRIOR-ART: settled-already\n\n%s\n\nFIXED: already-failed - tools/x.py:1 - y\n" % GC.DISPOSITION_MARK)
    rp = GW.check_review(rv)
    case("WR9 release line naming a slug the review did not issue (143-1) -> problem", any("already-failed" in x for x in rp), rp)

    # ---------------------------------------------------------------- diff-only prior art
    old = ["PLAN = 'tools/bench/plan_ring_p4_s02v18.json'", "STAGE = 's02v18'", "MEM = 596.5", "x = run(PLAN)"]
    new = ["PLAN = 'tools/bench/plan_ring_p4_s03v18.json'", "STAGE = 's03v18'", "MEM = 676.9", "x = run(PLAN, retry=2)"]
    pc, sub = PD.diff_lines(old, new)
    case("PA1 names/paths/numbers are parameter-only, a changed call is substantive", pc == 3 and len(sub) == 1, (pc, sub))
    case("PA2 pattern key masks digit runs", PD.pattern_key("stage_d1_ring_p4_s03v18.py") == PD.pattern_key("stage_d1_ring_p4_s02v18.py"))
    sc = PD.scope(os.path.join(TOOLS, "recipes", "stage_d1_ring_p4_s03v18.py"), new_classes=[])
    case("PA3 s03v18 vs its approved sibling (informational)", True,
         None if sc is None else "sibling %s param %d substantive %d" % (sc["sibling"], sc["param_only"], len(sc["substantive"])))
finally:
    shutil.rmtree(TMP, ignore_errors=True)
    shutil.rmtree(XT, ignore_errors=True)

n_fail = sum(1 for _n, ok in R if not ok)
print(P.result_line(P.make_result(len(R) - n_fail, n_fail, next((n for n, ok in R if not ok), None))), flush=True)
sys.exit(1 if n_fail else 0)
