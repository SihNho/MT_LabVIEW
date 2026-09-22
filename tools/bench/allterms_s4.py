r"""allterms_s4 - STEP 1 / sub-step S4: the ACCEPTANCE TEST of `OpAllTerms_v0.vi`.

The criteria are `docs/connectivity-map-plan.md:48`'s row, verbatim, against the bed
`claudeDev\D1_s3b_m3a3b_rowD_20260922_161040.vi` (md5 0b84595245dd650c0e8fd3f57104782c) - the same file
`tools/bench/diag_allwires_probe.py` measured, so its 1,920 wires / 5,811 terminals are PRIOR numbers,
not this run's. Everything happens on a dated SCRATCH copy; the bed is never written.

  T1  cold `ExecState` 1 in a freshly restarted LabVIEW (the op is never cold-loaded broken)
  T2  5,811 terminal rows in <= 15 s, ONE op run
  T3  `tools/allterms.py` join -> 1,920 wires
  T4  the severed set is exactly [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540] and the
      PATTERN of which side is missing is reported
  T5  the four known endpoints agree: w1731 src LeftShiftRegister #4344 - w3947 src LeftShiftRegister
      #4274 - w9635 src LoopTunnel #9641 - w7337 sink RightShiftRegister #4334
  T6  5 random wires agree with an INDEPENDENT reader.
      ⚠️ SUBSTITUTION, stated: the plan says `node_terms`, which is addressed by (diagram, Nodes[] index)
      and would need a several-hundred-call scan to find one owner on the bed's root diagram. This uses
      `OpWireSource_v5` through `Stage.net_sources` instead - UID-addressed, one call per wire, and the
      reader this project already uses for exactly this question (`tools/bench/diag_c90_endpoints.log`).
  T7  20 consecutive calls: handles within +-100 of call 1, private bytes growth <= 5 MB
  Reported, not gated: how many rows carry `owner_uid` 0, by owner class; and OPEN B - whether a
  case/sequence inner-terminal row carries any frame identity.

READ-ONLY on the op and the bed: nothing is built, nothing is saved, the scratch is deleted at close.
  py tools/bgrun.py --material --max-min 40 --log tools/bench/allterms_s4.log -- py -u tools/bench/allterms_s4.py
"""
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import allterms as A                                                               # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
OP = os.path.join(K.CLAUDEDEV, "OpAllTerms_v0.vi")
OP_MD5 = "484853aad3a9c2819d7fd36028491a81"
SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
ENDPOINTS = [(1731, "src", "LeftShiftRegister", 4344), (3947, "src", "LeftShiftRegister", 4274),
             (9635, "src", "LoopTunnel", 9641), (7337, "sink", "RightShiftRegister", 4334)]
