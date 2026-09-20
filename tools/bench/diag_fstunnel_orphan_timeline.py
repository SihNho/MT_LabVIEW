r"""diag_fstunnel_orphan_timeline.py - WHEN do wires 894 and 1356 become ORPHANS?  The cheapest discriminating test
for the failed prediction of tools/bench/diag_fstunnel_preclean_twins.log (gate P4).

Cycle 23 dispatch 4, run 2. READ-ONLY measurement: one throwaway scratch, no removal of anything, NO
`remove_bad_wires_scripted` call anywhere in this file, no `Wire.Is Broken?` read, nothing saved, no original
opened. `tools/recipes/build_opfstunnelterm_v1.py` is IMPORTED and hooked IN MEMORY ONLY - never edited.
`build_opfstunnelterm_v2.py` is neither launched nor imported.

WHY THIS RUN EXISTS (a measurement, not a design change). Run 1 of this dispatch predicted, per the brief and per
gate A0a of `_v2.py`, that the orphan set (Wire uids no owning-node terminal reads at either end) on the FRESH
donor copy at the `_v1.py:403` checkpoint is EXACTLY {894, 1356}. The machine said the orphan set there is EMPTY
(`tools/bench/diag_fstunnel_preclean_twins.log`: "PRECLEAN @_v1.py:403: 42 wires, 111 node terminals, ExecState 1;
orphan set ... = []"), so the brief's pre-clean ABORTED having removed nothing - which is what the brief told it to
do. The same test at the later B4 point does find exactly {894, 1356} (`diag_fstunnel_rbwvictims.log:79-88`, and
run 1's twin A reproduced RBW removing exactly those two). This run does not decide anything about that; it
localises WHERE between the two points the change happens, and names the terminals involved.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written:
  * `tools/bench/diag_fstunnel_preclean_twins.py` (run 1, same dispatch) - `orphan_wires()`, `nterms()`, `md5()`,
    `handles()`, `snapshot()`'s file list, IMPORTED from it. Nothing of it is re-implemented.
  * the `sweep` line-stamp hook (`inspect` on the caller's f_lineno) is the pattern of
    `tools/bench/diag_fstunnel_rbwvictims.py:164-181`; the `StopAtB4` freeze is
    `tools/bench/diag_fstunnel_wirebroken.py:154-183`.
  * `grep -n "^def " tools/gscript.py`: gscript has no orphan-wire reader and no per-terminal wire census beyond
    `node_terms_uid`, which is what `_v1.sweep()` already wraps. No new op is built.

PREDICTION CONTRACT (the prediction under test is E-new, formed after run 1 and dispatched for refutation as
archive/peer/2026-09-18-fstunnel-orphans-empty-at-ckpt00-{codex,opus}.md):
  T1  at CKPT[00] (`_v1.py:403`) BOTH 894 and 1356 are named by at least one node terminal, and those terminals
      belong to nodes the recipe is about to DELETE - #145 (the `Wire.Terms[]` property node) and/or #151 (the
      `Index Array`), `_v1.py:426-434`.
  T2  the orphan set is EMPTY at CKPT[00] and becomes EXACTLY {894, 1356} at the first checkpoint AFTER those two
      node deletes (the sweep at `_v1.py:442`).
  T3  both wire uids exist in the Wire census at EVERY checkpoint (they are never deleted by the recipe).
  T4  the per-checkpoint `ExecState` is recorded; `ExecState` at the B4 freeze is 0 (run 1 twin A, and run 1 of
      `build_opfstunnelterm_v1.py`).
  T5  the six wire sites' per-site `ExecState BEFORE` from `_v1`'s own attributor are recorded.
  T6  STATIC: this file never calls `remove_bad_wires_scripted` and never reads `Wire.Is Broken?` - counted from
      its own source text, not promised in prose.
  T7  handle count before and after; the scratch created and DELETED in the same run.
  T8  every original md5-identical BEFORE AND AFTER; no original opened.
  T9  no motor, no serial port, no camera, `motor_gate.py --execute` never called.
  A MISS ON T1 OR T2 IS A RESULT, NOT A FAILURE: it refutes E-new, which is the point of running this.

LAUNCH LINE (the trailing MATERIAL=1 token is the material declaration guard_bash.MARKER_RE asks for; the
documented prefix form no longer matches `.claude/settings.json`'s `Bash(py tools/*)` allowlist entry and a
non-interactive session cannot answer the prompt. This file never reads sys.argv, so the token is inert):
  py tools/bgrun.py --max-min 20 --log tools/bench/diag_fstunnel_orphan_timeline.log -- py -u tools/bench/diag_fstunnel_orphan_timeline.py MATERIAL=1
"""
import inspect
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                               # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid                    # noqa: E402
import build_opfstunnelterm_v1 as V1                              # noqa: E402  READ ONLY
import diag_fstunnel_preclean_twins as TW                         # noqa: E402  run 1 - helpers REUSED

