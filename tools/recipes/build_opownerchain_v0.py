r"""build_opownerchain_v0.py - OpOwnerChain_v0.vi: a UID in, its OWNER's class and UID out.

WHY IT IS NEEDED, measured rather than assumed. docs/diagram-hierarchy.md: 129 of the main VI's 170 diagrams were
matched to their owning structure by position, and every ancestry chain then stopped at the same place - the
diagram that a STRUCTURE itself lives on. Position matching cannot supply it here (structures sit tens of pixels
apart; the 21x margin behind `gscript.loop_diagram` came from three loops 700 px apart). Without that link nobody
can say which loop encloses the PI motor / rotor call sites, which is the user's open question.

WHY IT IS CHEAP. `OpWireSource_v5` already contains the whole chain. Its census (tools/bench/census_opwiresource_v5.log)
shows the top-level diagram in full:

  node 9  uid 990   `UID to GObject Reference.vi`   GObject -> wire 1081
  node 3  uid 241   Property  reference <- 318 (Traverse+IndexArray element),  Position/ClassName/UID/**Owner (t7, UNWIRED)**
  node 10 uid 1044  To More Specific Class -> Wire   reference <- 1081, out -> 384
  node 5  uid 145   Property `Terms[]`  reference <- 384      node 6 uid 151 IndexArray      node 7 uid 157 Property `Owner` -> wire 751
  node 8  uid 163   Property `ClassName`  reference <- **751**
  node 14 uid 1221  To More Specific Class -> GObject  reference <- **751**  -> 1257
  node 13 uid 1186  Property `UID`  reference <- 1257 -> indicator

So "owner -> ClassName + UID" is wire 751 and everything downstream of it, and it is already built and working.
Only the SOURCE of 751 is wrong for our purpose: it is the owner of an indexed WIRE TERMINAL. Two rewires move it
to the owner of the UID-addressed object:

  R1  node 3 `reference`  : 318  ->  1081      (read the object that `UID to GObject Reference` returned)
  R2  node 3 `Owner` (t7) ->  the consumers of 751 (node 8 `reference`, node 14 `reference`)

and the Wire-specific front section (nodes 10, 5, 6, 7, 15, 16, 17) is deleted so no Wire cast can fail on a
Diagram or a CaseStructure.

PREDICTION CONTRACT:
  B1 the copy opens and starts at ExecState 1
  B2 R1 lands: node 3's `reference` carries the same wire as node 9's `GObject` output
  B3 R2 lands: node 3's `Owner` terminal is wired, and node 8 / node 14 read that wire
  B4 the Wire-only nodes are gone (SubVI/PropertyNode counts drop by the expected amounts)
  B5 ExecState == 1 before the single save
  B6 FUNCTIONAL: asked for the UID of `CaseStructure#10407`, the op reports an owner whose class is `Diagram`
     and whose UID is 639 - the frame loop's body, which two independent measurements already established.
     That is a real answer with a known-correct value, not a self-check.

Scratch discipline: the new op is written to claudeDev (save authority, CLAUDE.md rule 3). No original is opened.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opownerchain_v0.log -- py -u tools/recipes/build_opownerchain_v0.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR = os.path.join(CLAUDEDEV, "OpWireSource_v5.vi")
OP = os.path.join(CLAUDEDEV, "OpOwnerChain_v0.vi")

# uids read from tools/bench/census_opwiresource_v5.log - resolved BEFORE the recipe was written
N_OPENREF, N_TRAVERSE, N_IA1, N_PROP3 = 43, 124, 167, 241
N_OWNER_CLASSNAME, N_TERMS, N_IA2, N_TERMOWNER = 163, 145, 151, 157
N_UID2GOBJ, N_CASTWIRE, N_UIDREAD, N_CLSREAD = 990, 1044, 307, 310
N_CASTGOBJ, N_OWNERUID, N_ISSOURCE, N_CONNWIRE = 1221, 1186, 1319, 1326
N_OWNER_CLASSNAME2, N_CONNWIRE_UID = 482, 1329

# THE THIRD CONSUMER. The prior-art review (archive/peer/2026-09-15-priorart-ownerchain.md, the first run of
# tools/prior_art_review.py) caught this before the build was ever launched: wire 751 has THREE consumers, not two -
# node 163, node 1221 AND **node 482** - and `tools/bench/build_opwiresource_v5.log:35-39` records that the first v5
# rewire failed for exactly this reason, staying broken until the orphaned reference was re-fed. The census showed
# node 482 consuming 751 and I read past it. All three are rewired below.
# THE TRAVERSE CLASS NAME IS `Property`, NOT `PropertyNode` - and this recipe had the wrong one in three places.
# Measured 2026-09-16 (tools/bench/diag_autofocus_panel.log, a 2x2 grid over {PropertyNode, Property} x {main VI,
# op VI}): `PropertyNode` raises **error 1092** inside `Traverse for GObjects` on BOTH VIs, while `Property`
# returns 106 and 12. The failure follows the NAME, not the VI. Worse, it was already on disk: line 11 of
# `tools/bench/census_opwiresource_v5.log` - the very census this recipe's uids were read from - records
# `== PropertyNode: raised ... error 1092`, and `InvokeNode` fails the same way. So this recipe would have died
# at its first count(), and the evidence had been sitting in its own cited source file.
PROP_CLS = "Property"
REWIRE_SINKS = [N_OWNER_CLASSNAME, N_CASTGOBJ, N_OWNER_CLASSNAME2]
# The same review found the docstring promising seven deletions while this list held six: uid 1329 (the UID read on
# the Connected Wire) was omitted. It belongs to the Wire-only section and goes with it.
DELETE_UIDS = [N_CASTWIRE, N_TERMS, N_IA2, N_TERMOWNER, N_ISSOURCE, N_CONNWIRE, N_CONNWIRE_UID]

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def nodes_by_uid():
    n, _ = g.net_map(OP, diagram_index=0, max_nodes=80, max_terms=30)
    return {uid: (k, lbl, terms) for k, (uid, lbl, terms) in n.items()}


def term_wire(by_uid, uid, name):
    rec = by_uid.get(uid)
    if not rec:
        return None
    for _i, nm, w in rec[2]:
        if nm == name:
            return w
    return None


def term_index(by_uid, uid, name):
    rec = by_uid.get(uid)
    if not rec:
        return None
    for i, nm, _w in rec[2]:
        if nm == name:
            return i
    return None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    if not os.path.exists(DONOR):
        print("STOP: donor missing", flush=True)
        return 3
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copy2(DONOR, OP)
    st0 = g.exec_state(OP)
    print(f"copied donor -> {os.path.basename(OP)}   ExecState {st0}", flush=True)
    gate("B1 the copy starts legal", st0 == 1, str(st0))

    by = nodes_by_uid()
    w_gobj = term_wire(by, N_UID2GOBJ, "GObject")
    print(f"  UID-to-GObject output wire = {w_gobj}", flush=True)

    # R1 - point the Position/ClassName/UID/Owner property node at the UID-addressed object
    ni_prop = by[N_PROP3][0]
    ni_u2g = by[N_UID2GOBJ][0]
    try:
        g.connect2(OP, 0, ni_prop, "reference", ni_u2g, "GObject")
        print("  R1 connect2 returned", flush=True)
    except Exception as e:
        print(f"  R1 connect2 raised: {e}", flush=True)
    by = nodes_by_uid()
    gate("B2 node 241 `reference` now carries the UID-addressed object",
         term_wire(by, N_PROP3, "reference") == w_gobj,
         f"{term_wire(by, N_PROP3, 'reference')} vs {w_gobj}")

    # R2 - its `Owner` output feeds EVERY consumer of the old owner wire 751: the two ClassName readers and the
    # GObject cast. Leaving one behind is the recorded failure mode (see REWIRE_SINKS).
    for sink_uid in REWIRE_SINKS:
        if by.get(sink_uid) is None:
            print(f"  R2 -> #{sink_uid}: node not present", flush=True)
            continue
        try:
            g.connect2(OP, 0, by[sink_uid][0], "reference", by[N_PROP3][0], "Owner")
            print(f"  R2 connect2 -> #{sink_uid} returned", flush=True)
        except Exception as e:
            print(f"  R2 connect2 -> #{sink_uid} raised: {e}", flush=True)
        by = nodes_by_uid()
    w_owner = term_wire(by, N_PROP3, "Owner")
    reads = {u: term_wire(by, u, "reference") for u in REWIRE_SINKS}
    gate("B3 `Owner` is wired and ALL THREE consumers read it",
         bool(w_owner) and all(v == w_owner for v in reads.values()),
         f"owner wire {w_owner}, consumers {reads}")

    # B4 - remove the Wire-only front section so no Wire cast can fail on a Diagram
    before = {c: g.count(OP, c) for c in (PROP_CLS, "SubVI", "IndexArray")}
    for uid in DELETE_UIDS:
        rec = by.get(uid)
        if rec is None:
            print(f"  delete #{uid}: already gone", flush=True)
            continue
        cls = "IndexArray" if uid == N_IA2 else ("SubVI" if uid in (N_CASTWIRE,) else PROP_CLS)
        try:
            idx = [o["uid"] for o in g.report_all(OP, cls)].index(uid)
            g.delete_object(OP, cls, idx, verify=False)
            print(f"  deleted #{uid} ({cls})", flush=True)
        except Exception as e:
            print(f"  delete #{uid} ({cls}) raised: {e}", flush=True)
        by = nodes_by_uid()
    after = {c: g.count(OP, c) for c in (PROP_CLS, "SubVI", "IndexArray")}
    gate("B4 the Wire-only nodes are gone", all(by.get(u) is None for u in DELETE_UIDS),
         f"{before} -> {after}")

    try:
        g.remove_bad_wires_scripted(OP)
    except Exception as e:
        print(f"  remove_bad_wires_scripted raised: {e}", flush=True)
    st = g.exec_state(OP)
    gate("B5 ExecState == 1 before saving", st == 1, str(st))
    if st == 1:
        try:
            g.save(OP)
            print("  saved", flush=True)
        except Exception as e:
            print(f"  save raised: {e}", flush=True)
    g._lv = None
    print(f"\n=== OpOwnerChain_v0 build: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    print("B6 (functional, next run): ask it for CaseStructure#10407 and require owner class Diagram, uid 639.",
          flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
