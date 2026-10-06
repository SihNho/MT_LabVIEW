# ---
# labview: none
# hardware: none
# ---
r"""stub_claude - stand-in for `claude -p` in the livebench STUB dry run (card chat-B7). Runs with cwd = the arm worktree
(cycle_runner passes it as --dry-cmd / --assign-dry-cmd, whitespace-split, so this file is copied to a space-free %TEMP%
path first). No LabVIEW, no motor, no model call.
  judge   CYCLE_ROLE=judgement (or unset, --flow legacy): writes tools/bench/next.json = the fixed purpose with
          `cycle` = the newest cards/cycle_<n>.json and act "STUB cycle <n>: ..."; a hand-back phase leaves it unchanged.
  assign  CYCLE_ROLE=assign: writes stub task/result cards (cycle 1: one PASS; cycle 2: one FAIL + a PASS retry), a
          fake bgrun log of a LabVIEW stage launch (text only, nothing runs), a fake transcript with one guard_write and
          one guard_bash refusal (in LIVEBENCH_STUB_TRANSCRIPTS), one write into the arm folder and one into the fenced
          claudeDev root (the fence must refuse it), then assign-result/1 PURPOSE_MET with evidence for every pass item.
Both print one `--output-format json`-shaped envelope ($0.01, a fresh session_id) as their last line."""
import glob
import json
import os
import re
import sys
import time
import uuid

ROLE = sys.argv[1] if len(sys.argv) > 1 else "judge"
WT = os.getcwd()
BENCH = os.path.join(WT, "tools", "bench")
CARDS = os.path.join(BENCH, "cards")


def cycle_n():
    ns = [int(m.group(1)) for p in glob.glob(os.path.join(CARDS, "cycle_*.json"))
          for m in [re.search(r"cycle_(\d+)\.json$", p)] if m]
    return max(ns) if ns else 0


def envelope(note):
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0.01,
                      "session_id": str(uuid.uuid4()), "result": note}), flush=True)


def judge():
    n = cycle_n()
    if os.environ.get("PURPOSE_PHASE") == "handback":
        envelope("stub judge: hand-back judged, next.json unchanged")
        return
    p = os.path.join(BENCH, "next.json")
    d = json.load(open(p, encoding="utf-8"))
    act = re.sub(r"^STUB cycle \d+: ", "", d.get("act") or "")
    d["cycle"], d["act"] = n, "STUB cycle %d: %s" % (n, act)
    d["advances"] = ["M8", "R5"] if n % 2 == 0 else ["M3", "R1"]    # exercises the collector's re-plan detection
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    envelope("stub judge: next.json written for cycle %d" % n)


def card(cid, status, ff=None, retry=None):
    t = {"schema": "task/1", "id": cid, "kind": "build", "goal": "stub", "flags": {"labview": "build"},
         "budget": {"failures": 2, "minutes": 30}, "advances": ["M3", "R1"]}
    if retry:
        t["retry_of_card"] = retry
    json.dump(t, open(os.path.join(CARDS, "task_%s.json" % cid), "w", encoding="utf-8"))
    json.dump({"schema": "result/1", "id": cid, "status": status, "gates": {"pass": 1, "fail": 0 if status == "PASS" else 1},
               "first_fail": ff, "blocked_by": None, "artefacts": [], "facts": [], "open": [],
               "cost": {"usd": None, "minutes": 1, "labview_runs": 1}, "note": "stub"},
              open(os.path.join(CARDS, "result_%s.json" % cid), "w", encoding="utf-8"))


def assign():
    n = cycle_n()
    st = json.load(open(os.environ["ASSIGN_STATE"], encoding="utf-8"))
    n_pass = len((st.get("purpose") or {}).get("pass") or [])
    ids = []
    if n % 2:
        card("stub-c%d-1" % n, "PASS")
        ids.append("stub-c%d-1" % n)
        import hashlib
        pp = os.path.join(BENCH, "plan_ring_p4_s03v18.json")
        if os.path.exists(pp):              # a fake adopt/1 line: exercises the M3 detail (ops/sessions adopted)
            with open(os.path.join(BENCH, "adopted_scratch.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"schema": "adopt/1", "stage": "stage_d1_ring_p4_s03v18.py", "t": time.time(),
                                    "iso": time.strftime("%Y-%m-%d %H:%M:%S"), "note": "STUB",
                                    "artefact": {"path": "stub", "md5": "0" * 32},
                                    "plan_md5s": {"tools/bench/plan_ring_p4_s03v18.json":
                                                  hashlib.md5(open(pp, "rb").read()).hexdigest()},
                                    "gates": {"pass": 1, "log_fails": 0}, "required": ["E1"]}) + "\n")
    else:
        card("stub-c%d-1" % n, "FAIL", "GATE X10 peak 702 MB > 680")
        card("stub-c%d-2" % n, "PASS", retry="stub-c%d-1" % n)
        ids += ["stub-c%d-1" % n, "stub-c%d-2" % n]
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(BENCH, "stub_lvrun_c%d.log" % n), "w", encoding="utf-8") as f:
        f.write("BGRUN START %s limit 50.0 min: py -u tools/recipes/stage_d1_ring_p4_s03v18_scratch.py\n"
                "STUB - nothing ran\nBGRUN END rc=0 after 1s\n" % ts)
    tdir = os.environ.get("LIVEBENCH_STUB_TRANSCRIPTS")
    if tdir:
        os.makedirs(tdir, exist_ok=True)
        with open(os.path.join(tdir, "stub_c%d.jsonl" % n), "w", encoding="utf-8") as f:
            f.write(json.dumps({"uuid": str(uuid.uuid4()), "text": "WRITE-CHECK (tools/hooks/guard_write.py, card chat-E3) "
                                "tools/recipes/x.py:\n  - no scope header - every tools/ script carries one"}) + "\n")
            f.write(json.dumps({"uuid": str(uuid.uuid4()), "text": "BLOCKED by tools/hooks/guard_bash.py (scope header, "
                                "card chat-E3): x"}) + "\n")
    out = os.environ.get("LIVEBENCH_CLAUDEDEV")
    root = os.environ.get("LIVEBENCH_CLAUDEDEV_ROOT")
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "stub_saved_c%d.vi" % n), "wb") as f:
            f.write(b"STUB-VI-BYTES cycle %d" % n)
    if root:
        try:
            with open(os.path.join(root, "stub_must_be_refused_c%d.vi" % n), "wb") as f:
                f.write(b"x")
            print("FENCE-MISSED: a write outside the arm folder was NOT refused", flush=True)
        except PermissionError as e:
            print("FENCE-OK: %s" % str(e)[:160], flush=True)
    res = {"schema": "assign-result/1", "cycle": st.get("cycle", n), "round": st.get("round", 1), "status": "PURPOSE_MET",
           "cards": ids, "pass_evidence": [{"item": i, "met": True, "evidence": ["stub result_%s.json" % ids[-1]]}
                                           for i in range(n_pass)], "handback": None}
    json.dump(res, open(os.environ["ASSIGN_RESULT"], "w", encoding="utf-8"))
    envelope("stub assign: %d card(s), PURPOSE_MET" % len(ids))


if __name__ == "__main__":
    os.makedirs(CARDS, exist_ok=True)
    (assign if ROLE == "assign" else judge)()
