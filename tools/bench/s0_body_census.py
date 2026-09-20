r"""s0_body_census.py - READ-ONLY. The discriminating test the failed-prediction review asked for
(`archive/peer/2026-09-19-s0run1-closeorder.md` §4), run on `OpReportAll_v0.vi` and nothing else.

IT WRITES NOTHING. No edit, no save, no new op, no scratch VI. It opens three ops that already exist
(`OpReportAll_v0` as the subject; `OpReport_v3` and `OpWireSource_v5` as the readers) and prints numbers.

⚠️ THE REVIEW'S OWN SCRIPT IS NOT USED VERBATIM. It proposed `g.net_map(RA_V0, 1)`; `docs/cycle27-plan.md`
Pre-decided 17 BANS `net_map` as an instrument because it calls `remove_bad_wires_scripted(target)` internally
(`tools/gscript.py:2507-2516`) - i.e. it WRITES, and here the target would be one of our own op VIs. The same
three questions are answered by `build_track_v6_core.walk` (node_labels + node_terms_uid), `wire_source_owner`
(`OpWireSource_v5`, UID-addressed) and `gscript.tunnels` (`OpTunnels_v0`), all read-only.

WHAT ALREADY EXISTS (checked first): `tools/bench/s0_hygiene_probe.py` censused NODE COUNTS of these ops but
never their body wiring; `tools/bench/s0_terminal_names.log` read the Traverse/Close Reference terminal NAMES.
Neither answers who drives PN #115's `reference`. No new op is built here (Pre-decided 2).

THE TWO READINGS UNDER TEST - the review's claim vs the S0 material session's:
  R (review)   `build_opreportall_v1.py:144-171` built the body as a CHAIN: PN1 = Property on GObject
               (Position/UID/ClassName/**Owner**) fed by the auto-indexed `References` tunnel, and PN2's
               `reference` fed by **PN1's `Owner` OUTPUT** - a NEWLY MINTED reference that nothing closes.
  S (session)  run 1's log (`build_s0_closeref_v1.log:114-117`) was read as "the two Property nodes are
               PARALLEL", because both have `reference out` = 0 and their `reference` inputs carry different
               wires (w421, w548).

PREDICTION CONTRACT - printed PASS/FAIL, nothing branches on a result:
  C1 the body diagram holds exactly two Property nodes (#114, #115) plus the copied-in nodes of no run.
  C2 EVERY terminal of both body Property nodes is printed with name / is_source / wire - so "reference out = 0"
     can be read in context instead of in isolation.
  C3 `wire_source_owner` names the OWNER and the SOURCE TERMINAL of w421 and of w548.
     *** THE DISCRIMINATOR: if w548's source terminal is owned by #114 and is named `Owner`, reading R is right
     and S is wrong - the nodes are chained and an Owner reference is minted per iteration. If w548's source is
     a LoopTunnel inner terminal, reading S is right. ***
  C4 every LoopTunnel of the op is printed with IndexMode, outer wire and inner wires - so "how many tunnels
     does the loop have, and is the References tunnel auto-indexed in the ORIGINAL op" is measured, not assumed.
  C5 `OpReportAll_v0.vi`'s md5 is IDENTICAL before and after this script - the proof it wrote nothing.

  py tools/bgrun.py --material --max-min 12 --log tools/bench/s0_body_census.log -- py -u tools/bench/s0_body_census.py
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner  # noqa: E402

RA_V0 = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
PASS = []


def gate(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"  {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    t0 = time.time()
    print(f"=== S0 BODY CENSUS (read-only)  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    m0 = md5(RA_V0)
    print(f"OpReportAll_v0.vi md5 BEFORE {m0}", flush=True)

    dias = g.report(RA_V0, "Diagram")
    print(f"diagrams: {[(d['i'], d['uid'], d['owner']) for d in dias]}", flush=True)
    body = [d for d in dias if d["owner"] == "ForLoop"]
    gate("C0 exactly one ForLoop-owned Diagram", len(body) == 1, str(body))
    bi = body[0]["i"]

    props = [o["uid"] for o in g.report_all(RA_V0, "Property")]
    for di, label in ((0, "TOP DIAGRAM"), (bi, "LOOP BODY")):
        w = B.walk(RA_V0, di)
        print(f"\n-- {label} (Diagram[{di}]) : {len(w)} nodes", flush=True)
        for u, (n, lab, rows) in sorted(w.items(), key=lambda kv: kv[1][0]):
            print(f"   Nodes[{n}] #{u} {lab!r}", flush=True)
            for r in rows:
                print(f"        [{r['i']:2d}] {r['name']!r:<34} source={r['is_source']!s:<5} wire={r['wire']}",
                      flush=True)
        if di == bi:
            body_pns = sorted(u for u in w if u in props)
            gate("C1 the body holds exactly two Property nodes", len(body_pns) == 2, str(body_pns))
            gate("C2 every body terminal printed above", True, f"nodes {sorted(w)}")

    print("\n-- WHO DRIVES EACH `reference` (OpWireSource_v5, UID-addressed, read-only)", flush=True)
    seen = {}
    for wu in (421, 548):
        rows = wire_source_owner(RA_V0, wu, n=8)
        print(f"   wire {wu}: {rows}", flush=True)
        src = next((r for r in rows if r.get("is_source")), None)
        seen[wu] = src
        gate(f"C3 wire {wu} has exactly one SOURCE terminal", src is not None, str(rows))
    s548 = seen.get(548) or {}
    print(f"\n   *** DISCRIMINATOR: w548 source owner = {s548.get('owner_class')}#{s548.get('owner_uid')} ***",
          flush=True)
    print("   reading R (review)  = owner 114, i.e. PN1.Owner -> PN2.reference : the body is a CHAIN and an "
          "Owner reference is MINTED per iteration and closed by nobody.", flush=True)
    print("   reading S (session) = owner is a LoopTunnel/other            : the body is PARALLEL.", flush=True)

    n_tun = g.count(RA_V0, "LoopTunnel")
    print(f"\n-- LOOP TUNNELS: {n_tun}", flush=True)
    for i in range(n_tun):
        t = g.tunnels(RA_V0, i)
        print(f"   [{i}] uid {t['uid']}  IndexMode {t['index_mode']}  out {t['out_name']!r} "
              f"is_source={t['out_is_source']} wire {t['out_wire']}  in {t['in_names']} wires {t['in_wires']}",
              flush=True)
    gate("C4 every LoopTunnel printed with its IndexMode", n_tun >= 1, f"{n_tun} tunnels")

    m1 = md5(RA_V0)
    gate("C5 OpReportAll_v0.vi is byte-identical after this script", m0 == m1, f"{m0} -> {m1}")
    print(f"\n({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        np_ = sum(1 for _n, ok in PASS if ok)
        nf = sum(1 for _n, ok in PASS if not ok)
        print(f"\nGATES: {np_} PASS / {nf} FAIL", flush=True)
        if nf:
            print("failing: " + ", ".join(n for n, ok in PASS if not ok), flush=True)
    sys.exit(0 if (rc == 0 and not any(not ok for _n, ok in PASS)) else 1)
