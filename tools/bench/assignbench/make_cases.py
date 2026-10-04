r"""assignbench case builder (card chat-B6). Writes tools/bench/assignbench/cases.json from SPEC below.

Each case = one decision point INSIDE a runner cycle (130-143): the cycle purpose (tools/bench/next.json at the cycle's
base commit = the previous cycle's NEXT), the cards done so far (their task goal + result/1 object as committed by the
cycle's auto-commit), card minutes / reported USD so far, and the caps. The answer is the NEXT ACTION from a fixed
menu. The known answer is what later cards/cycles PROVED; every evidence ref is (path, regex) and is resolved here to
path:line against the working tree, failing loudly when absent. Cases history does not settle were left out.

    py -u tools/bench/assignbench/make_cases.py          -> cases.json + a RESULT line

WHAT EXISTED FIRST: decbench (cases.json format, prepare/leak_check/run_arm/blind, dec_score) - the case dicts below
use the same keys (base, copy, leak, rubric, known_answer, category, fields) so decbench's functions run them unchanged.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CYCLE_COMMIT = {130: "5f1b8a56", 131: "83dd0e70", 132: "53737825", 133: "0b72718d", 134: "23cd9f3e",
                135: "c13463c1", 136: "421d6108", 137: "fb098a75", 138: "f9b5d650", 139: "1593b640",
                140: "2188ca56", 141: "5a579592", 142: "eed09beb", 143: "67b4f319"}
CAPS = {"minutes": 180, "usd": 60}
A = r"ACTION:[^\n]*"          # the answer's ACTION line


def act(*names):
    return [A + "(" + "|".join(names) + ")"]


C = "tools/bench/cards/"
SPEC = [
 dict(id="A01-c130-review-owed", cycle=130, done=["130-1", "130-2"], action="RETRY",
      answer="RETRY 130-1 (same goal, from its step 3) with flags.peers widened to include `hypothesis`, so the owed "
             "hypothesis review of selftest_x10_c130_1.log can be dispatched inside the card. The block is a card-flag "
             "mismatch named by the hook, not a model or design problem.",
      ev=[(C + "task_130-3.json", r'"retry_of_card": "130-1"'), (C + "task_130-3.json", r'"goal"'),
          (C + "result_130-3.json", r'"pass": 1')],
      m2=("the retry carries the owed hypothesis review (peers flag)", [r"hypothesis"]),
      forbid=act("ESCALATE", "CLOSE")),
 dict(id="A02-c130-fp24", cycle=130, done=["130-1", "130-2", "130-3"], action="RETRY",
      answer="RETRY 130-3 from its P1 with the owed review of card 130-2's failing log diag_c130_2_suite_gb.log done "
             "first (that log, not 130-3's own work, is what guard_peer blocked on), then the X10 self-test, re-cut and "
             "P3b-1 dry/prerun.",
      ev=[(C + "task_130-4.json", r'"retry_of_card": "130-3"'), (C + "task_130-4.json", r'"goal"'),
          (C + "result_130-4.json", r'"first_fail"')],
      m2=("names the owed review of 130-2's log (diag_c130_2_suite_gb.log) as the unblocking step",
          [r"suite_gb", r"130-2[^\n]{0,80}(log|review)", r"review[^\n]{0,80}130-2"]),
      forbid=act("ESCALATE", "CLOSE")),
 dict(id="A03-c131-peak-680", cycle=131, done=["131-1", "131-2", "131-3"], action="HANDBACK",
      answer="HANDBACK: the measured peak 680.8 MB exceeds the 675 MB fail_above only through the final whole-VI read; "
             "whether to accept it / raise the threshold / re-cut is a memory-threshold decision for judgement. "
             "Judgement decided PD272 (fail_above 690, then S3/S4 and launch) and P3b-1 was then launched and read.",
      ev=[(C + "task_131-4.json", r'fail_above 690'), (C + "result_131-6.json", r'"status"')],
      m2=("asks judgement about the 675 MB limit vs the measured 680.8 MB (threshold / re-cut)",
          [r"675", r"680", r"threshold|fail_above|memory limit"]),
      forbid=act("ESCALATE", "RETRY", "CLOSE")),
 dict(id="A04-c131-close", cycle=131, done=["131-1", "131-2", "131-3", "131-4", "131-5", "131-6"], action="CLOSE",
      answer="CLOSE: the purpose (P3b-1 scratch pin4 then ONE launch) is met - P3b-1 launched as "
             "D1_ring_p3b1_20261002_060910.vi and its full Error List read (53) by 131-6, 129 card-minutes used of 180. "
             "The next step (P3b-2 rebase tooling, moving the bed) needs judgement; the next cycle started from the "
             "P3b-1 file as bed.",
      ev=[(C + "result_131-6.json", r'"status"'), (C + "cycle_132.json", r'D1_ring_p3b1_20261002_060910')],
      m2=("states that P3b-1 is launched and read (purpose met)", [r"P3b-1|p3b1", r"launch|purpose"]),
      forbid=act("ESCALATE", "RETRY")),
 dict(id="A05-c132-seq-block", cycle=132, done=["132-1", "132-2"], action="RETRY",
      answer="RETRY 132-2 now (as 132-3): it was BLOCKED only because card 132-1 was editing tools/stage_prerun.py; "
             "132-1 has returned, so the re-issue may run stage_prerun --dry/--prerun on the graph reader first.",
      ev=[(C + "task_132-3.json", r'"retry_of_card": "132-2"'), (C + "task_132-3.json", r'"goal"')],
      m2=("the re-issue includes the dry + prerun of the reader (now that 132-1 is done)", [r"dry", r"prerun"]),
      forbid=act("ESCALATE", "CLOSE"),
      leak_ok={"132-3": "brief_132-1.md:25 (written at cycle start) names a PLANNED rebase card 132-3; the id became "
                        "the re-issue of 132-2 later, the brief does not say so"}),
 dict(id="A06-c132-fp29", cycle=132, done=["132-1", "132-2", "132-3"], action="ISSUE",
      answer="ISSUE a card that first makes X10 model a 0-edit read-only reader (gate false positive fp-29: the check "
             "refuses the very run that would produce its meter), then runs the P3b-1 graph read and continues to the "
             "rebase. Judgement wrote it as PD277 (132-4); 132-4 then did the graph read with LabVIEW.",
      ev=[(C + "task_132-4.json", r'fp-29'), (C + "result_132-4.json", r'"labview_runs": 1')],
      m2=("fix X10 for the read-only reader (fp-29 / UNMEASURED) and then run the graph read",
          [r"X10|fp-29|UNMEASURED"]),
      forbid=act("ESCALATE", "CLOSE")),
 dict(id="A07-c134-owner-absent", cycle=134, done=["134-1", "134-2", "134-3"], action="HANDBACK",
      answer="HANDBACK: 134-3 returned by its own card rule (no inference) because FS 27509's diagram uid is absent from "
             "the measured graph; whether owners derived from measured border links (outer-face frame_diagram, 8/8 "
             "agree) count as 'measured' is a definition judgement must make. Judgement decided PD289(f) and 134-4 "
             "built on it.",
      ev=[(C + "task_134-4.json", r'PD289\(f\)'), (C + "result_134-4.json", r'"pass": 4')],
      m2=("asks whether owners from measured border links count as measured", [r"measured", r"owner|border|outer"]),
      forbid=act("ESCALATE", "RETRY")),
 dict(id="A08-c135-close", cycle=135, done=["135-1", "135-P1", "135-P2", "135-2", "135-3", "135-4", "135-5"],
      action="CLOSE",
      answer="CLOSE: the purpose (ONE launch of P3b-2, bed moves to the P3b-2 final) is met by 135-4 (PASS 13/0) and "
             "135-5 (acceptance bookkeeping PASS 18/0), and the P4 offline facts are in. The next step (P4 routes) "
             "needed a new judgement design (PD295) - the next cycle started from it with the P3b-2 file as bed.",
      ev=[(C + "result_135-5.json", r'"status"'), (C + "cycle_136.json", r'D1_ring_p3b2b_20261002_130007')],
      m2=("states P3b-2 launched/accepted (purpose met)", [r"P3b-2|p3b2", r"accept|launch|purpose|bed"]),
      forbid=act("ESCALATE", "RETRY")),
 dict(id="A09-c137-lookup-twice", cycle=137, done=["137-1", "137-P1"], action="ISSUE",
      answer="ISSUE a scratch-VI verification card of the failing node lookup (constant/primitive created inside a NEW "
             "While body, each read method) - the same lookup failed in 136-3 and 137-1, and the standing rule makes the "
             "next LabVIEW act a scratch-VI check, not a third routes run. 137-3 did it (PASS 5/0) and found that "
             "node_labels cannot see constants; 137-5 then used read_terms.",
      ev=[(C + "task_137-3.json", r'"goal"'), (C + "result_137-3.json", r'"status"')],
      m2=("a scratch-VI check of the lookup before any third routes run", [r"scratch"]),
      forbid=act("RETRY", "ESCALATE"),
      leak_ok={"137-2": "task_137-1.json names 137-2 as the parallel stop-mode op card issued with it (no result)"}),
 dict(id="A10-c137-select-array", cycle=137,
      done=["137-1", "137-P1", "137-P2", "137-3", "137-P3", "137-4", "137-5", "137-6", "137-7"], action="HANDBACK",
      answer="HANDBACK: 137-7 measured that Select rejects a Boolean ARRAY on s whatever t/f carry, so the P4 reader core "
             "('Select with a Boolean-ARRAY s') must be redesigned - a design / rule-1a decision. Judgement replaced it "
             "with a For-loop + scalar Select + Array Min group (PD311(b), plan v8).",
      ev=[(C + "result_137-7.json", r'redesign'), (C + "task_138-4.json", r'PD311\(b\)')],
      m2=("names the Select / Boolean-array reader-core redesign as the question", [r"Select", r"array"]),
      forbid=act("RETRY", "ESCALATE"),
      leak_ok={"137-2": "task_137-1.json names 137-2 as the parallel stop-mode op card issued with it (no result)"}),
 dict(id="A11-c139-x10-750", cycle=139,
      done=["139-1", "139-P1", "139-2", "139-P2", "139-3", "139-4", "139-5", "139-6", "139-7"], action="HANDBACK",
      answer="HANDBACK: the step-1 plan predicts 750.7 MB > 690 at 29 reads; splitting step 1 by memory vs changing the "
             "checkpoint set (and re-sizing steps 2-5 against X10) is a plan decision. Judgement's next act was PD319(c), "
             "an offline X10 session table of the whole plan before any cut.",
      ev=[(C + "result_139-7.json", r'750\.7'), (C + "task_140-1.json", r'PD319\(c\)')],
      m2=("asks how to cut by memory (750.7 > 690)", [r"750|690|X10|memory"]),
      forbid=act("RETRY", "ESCALATE")),
 dict(id="A12-c140-rle-order", cycle=140, done=["140-1", "140-2"], action="HANDBACK",
      answer="HANDBACK (two competing explanations: plan order vs op behaviour) - judgement decided PD321: delete_wire "
             "w23255 before deleting #10171 (plan v15) and gate w23255's sinks; 140-3 (retry of 140-2) then passed op 3. "
             "A card that itself re-orders the plan this way also matches history.",
      ev=[(C + "task_140-3.json", r'"retry_of_card": "140-2"'), (C + "task_140-3.json", r'delete_wire w23255')],
      m2=("the fix is the plan order: remove wire w23255 before deleting #10171",
          [r"w23255[^\n]{0,120}(before|first)|(before|first)[^\n]{0,120}(10171|w23255)|order"]),
      forbid=act("ESCALATE", "CLOSE"), m1=act("HANDBACK", "RETRY", "ISSUE")),
 dict(id="A13-c140-insert-vs-ras", cycle=140, done=["140-1", "140-2", "140-P1", "140-3"], action="HANDBACK",
      answer="HANDBACK (rule 1a): the extra Error List item shows the ring's per-slot write node is an Insert Into Array "
             "where Replace Array Subset is meant - a computation question, not a count to re-pin. Judgement had it "
             "measured (140-4: 5 bed nodes are Insert Into Array where PD246(c) says Replace Array Subset) and repaired "
             "them first in plan v16 (141-1).",
      ev=[(C + "result_140-4.json", r'Insert Into Array'), (C + "task_141-1.json", r'repair')],
      m2=("raises Insert Into Array vs Replace Array Subset as a computation (rule 1a) question",
          [r"Insert Into Array|Replace Array Subset|rule 1a|computation"]),
      forbid=act("RETRY", "ESCALATE", "CLOSE")),
 dict(id="A14-c142-first-fail", cycle=142, done=["142-1"], action="RETRY",
      answer="RETRY 142-1 (failure 1 of the budget of 2): the run stopped on our own script's delete check "
             "(expected 1 object gone, got 2), not on a design question. 142-2 (retry) got past that step (16 gates vs 9).",
      ev=[(C + "task_142-2.json", r'"retry_of_card": "142-1"'), (C + "result_142-2.json", r'"pass": 16')],
      m2=("treats it as a script-side failure to retry", [r"delete|script|constant|retry"]),
      forbid=act("ESCALATE", "CLOSE")),
 dict(id="A15-c142-escalate", cycle=142, done=["142-1", "142-P1", "142-2"], action="ESCALATE",
      answer="ESCALATE to Opus max (rung 1): the same card goal failed twice on Opus high (142-1, 142-2), so the failure "
             "budget is spent. 142-3 (escalation 1, Opus max) passed 87/0 on its first LabVIEW run.",
      ev=[(C + "task_142-3.json", r'"escalation": 1'), (C + "result_142-3.json", r'"pass": 87')],
      m2=("the rung is Opus max (not Fable low first)", [r"opus[ -]?max|max"]),
      forbid=act("RETRY", "CLOSE")),
 dict(id="A16-c143-first", cycle=143, done=[], action="ISSUE",
      answer="ISSUE the session-2 LabVIEW card (prior-art review of the s02v18 recipe, ONE scratch on a byte copy of the "
             "s01 file, adopt on full PASS) and, beside it, an offline PREP card for the session-3 plan (provisional on "
             "stagesim's end of s02). Cycle 143 started exactly so (143-1 + 143-P1).",
      ev=[(C + "task_143-1.json", r'"goal"'), (C + "task_143-P1.json", r'"goal"')],
      m2=("the session-2 scratch / adopt card", [r"s02|session[ -]?2"]),
      bonus=("an offline session-3 prep card beside it", [A + "PREP", r"s03|session[ -]?3"]),
      forbid=act("CLOSE", "HANDBACK", "ESCALATE")),
 dict(id="A17-c143-el53", cycle=143, done=["143-P1", "143-1"], action="ISSUE",
      answer="ISSUE a read-only card that loads the s02 scratch file in a fresh instance, reads its graph and identifies "
             "the 2 extra Error List items by uid (then the failed-prediction review). 143-2 did so: both items were the "
             "by-design session-boundary state (1.2 loop stop terminal, StopAll read Local), so s02 was adopted in 143-3; "
             "the S1 replay confirms 143-1 would have passed with the by-design rule.",
      ev=[(C + "result_143-2.json", r'"status"'), ("tools/bench/replay_s5.log", r'by.?design|53')],
      m2=("identify the 2 extra Error List items (read-only) before deciding", [r"identif|which|extra|by.?design"]),
      forbid=act("RETRY", "ESCALATE")),
 dict(id="A18-c143-uidreuse", cycle=143, done=["143-P1", "143-1", "143-2", "143-P2", "143-3"], action="ISSUE",
      answer="ISSUE an offline tooling card: the rebase refusal is a checker false failure (LabVIEW re-issued the deleted "
             "Comparison's terminal uid 23276 to the new Local) - make the rebase path key terminals by (uid, owner, name) "
             "/ note uid re-use, then rebase s03 again. 143-4 did it and UID-REUSE was gone (REUSE-NOTED 23276); the S1 "
             "replay resolves it without a card.",
      ev=[(C + "result_143-4.json", r'REUSE-NOTED'), ("tools/bench/replay_s5.log", r'REUSE-NOTED')],
      m2=("fix the uid-reuse keying on the rebase path and rebase again", [r"uid|reuse|re-use"]),
      forbid=act("ESCALATE", "CLOSE")),
 dict(id="A19-c143-value-stopall", cycle=143, done=["143-P1", "143-1", "143-2", "143-P2", "143-3", "143-4"],
      action="ISSUE",
      answer="ISSUE (or retry with the fix): correct the s03 plan's Local terminal addresses from the simulator name "
             "'value' to the measured name 'StopAll' by script, then rebase on the s02 graph. 143-5 did it and the rebase "
             "PASSed (plan da66a030); the S1 replay resolves it by position.",
      ev=[(C + "result_143-5.json", r'REBASED'), ("tools/bench/replay_s5.log", r'ADDRESS-RESOLVED')],
      m2=("re-address the Local terminal to its measured name (StopAll) and rebase", [r"StopAll|address|measured name"]),
      forbid=act("ESCALATE", "CLOSE"), m1=act("ISSUE", "RETRY")),
 dict(id="A20-c143-why-scan", cycle=143, done=["143-P1", "143-1", "143-2", "143-P2", "143-3", "143-4", "143-5"],
      action="RETRY",
      answer="RETRY the remaining s03 checks with our own pred script fixed (scan uids outside `why`/notes): the failure is "
             "our script tokenising prose, fully explained in the result. 143-6 did it and PASSed 8/0 (X10 676.4, EL 56, "
             "dry + prerun 16/0).",
      ev=[(C + "task_143-6.json", r'why'), (C + "result_143-6.json", r'"pass": 8')],
      m2=("fix the script's scan of the `why` text and rerun", [r"why"]),
      forbid=act("ESCALATE", "CLOSE", "HANDBACK"), m1=act("RETRY", "ISSUE")),
 dict(id="A21-c143-cap-launch-s03", cycle=143,
      done=["143-P1", "143-1", "143-2", "143-P2", "143-3", "143-4", "143-5", "143-6"], action="ISSUE",
      answer="ISSUE the session-3 LabVIEW card: ONE scratch of plan_ring_p4_s03v18.json (da66a030) on a byte copy of the "
             "adopted s02 file, adopt on full PASS, full Error List + graph read (session-4 prep may run beside). "
             "Session 2 is adopted and session 3 is ready (dry + prerun 16/0, prior-art novel, scratch required); 88 min "
             "and $35 of 180 min / $60 used. Cycle 143 stopped here only because the 6-card dispatch cap was reached, and "
             "the next cycle's first act was exactly this card.",
      ev=[("STATUS.md", r'FIRST ACT of cycle 144 = P4 SESSION 3'), ("docs/chat-handoff.md", r'cycle 143 used 6 = cap'),
          ("tools/bench/cycle_runner.log", r'CYCLE 143 \| 2026-10-03 10:47:54')],
      m2=("the session-3 scratch card on a copy of the s02 file", [r"s03|session[ -]?3"]),
      bonus=("session-4 prep beside it", [A + "PREP", r"s04|session[ -]?4"]),
      forbid=act("CLOSE")),
]


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=MAIN, capture_output=True, text=True, encoding="utf-8").stdout


def resolve(path, rx):
    p = os.path.join(MAIN, path)
    rx = rx.replace('": ', '":\\s*')       # result files are compact JSON, task files pretty-printed
    with open(p, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if re.search(rx, line):
                return "%s:%d" % (path, i)
    raise SystemExit("EVIDENCE NOT FOUND %s /%s/" % (path, rx))


def card_view(commit, cid):
    t = json.loads(git("show", "%s:tools/bench/cards/task_%s.json" % (commit, cid)))
    r_txt = git("show", "%s:tools/bench/cards/result_%s.json" % (commit, cid))
    r = json.loads(r_txt) if r_txt.strip() else None
    return {"card": cid, "kind": t.get("kind"), "goal": t.get("goal"), "escalation": t.get("escalation"),
            "retry_of_card": t.get("retry_of_card"), "flags": t.get("flags"), "budget": t.get("budget"),
            "result": r}


def main():
    cases, used_ids = [], set()
    for s in SPEC:
        cyc, commit = s["cycle"], CYCLE_COMMIT[s["cycle"]]
        base = git("rev-parse", commit + "^").strip()
        nxt = json.loads(git("show", base + ":tools/bench/next.json"))
        views = [card_view(commit, c) for c in s["done"]]
        mins = sum(((v["result"] or {}).get("cost") or {}).get("minutes") or 0 for v in views)
        usd = sum(((v["result"] or {}).get("cost") or {}).get("usd") or 0 for v in views)
        all_ids = sorted({f[5:-5] for f in git("ls-tree", "--name-only", commit, "tools/bench/cards/").split()
                          for f in [os.path.basename(f)] if re.match(r"task_%d-" % cyc, f)})
        later = [c for c in all_ids if c not in s["done"]]
        copy = [{"from": commit, "path": "tools/bench/cards/cycle_%d.json" % cyc}]
        for c in s["done"]:
            for pat in ("task_%s.json", "result_%s.json", "brief_%s.md"):
                path = "tools/bench/cards/" + pat % c
                if subprocess.run(["git", "cat-file", "-e", "%s:%s" % (commit, path)], cwd=MAIN,
                                  capture_output=True).returncode == 0:
                    copy.append({"from": commit, "path": path})
        leak = []
        for c in later + ["%d-1" % (cyc + 1), "%d-P1" % (cyc + 1)]:
            n, k = c.split("-", 1)
            if c not in s.get("leak_ok", {}):  # bare id named by a done card BEFORE the decision (see leak_ok reason)
                leak.append(r"(?<![\w.-])%s-%s(?![\w])" % (n, re.escape(k)))
            leak.append(r"c%s_%s(?![\w])" % (n, k.lower()))
        ev = [resolve(p, rx) for p, rx in s["ev"]]
        known = s["answer"] + " Evidence: " + "; ".join(ev) + "."
        m1 = s.get("m1") or act(s["action"])
        rubric = {"must_hit": [{"id": "M1", "text": "ACTION is %s" % s["action"], "re": m1},
                               {"id": "M2", "text": s["m2"][0], "re": s["m2"][1]}],
                  "forbidden": [{"id": "F1", "text": "chooses a forbidden action: %s" % s["forbid"][0], "re": s["forbid"]}]}
        if s.get("bonus"):
            rubric["bonus"] = [{"id": "B1", "text": s["bonus"][0], "re": s["bonus"][1]}]
        ctx = {"cycle": cyc, "purpose": {"act": nxt.get("act"), "pass": nxt.get("pass"), "advances": nxt.get("advances")},
               "caps": CAPS, "used": {"card_minutes": mins, "usd_reported_by_cards": round(usd, 2),
                                      "note": "card minutes only; judgement/assignment overhead not included"},
               "cards_done_in_order": views}
        stub = "ACTION: %s\nCARD: (stub) %s\nREASON: stub answer built from the known answer\nHANDBACK-QUESTION: -" % (
            s["action"], s["answer"][:300])
        cases.append({"id": s["id"], "category": "assign", "base": base, "copy": copy, "leak": leak, "absent": [],
                      "rubric": rubric, "known_answer": known, "known_action": s["action"], "evidence": ev,
                      "leak_ok": s.get("leak_ok", {}),
                      "fields": {"context": json.dumps(ctx, ensure_ascii=False, indent=1)}, "stub_answer": stub})
        used_ids.add(s["id"])
        print("CASE %s base %s done %d later %d ev %s" % (s["id"], base[:8], len(views), len(later), ev[0]))
    doc = {"schema": "assignbench-cases/1", "made_by": "tools/bench/assignbench/make_cases.py", "caps": CAPS,
           "templates": {"preamble": PREAMBLE, "assign": "DECISION POINT (JSON):\n{context}\n"}, "cases": cases}
    out = os.path.join(HERE, "cases.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    acts = {}
    for c in cases:
        acts[c["known_action"]] = acts.get(c["known_action"], 0) + 1
    print("ACTIONS", acts)
    import hashlib
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": len(cases), "fail": 0},
                                  "first_fail": None, "artefacts": [{"path": "tools/bench/assignbench/cases.json",
                                  "md5": hashlib.md5(open(out, "rb").read()).hexdigest()}]}), flush=True)


PREAMBLE = """You are the CYCLE ASSIGNMENT AGENT of an unattended LabVIEW-refactoring project (this checkout, read-only, as it
was when the cycle started; the cards already done in this cycle are under tools/bench/cards/ and are also given below).

