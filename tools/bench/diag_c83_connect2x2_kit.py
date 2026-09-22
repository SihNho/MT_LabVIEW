r"""diag_c83_connect2x2_kit - `tools/bench/diag_c83_connect2x2_r2.py` (595 lines) RE-CUT ON `tools/stagekit.py`.
Pre-decided 103's acceptance: "re-cut one existing diagnostic on the kit, identical gate outcomes, fewer lines".

SCOPE, narrower than run 2's file and said so out loud: the three cells that address THE OP AS IT SITS ON
DISK - R0, R0b (control, 7506 ALIVE, poison ON/OFF) and R1 (7506 DELETED). NOT re-cut: [S0] (it EDITED and
re-saved the op, `cda1e36e` -> `50a1e58a`; re-running it would mutate a delivered op for no measurement),
[S-ARF]/[S-SWAP] and cells R2/R3/R4 (two one-off scratch op VARIANTS, ~95 lines of question-specific net
surgery, whose recorded rows are identical to R1's), and `F0` (it pinned the PRE-S0 md5, so it is
unreproducible by construction; this file pins the POST-S0 one instead).
WHAT IS COMPARED: every gate row run 2 printed for those cells, BY LABEL, against
`tools/bench/diag_c83_connect2x2_r2.log:51-80`. Each prints as a `  ROW  ` line (observed vs recorded) and
the GATE is the MATCH - so reproducing a recorded FAIL does not arm `guard_peer.FAILURE_RE`, while a row
that STOPS matching fails loudly. THE MEASUREMENT IS NOT RE-IMPLEMENTED: `fsit_call2` is imported from run
2's own file, so any difference between the runs is in the SKELETON, which is what this tests.
Nothing is saved; the bed's md5 is pinned at both ends; every scratch is deleted. No motor/ASI/camera."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import stagekit as K                                                               # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                      # noqa: E402
from diag_c83_connect2x2_r2 import fsit_call2                                      # noqa: E402

OP_MD5_NOW = "50a1e58a4825c2ce030ed9a41e204931"          # what run 2's [S0] left on disk
# (cell, delete 7506?, poison?) and THE RECORDED OUTCOMES (diag_c83_connect2x2_r2.log:51-80)
CELLS = [("R0", False, True, "CONTROL - 7506 ALIVE, today's roles, POISON ON"),
         ("R0b", False, False, "CONTROL - 7506 ALIVE, today's roles, POISON OFF"),
         ("R1", True, False, "B2 - today's roles, 7506 deleted, Auto Route default FALSE")]
EXPECT = {"R0": {"copy": True, "wire_err": False, "term_uid": True, "bare": None, "deleted": True},
          "R0b": {"copy": True, "wire_err": False, "term_uid": True, "bare": None, "deleted": True},
          "R1": {"copy": True, "wire_err": False, "term_uid": False, "bare": False, "deleted": True}}
LABEL = {"copy": "{0} the scratch is a byte-identical copy of the bed",
         "wire_err": "{0} the border terminal's own `Wire` property read returned NO error",
         "term_uid": "{0} the FSIT uid 7468 still resolves to LeftTerm #7488 (term_uid echo)",
         "bare": "{0} the border terminal went BARE -> NON-ZERO",
         "deleted": "{0} bed scratch deleted"}

def cell(s, labels, name, do_del, poison, note):
    s.head("[{0}] {1}".format(name, note))
    got = {"copy": None, "wire_err": None, "term_uid": None, "bare": None, "deleted": None}
    sc = s.scratch(name)                       # its own PASS row == run 2's "byte-identical copy" row
    got["copy"] = os.path.exists(sc)
    (d_idx, _trip), e = s.safe("{0} resolve_triple".format(name),
                               lambda: C82.resolve_triple(sc, name), (None, None))
    if d_idx is None:
        s.gate("{0} the NEW loop's index triple resolves".format(name), False, e[:160])
        s.drop_scratch(sc)
        return got
    if do_del:
        s.safe("{0} del_wire({1})".format(name, C82.ROWD_WIRE),
               lambda: C82.del_wire(sc, C82.ROWD_WIRE, name + " "))
        s.safe("{0} remove_bad_wires_scripted".format(name),
               lambda: g.remove_bad_wires_scripted(sc))
    (_u, trows), _e = s.safe("{0} node_terms_uid".format(name),
                             lambda: g.node_terms_uid(sc, d_idx, C82.LOOP_NODES_IDX), (None, []))
    before = next((x for x in (trows or []) if x["i"] == C82.LOOP_TERM_IDX), None) or {}
    got["wire_err"] = (before.get("wire_err") == 0)
    s.fact("{0} border t{1} BEFORE the call: wire={2!r} error columns {3!r} (7506 deleted: {4!r})".format(
        name, C82.LOOP_TERM_IDX, before.get("wire"),
        {k: v for k, v in before.items() if k.endswith("_err")}, do_del))
    r, _e = s.safe("{0} fsit_call2".format(name),
                   lambda: fsit_call2(C82.OP, labels, sc, C82.FSIT_UID, d_idx, C82.LOOP_NODES_IDX,
                                      C82.LOOP_TERM_IDX, inv_err_label="error out 7", poison=poison), {})
    r = r or {}
    got["term_uid"] = (r.get("term_uid") == C82.LEFT_TERM_EXPECT)
    (_u2, trows2), _e2 = s.safe("{0} node_terms_uid AFTER".format(name),
                                lambda: g.node_terms_uid(sc, d_idx, C82.LOOP_NODES_IDX), (None, []))
    after = next((x for x in (trows2 or []) if x["i"] == C82.LOOP_TERM_IDX), None) or {}
    if do_del:
        got["bare"] = bool(after.get("wire"))
    s.fact("{0} RESULT: RAW INVOKE ERROR={1!r} | op_err={2!r} | term_uid={3!r} uid_back={4!r} | "
           "err_uidvi={5!r} | `UID 2`={6!r} border_wire={7!r} (was {8!r}) wire_delta={9!r} "
           "junk_Invoke={10!r} is_broken={11!r}".format(
               name, r.get("invoke_err"), r.get("err"), r.get("term_uid"), r.get("uid_back"),
               r.get("err_uidvi"), r.get("sink_wire_uid"), after.get("wire"), before.get("wire"),
               r.get("wire_delta"), r.get("invoke_delta"), r.get("is_broken")))
    s.R.setdefault("cells", {})[name] = {"note": note, "readout": r, "border_before": before,
                                         "border_after": after, "outcomes": dict(got)}
    got["deleted"] = s.drop_scratch(sc, tag="{0}".format(name))
    return got

def work(s):
    s.start()                                  # inside run(), so the hygiene tail runs even on a FATAL pin
    s.discard_work()
    s.fact("the op under test: {0} md5 {1} (want {2})".format(
        os.path.basename(C82.OP), K.md5(C82.OP), OP_MD5_NOW))
    s.gate("K4 the op on disk is the one run 2's [S0] saved", K.md5(C82.OP) == OP_MD5_NOW, K.md5(C82.OP))
    labels = json.load(open(C82.MAP_OUT, encoding="utf-8"))
    table = {}
    for name, do_del, poison, note in CELLS:
        if s.left_s() < 150:
            s.gate("{0} had time to run".format(name), False, "{0:.0f} s left".format(s.left_s()))
            continue
        table[name] = cell(s, labels, name, do_del, poison, note)
    s.head("ROW-FOR-ROW AGAINST diag_c83_connect2x2_r2.log:51-80")
    for name, _d, _p, _n in CELLS:
        for key in ("copy", "wire_err", "term_uid", "bare", "deleted"):
            want = EXPECT[name][key]
            if want is None:
                continue
            obs = (table.get(name) or {}).get(key)
            lab = LABEL[key].format(name)
            s.row(lab, "PASS" if obs else "FAIL", "PASS" if want else "FAIL")
            s.gate("MATCH r2 row: {0}".format(lab), obs == want,
                   "observed {0!r} vs recorded {1!r}".format(obs, want))
    s.R["row_table"] = table


if __name__ == "__main__":
    st = K.Stage(C82.BED, C82.BED_MD5, "diag_c83_connect2x2_kit", fresh=True, preload=False,
                 pins=C82.PINS, deadline_min=26, reserve_s=240,
                 task="Pre-decided 103 acceptance: r2's cells R0/R0b/R1 re-cut on stagekit")
    sys.exit(K.run(work, st))
