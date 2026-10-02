r"""s2_replay - card chat-S2 item 4 (offline): classify the first_fail line of every non-PASS result card of cycles 130-141 under
the STOP / LOG-only rule (tools/gateclass.py) and count how many would have CONTINUED.

The first_fail lines are PROSE summaries written by material agents, not gate rows, so each card carries a CATEGORY assigned
from the rule's own lists (brief_chat-S2.md "Rule to implement") and, where the line cites a gate with numbers, the module's
verdict on those numbers is computed and printed beside it (the two must agree, else the row is flagged DISAGREE).
Categories: LOG-name, LOG-count, LOG-arith, LOG-fixture  -> would continue;  STOP-<why> -> would still stop;
NOT-A-GATE (a hook / gate-false-positive BLOCKED, not a stage-gate mismatch) -> outside this rule.
PREDICTION CONTRACT: every non-PASS result of 130-141 gets exactly one category; every computed module verdict agrees.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gateclass as GC                                                 # noqa: E402
import protocol                                                        # noqa: E402

# id -> (category, evidence). Evidence = the cited log line or the first_fail text itself.
CAT = {
    "130-1": ("LOG-fixture", "self-test fixture md5 from git LF vs working CRLF (stale fixture)"),
    "130-3": ("NOT-A-GATE", "gate-fp:fp-24 (hook false positive)"),
    "130-4": ("STOP-crash", "plan script crashed (ExecStop half names) - not a gate mismatch"),
    "130-5": ("STOP-structure", "FS frame f0 with 0 terminals; FS/FU frame gates"),
    "130-6": ("LOG-name", "stage_d1_ring_p3b1_scratch_pin3.log:370 BINDING FSOT keys differ ONLY by name ''/'Image Out'; "
                          "name-free keys (Terminal,False):1,(Terminal,True):1 unique and equal"),
    "131-3": ("STOP-memory", "peak memory above fail_above"),
    "131-4": ("STOP-errorlist", "Error List 53 vs 54, missing item class not identified as loose ends (fail-closed)"),
    "131-5": ("LOG-arith", "helper's own arithmetic: 55 - 2 == 53 but loose-ends entry 1 -> -1"),
    "132-1": ("STOP-binding", "dry stops at STEPX 00, unbound ids"),
    "132-2": ("NOT-A-GATE", "launch gate prerun record (hook)"),
    "132-3": ("NOT-A-GATE", "gate-fp:fp-29"),
    "132-4": ("LOG-name", "stage_prerun_c132_4_rebase_p3b2.log:3 created objects differ only by terminal-name keys "
                          "(rebind is name-free since card 132-5, stage_prerun.py:3324-3326)"),
    "132-5": ("STOP-sim", "re-sim: a border needs a tunnel"),
    "132-6": ("STOP-binding", "route check unbound terms"),
    "133-1": ("STOP-input", "L0 plan_in path pin"),
    "133-4": ("LOG-fixture", "selftest_chat_p1 fixture cards copy task_chat-P1 write globs (stale fixture)"),
    "133-5": ("STOP-structure", "FR created objects on base frames, no new frame"),
    "133-6": ("STOP-binding", "FS-CARRY created uid not bound"),
    "134-1": ("STOP-tool", "7 of 68 FSOT not classified by stagesim"),
    "134-2": ("STOP-sim", "no common diagram"),
    "134-3": ("STOP-tool", "owner row absent"),
    "134-4": ("NOT-A-GATE", "gate-fp:fp-30"),
    "134-5": ("STOP-prediction", "pred census not written (nothing predicted)"),
    "135-1": ("STOP-count", "object count 10363 vs 10334 over all classes, class not identified (fail-closed)"),
    "135-2": ("STOP-tool", "offline self-test rc 1"),
    "135-3": ("STOP-sim", "19/19 step states differ"),
    "136-1": ("NOT-A-GATE", "gate-fp:fp-33"),
    "136-2": ("STOP-memory", "X10 UNMEASURED"),
    "136-3": ("STOP-crash", "ValueError const not in Diagram"),
    "136-P1": ("STOP-sim", "a border needs a tunnel"),
    "136-P2": ("STOP-sim", "owns no terminal"),
    "137-1": ("STOP-crash", "ValueError"),
    "137-4": ("STOP-sim", "a border needs a tunnel"),
    "137-5": ("STOP-broken", "Is Broken? True"),
    "137-6": ("STOP-sim", "replay stops at another step than predicted"),
    "137-P3": ("STOP-plan", "per-build-step action count 43 > 40 (plan limit, not in the LOG list)"),
    "138-1": ("STOP-crash", "KeyError beside a fixture failure (mixed -> STOP)"),
    "138-6": ("STOP-crash", "ValueError create_control_nested"),
    "138-P1": ("STOP-route", "op route changed outside the step"),
    "139-1": ("STOP-crash", "error 1055 in an op VI"),
    "139-4": ("STOP-sim", "UNROUTABLE"),
    "139-5": ("STOP-plan", "meta-step gate: ids without a step"),
    "139-6": ("STOP-plan", "meta-step 43 > 42"),
    "139-7": ("STOP-memory", "X10 predicted peak > fail"),
    "140-2": ("STOP-crash", "E1 error 1055 in an op VI"),
    "140-3": ("STOP-errorlist", "extra 'Insert Into Array: Contains unwired or bad terminal' (not loose ends)"),
    "140-4": ("STOP-tool", "image unidentifiable (UNMEASURED)"),
    "140-P1": ("STOP-binding", "BASE unbound ids"),
    "141-2": ("LOG-count", "diag_c141_p4s01_scratch.log:280 TD unwired [], lost 6 vs plan deletes 8"),
}
# where the cited log line carries the gate's own detail, the module computes the verdict from it
COMPUTED = {
    "141-2": ("TD", "diag_c141_p4s01_scratch.log", r"^\s*FAIL\s+TD "),
    "130-6": ("BINDING-NAME", None, None),
    "140-3": ("EL", None, None),
}


def computed(cid):
    if cid == "141-2":
        _g, log, rx = COMPUTED[cid]
        for ln in open(os.path.join(HERE, log), encoding="utf-8", errors="replace"):
            if re.match(rx, ln):
                return GC.classify_line(ln)
        return "unread"
    if cid == "130-6":
        return GC.classify_gate("BINDING-NAME FlatSequenceOuterTunnel")["verdict"]
    if cid == "140-3":
        return GC.errorlist_verdict(["Insert Into Array: Contains unwired or bad terminal"], [], 51)[0]
    return None


def main():
    rows, n = [], {}
    for f in sorted(glob.glob(os.path.join(HERE, "cards", "result_1[34]*.json"))):
        cid = os.path.basename(f)[len("result_"):-len(".json")]
        m = re.match(r"^(\d+)-", cid)
        if not m or not 130 <= int(m.group(1)) <= 141:
            continue
        d = json.load(open(f, encoding="utf-8"))
        if d.get("status") == "PASS":
            continue
        cat, ev = CAT.get(cid, ("UNCATEGORISED", ""))
        c = computed(cid)
        agree = c is None or (c == "log") == cat.startswith("LOG")
        rows.append((cid, d.get("status"), cat, c, agree))
        n[cat.split("-")[0]] = n.get(cat.split("-")[0], 0) + 1
        print("%-7s %-7s %-16s module=%-5s %s | %s" % (cid, d.get("status"), cat, c or "-", "" if agree else "DISAGREE",
                                                      (d.get("first_fail") or "")[:110]), flush=True)
    unc = [r[0] for r in rows if r[2] == "UNCATEGORISED"]
    dis = [r[0] for r in rows if not r[4]]
    logs = [r[0] for r in rows if r[2].startswith("LOG")]
    print("TOTAL non-PASS %d: LOG (would continue) %d %s; STOP %d; NOT-A-GATE %d; uncategorised %s; disagree %s" % (
        len(rows), n.get("LOG", 0), logs, n.get("STOP", 0), n.get("NOT", 0), unc, dis), flush=True)
    nf = len(unc) + len(dis)
    print(protocol.result_line(protocol.make_result(2 - (1 if unc else 0) - (1 if dis else 0), nf,
                                                    (unc or dis or [None])[0] if nf else None)), flush=True)
    return 0 if not nf else 1


if __name__ == "__main__":
    sys.exit(main())
