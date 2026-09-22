r"""diag_c78_rowd_writer.py - TWO measurements, no LabVIEW, nothing mutated.

  [A] THE CYCLE GATE'S BUDGET, RECOUNTED through the Pre-decided 112 predicate: how many RECIPE builds are newer
      than the newest retrospective, what span they cover, and whether `overdue` is now False. Computed by
      IMPORTING `tools/hooks/guard_cycle.py` and re-running its own arithmetic - never by re-deriving it here,
      because a second copy of a classifier is how `tools/logclass.py` came to exist in the first place.

  [B] ROW D's WRITER - DOES ONE EXIST? Pre-decided 111 fixes Row D's sink as `FlatSequenceInnerTunnel #7468`
      LeftTerm **#7488**, "which is in no `Nodes[]` and is reached only by 109's route", and 109's route is the
      READER `OpFsInnerTunnelTerm_v0`. `Terminal.Connect Wire` **6349C03 is invoked ON THE SINK TERMINAL**
      (`docs/NAMES.md:245`, `:847`), so writing Row D needs a writer whose SINK LADDER ends on a terminal
      reference obtained WITHOUT `Nodes[]`. This phase censuses, from files only, every writer this fleet owns
      and how each one ADDRESSES ITS SINK - so the answer is read off the machine's own label maps instead of
      being asserted from a directory listing.

      THIS IS A MEASUREMENT, NOT A DECISION. Whatever it says, this file writes no VI, builds no op and changes
      no plan. What M3a-3b does about it is the judgement session's call (CLAUDE.md sec.3, "What you do NOT decide").

PRIOR ART, CHECKED BEFORE A LINE WAS WRITTEN. `grep "^def " tools/gscript.py` -> the connect verbs are
`connect_ctl` (:1013), `wire` (:1370), `connect_terminals` (:2518), `connect2` (:2744), `connect_nested_v2`
(:2965) and `wire_sr` (:737); `docs/toolkit-capabilities.md` rows 25/35/54/67/68/70 record each one's sink
addressing as MEASURED; `ls tools/bench/*labels*.json` holds the machine-written control maps this file reads.
No new op, no new verb, no new checker, no new device is created here - only files already on disk are read.

PREDICTION CONTRACT, WRITTEN BEFORE THE RUN.
  A1 `guard_cycle` imports and its `newest_retrospective()` answers with an archived file.
  A2 the recipe-build set is a STRICT SUBSET of the old `is_build_log` set.
  B1 every label map that declares `"method": "6349C03"` is found and printed with its sink keys.
  B2 `opfsinnertunnelterm_labels.json` declares NO `method` key at all - it is a reader (`kind: IN`).
  B3 the count of writers whose sink is addressed by something OTHER than (diagram, Nodes[], Terminals[]) /
     a panel control / a loop-end-ref is REPORTED. Zero is a FACT line, not a gate failure: a negative
     measurement is a fact (Pre-decided 63).
A gate here fails only if a FILE THIS SCRIPT NEEDS is missing or unreadable - never because the machine's answer
was unwelcome.
"""
import glob
import json
import os
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, _p)
import logclass                                                                    # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
OUT = os.path.join(BENCH, "diag_c78_rowd_writer.json")
CONNECT_WIRE = "6349C03"

R = {"script": os.path.abspath(__file__), "A": {}, "B": {}}
passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(t):
    print("\n---------- %s" % t, flush=True)


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