How cycles now work: the JUDGEMENT agent sets the cycle PURPOSE (tools/bench/next.json: act + pass items). You turn it into
work: you issue task cards (task/1) to material agents, read their result/1 objects, retry a card, escalate a card whose
goal has failed twice on the default model (rung 1 = Opus max, rung 2 = Fable low), start an OFFLINE prep card beside a
LabVIEW card (at most one LabVIEW card at a time plus one offline card), and end the cycle when the purpose is met. You
HAND BACK to judgement when a failure is not explained by the facts, or when the next step needs a design, threshold,
rule (e.g. rule 1a: never change the original's computation) or plan decision. There is NO cap on the number of cards;
the caps are time and cost per cycle (given below). Project rules: CLAUDE.md and STATUS.md in this checkout.

Decide the ONE next action after the cards listed below. Answer in exactly this format, nothing before it:
ACTION: <one of ISSUE | RETRY | ESCALATE | PREP | CLOSE | HANDBACK>   (a LabVIEW card plus an offline prep card in one
        step is written "ACTION: ISSUE + PREP")
CARD: <one-line goal of the card you issue / retry / escalate (and of the prep card), or "-">
REASON: <at most 5 lines, citing the result facts you rely on>
HANDBACK-QUESTION: <the one question for judgement if ACTION is HANDBACK, else "-">

Menu: ISSUE <card goal> = a new card | RETRY = re-issue the same card goal (optionally with a fix of our own script or a
widened flag) | ESCALATE = the same goal on the next model rung | PREP = start an offline prep card beside | CLOSE =
purpose met, end the cycle | HANDBACK = return to judgement with one question.

"""


if __name__ == "__main__":
    main()
