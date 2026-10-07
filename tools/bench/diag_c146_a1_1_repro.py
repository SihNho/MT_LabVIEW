# ---
# labview: none
# hardware: none
# ---
"""Card 146-a1-1: REPRODUCE gate-fp fp-43..50 against the CURRENT hooks (live functions imported, never a copy).
OFFLINE: no LabVIEW, no Jev call (the ladder verdict is the one jev_gate.log recorded for that log), no file written
outside %TEMP% (the hooks' log writers are stubbed).
Existing tools reused: guard_write.open_card_pins, guard_peer.log_failure/main, protocol.path_in_globs, scope_header.

PREDICTION before the fix (the reproduction):
  W-fp43/45/48/49/50  the cited card (copied, fresh mtime, open) pins the file AND lists it in flags.write -> stale msg
  W-fp47              reported as stale too (whether its flags.write lists the file is printed - FACT)
  W-own / W-other     scratch pair: own-write pin -> stale msg (the false positive); non-write pin -> stale msg
  P-fp44 / P-fp46     the cited log's failing segment fails, its command is header-offline, main() with the recorded
                      new-problem ladder verdict returns 2 (BLOCK)
After the fix the same script prints the new verdicts (W-own/W-fp* no msg when listed, W-other still msg; P-* rc 0).
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
os.chdir(ROOT)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import protocol as P          # noqa: E402
import scope_header as SH     # noqa: E402
import guard_write as GW      # noqa: E402
import guard_peer as GP       # noqa: E402

XT = tempfile.mkdtemp(prefix="c146a1_")
CARDS = os.path.join(XT, "cards")
os.makedirs(CARDS)
GW.CARDS = CARDS
G = {"pass": 0, "fail": 0, "first": None}


def fact(s):
    print("FACT " + s, flush=True)


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


W_ROWS = [("fp-43", "144-3", "tools/stage_prerun.py"), ("fp-45", "144-a2-3", "tools/hooks/guard_peer.py"),
          ("fp-47", "145-a2-4", "tools/bench/build_opwiringrules_v0.py"), ("fp-48", "145-a2-2", "tools/elrule.py"),
          ("fp-49", "145-a2-2", "tools/bench/selftest_elpred.py"), ("fp-50", "145-a2-5", "tools/elrule.py")]


def w_case(fp, cid, rel):
    src = os.path.join(TOOLS, "bench", "cards", "task_%s.json" % cid)
    for n in os.listdir(CARDS):
        os.remove(os.path.join(CARDS, n))
    shutil.copy(src, os.path.join(CARDS, "task_%s.json" % cid))          # fresh mtime, no result file -> OPEN
    card = json.load(open(src, encoding="utf-8"))
    pin = next((i.get("md5") for i in card.get("inputs") or [] if os.path.normcase(os.path.abspath(
        os.path.join(ROOT, i["path"]))) == os.path.normcase(os.path.abspath(os.path.join(ROOT, rel)))), None)
    in_w = P.path_in_globs(os.path.join(ROOT, rel), (card.get("flags") or {}).get("write") or [])
    msg = GW.open_card_pins(os.path.join(ROOT, rel))
    print("REPRO W-%s card %s file %s pin %s disk %s in_flags.write %s -> %s" % (
        fp, cid, rel, (pin or "-")[:8], md5(os.path.join(ROOT, rel))[:8], in_w,
        ("STALE: " + msg[0][:90]) if msg else "no message"), flush=True)


def scratch_pair():
    tgt = os.path.join(XT, "scratch_target.py")
    with open(tgt, "w") as f:
        f.write("x = 2\n")
    for n in os.listdir(CARDS):
        os.remove(os.path.join(CARDS, n))
    for cid, w in (("OWN", [tgt.replace("\\", "/")]), ("OTHER", ["tools/bench/elsewhere_*"])):
        with open(os.path.join(CARDS, "task_%s.json" % cid), "w", encoding="utf-8") as f:
            json.dump({"schema": "task/1", "id": cid, "inputs": [{"path": tgt, "md5": "0" * 32}],
                       "flags": {"write": w}}, f)
    msg = GW.open_card_pins(tgt)
    print("REPRO W-own   %s" % ("STALE" if any("card OWN " in m for m in msg) else "no message"), flush=True)
    print("REPRO W-other %s" % ("STALE" if any("card OTHER " in m for m in msg) else "no message"), flush=True)


def first_segment(text):
    i = text.find("BGRUN END")
    return text[: text.find("\n", i) + 1] if i >= 0 else text


def simulate_main(path, text, cmd, ladder_line):
    """guard_peer.main() at the moment of the refusal: the failing log is `path`/`text`, no peer covers it, the gate-fp
    queue entry does not exist yet, the Jev ladder returns the recorded verdict. Every log writer is stubbed."""
    saved = {k: getattr(GP, k) for k in ("newest_failing_log", "newest_bound_peer", "same_row_review", "_jev_decide",
                                        "_gate_log", "gaterow_advisory", "cite_same_row")}
    import gate_fp
    saved_fp = gate_fp.discharge_for_log
    GP.newest_failing_log = lambda: (path, os.path.getmtime(path), text)
    GP.newest_bound_peer = lambda *a: (None, [])
    GP.same_row_review = lambda *a, **k: None
    GP._jev_decide = lambda *a: (False, ladder_line, False, ladder_line)
    GP._gate_log = lambda line: None
    GP.gaterow_advisory = lambda *a: None
    GP.cite_same_row = lambda *a: None
    gate_fp.discharge_for_log = lambda *a: (None, None)
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin, sys.stderr = io.StringIO(json.dumps({"tool_input": {"command": cmd}})), io.StringIO()
    try:
        rc = GP.main()
        err = sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stderr = old_in, old_err
        for k, v in saved.items():
            setattr(GP, k, v)
        gate_fp.discharge_for_log = saved_fp
    return rc, err


def p_case(fp, log_rel, seg, cmd, ladder_line):
    path = os.path.join(ROOT, log_rel)
    text = open(path, encoding="utf-8", errors="replace").read().lstrip("﻿")
    if seg == "first":
        text = first_segment(text)
    lf = GP.log_failure(text, os.path.getmtime(path))
    own = P.last_segment(text)[1]
    sc = SH.launch_scope(own or "", [p for p in P._launched_scripts(own or "") if SH.in_tools(p)])
    rc, err = simulate_main(path, text, cmd, ladder_line)
    tag = next((ln for ln in err.splitlines() if ln.startswith(("RULE-", "BLOCKED"))), err.strip()[:80])
    print("REPRO P-%s log %s failed %s first %r | own cmd %r scope %s | main rc %d | %s" % (
        fp, log_rel, lf[0], str(lf[1])[:70], own, [(SH._rel(p), lv, hw, pr) for p, lv, hw, pr in sc], rc, tag[:160]),
        flush=True)


try:
    for row in W_ROWS:
        w_case(*row)
    scratch_pair()
    p_case("fp-44", "tools/bench/diag_c144_2_cls.log", "first",
           "py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c144_2_cls.log -- py -u tools/bench/diag_c144_2_cls.py",
           "JEV-LADDER | 2026-10-07 20:41:04 | diag_c144_2_cls.log | new-problem p=0.750 | BLOCK (review owed) | "
           "NEXT-ACTION: hypothesis review owed (old path)")
    p_case("fp-46", "tools/bench/prep_c145_2_pred.log", "all",
           "py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c145_2_dry.log -- py -u tools/stage_prerun.py "
           "--dry tools/recipes/stage_d1_ring_p4_s04v18.py",
           "JEV-LADDER | 2026-10-07 21:47:19 | prep_c145_2_pred.log | new-problem p=0.800 | BLOCK (review owed) | "
           "NEXT-ACTION: hypothesis review owed (old path)")
finally:
    shutil.rmtree(XT, ignore_errors=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