OUT_TERMS = os.path.join(K.BENCH, "allterms_bed_20260923.json")
OUT_WIRES = os.path.join(K.BENCH, "allterms_bed_20260923_wires.json")


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[T1] the op itself - identity and COLD ExecState in a freshly restarted LabVIEW")
    s.file_facts("OP", OP)
    s.gate("T1a the op's md5 is the one S3 saved", K.md5(OP) == OP_MD5, K.md5(OP), fatal=True)
    es = s.es("op, COLD", target=OP)
    s.gate("T1 cold ExecState 1", es == 1, "ExecState {0!r}".format(es), fatal=True)

    s.head("[T2/T3] ONE op run on a scratch of the bed -> the terminal table and the wire join")
    rows, dt = A.read_terms(p, OP)
    s.R["read_seconds"] = round(dt, 2)
    s.fact("read_terms: {0} rows in {1:.2f} s".format(len(rows), dt))
    s.gate("T2a 5,811 terminal rows", len(rows) == 5811, "{0} rows".format(len(rows)))
    s.gate("T2b <= 15 s in ONE op run", dt <= 15.0, "{0:.2f} s".format(dt))
    wires = A.join_wires(rows)
    s.gate("T3 the wire join returns 1,920 wires", len(wires) == 1920, "{0} wires".format(len(wires)))

    s.head("[T4] the severed half-wires")
    bad = A.severed(wires)
    got = sorted(w["wire_uid"] for w in bad)
    s.gate("T4 the severed set is exactly the 11 known uids", got == SEVERED, "{0!r}".format(got))
    pat = collections.Counter(("no source" if w["n_src"] == 0 else "no sink") for w in bad)
    for w in bad:
        s.fact("severed w{0}: n_src={1} n_sink={2} src {3}#{4} sink {5}#{6}".format(
            w["wire_uid"], w["n_src"], w["n_sink"], w["src_class"], w["src_uid"],
            w["sink_class"], w["sink_uid"]))
    s.R["severed_pattern"] = dict(pat)
    s.fact("SEVERED PATTERN: {0!r}".format(dict(pat)))

    s.head("[T5] the four known endpoints")
    byuid = dict((w["wire_uid"], w) for w in wires)
    ok5 = True
    for wu, side, cls, owner in ENDPOINTS:
        w = byuid.get(wu) or {}
        gc, go = w.get(side + "_class"), w.get(side + "_uid")
        hit = (gc == cls and go == owner)
        ok5 = ok5 and hit
        s.row("endpoint w{0} {1}".format(wu, side), "{0}#{1}".format(gc, go), "{0}#{1}".format(cls, owner))
    s.gate("T5 all four known endpoints agree", ok5, "")

    s.head("[T6] 5 random wires against OpWireSource_v5 (the independent, UID-addressed reader)")
    random.seed(23)
    pool = [w for w in wires if w["n_src"] == 1 and w["src_uid"]]
    picks = random.sample(pool, min(5, len(pool)))
    agree = 0
    for w in picks:
        res, _e = s.safe("net_sources(w{0})".format(w["wire_uid"]),
                         lambda u=w["wire_uid"]: s.net_sources(u, n=8, target=p), {})
        srcs = (res or {}).get("source_owners") or []          # [(owner_class, owner_uid), ...]
        got = "{0}#{1}".format(srcs[0][0], srcs[0][1]) if srcs else None
        want = "{0}#{1}".format(w["src_class"], w["src_uid"])
        agree += 1 if got == want else 0
        s.row("w{0} source owner".format(w["wire_uid"]), got, want)
    s.gate("T6 5/5 random wires agree with OpWireSource_v5", agree == len(picks),
           "{0}/{1}".format(agree, len(picks)))

    s.head("[T7] 20 consecutive calls - handles flat, private bytes bounded")
    bp = K.mod("bench_prep")
    h, pb, secs = [], [], []
    for i in range(20):
        if s.left_s() < 240:
            s.fact("deadline reserve reached after {0} call(s) - the rest were not run".format(i))
            break
        _r, d = A.read_terms(p, OP)
        secs.append(round(d, 2))
        hv, _e = s.safe("handles", bp.labview_handles)
        h.append(hv)
        pb.append(K.private_bytes())
    s.R["repeat"] = {"seconds": secs, "handles": h, "private_bytes": pb}
    s.fact("20-call seconds {0!r}".format(secs))
    s.fact("handles {0!r}".format(h))
    hh = [x for x in h if isinstance(x, int)]
    s.gate("T7a handles within +-100 of call 1 over {0} calls".format(len(hh)),
           bool(hh) and max(abs(x - hh[0]) for x in hh) <= 100,
           "range {0}..{1} from {2}".format(min(hh or [0]), max(hh or [0]), hh[0] if hh else "-"))
    grow = (max(pb) - pb[0]) / 1e6 if pb else 0.0
    s.gate("T7b private-bytes growth <= 5 MB", grow <= 5.0, "{0:.2f} MB".format(grow))
    s.fact("seconds per call: min {0} max {1}".format(min(secs or [0]), max(secs or [0])))

    s.head("[REPORTED] owner_uid 0 by class, and OPEN B - frame identity on inner terminals")
    z = collections.Counter(r["owner_class"] for r in rows if not r["owner_uid"])
    s.R["owner_uid_zero_by_class"] = dict(z)
    s.fact("rows with owner_uid 0: {0} of {1}; by class {2!r}".format(
        sum(z.values()), len(rows), dict(z.most_common(12))))
    inner = [r for r in rows if "Inner" in (r["owner_class"] or "") or "Frame" in (r["owner_class"] or "")]
    s.R["inner_terminal_sample"] = inner[:8]
    s.fact("OPEN B: {0} row(s) whose owner class carries Inner/Frame; sample {1!r}".format(
        len(inner), [(r["term_uid"], r["term_name"], r["owner_class"], r["owner_uid"])
                     for r in inner[:6]]))
    s.fact("OPEN B ANSWER: the row's six columns are term_uid/term_name/is_source/wire_uid/owner_uid/"
           "owner_class - NO frame column exists, and the owner uid is the TUNNEL, not a frame. Frame "
           "identity would have to come from `Terminal.Diagram` 634A002, which `OpTunnelRead_v0` already "
           "reads (docs/toolkit-capabilities.md, last row). This is a FACT for judgement, not a decision.")

    for path, payload in ((OUT_TERMS, {"meta": {"vi": BED, "op": OP, "read_seconds": round(dt, 2),
                                                "n_terminals": len(rows), "n_wires": len(wires),
                                                "severed": got}, "terminals": rows}),
                          (OUT_WIRES, {"meta": {"vi": BED, "op": OP, "n_wires": len(wires)},
                                       "wires": wires})):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1)
    s.fact("WROTE {0} and {1}".format(OUT_TERMS, OUT_WIRES))


S = K.Stage(BED, BED_MD5, "allterms_s4", fresh=True, preload=False, deadline_min=34.0, reserve_s=200.0,
            out_json=os.path.join(K.BENCH, "allterms_s4.json"),
            task="S4: the acceptance test of OpAllTerms_v0.vi against docs/connectivity-map-plan.md:48 "
                 "on a scratch of the bed - row count, timing, wire join, the 11 severed wires, four "
                 "known endpoints, an independent cross-check, and the 20-call resource test.")
sys.exit(K.run(main, S))
