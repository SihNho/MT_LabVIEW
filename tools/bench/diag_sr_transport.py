r"""diag_sr_transport.py - READ-ONLY. The three facts route B run 3 needs and nobody has measured.

WHY THIS AND NOT A GUESS. The judgement session decided (brief 2026-09-17): `#1359` t1 and `#29874` t3 cross from
loop 1.1 to 1.2 through two lock-stepped queues `Q_sr1`/`Q_sr2`, and `#2222` t0 <- `Z/dZ` is made by wiring the
control to a TEMPORARY named sink and branching off that wire. Both need facts this project does not have:

  Q1  `queue_node('obtain', target, src_cls, src_index, src_name, ...)` types the queue from a NAMED OUTPUT
      TERMINAL of an existing node (`tools/gscript.py:1068-1074`). STATUS NEXT says route B section 2b "never says
      which terminal each of the 8 queues takes". For Q_sr1/Q_sr2 the element type must equal the type carried by
      `LeftShiftRegister` #9025 / #29512 of `#637` (MEASURED in `tools/bench/d1_tunnel_sources.json`: the source
      terminal of w9097 / w28039 is owned by those two registers). So: WHICH named node output carries that type?
      The natural candidate is the node that writes the PARTNER RIGHT register, because the same net passes through
      it - and using it only as a TYPE source changes no value, so rule 1a is untouched.
  Q2  the ENQUEUE's element must be the LEFT register's OWN output (the previous iteration's value that `#1359` t1
      actually consumed). Enqueueing the right register's writer instead would advance the value by one iteration -
      a computation change in disguise (CLAUDE.md rule 1a). So: what is on w9097 / w28039, and is a branch from it
      expressible by `OpConnectFromWire_v0` (same diagram as the enqueue would be)?
  Q3  does control `Z/dZ` (uid 47) ALREADY drive a wire, and does that net already contain a NAMED sink? If it
      does, the temporary sink of the brief's decision (2) is unnecessary and the branch can be taken from the
      existing wire directly. Measuring this before building it is the difference between one op call and a
      create/wire/branch/delete sequence with a Remove Bad Wires in the middle.

PRIOR ART CHECKED (nothing here is rebuilt): `gscript.shift_reg` (:699) / `shift_reg_left` (:732, left/right
pairing, OpShiftRegs_v1) / `panel_wiring` (:772) / `node_terms` (:816) already exist; `build_d1_v0.sr_census`
(:383), `diag_index` (:357), `wmap`/`terms_of` (:364,:375), `class_index` (:946) already exist;
`build_opconnectfromwire_v0.wire_source_owner` (:423) already exists. `ls tools/bench/diag_*.py` has
`diag_connectfromwire_facts`, `diag_moved_structure_terminals`, `diag_tunnelsource_onehop` - none answers Q1-Q3.

PREDICTION CONTRACT (each line PASS/FAIL, no judgement):
  P0  a fresh copy of the ORIGINAL reads md5 2a78e17c449cacdaf5da389818526859 before AND after; nothing is saved.
  P1  `#637`'s shift-register census finds a right register whose LEFT register uid is 9025, and another whose
      LEFT register uid is 29512.                                              EXPECT: both found.
  P2  the LEFT register's inside terminal carries w9097 / w28039 respectively. EXPECT: match.
  P3  each PARTNER RIGHT register's inside wire is traced to its single source terminal, and that terminal is
      **UNNAMED** - `docs/frame-loop-wire-graph.md:417,:421` record `#1359` t2 and `#29874` t5 as `(unnamed)`
      and `tools/bench/d1_rewire_sources.json` gives `"name": ""`.            EXPECT: 2/2 UNNAMED, i.e. there
      is NO named type source and `queue_node('obtain', …)` cannot be typed this way. (The expectation was
      inverted before the run, not after it - see the note at the gate.)
  P4  `Z/dZ` appears in `panel_wiring` exactly once, as a CONTROL (indicator False), and its `wire` is reported.
  P5  if `Z/dZ`'s wire is non-zero: every terminal on that wire is listed with owner class/uid and, for node
      owners on Diagram #639, the terminal NAME - so "is there already a named sink" is answered, not assumed.
  P6  `#2222` t0 on the pristine original reads is_source FALSE (it is a sink) and carries a wire.

  MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_sr_transport.log -- py -u tools/bench/diag_sr_transport.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                                                            # noqa: E402
import build_d1_v0 as D1                                                       # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner                       # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
FRAME_LOOP_UID, FRAME_BODY_UID = 637, 639
TARGETS = {9025: 9097, 29512: 28039}          # LeftShiftRegister uid -> the outer wire d1_tunnel_sources recorded
SINKS = {9025: (1359, 1), 29512: (29874, 3)}
ZDZ_UID = 47
COPY = os.path.join(g.CLAUDEDEV, "SCRATCH_srdiag_%s.vi" % time.strftime("%H%M%S"))
OUT = os.path.join(HERE, "sr_transport.json")

g._run.__defaults__ = (6.0, 180.0)
passes, fails, res = [], [], {}


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(("  PASS  " if ok else "  FAIL  ") + name + ("  " + detail if detail else ""), flush=True)
    return ok


def fact(s):
    print("  FACT  " + s, flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    g._lv = None
    before = md5(ORIGINAL)
    gate("P0a original md5 BEFORE", before == ORIG_MD5, before)
    if before != ORIG_MD5:
        return 2
    shutil.copyfile(ORIGINAL, COPY)
    g.report(COPY, "SubVI")
    g.open_panel(COPY)
    time.sleep(1.0)
    try:
        d43 = D1.diag_index(COPY, FRAME_BODY_UID)
        loop_i = [o["uid"] for o in g.report_all(COPY, "WhileLoop")].index(FRAME_LOOP_UID)
        fact(f"#637 is WhileLoop[{loop_i}]; Diagram #639 is Traverse index {d43}")

        # ---- P1/P2/P3: the two registers --------------------------------------------------------
        found = {}
        for r in range(14):
            try:
                rec = g.shift_reg_left(COPY, loop_i, r, 0, "WhileLoop")
            except Exception as e:
                fact(f"reg {r}: {str(e)[:80]}")
                continue
            lt = rec.get("left") or {}
            luid = lt.get("uid")
            if luid in TARGETS:
                found[luid] = (r, rec)
                fact(f"reg[{r}] RIGHT #{rec.get('uid')} <-> LEFT #{luid}; left inside "
                     f"{[t.get('wire') for t in (lt.get('inside') or [])]}, left outside "
                     f"{(lt.get('out') or {}).get('wire')}; right inside "
                     f"{[t.get('wire') for t in (rec.get('inside') or [])]}, right outside "
                     f"{(rec.get('out') or {}).get('wire')}")
        gate("P1 both LeftShiftRegisters found on #637", set(found) == set(TARGETS),
             f"found {sorted(found)} of {sorted(TARGETS)}")

        ci = D1.class_index(COPY)
        wm = D1.wmap(COPY, d43)
        for luid, want_w in TARGETS.items():
            if luid not in found:
                continue
            r, rec = found[luid]
            lt = rec.get("left") or {}
            lw = [t.get("wire") for t in (lt.get("inside") or [])]
            gate(f"P2 LEFT #{luid} inside wire == w{want_w}", want_w in lw, f"inside wires {lw}")
            # P3: the PARTNER RIGHT register's inside wire -> its single source terminal -> a NAMED node output
            rws = [t.get("wire") for t in (rec.get("inside") or []) if t.get("wire")]
            named = None
            for rw in rws:
                terms = wire_source_owner(COPY, rw)
                srcs = [x for x in terms if x.get("is_source") and x.get("recip") == rw]
                fact(f"RIGHT #{rec.get('uid')} inside w{rw}: "
                     f"{[(x.get('owner_class'), x.get('owner_uid'), x.get('is_source')) for x in terms]}")
                if len(srcs) != 1:
                    continue
                ou = srcs[0].get("owner_uid")
                nm = None
                node = wm.get(int(ou)) if ou else None
                if node:
                    for t in node[2]:
                        if t.get("wire") == rw and t.get("is_source"):
                            nm = t.get("name")
                            named = dict(reg=r, right_uid=rec.get("uid"), left_uid=luid, wire=rw,
                                         owner_uid=ou, owner_class=srcs[0].get("owner_class"),
                                         term_index=t.get("i"), term_name=nm,
                                         traverse=ci.get(int(ou)), node_label=node[0] if node else None)
                            break
                fact(f"   w{rw} source owner #{ou} ({srcs[0].get('owner_class')}), on diagram 43 = "
                     f"{bool(node)}, terminal name {nm!r}, Traverse {ci.get(int(ou)) if ou else None}")
                if named:
                    break
            # ⚠️ P3's EXPECTATION WAS INVERTED before this run, 2026-09-17 17:45, and the reason is on disk, not
            # in LabVIEW: `docs/frame-loop-wire-graph.md:417,:421` record the partner-right writers `#1359` t2
            # and `#29874` t5 as `(unnamed)`. The prior-art review of the run-3 plan
            # (`archive/peer/2026-09-17-priorart-routeb-run3-opus.md` A3-i) found it, and `d1_rewire_sources.json`
            # agrees (`"name": ""`). So the honest prediction is that there is NO named type source, and this
            # gate now asserts that - a diagnostic that predicts what the documents already state, and goes to
            # the machine only to confirm it, is the cheap half of this run; the Z/dZ facts below are the half
            # that is genuinely unmeasured.
            gate(f"P3 #{luid}: the partner-right writer's terminal is UNNAMED (documents confirmed on the machine)",
                 not (named and named.get("term_name")),
                 json.dumps(named) if named else "no named terminal on any right-inside wire - as predicted")
            res.setdefault("regs", {})[str(luid)] = dict(
                left_uid=luid, right_uid=rec.get("uid"), reg_index=r, left_inside=lw,
                right_inside=rws, sink=SINKS[luid], type_source=named)

        # ---- P4/P5: Z/dZ -------------------------------------------------------------------------
        pw = g.panel_wiring(COPY)
        zrows = [x for x in pw if x.get("label") == "Z/dZ"]
        gate("P4 Z/dZ present exactly once as a CONTROL", len(zrows) == 1 and not zrows[0].get("indicator"),
             json.dumps(zrows)[:300])
        res["zdz"] = dict(rows=zrows)
        if zrows and zrows[0].get("wire"):
            zw = int(zrows[0]["wire"])
            terms = wire_source_owner(COPY, zw, n=8)
            rows = []
            for x in terms:
                ou = x.get("owner_uid")
                node = wm.get(int(ou)) if ou else None
                nm = None
                if node:
                    for t in node[2]:
                        if t.get("wire") == zw:
                            nm = t.get("name")
                            break
                rows.append(dict(i=x.get("i"), is_source=x.get("is_source"), owner_class=x.get("owner_class"),
                                 owner_uid=ou, recip=x.get("recip"), term_name=nm,
                                 traverse=ci.get(int(ou)) if ou else None, on_d43=bool(node)))
                fact(f"Z/dZ w{zw}[{x.get('i')}]: is_source={x.get('is_source')} owner "
                     f"{x.get('owner_class')}#{ou} name {nm!r} traverse {ci.get(int(ou)) if ou else None}")
            res["zdz"]["wire"] = zw
            res["zdz"]["terminals"] = rows
            gate("P5 Z/dZ's net enumerated", bool(rows),
                 f"{len(rows)} terminals; named sinks "
                 f"{[r['term_name'] for r in rows if r['term_name'] and not r['is_source']]}")
        else:
            gate("P5 Z/dZ's net enumerated", False, "Z/dZ carries NO wire on the pristine original")

        # ---- P6: #2222 t0 -------------------------------------------------------------------------
        t2222 = D1.terms_of(COPY, d43, 2222)
        nm, is_src, w = t2222.get(0, ("<absent>", None, None))
        gate("P6 #2222 t0 is a bare-able SINK with a wire", is_src is False and bool(w),
             f"name {nm!r} is_source {is_src} wire {w}")
        res["n2222_t0"] = dict(name=nm, is_source=is_src, wire=w)
        # what else is on that wire - the same question as Z/dZ, from the sink's side
        if w:
            terms = wire_source_owner(COPY, int(w), n=8)
            fact(f"#2222 t0's wire w{w}: "
                 f"{[(x.get('owner_class'), x.get('owner_uid'), x.get('is_source')) for x in terms]}")
            res["n2222_t0"]["wire_terms"] = terms
    finally:
        try:
            g.close_panel(COPY)
        except Exception as e:
            print("close_panel:", str(e)[:80], flush=True)
        for p in (COPY,):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception as e:
                print("cleanup:", str(e)[:80], flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    after = md5(ORIGINAL)
    gate("P0b original md5 AFTER", after == ORIG_MD5, after)
    print(f"\n=== diag_sr_transport: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {fails}" if fails else "") + f"; json {OUT} ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
