r"""sweep_nodeterms_3state.py - the ORIGINAL's OWN read-only node/terminal sweep.

docs/motor-limit-assurance-plan.md §A.1 item 8: "The V6 working copy is not pristine - Claude inserted a per-frame
TIFF writer into it on 2026-09-01 ... so a baseline drawn from V6 begs §A's question. V6 stays the development
fixture (it has the cache); the ORIGINAL needs its own read-only node/terminal sweep (~11 min), and the
ORIGINAL-vs-V6 row diff is itself a recorded finding."  This file is that sweep and that diff, nothing more.
§A.1 is SETTLED - this does not redesign it and does not touch the later items (forward reachability from the 3
coerces, control Data-Entry ranges, the 3 comparator mutation negatives).

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "before creating any new op"):
  * `tools/bench/sweep_nodeterms_main.py` - the SAME sweep against the V6 working copy. Its per-diagram /
    per-node loop and its output shape are copied here deliberately so the two files' rows are comparable. It
    cannot simply be re-pointed: it reads `diagram_tree_main.json` (a V6 uid tree built with `net_map`, which
    §A.1 item 6 keeps unused) and cross-checks against `main_vi_netmap.json`, and NEITHER cache exists for the
    ORIGINAL. This file drops both caches and enumerates each diagram's nodes by index until the op reports
    UID 0 - `node_terms_uid`'s documented out-of-range signal (gscript.py:872) - so no tree is needed.
  * `gscript.node_terms_uid` / `report` / `report_all` / `uids` - reused unchanged; NO new op is built.
  * `grep "^def " tools/gscript.py`, `ls tools/bench tools/recipes`: there is no existing sweep, cache or JSON
    for the 3StateClamping ORIGINAL (only `motor_census_3state-ORIGINAL.json`, a motion-call-site census).

READ-ONLY ON THE ORIGINAL (rule 1): reference reads only - the panel is never opened, nothing is edited, saved
or run, no VI is created. md5 recorded before AND after; expected c39f36e0675339673b707c59f0784fee.
No motor, no serial, no camera (cycle21 Pre-decided 2 / P1).
CHECKPOINTED: every diagram is written to the JSON as soon as it is read, and a rerun skips what is recorded.

PREDICTION CONTRACT:
  S0  the ORIGINAL's md5 is c39f36e0675339673b707c59f0784fee before AND after the sweep.
  S1  the sweep completes every diagram the ORIGINAL reports (no diagram left unread).
  S2  nodes > 0 and terminals > 0; the counts are the recorded finding, not a pass/fail threshold.
  S3  the ORIGINAL-vs-V6 row diff is recorded: diagram count, node count, terminal count, and every diagram
      index whose node count or owner differs from tools/bench/main_vi_nodeterms.json.

  MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/sweep_nodeterms_3state.log -- py -u tools/bench/sweep_nodeterms_3state.py
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

TRACKING = os.path.dirname(ROOT)
ORIG = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
ORIG_MD5 = "c39f36e0675339673b707c59f0784fee"
V6_CACHE = os.path.join(HERE, "main_vi_nodeterms.json")
OUT = os.path.join(HERE, "orig_3state_nodeterms.json")
g._run.__defaults__ = (6.0, 120.0)
GATES = []


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    GATES.append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return bool(ok)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def load():
    if os.path.exists(OUT):
        try:
            d = json.load(open(OUT, encoding="utf-8"))
            if d.get("vi") == ORIG:
                return d
        except Exception:
            pass
    return {"vi": ORIG, "md5": {}, "owners": [], "diagrams": {}, "stats": {}, "diff_vs_v6": {}, "gates": []}


def save(st):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1, ensure_ascii=False)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    print("A.1 item 1 - the ORIGINAL's own read-only node/terminal sweep. Contract S0..S3 in the docstring.",
          flush=True)
    st = load()
    before = md5(ORIG)
    st["md5"]["before"] = before
    print(f"   target : {ORIG}\n   md5    : {before}", flush=True)
    must("S0a the ORIGINAL is the expected file before the sweep", before == ORIG_MD5, before)
    print(f"   resuming with {len(st['diagrams'])} diagram(s) already recorded", flush=True)

    if not st["owners"]:
        for cls in ("Global", "Local", "LocalVariable", "Property", "Invoke", "SubVI", "WhileLoop", "ForLoop",
                    "CaseStructure", "Sequence", "FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel",
                    "LoopTunnel", "Wire"):
            try:
                us = g.uids(ORIG, cls)
                st["stats"][f"class_{cls}"] = len(us)
                print(f"   class {cls:26s} n={len(us)}", flush=True)
            except Exception as e:
                st["stats"][f"class_{cls}"] = f"EXC {str(e)[:100]}"
                print(f"   class {cls:26s} RAISED {str(e)[:100]}", flush=True)
        dias = g.report(ORIG, "Diagram")
        st["owners"] = [d["owner"] for d in dias]
        save(st)
    n_dia = len(st["owners"])
    print(f"\n   diagrams: {n_dia} | owners: "
          f"{json.dumps({o: st['owners'].count(o) for o in sorted(set(st['owners']))}, ensure_ascii=False)}",
          flush=True)

    t0 = time.time()
    for k in range(n_dia):
        if str(k) in st["diagrams"]:
            continue
        rows, n = [], 0
        err = None
        while n < 400:
            try:
                node_uid, trows = g.node_terms_uid(ORIG, k, n)
            except Exception as e:
                err = f"EXC n={n} {str(e)[:160]}"
                break
            if not node_uid:
                break
            terms = [{"i": r["i"], "name": r["name"], "is_source": r["is_source"], "wire": r["wire"],
                      "errs": [r["name_err"], r["src_err"], r["conn_err"], r["wire_err"]]} for r in trows]
            while terms and not terms[-1]["name"] and not terms[-1]["wire"]:
                terms.pop()
            rows.append({"n": n, "uid": node_uid, "terms": terms})
            n += 1
        st["diagrams"][str(k)] = {"owner": st["owners"][k], "nodes": rows, "error": err}
        save(st)
        print(f"   diagram {k:>3} ({st['owners'][k] or 'top'}): {len(rows)} nodes, "
              f"{sum(len(d['terms']) for d in rows)} terminals  ({time.time() - t0:.0f} s)"
              + (f"  ERROR {err}" if err else ""), flush=True)

    done = [k for k in st["diagrams"] if st["diagrams"][k].get("error") is None]
    n_nodes = sum(len(st["diagrams"][k]["nodes"]) for k in st["diagrams"])
    n_terms = sum(len(d["terms"]) for k in st["diagrams"] for d in st["diagrams"][k]["nodes"])
    st["stats"].update({"diagrams": n_dia, "diagrams_read_clean": len(done), "nodes": n_nodes,
                        "terminals": n_terms, "seconds": round(time.time() - t0)})
    must("S1 every diagram the ORIGINAL reports was read without an error", len(done) == n_dia,
         f"{len(done)}/{n_dia} clean; errors on "
         f"{[k for k in st['diagrams'] if st['diagrams'][k].get('error')]}")
    must("S2 the sweep produced nodes and terminals", n_nodes > 0 and n_terms > 0,
         f"{n_dia} diagrams / {n_nodes} nodes / {n_terms} terminals in {round(time.time() - t0)} s")

    # ------------------------------------------------------------------ S3  the ORIGINAL-vs-V6 row diff
    diff = {}
    try:
        v6 = json.load(open(V6_CACHE, encoding="utf-8"))
        v6d = v6["diagrams"]
        v6_nodes = sum(len(v6d[k]["nodes"]) for k in v6d)
        v6_terms = sum(len(d["terms"]) for k in v6d for d in v6d[k]["nodes"])
        diff["v6_file"] = V6_CACHE
        diff["v6_vi"] = v6.get("vi")
        diff["totals"] = {"diagrams": [n_dia, len(v6d)], "nodes": [n_nodes, v6_nodes],
                          "terminals": [n_terms, v6_terms]}
        per = []
        for k in sorted(set(list(st["diagrams"]) + list(v6d)), key=int):
            a = st["diagrams"].get(k)
            b = v6d.get(k)
            na = len(a["nodes"]) if a else None
            nb = len(b["nodes"]) if b else None
            oa = a["owner"] if a else None
            ob = b["owner"] if b else None
            if na != nb or oa != ob:
                per.append({"diagram": int(k), "orig_nodes": na, "v6_nodes": nb,
                            "orig_owner": oa, "v6_owner": ob})
        diff["per_diagram"] = per
        print(f"\n   === ORIGINAL vs V6 (tools/bench/main_vi_nodeterms.json) ===", flush=True)
        print(f"      diagrams  ORIGINAL {n_dia:5d}   V6 {len(v6d):5d}", flush=True)
        print(f"      nodes     ORIGINAL {n_nodes:5d}   V6 {v6_nodes:5d}", flush=True)
        print(f"      terminals ORIGINAL {n_terms:5d}   V6 {v6_terms:5d}", flush=True)
        print(f"      diagrams differing in node count or owner: {len(per)}", flush=True)
        for r in per[:40]:
            print(f"         d{r['diagram']:<4} nodes {r['orig_nodes']} vs {r['v6_nodes']}   "
                  f"owner {r['orig_owner']!r} vs {r['v6_owner']!r}", flush=True)
        must("S3 the ORIGINAL-vs-V6 row diff is recorded", True,
             f"{len(per)} differing diagram(s); totals {diff['totals']}")
    except Exception as e:
        diff["error"] = str(e)[:300]
        must("S3 the ORIGINAL-vs-V6 row diff is recorded", False, str(e)[:200])
    st["diff_vs_v6"] = diff

    after = md5(ORIG)
    st["md5"]["after"] = after
    must("S0b the ORIGINAL is byte-identical after the sweep", after == before == ORIG_MD5, after)
    st["gates"] = GATES
    save(st)
    bad = [x["label"] for x in GATES if not x["ok"]]
    print(f"\n   -> {OUT}", flush=True)
    print(f"\nGATES {len(GATES) - len(bad)}/{len(GATES)} pass" + (f"; failing: {bad}" if bad else ""), flush=True)
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