# =============================================================== [A] the cycle gate's budget, recounted
def phase_a():
    head("[A] THE CYCLE GATE'S BUDGET, recounted through Pre-decided 112's predicate")
    try:
        import guard_cycle as GC
    except Exception as e:                                                         # noqa: BLE001
        gate("A1 tools/hooks/guard_cycle.py imports", False, "%s: %s" % (type(e).__name__, str(e)[:200]))
        return
    gate("A1 tools/hooks/guard_cycle.py imports", True, "CYCLE_BUILD_BUDGET=%r CYCLE_HOURS=%r"
         % (GC.CYCLE_BUILD_BUDGET, GC.CYCLE_HOURS))
    retro = GC.newest_retrospective()
    R["A"]["newest_retrospective"] = (None if not retro else
                                      [os.path.basename(retro[0]),
                                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(retro[1]))])
    fact("newest retrospective THAT ANSWERED: %r" % (R["A"]["newest_retrospective"],))
    allp = sorted(glob.glob(os.path.join(BENCH, "*.log")))
    old = [p for p in allp
           if logclass.is_build_log(p)
           and (retro is None or os.path.getmtime(p) > retro[1])
           and time.time() - os.path.getmtime(p) <= GC.MAX_AGE_S]
    new = [p for p in allp
           if logclass.is_recipe_build_log(p)
           and (retro is None or os.path.getmtime(p) > retro[1])
           and time.time() - os.path.getmtime(p) <= GC.MAX_AGE_S]
    R["A"]["since_old_predicate"] = sorted(os.path.basename(p) for p in old)
    R["A"]["since_recipe_predicate"] = sorted(os.path.basename(p) for p in new)
    fact("`since` under the OLD predicate (is_build_log): %d log(s) -> %r"
         % (len(old), R["A"]["since_old_predicate"]))
    fact("`since` under the NEW predicate (is_recipe_build_log): %d log(s)" % len(new))
    for p in sorted(new, key=os.path.getmtime):
        fact("  RECIPE BUILD  %s  %s  cmd %r"
             % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
                os.path.basename(p), logclass.last_bgrun_command(p)))
    for label, s in (("old", old), ("new", new)):
        if retro is None:
            hours = 999.0
        elif len(s) >= 2:
            ts = [os.path.getmtime(p) for p in s]
            hours = (max(ts) - min(ts)) / 3600.0
        else:
            hours = 0.0
        overdue = len(s) >= GC.CYCLE_BUILD_BUDGET or hours >= GC.CYCLE_HOURS
        R["A"]["%s_count" % label] = len(s)
        R["A"]["%s_span_hours" % label] = round(hours, 2)
        R["A"]["%s_overdue" % label] = overdue
        fact("%s predicate: count %d (budget %d) ; span %.2f h (limit %s) ; OVERDUE %r"
             % (label.upper(), len(s), GC.CYCLE_BUILD_BUDGET, hours, GC.CYCLE_HOURS, overdue))
    gate("A2 the recipe-build set is a STRICT SUBSET of the old set", set(new) <= set(old),
         "%d of %d" % (len(new), len(old)))
    newest = GC.newest_build_log()
    R["A"]["newest_build_log"] = (None if not newest else os.path.basename(newest[0]))
    fact("newest_build_log() (still on `is_build_log`, deliberately untouched): %r" % R["A"]["newest_build_log"])
    dump()


