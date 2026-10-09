# ---
# labview: none
# hardware: none
# offline-args: tools/bench/prep_c155_a5_1_before.json
# evidence: tools/bench/cards/task_155-a5-1.json
# ---
r"""prep_c155_a5_1_classify - card 155-a5-1 step 1: classify every tools/**/*.py with the CURRENT
stage_prerun.vi_modifying_calls and write {relpath: [verbs]} for the VI-modifying ones to argv[1].
FOUND FIRST: no existing census script; uses stage_prerun.vi_modifying_calls itself (logic lives once).
PREDICTION: before the fp-73 fix the census includes tools/bench/diag_c153_a2_2_queue_hygiene.py with ['discard_work'];
after it, only files whose verb list is exactly ['discard_work'] drop out. Offline, no LabVIEW, no COM.
With two args (before.json after.json) it diffs the two censuses instead."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import protocol  # noqa: E402


def census():
    import stage_prerun as SP
    out = {}
    n = 0
    for dp, dn, fn in os.walk(TOOLS):
        dn[:] = [d for d in dn if d not in ("__pycache__",)]
        for f in fn:
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            n += 1
            v = SP.vi_modifying_calls(p)
            if v:
                out[os.path.relpath(p, ROOT).replace("\\", "/")] = v
    return n, out


def main():
    if len(sys.argv) == 3:
        a = json.load(open(sys.argv[1], encoding="utf-8"))
        b = json.load(open(sys.argv[2], encoding="utf-8"))
        gone = sorted(set(a["modifying"]) - set(b["modifying"]))
        new = sorted(set(b["modifying"]) - set(a["modifying"]))
        changed = sorted(k for k in set(a["modifying"]) & set(b["modifying"]) if a["modifying"][k] != b["modifying"][k])
        bad = [k for k in gone if a["modifying"][k] != ["discard_work"]]
        print("BEFORE files=%d modifying=%d | AFTER files=%d modifying=%d" % (a["files"], len(a["modifying"]),
                                                                              b["files"], len(b["modifying"])))
        for k in gone:
            print("DECLASSIFIED %s %s" % (k, a["modifying"][k]))
        for k in new + changed:
            print("OTHER-CHANGE %s" % k)
        ok = not bad and not new and not changed
        print(protocol.result_line({"status": "PASS" if ok else "FAIL",
                                    "gates": {"pass": 1 if ok else 0, "fail": 0 if ok else 1},
                                    "first_fail": None if ok else "non-discard-only class change"}))
        return 0 if ok else 1
    n, out = census()
    disc_only = sorted(k for k, v in out.items() if v == ["discard_work"])
    with_disc = sorted(k for k, v in out.items() if "discard_work" in v)
    json.dump({"files": n, "modifying": out}, open(sys.argv[1], "w", encoding="utf-8"), indent=1, sort_keys=True)
    print("files=%d modifying=%d calls_discard_work=%d discard_only=%d" % (n, len(out), len(with_disc), len(disc_only)))
    for k in disc_only:
        print("DISCARD-ONLY %s" % k)
    print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