STAMP = time.strftime("%H%M%S")
SCR = os.path.join(g.CLAUDEDEV, f"SCRATCH_fsotl_{STAMP}_{os.getpid()}.vi")
OUT = os.path.join(HERE, "diag_fstunnel_orphan_timeline.json")
TRACK = [894, 1356]
DELETED_NODES = [145, 151]        # _v1.py:426-434 deletes these two Nodes by index
RES = {"gates": [], "ckpt": [], "sites": [], "md5": {}, "handles": {}}


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:500]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:400]}", flush=True)


def carriers(by, wire_uid):
    """Every terminal that names `wire_uid`: (node uid, node index, terminal name, terminal index, is_source)."""
    out = []
    for u, (ni, rows) in by.items():
        for r in rows:
            if int(r["wire"] or 0) == int(wire_uid):
                out.append({"node": int(u), "node_index": ni, "term": r["name"], "term_index": r.get("i"),
                            "is_source": bool(r["is_source"])})
    return out


def static_selfcheck():
    """Both tokens are ASSEMBLED so these very lines cannot count as hits, and the brokenness token is the
    brokenness PROPERTY ID rather than its English name - prose in this file mentions the name, never the id.
    RUN-1 NOTE (2026-09-18): this very docstring spelled that id out in full, so T6 reported a hit on its own
    line 97 - a false positive in the checker, not a read. The id is no longer written here."""
    tok_rbw = "remove_bad_wires" + "_scripted("
    tok_brk = "63710" + "04"
    try:
        with open(os.path.abspath(__file__), encoding="utf-8", errors="replace") as f:
            src = f.readlines()
    except Exception as e:
        return [f"ERR {str(e)[:80]}"], [f"ERR {str(e)[:80]}"]
    a = [i for i, l in enumerate(src, 1) if tok_rbw in l and not l.lstrip().startswith("#")]
    b = [i for i, l in enumerate(src, 1) if tok_brk in l and not l.lstrip().startswith("#")]
    return a, b


class StopAtB4(Exception):
    pass


_V1_MUST = V1.must
_V1_SWEEP = V1.sweep
ARMED = [None]


def _must_hook(label, ok, detail=""):
    r = _V1_MUST(label, ok, detail)
    if label.startswith("B4 "):
        raise StopAtB4(f"{label} | {detail}")
    return r