# =========================================================== [B] does a Row-D writer exist at all?
def phase_b():
    head("[B] ROW D's WRITER - every 6349C03 writer this fleet owns, and how it ADDRESSES ITS SINK")
    fact("Terminal.Connect Wire 6349C03 is INVOKED ON THE SINK TERMINAL, `Wire Source` = the source terminal "
         "(docs/NAMES.md:245, :847). So a writer can only reach a sink it can hold a REFERENCE to.")
    fact("Row D's sink is FlatSequenceInnerTunnel #7468 LeftTerm #7488 (Pre-decided 111), and a FlatSequence is "
         "a direct child of GObject, never a Node - so it is in no diagram's Nodes[] "
         "(measured: tools/bench/diag_c77_rowd_addr.log, 173/173 diagrams, 635 nodes, 0 scan errors).")
    maps = sorted(glob.glob(os.path.join(BENCH, "*labels*.json")))
    gate("B1 the label maps are on disk", bool(maps), "%d file(s)" % len(maps))
    rows, readers = [], []
    for p in maps:
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception as e:                                                     # noqa: BLE001
            fact("UNREADABLE %s: %s" % (os.path.basename(p), str(e)[:120]))
            continue
        if not isinstance(d, dict):
            continue
        name = os.path.basename(p)
        if d.get("method") == CONNECT_WIRE:
            sink_keys = sorted(k for k in d if k.startswith("sink"))
            src_keys = sorted(k for k in d if k.startswith(("src", "wire_", "dead_src")))
            rows.append({"labels": name, "route": d.get("route"),
                         "sink_keys": {k: d[k] for k in sink_keys},
                         "source_keys": {k: d[k] for k in src_keys}})
        elif "FlatSequenceInnerTunnel" in json.dumps(d):
            readers.append({"labels": name, "kind": d.get("kind"), "class": d.get("class"),
                            "declares_method": d.get("method"),
                            "outputs": sorted(k for k in d if k.startswith(("term_", "wire_")))})
    R["B"]["connect_wire_writers"] = rows
    R["B"]["fsit_maps"] = readers
    fact("label maps declaring method %s (i.e. Connect Wire WRITERS): %d" % (CONNECT_WIRE, len(rows)))
    for r in rows:
        fact("  WRITER %-34s route %-22r SINK %r" % (r["labels"], r["route"], r["sink_keys"]))
        fact("         %-34s               SOURCE %r" % ("", r["source_keys"]))
    for r in readers:
        fact("  FlatSequenceInnerTunnel MAP %s kind %r class %r declares method %r ; outputs %r"
             % (r["labels"], r["kind"], r["class"], r["declares_method"], r["outputs"]))
    gate("B2 opfsinnertunnelterm_labels.json declares NO `method` key - it is a READER, not a writer",
         any(r["labels"] == "opfsinnertunnelterm_labels.json" and r["declares_method"] is None
             for r in readers),
         "%r" % ([(r["labels"], r["declares_method"]) for r in readers],))
    # A sink addressed by a TERMINAL UID would show up as a sink key that is a UID, not an index.
    uid_sinks = [r for r in rows
                 if any(str(v).lower().startswith("uid") for v in r["sink_keys"].values())]
    R["B"]["writers_with_uid_addressed_sink"] = [r["labels"] for r in uid_sinks]
    fact("writers whose SINK is addressed by a UID rather than by (diagram, Nodes[], Terminals[]) indices: "
         "%d -> %r  <- THE MEASUREMENT Row D turns on; zero is a FACT, not a gate failure (Pre-decided 63)"
         % (len(uid_sinks), R["B"]["writers_with_uid_addressed_sink"]))
    # the op VIs themselves, on disk, so the answer is not a label-map artefact
    ops = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CLAUDEDEV, "Op*.vi")))
    R["B"]["ops_on_disk"] = len(ops)
    R["B"]["connect_ops_on_disk"] = [o for o in ops if o.lower().startswith(("opconnect", "opwire", "opstop"))]
    gate("B3 the claudeDev op inventory is readable", bool(ops), "%d Op*.vi" % len(ops))
    fact("connect/wire/stop ops on disk (%d of %d): %r"
         % (len(R["B"]["connect_ops_on_disk"]), len(ops), R["B"]["connect_ops_on_disk"]))
    fact("the two FlatSequence tunnel ops on disk: %r"
         % [o for o in ops if "FsTunnel" in o or "FsInnerTunnel" in o])
    dump()


def main():
    print("=" * 100, flush=True)
    print("=== diag_c78_rowd_writer - [A] the cycle-gate budget under Pre-decided 112 ; [B] does Row D's "
          "writer exist? FILES ONLY, no LabVIEW, nothing mutated.", flush=True)
    print("=" * 100, flush=True)
    phase_a()
    phase_b()
    dump()
    print("\n" + "=" * 100, flush=True)
    print("=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                              ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
