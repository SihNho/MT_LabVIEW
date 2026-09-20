r"""diag_movein_p1_break.py - WHY does OpMoveIn_v0 read ExecState 0 when every requested wire exists?

NOT a third build attempt. `tools/recipes/probe_move_into_v0.py`'s failure budget (2) is SPENT - runs 1 and 2 both
died at gate P1 - and nothing here builds, edits or saves anything. This is the single cheapest DISCRIMINATING
READ the mandatory failed-prediction review named (`archive/peer/2026-09-17-moveinto-p1-execstate0.md`, codex,
ANSWERED, 227 s), run so the judgement session decides on measurements instead of on three hypotheses.

THE THREE HYPOTHESES (the third is the peer's, and it is the one neither of mine covered):
  A  the creators' junk: phase 1 has NO Invoke purge on the op it builds, and docs/NAMES.md:307-313 records that
     an Invoke with an unwired `reference` makes a VI non-executable while Remove Bad Wires reports nothing.
  B  a type break at one of the two new wires. The peer argues this is largely REFUTED already: a class conflict
     makes a BROKEN wire, and both replacement wires survived Remove Bad Wires and were then read back connected;
     `Diagram` inherits from `GObject` through `AbstractDiagram`, and `GObject.Move`'s `owner` takes an owning
     object, so the declared types agree.
  C  **collateral disconnection.** A LabVIEW wire is ONE NET with one source and possibly many sinks, so deleting
     the Wire object for 464 removed every sink on it - not just `Move.reference`. If another of those sinks was
     a REQUIRED input, the result is exactly what was observed: both replacement wires exist, no broken wire is
     left for Remove Bad Wires to find, and ExecState stays 0 because a required terminal elsewhere is now bare.
     NI distinguishes an unwired required terminal from a broken wire; Remove Broken Wires only addresses the
     latter.

WHAT ALREADY EXISTS - checked before writing a line:
  * `OpWireSource_v5.vi` reads a wire's `Terms[]` with, per terminal, `Is Source?`, the reciprocal `Connected
    Wire`, and the OWNER's class and uid (docs/toolkit-capabilities.md:48, INDEX row 43, 12/12). That IS the
    `Wire.Terminals[]` read the peer prescribes - nothing new is needed for C.
  * `read_terminal()` in `tools/recipes/build_opwiresource_v5.py:155` is its driver, but it HARD-WIRES `vi path`
    to the main VI (`:161`), and this question is about the DONOR op, so the target must be a parameter. The body
    below is that function with one line changed, and it is marked as such rather than silently re-derived.
  * `gscript.report_all(target, 'Invoke')` / `node_terms_uid` answer A with no new code.
  * `gscript.subvis(target, 0)` names the subVI calls for the peer's second alternative (a stale/broken U2G).

NO MUTATION AT ALL. The donor is COPIED to a scratch name and only read; OpMoveIn_v0.vi (left on disk by probe
run 2) is only read; the original main VI is not opened and its md5 is asserted before and after anyway.

PREDICTION CONTRACT (all three are reported; there is no "expected" outcome)
  H1 (tests C) wire 464 in the DONOR `OpMoveOut_v0.vi` resolves to a terminal list. If it carries MORE than one
     SINK terminal, C is live and names the collateral sinks by owner class/uid. Exactly one sink refutes C.
  H2 (tests A) `OpMoveIn_v0.vi` minus `OpMoveOut_v0.vi` on class `Invoke`: any extra Invoke, and whether its
     `reference` terminal is bare. Zero extras falsifies A outright.
  H3 (peer's second alternative) both files' `SubVI` calls are listed with their paths, so a stale/broken link to
     `UID to GObject Reference.vi` is visible rather than assumed.

  MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_movein_p1_break.log \
      -- py -u tools/bench/diag_movein_p1_break.py
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
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g  # noqa: E402
from build_opwiresource_v5 import OP as OP_WS, MAP_OUT as MAP_WS  # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpMoveOut_v0.vi")
OPIN = os.path.join(g.CLAUDEDEV, "OpMoveIn_v0.vi")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_p1break_{int(time.time())}.vi")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
OUT = os.path.join(HERE, "movein_p1_break.json")
REF_WIRE = 464          # the wire probe run 2 deleted: "deleted wire 464 (old Move.reference source)"

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def read_term(vi, labels, target, wire_uid, idx):
    """build_opwiresource_v5.read_terminal() with ONE change: `vi path` is a parameter, not the main VI
    (that function pins it at :161 and this question is about an op under claudeDev). Everything else -
    the poisoning, the error columns, the printed line - is that function's."""
    for lab in (labels["ownercls"], labels["cls_back"]):
        vi.SetControlValue(lab, "POISON")
    for lab in (labels["uid_back"], labels["owner_uid"], labels["recip_wire"]):
        vi.SetControlValue(lab, 0)
    vi.SetControlValue(labels["is_source"], False)
    vi.SetControlValue(labels["cast_class"], "POISON")
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(labels["uid_in"], wire_uid)
    vi.SetControlValue(labels["term_index"], idx)
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or ""
                                for k in ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO")) if x)
    r = dict(wire=wire_uid, index=idx, uid_back=int(vi.GetControlValue(labels["uid_back"])),
             wire_class=vi.GetControlValue(labels["cls_back"]),
             is_source=bool(vi.GetControlValue(labels["is_source"])),
             owner_class=vi.GetControlValue(labels["ownercls"]),
             owner_uid=int(vi.GetControlValue(labels["owner_uid"])),
             recip_wire=int(vi.GetControlValue(labels["recip_wire"])),
             cast_class=vi.GetControlValue(labels["cast_class"]), err=err, errs=errs)
    print(f"  OBSERVED wire {wire_uid} Terms[{idx}] source={r['is_source']} owner {r['owner_class']!r:.26} "
          f"uid {r['owner_uid']} reciprocal {r['recip_wire']} | {err[:24]} {errs[:50]}", flush=True)
    return r


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = hashlib.md5(open(ORIGINAL, "rb").read()).hexdigest()
    gate("D0a original md5 before", m0 == ORIG_MD5, m0)
    out = {}
    for p, tag in ((DONOR, "donor"), (OPIN, "opmovein")):
        if not os.path.exists(p):
            gate(f"D0 {tag} present", False, p)
            return 1

    # ---- H2 / H3 first: pure counts, no scratch needed ------------------------------------------
    print("\n=== H2: Invoke and SubVI census, OpMoveOut_v0 (donor) vs OpMoveIn_v0 (probe run 2's artefact)",
          flush=True)
    cen = {}
    for p, tag in ((DONOR, "donor"), (OPIN, "opmovein")):
        g.open_panel(p)
        time.sleep(0.4)
        inv = g.report_all(p, "Invoke")
        cen[tag] = dict(exec_state=g.exec_state(p),
                        invoke=[o["uid"] for o in inv],
                        nodes=g.count(p, "Node"), wires=g.count(p, "Wire"),
                        subvis=[{k: s.get(k) for k in ("uid", "name", "path")} for s in g.subvis(p, 0)])
        fact(f"{tag}: ExecState {cen[tag]['exec_state']}, Node {cen[tag]['nodes']}, Wire {cen[tag]['wires']}, "
             f"Invoke {cen[tag]['invoke']}")
        fact(f"{tag} subVIs: {[(s['uid'], s['name']) for s in cen[tag]['subvis']]}")
    extra = [u for u in cen["opmovein"]["invoke"] if u not in cen["donor"]["invoke"]]
    out["census"] = cen
    out["extra_invoke"] = extra
    fact(f"H2 EXTRA Invoke nodes on OpMoveIn_v0 that the donor does not have: {extra}")
    if extra:
        by = {}
        for n in range(80):
            u, rows = g.node_terms_uid(OPIN, 0, n)
            if not u:
                break
            by[u] = rows
        for u in extra:
            rows = by.get(u, [])
            ref = next((r for r in rows if r["name"] == "reference" and not r["is_source"]), None)
            fact(f"  extra Invoke #{u}: reference terminal = {ref}; all terminals "
                 f"{[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}")
            out.setdefault("extra_invoke_terms", {})[str(u)] = rows
    gate("H2 verdict recorded (A is live iff an extra Invoke has a BARE required `reference`)", True,
         f"{len(extra)} extra Invoke node(s)")

    # ---- H1: wire 464's whole net in the DONOR - the peer's hypothesis C ------------------------
    print(f"\n=== H1: every terminal on wire {REF_WIRE} in an UNTOUCHED copy of the donor", flush=True)
    shutil.copy2(DONOR, SCRATCH)
    rows = []
    try:
        g.open_panel(SCRATCH)
        time.sleep(0.4)
        with open(MAP_WS, encoding="utf-8") as f:
            wslab = json.load(f)
        ws = g.op(OP_WS)
        for i in range(10):
            r = read_term(ws, wslab, SCRATCH, REF_WIRE, i)
            if r["errs"] and r["owner_uid"] == 0 and not r["is_source"]:
                print(f"  (index {i} is past the end of Terms[] - stopping)", flush=True)
                break
            rows.append(r)
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("  scratch deleted", flush=True)
            except Exception as e:
                print(f"  scratch NOT deleted: {e}", flush=True)
    sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
    srcs = [(r["owner_class"], r["owner_uid"]) for r in rows if r["is_source"]]
    out["wire_464"] = dict(rows=rows, sinks=sinks, sources=srcs)
    fact(f"H1 wire {REF_WIRE}: {len(rows)} terminals; SOURCE {srcs}; SINKS {sinks}")
    if len(sinks) > 1:
        fact(f"H1 VERDICT: **C IS LIVE** - deleting wire {REF_WIRE} removed {len(sinks)} sinks, not one. "
             f"The collateral sinks are {[s for s in sinks]}; any that is a REQUIRED input is now bare and "
             f"alone explains ExecState 0 with no broken wire for Remove Bad Wires to find.")
    elif len(sinks) == 1:
        fact(f"H1 VERDICT: C IS REFUTED - wire {REF_WIRE} has exactly one sink {sinks}, so its deletion cost "
             f"nothing but the intended connection.")
    else:
        fact(f"H1 VERDICT: INCONCLUSIVE - {len(rows)} terminals read, {len(sinks)} sinks; the wire uid may not "
             f"exist in this copy (it was read from the RUN's log, on a copy with the same bytes).")
    gate("H1 wire 464's net was read", bool(rows), f"{len(rows)} terminals")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    m1 = hashlib.md5(open(ORIGINAL, "rb").read()).hexdigest()
    gate("D0b original md5 after", m1 == ORIG_MD5, m1)
    print("\n--- FACTS ---", flush=True)
    for line in facts:
        print("  " + line, flush=True)
    print(f"\n=== diag_movein_p1_break: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
