r"""diag_ownerchain_state.py - what is ACTUALLY in the saved OpOwnerChain_v0.vi?

WHY. tools/bench/build_opownerchain_v0.log reports three things that cannot all be true:

  * six deletes reported SUCCESS ("deleted #145 (Property)", #151, #157, #1319, #1326, #1329),
  * B4's own before/after class counts are IDENTICAL: {'Property': 12, 'SubVI': 2, 'IndexArray': 2} both times,
  * B4's membership test `all(by.get(u) is None ...)` FAILED, i.e. the net walk still sees those nodes.

Reported success plus an unchanged count is the `unreported-fact` family: an operation that says it worked while
nothing moved. It has to be read from the machine before anything is rebuilt, because the two possible worlds need
opposite fixes - "the deletes did nothing" (fix the delete path) versus "the deletes worked and the counters lie"
(fix the counter, and beware that `report_all` indices may have addressed the wrong objects).

The VI was SAVED in that state (claudeDev, save authority), so this reads the artefact on disk, not a rebuild.

PREDICTION CONTRACT:
  P1 `g.count` for Property / SubVI / IndexArray returns the same numbers the build's `after` reported (12/2/2).
     If it does NOT, the build's own counter was stale and B4's detail line is the unreliable part.
  P2 The six reportedly-deleted uids (145, 151, 157, 1319, 1326, 1329) are enumerated by `report_all` for their
     class. PRESENT => the deletes did nothing and reported success. ABSENT => they were deleted and `count` lies.
  P3 uid 1044's real class is reported, so the one delete that raised ("1044 is not in list", tried as SubVI) can
     be re-aimed. Its expected shape is a 'To More Specific Class' primitive, which is NOT a SubVI.
  P4 The rewire targets are enumerated with their terminals: node 241's every terminal + wire, and the `reference`
     terminal wire of 163 / 1221 / 482. This is the direct evidence for B2/B3, which are under peer review.
  Any mixed outcome (some present, some absent) is itself the answer and must be reported, not smoothed over.

Read-only on OpOwnerChain_v0.vi in claudeDev. No original is opened, nothing is built, nothing is saved.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_ownerchain_state.log -- py -u tools/bench/diag_ownerchain_state.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpOwnerChain_v0.vi")
DELETED_CLAIMED = {145: "Property", 151: "IndexArray", 157: "Property",
                   1319: "Property", 1326: "Property", 1329: "Property"}
REWIRE = {241: None, 163: "reference", 1221: "reference", 482: "reference", 990: "GObject", 1044: None}
CLASSES = ("Property", "SubVI", "IndexArray", "Node")
OUT = os.path.join(HERE, "diag_ownerchain_state.json")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"op": OP, "exists": os.path.exists(OP)}
    print(f"target {OP}\n  exists={out['exists']}", flush=True)
    if not out["exists"]:
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print("FAIL the built VI is not on disk", flush=True)
        return 1

    try:
        out["exec_state"] = g.exec_state(OP)
        print(f"  ExecState {out['exec_state']}", flush=True)

        print("\n=== P1 class counts (compare with the build's 12/2/2) ===", flush=True)
        out["counts"] = {}
        for c in CLASSES:
            try:
                out["counts"][c] = g.count(OP, c)
            except Exception as e:
                out["counts"][c] = f"ERR {str(e)[:60]}"
            print(f"  {c:<12} {out['counts'][c]}", flush=True)

        print("\n=== P2/P3 which uids are still enumerated, and under which class ===", flush=True)
        seen = {}
        for c in ("Property", "SubVI", "IndexArray", "Node"):
            try:
                seen[c] = [o["uid"] for o in g.report_all(OP, c)]
            except Exception as e:
                seen[c] = []
                print(f"  report_all({c}) raised: {str(e)[:70]}", flush=True)
        out["uid_lists"] = {c: v for c, v in seen.items()}
        for uid, cls in DELETED_CLAIMED.items():
            where = [c for c, v in seen.items() if uid in v]
            verdict = "STILL PRESENT (delete reported success and did nothing)" if where else "gone (delete worked)"
            print(f"  uid {uid:<5} claimed deleted as {cls:<11} -> found in {where or '[]'}  {verdict}", flush=True)
        for uid in (1044, 241, 163, 1221, 482, 990):
            where = [c for c, v in seen.items() if uid in v]
            print(f"  uid {uid:<5} classes: {where or '[] NOT ENUMERATED'}", flush=True)

        print("\n=== P4 terminals of the rewire targets ===", flush=True)
        n, _ = g.net_map(OP, diagram_index=0, max_nodes=80, max_terms=30)
        by = {uid: (lbl, terms) for _k, (uid, lbl, terms) in n.items()}
        out["nodes_seen"] = sorted(by)
        print(f"  net_map sees {len(by)} nodes: {sorted(by)}", flush=True)
        out["terms"] = {}
        for uid, want in REWIRE.items():
            rec = by.get(uid)
            if rec is None:
                print(f"  uid {uid}: not on diagram 0", flush=True)
                continue
            out["terms"][uid] = [[i, nm, w] for i, nm, w in rec[1]]
            if want is None:
                print(f"  uid {uid} ALL terminals: {[(nm, w) for _i, nm, w in rec[1]]}", flush=True)
            else:
                hit = [(nm, w) for _i, nm, w in rec[1] if nm == want]
                print(f"  uid {uid} '{want}' -> {hit}", flush=True)
    finally:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"\nwrote {OUT}", flush=True)
        g._lv = None
    return 0


if __name__ == "__main__":
    sys.exit(main())