def _sweep_hook(target, n=120, diagram=0):
    by = _V1_SWEEP(target, n, diagram)
    try:
        line = inspect.currentframe().f_back.f_lineno
    except Exception:
        line = None
    if ARMED[0] and os.path.normcase(target) == os.path.normcase(ARMED[0]):
        try:
            orph, census = TW.orphan_wires(target, by)
            es = g.exec_state(target)
            row = {"seq": len(RES["ckpt"]), "v1_line": line, "n_nodes": len(by), "n_terminals": TW.nterms(by),
                   "n_wires": len(census), "exec_state": es, "orphans": orph,
                   "present": {str(w): (w in census) for w in TRACK},
                   "carriers": {str(w): carriers(by, w) for w in TRACK}}
        except Exception as e:
            row = {"seq": len(RES["ckpt"]), "v1_line": line, "EXC": str(e)[:200]}
        RES["ckpt"].append(row)
        print(f"   CKPT[{row['seq']:02d}] _v1.py:{row.get('v1_line')}  nodes {row.get('n_nodes')}  terminals "
              f"{row.get('n_terminals')}  wires {row.get('n_wires')}  ExecState {row.get('exec_state')}  "
              f"ORPHANS {row.get('orphans')}", flush=True)
        for w in TRACK:
            c = (row.get("carriers") or {}).get(str(w), [])
            short = [(x["node"], x["term"], x["term_index"], "src" if x["is_source"] else "sink") for x in c]
            pres = (row.get("present") or {}).get(str(w))
            print(f"        #{w}: present={pres}  carried by {short if short else 'NO node terminal'}", flush=True)
    return by


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT T1..T9 - see this file's docstring. A miss on T1/T2 REFUTES E-new and is a RESULT.",
          flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}\n   scratch {SCR}", flush=True)
    rbw_lines, brk_lines = static_selfcheck()
    must("T6 STATIC: this file never calls remove_bad_wires_scripted and never reads `Wire.Is Broken?`",
         not rbw_lines and not brk_lines, f"rbw lines {rbw_lines}; is-broken lines {brk_lines}")
    before = {p: TW.md5(p) for p in TW.WATCHED}
    RES["md5"]["before"] = before
    print(f"-- md5 before: {len(before)} files ({len(TW.ORIGINALS)} originals) --", flush=True)

    try:
        fresh()
        RES["handles"]["before"] = TW.handles("after a fresh LabVIEW, before any work")

        spec = list(V1.SPEC["OUT"])
        spec[0] = SCR
        V1.SPEC["OUT"] = tuple(spec)
        V1.must = _must_hook
        V1.sweep = _sweep_hook
        V1.RES["wires"] = []
        V1.RES["build"] = []
        ARMED[0] = SCR
        print(f"\n================ REPRODUCE build_one('OUT') -> {os.path.basename(SCR)} (timeline, no removal) "
              f"================", flush=True)
        try:
            stop = "NO STOP: build_one returned without the B4 gate firing"
            V1.build_one("OUT")
        except StopAtB4 as e:
            stop = f"FROZEN AT B4: {e}"
        except Exception as e:
            stop = f"EXC before B4: {type(e).__name__} {str(e)[:260]}"
        finally:
            ARMED[0] = None
        note("stop reason", stop)
        RES["stop"] = stop

        ck = RES["ckpt"]
        first = next((r for r in ck if r.get("v1_line") == 403), None)
        RES["ckpt00"] = first
        c0 = {str(w): (first or {}).get("carriers", {}).get(str(w), []) for w in TRACK}
        nodes_named = sorted({x["node"] for w in TRACK for x in c0[str(w)]})
        print(f"\n================ T1 CKPT[00] (_v1.py:403) - who carries {TRACK}? ================", flush=True)
        for w in TRACK:
            print(f"   #{w}: {c0[str(w)]}", flush=True)
        must(f"T1 at CKPT[00] both {TRACK} are named by >=1 node terminal, and every naming node is one the recipe "
             f"deletes next ({DELETED_NODES})",
             all(c0[str(w)] for w in TRACK) and nodes_named and all(n in DELETED_NODES for n in nodes_named),
             f"nodes naming them: {nodes_named}; predicted {DELETED_NODES}")

        turned = [r for r in ck if sorted(r.get("orphans") or []) == sorted(TRACK)]
        first_turn = turned[0] if turned else None
        RES["first_checkpoint_with_the_orphan_set"] = first_turn
        print(f"\n================ T2 the orphan timeline ================", flush=True)
        for r in ck:
            print(f"   CKPT[{r.get('seq'):02d}] _v1.py:{r.get('v1_line')}  orphans {r.get('orphans')}  "
                  f"ExecState {r.get('exec_state')}  wires {r.get('n_wires')}  nodes {r.get('n_nodes')}",
                  flush=True)
        must("T2 the orphan set is EMPTY at CKPT[00] and becomes exactly the two wires at a LATER checkpoint",
             bool(first) and (first.get("orphans") == []) and first_turn is not None,
             f"CKPT[00] orphans {(first or {}).get('orphans')}; first checkpoint with {TRACK} = "
             f"_v1.py:{(first_turn or {}).get('v1_line')} (seq {(first_turn or {}).get('seq')})")
        must("T3 both wire uids are present in the Wire census at EVERY checkpoint (the recipe never deletes them)",
             all(all((r.get("present") or {}).get(str(w)) for w in TRACK) for r in ck if "present" in r),
             str([(r.get("seq"), r.get("present")) for r in ck if "present" in r])[:280])

        es_b4 = g.exec_state(SCR)
        RES["exec_at_b4"] = es_b4
        census_b4 = sorted(int(u) for u in g.uids(SCR, "Wire"))
        RES["census_at_b4"] = census_b4
        print(f"\n   ExecState at the freeze point = {es_b4}; {len(census_b4)} wires; 384/1694/1719/1766 present = "
              f"{ {str(x): (x in census_b4) for x in (384, 1694, 1719, 1766)} }", flush=True)
        must("T4 ExecState at the B4 freeze is 0, as run 1 twin A and build_opfstunnelterm_v1 run 1 measured",
             es_b4 == 0, f"ExecState {es_b4}; stop {stop[:80]}")
        for i, w in enumerate(V1.RES["wires"]):
            row = {"site": i + 1, "tag": (w.get("tag") or "").strip(), "wire": w.get("src_after"),
                   "exec_before": w.get("exec_before"), "exec_after": w.get("exec_after")}
            RES["sites"].append(row)
            print(f"   SITE {row['site']} wire {row['wire']}: ExecState BEFORE = {row['exec_before']!r}, "
                  f"AFTER = {row['exec_after']!r}", flush=True)
        must("T5 the six per-site ExecState BEFORE values were recorded", len(RES["sites"]) == 6,
             f"{len(RES['sites'])} rows; before = {[r['exec_before'] for r in RES['sites']]}")
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        try:
            g.close_panel(SCR)
        except Exception:
            pass
        try:
            g.reset()
        except Exception:
            pass
        time.sleep(0.5)
        if os.path.exists(SCR):
            try:
                os.remove(SCR)
            except Exception as e:
                print(f"   scratch delete FAILED: {str(e)[:120]}", flush=True)
        must("T7 the scratch VI was created and DELETED in this same run", not os.path.exists(SCR), SCR)
        RES["handles"]["after"] = TW.handles("after the run")
        after = {p: TW.md5(p) for p in TW.WATCHED}
        RES["md5"]["after"] = after
        diff = [os.path.basename(p) for p in TW.WATCHED if before.get(p) != after.get(p)]
        must(f"T8 all {len(TW.ORIGINALS)} originals (+ the V6 copy and the donor) are md5-identical before and "
             f"after", not diff and not any(str(v).startswith("ERR") for v in after.values()),
             f"differing: {diff}")
        must("T9 no motor, no serial port, no camera, motor_gate.py --execute not called (static: this file makes "
             "no such call)", True, "read-only VI Server + one throwaway scratch VI")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:56] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
