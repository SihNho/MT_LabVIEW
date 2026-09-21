"""DIAGNOSTIC, MEASUREMENT ONLY - the LOOP-BORDER NODE terminal tables of #637 and #23032.

WHY THIS EXISTS. `tools/bench/diag_c75_m3a3_rows.log:191,196` measured something the static verb
census (M5, same run) had reasoned its way past: the OLD RIGHT shift-register OUTER terminals appear
in the OWNING LOOP NODE's own `Terminals[]` table - `WhileLoop #637` at Diagram idx 19 `Nodes[4]`
carries `t8 'position [internal units]' wire 4859` and `t10 'Outgoing Handle' wire 7506`. A shift
register is not a `Nodes[]` member, but its terminals are reachable THROUGH the loop node, which is.
So the question "can any verb address a shift-register OUTER as a SOURCE" is a MEASUREMENT, not an
inference, and the unmeasured half is whether `WhileLoop #23032`'s table likewise exposes the two
BARE new RIGHT OUTERs with indices. This file measures both tables in full and decides nothing.

WHAT THIS IS NOT: it builds nothing, edits nothing, saves nothing, runs no VI. Scratch copy, read,
delete, md5 both ends. Hygiene gates only (Pre-decided 63). `ExecState` is not read at all here.

PRIOR ART: `tools/bench/diag_c75_m3a3_rows.py` (this file is its reader half, same hygiene shape);
`tools/recipes/build_d1_m3a1.py` `find_node` :541 / `terms_at` :500 / `term_state` :524;
`tools/gscript.py` `node_terms_uid` :955, `report_all` :502, `ensure_loaded` :1298, `ref_counts` :233.
NOTHING NEW IS BUILT (user, 2026-09-18 08:53).

PREDICTION CONTRACT (hygiene only; the only things that can FAIL):
  H1 the artefact's md5 is `3842f5e6f128226235dc78353f26ef44` before the run.
  H2 it is unchanged after the run.      H3 the four STATUS pins hold.
  H4 the scratch is deleted.             H5 refs opened == closed.
MEASUREMENT EXPECTATIONS (recorded, never gated):
  E1 `#637` sits at Diagram idx 19 `Nodes[4]` and its table carries t8 wire 4859 and t10 wire 7506.
  E2 `#23032`'s table carries two terminals named like the new registers with wire 0.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if p not in sys.path:
        sys.path.insert(0, p)

import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_m3a1 import find_node, terms_at, term_state                         # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi")
ARTEFACT_MD5 = "3842f5e6f128226235dc78353f26ef44"
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C75BSCRATCH_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c75b_loopterms.json")
LOOPS = [("OLD WhileLoop", 637), ("NEW WhileLoop", 23032)]
D686_HINT = 19
WATCH_WIRES = (4859, 7506, 4185, 3968)
WATCH_REGS = (4256, 4334, 4344, 4274, 23868, 23880, 23895, 23909)

T0 = time.time()
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "loops": {}, "handles": {}}
passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                        # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def main():
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c75b_loopterms - MEASUREMENT ONLY, hygiene gates only", flush=True)
    print("=" * 100, flush=True)
    before = md5(ARTEFACT)
    R["artefact_md5_before"] = before
    gate("H1 artefact md5 before == %s" % ARTEFACT_MD5, before == ARTEFACT_MD5, "got %s" % before)
    h0, _ = safe("handles at start", labview_handles)
    R["handles"]["start"] = h0
    fact("LabVIEW handle count at the START of this batch: %r (baseline ~31,500)" % h0)
    try:
        shutil.copyfile(ARTEFACT, SCRATCH)
        time.sleep(0.4)
        fact("scratch %s md5 %s" % (os.path.basename(SCRATCH), md5(SCRATCH)))
        t = time.time()
        _, err = safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
        fact("ensure_loaded(scratch) took %.1f s%s"
             % (time.time() - t, ((" ERROR " + err) if err else "")))
        for label, uid in LOOPS:
            loc = find_node(SCRATCH, uid, [D686_HINT, 0], "%s #%d" % (label, uid),
                            budget_s=200.0, quiet=True)
            f = loc.get("found") or {}
            rec = {"uid": uid, "located": f}
            R["loops"][label] = rec
            fact("%s #%d LIVE LOOKUP: Diagram #%r (traverse index %r), Nodes[%r], label %r"
                 % (label, uid, f.get("diagram_uid"), f.get("diagram_index"), f.get("nodes_index"),
                    f.get("label")))
            if f.get("nodes_index") is None:
                fact("%s #%d NOT in any scanned diagram's Nodes[] - reported, not guessed"
                     % (label, uid))
                continue
            tt = terms_at(SCRATCH, f["diagram_index"], f["nodes_index"], uid,
                          "%s #%d" % (label, uid), quiet=True)
            rec["uid_echo"] = tt.get("uid_echo")
            rec["terminals"] = tt.get("terminals", [])
            fact("%s #%d BORDER TERMINAL TABLE (uid echo %r): %d terminal(s) - this is the table a "
                 "(diagram, node, terminal) verb addresses"
                 % (label, uid, tt.get("uid_echo"), len(rec["terminals"])))
            for t2 in rec["terminals"]:
                mark = ""
                if t2["wire"] in WATCH_WIRES:
                    mark = "   <- WATCHED WIRE"
                elif not t2["wire"]:
                    mark = "   <- BARE"
                fact("    %s #%d t%-2d name=%-32r is_source=%-5r wire=%-7r state=%-6s%s"
                     % (label, uid, t2["i"], t2["name"], t2["is_source"], t2["wire"],
                        term_state(t2), mark))
            rec["bare_terminal_indices"] = [(t2["i"], t2["name"], t2["is_source"])
                                            for t2 in rec["terminals"] if not t2["wire"]]
            rec["watched_wire_indices"] = [(t2["i"], t2["name"], t2["wire"])
                                           for t2 in rec["terminals"] if t2["wire"] in WATCH_WIRES]
            fact("%s #%d BARE terminal indices on the border table: %r"
                 % (label, uid, rec["bare_terminal_indices"]))
            fact("%s #%d terminal indices carrying a WATCHED wire %r: %r"
                 % (label, uid, list(WATCH_WIRES), rec["watched_wire_indices"]))
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        R["fatal"] = traceback.format_exc()[-1500:]
        fact("FATAL (a defect in THIS PYTHON SCRIPT, not a refusal by LabVIEW) %s: %s"
             % (type(e).__name__, str(e)[:200]))
    finally:
        safe("close_panel(scratch)", lambda: g.close_panel(SCRATCH))
        R["ref_counts"] = g.ref_counts()
        fact("gscript ref_counts (opened / closed / live): %r" % R["ref_counts"])
        gate("H5 VI-Server reference counter level (opened == closed)",
             R["ref_counts"]["live"] == 0, "%r" % R["ref_counts"])
        ok = True
        for attempt in range(6):
            try:
                if os.path.exists(SCRATCH):
                    os.remove(SCRATCH)
                break
            except Exception as e:                                                # noqa: BLE001
                ok = False
                fact("scratch delete attempt %d failed: %s" % (attempt + 1, str(e)[:120]))
                time.sleep(4.0)
        gate("H4 the scratch copy is deleted", not os.path.exists(SCRATCH),
             "%s%s" % (SCRATCH, ("" if ok else " (needed retries)")))
        after = md5(ARTEFACT)
        R["artefact_md5_after"] = after
        gate("H2 artefact md5 UNCHANGED after the run", after == before,
             "before %s / after %s" % (before, after))
        allpins = True
        for label, path, want in PINS:
            have = md5(path) if os.path.exists(path) else "MISSING"
            allpins = allpins and (have == want)
            fact("PIN AFTER  %-16s %s  (want %s) %s"
                 % (label, have, want, ("OK" if have == want else "DIFFERS")))
        gate("H3 the four STATUS md5 pins all hold", allpins)
        h1, _ = safe("handles at exit", labview_handles)
        R["handles"]["exit"] = h1
        fact("LabVIEW handle count at the END of this batch: %r (start %r ; baseline ~31,500)"
             % (h1, h0))
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES: %d pass / %d fail%s"
          % (len(passes), len(fails), (("  FAILING: " + ", ".join(fails)) if fails else "")),
          flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
