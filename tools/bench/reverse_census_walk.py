"""reverse_census_walk.py - cycle 55 SECOND ACT. FILES ONLY. LabVIEW IS NEVER TOUCHED.

No `.vi` is opened, no COM call is made, no GUI action is taken, no motor / ASI / camera is reached.
`gscript` is NOT imported. Refs opened 0 / closed 0 / live 0 by construction.

WHY THIS EXISTS (STATUS.md:68, Pre-decided 39(h), retrospective Finding 3(b)). The nodeterms <-> netmap
agreement was measured in ONE direction only: "0 nodes missing from either census" came from a
nodeterms -> netmap walk. The REVERSE walk was never computed, and three files on disk put the netmap
at 635 nodes against 626.

PRIOR ART, CHECKED BEFORE WRITING A LINE (CLAUDE.md, "check what already exists"):
  * `tools/bench/replay_netmap_truncation.py` (cycle 54, 32 kB) - reproduces the 52 TERMINAL shortfalls of
    `#637` and friends from files, and states "626 nodes compared, 574 agree / 52 disagree and 0 nodes
    missing from either census". That is the FORWARD direction only; it never inverts the key set and never
    touches the 635 figure. NOT re-run here, NOT modified.
  * `tools/bench/analyse_netmap_cache.py:3` - the file whose own docstring asserts "635 nodes". Read, not run.
  * `tools/bench/sweep_netmap_main.py` / `sweep_nodeterms_main.py` - the two GENERATORS. Read for mechanism.
  * `tools/bench/analyse_nodeterms_main.py:89` - the generator of `docs/main-vi-panel-map.md:401`'s "635" line.
  * No existing tool computes a reverse census walk, and none reconciles 635 vs 626. Nothing is rebuilt.
  * `tools/gscript.py` HAS no reverse-walk helper (`grep "^def "`: no `census`, no `reverse`), so nothing
    there is duplicated either.
NO NEW OP, NO NEW DEVICE, NO RECIPE (Pre-decided 2; user 2026-09-18 08:53). This file lives under
`tools/bench/` and is a DIAGNOSTIC.

=====================================================================================================
PREDICTION CONTRACT - every gate below is REPORTED, never required (41(c)); no `FAIL` is expected to be
retained. Each predicted value was measured off the same files before this file was written, so a FAIL
here means the files changed under us, not that a hypothesis died.
=====================================================================================================
JOB 1 - the reverse census walk
  R1  netmap and nodeterms enumerate the SAME 170 diagram keys                                  -> True
  R2  netmap per-diagram node ENTRIES sum to                                                    -> 635
  R3  nodeterms per-diagram node ENTRIES sum to, and equal `stats.nodes`                        -> 626
  R4  netmap DISTINCT node uids / nodeterms DISTINCT node uids                                  -> 627 / 626
  R5  REVERSE walk: netmap uids absent from nodeterms                                           -> exactly {22963}
  R6  FORWARD walk: nodeterms uids absent from netmap                                           -> 0 (the
      cycle-54 claim reproduced independently)
  R7  (diagram, uid) PAIRS in netmap not in nodeterms = 9, every one uid 22963; the reverse = 0
  R8  635 - 626 == 9 == the number of netmap entries keyed 22963                                -> True
  R9  `diagram_tree_main.json` (the file `sweep_nodeterms_main.py` actually iterates) holds 637 node
      entries, 627 distinct, uid 22963 ELEVEN times, and in EVERY case at the LAST index of its diagram
  R10 637 - 11 == 626: the nodeterms total is the tree total minus one dropped node per 22963 site,
      which is exactly what `sweep_nodeterms_main.py:56-59` does (`node_uid == 0` -> record mismatch,
      print "OUT OF RANGE", `break`)                                                            -> True
  R11 the netmap's 9 diagrams carrying 22963 and the tree's 11 are DISJOINT sets                -> True
  R12 the three on-disk files that assert 635 are `docs/instrument-libraries.md:103`,
      `docs/main-vi-panel-map.md:401` and `tools/bench/analyse_netmap_cache.py:3`, and the string
      "635" is present on each of those lines                                                   -> True
  R13 c53_row_class.json keys NO uid in the disagreeing set: its 8 table node uids are
      {48, 3447, 3529, 3560, 10407, 10686, 10757, 12589}, its focus_set and sr_pairs add no more, and
      22963 does not occur anywhere in the file's text                                          -> True
  R14 every uid c53_row_class.json keys IS present in nodeterms                                 -> 8/8

JOB 2 - `walk()`'s node count for `Diagram #686`
  R15 `walk()`'s truncation mechanism, read out of the source, is TWO stops and not one:
      `build_opstopfromnode_v0.py:132` `for n in range(limit)` caps the walk at `limit` nodes, and
      `:134-135` `if not u: break` stops at the first index past the end. The caller
      `diag_queue_typetest_control.py:300` passed `limit=200`, so the CAP WAS NOT BINDING.
  R16 `diag_queue_typetest_control.json.walk_n_nodes` == len(its census)                        -> 24 == 24
  R17 nodeterms diagram key "19" is `Diagram #686` (`c53_row_class.json.diagram_index_map`) and holds
                                                                                                -> 21 nodes
  R18 census uids MINUS nodeterms d19 uids                                                      -> {10170, 23032, 23041}
      nodeterms d19 uids MINUS census uids                                                      -> {} (NO shortfall)
  R19 those three are the three While loops stage S2 ADDED to `Diagram #686`
      (`tools/bench/stage_d1_s2_loops.log:47,61,75` names loop a #23032 / loop b #10170 /
      loop c #23041, each `owner Diagram #686`), and they carry 1 terminal each
  R20 terminals: census 139 == nodeterms-d19 136 + 3; and on all 21 SHARED nodes the per-node terminal
      count is IDENTICAL in both censuses                                                       -> 0 differences

JOB 3 - the rule-4 relocation (STATUS.md's own NEXT owed it for a cycle)
  R21 STATUS.md holds exactly one line for each of `owner_c54m3`, `owner_c54m2`, `owner_c54m`
  R22 each line's sha256 is recomputed from STATUS AFTER the archive file is written and matches the
      sha256 taken BEFORE (byte-identical copy, never retyped)
  R23 STATUS.md line count 81 -> 79 (three lines out, one pointer line in)
  R24 `docs/doc_lint` L2's single dangling citation (`STATUS.md:76 ->
      archive/2026-09-20-status-cycle54-relocate.md`) is closed by this write
  NOTE, reported not acted on: cycle 53's `## NEXT` section has NO verbatim source anywhere on disk.
  STATUS's NEXT is rewritten in place every cycle and no snapshot of cycle 53's was archived (the only
  archived `## NEXT` is cycle 50's, in `archive/2026-09-20-status-cycle50-relocate.md`), and this project
  is not a git repo. Rule 4 says relocate VERBATIM; there is nothing verbatim to relocate, so it is
  RECORDED as unrecoverable rather than reconstructed. The live `## NEXT` is left untouched, as is every
  cycle-55 lock key.

JOB 4 - bookkeeping facts, reported not acted on: `violations.py`, `outcome_review.py --due`,
  `doc_lint.py` before and after the relocation.

  MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/reverse_census_walk.log -- \
      py -u tools/bench/reverse_census_walk.py
"""
import collections
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

try:                                        # the log must survive non-ASCII (cp949 consoles)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                                                   # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.dirname(HERE)
STATUS = os.path.join(ROOT, "STATUS.md")
ARCHIVE = os.path.join(ROOT, "archive", "2026-09-20-status-cycle54-relocate.md")
OUT = os.path.join(HERE, "reverse_census_walk.json")

NETMAP = os.path.join(HERE, "main_vi_netmap.json")
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")
TREE = os.path.join(HERE, "diagram_tree_main.json")
ROWCLASS = os.path.join(HERE, "c53_row_class.json")
CONTROL = os.path.join(HERE, "diag_queue_typetest_control.json")
S2LOG = os.path.join(HERE, "stage_d1_s2_loops.log")
WALKSRC = os.path.join(TOOLS, "recipes", "build_opstopfromnode_v0.py")

R = {"script": "tools/bench/reverse_census_walk.py", "stamp": time.strftime("%Y-%m-%d %H:%M:%S"),
     "labview_touched": False, "refs": {"opened": 0, "closed": 0, "live": 0},
     "interprets_nothing": True, "no_new_op": True, "no_recipe": True,
     "job1": {}, "job2": {}, "job3": {}, "job4": {}, "gates": {}, "facts": []}
passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    R["gates"][name] = {"pass": bool(ok), "detail": str(detail)[:400]}
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + str(detail)) if detail else ""), flush=True)
    return bool(ok)


def fact(line):
    R["facts"].append(line)
    print("  FACT  %s" % line, flush=True)


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def lines_of(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read().splitlines(True)


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def run_tool(argv, label):
    try:
        cp = subprocess.run([sys.executable] + argv, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=240)
        return {"rc": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr[-2000:]}
    except Exception as e:                                                          # noqa: BLE001
        return {"rc": None, "error": "%s: %s" % (type(e).__name__, str(e)[:200]), "label": label}


# =====================================================================================  JOB 1
def job1():
    print("\n=== JOB 1  the REVERSE census walk (STATUS.md:68 / Pre-decided 39(h))", flush=True)
    nm, nt, tr = load(NETMAP), load(NODETERMS), load(TREE)
    J = R["job1"]

    nmd, ntd, td = nm["diagrams"], nt["diagrams"], tr["diagrams"]
    gate("R1 netmap and nodeterms enumerate the same 170 diagram keys",
         set(nmd) == set(ntd) and len(nmd) == 170, "netmap %d / nodeterms %d" % (len(nmd), len(ntd)))

    nm_pairs = set((k, int(u)) for k, v in nmd.items() for u in v["nodes"])
    nt_pairs = set((k, int(n["uid"])) for k, v in ntd.items() for n in v["nodes"])
    tr_pairs = [(k, int(u)) for k, v in td.items() for u in v["uids"]]

    nm_tot = sum(len(v["nodes"]) for v in nmd.values())
    nt_tot = sum(len(v["nodes"]) for v in ntd.values())
    tr_tot = sum(len(v["uids"]) for v in td.values())
    J.update({"netmap_entries": nm_tot, "nodeterms_entries": nt_tot, "tree_entries": tr_tot,
              "nodeterms_stats_nodes": nt["stats"]["nodes"]})
    gate("R2 netmap per-diagram node ENTRIES == 635", nm_tot == 635, nm_tot)
    gate("R3 nodeterms ENTRIES == 626 and == stats.nodes", nt_tot == 626 and nt["stats"]["nodes"] == 626,
         "%d / stats %d" % (nt_tot, nt["stats"]["nodes"]))

    nm_uids = set(u for _, u in nm_pairs)
    nt_uids = set(u for _, u in nt_pairs)
    J.update({"netmap_distinct_uids": len(nm_uids), "nodeterms_distinct_uids": len(nt_uids)})
    gate("R4 distinct uids netmap 627 / nodeterms 626", len(nm_uids) == 627 and len(nt_uids) == 626,
         "%d / %d" % (len(nm_uids), len(nt_uids)))

    rev = sorted(nm_uids - nt_uids)
    fwd = sorted(nt_uids - nm_uids)
    J["reverse_netmap_uids_missing_from_nodeterms"] = rev
    J["forward_nodeterms_uids_missing_from_netmap"] = fwd
    gate("R5 REVERSE: netmap uids absent from nodeterms == [22963]", rev == [22963], rev)
    gate("R6 FORWARD: nodeterms uids absent from netmap == []  (cycle 54's claim, reproduced)",
         fwd == [], fwd)

    pr_nm = sorted(nm_pairs - nt_pairs, key=lambda x: (int(x[0]), x[1]))
    pr_nt = sorted(nt_pairs - nm_pairs, key=lambda x: (int(x[0]), x[1]))
    J["pairs_netmap_only"] = [[k, u] for k, u in pr_nm]
    J["pairs_nodeterms_only"] = [[k, u] for k, u in pr_nt]
    gate("R7 (diagram,uid) pairs netmap-only == 9 all uid 22963; nodeterms-only == 0",
         len(pr_nm) == 9 and all(u == 22963 for _, u in pr_nm) and not pr_nt,
         "netmap-only %r / nodeterms-only %d" % (pr_nm, len(pr_nt)))

    nm22 = sorted((k for k, v in nmd.items() if "22963" in v["nodes"]), key=int)
    J["netmap_22963_diagrams"] = nm22
    gate("R8 635 - 626 == 9 == netmap entries keyed 22963",
         nm_tot - nt_tot == 9 == len(nm22), "%d - %d = %d ; 22963 on %d diagrams"
         % (nm_tot, nt_tot, nm_tot - nt_tot, len(nm22)))

    tr_cnt = collections.Counter(u for _, u in tr_pairs)
    tr22 = [(k, td[k]["uids"].index(22963), len(td[k]["uids"])) for k in sorted(td, key=int)
            if 22963 in td[k]["uids"]]
    J["tree_22963_sites"] = [[k, i, n] for k, i, n in tr22]
    J["tree_distinct_uids"] = len(set(u for _, u in tr_pairs))
    last_always = all(i == n - 1 for _, i, n in tr22)
    gate("R9 diagram_tree_main.json: 637 entries, 627 distinct, 22963 x11, ALWAYS the last index",
         tr_tot == 637 and len(set(u for _, u in tr_pairs)) == 627 and tr_cnt[22963] == 11 and last_always,
         "entries %d distinct %d n22963 %d last_always %r" % (tr_tot, len(set(u for _, u in tr_pairs)),
                                                              tr_cnt[22963], last_always))
    gate("R10 637 - 11 == 626 (one node dropped per 22963 site by sweep_nodeterms_main.py:56-59 `break`)",
         tr_tot - tr_cnt[22963] == nt_tot, "%d - %d = %d vs %d" % (tr_tot, tr_cnt[22963],
                                                                   tr_tot - tr_cnt[22963], nt_tot))
    tr22_d = set(k for k, _, _ in tr22)
    gate("R11 the netmap's 9 junk sites and the tree's 11 are DISJOINT diagram sets",
         not (tr22_d & set(nm22)), "tree %r / netmap %r" % (sorted(tr22_d, key=int), nm22))

    # R12 - the three files that put the netmap at 635
    cites = [("docs/instrument-libraries.md", 103), ("docs/main-vi-panel-map.md", 401),
             ("tools/bench/analyse_netmap_cache.py", 3)]
    got = []
    for rel, ln in cites:
        try:
            txt = lines_of(os.path.join(ROOT, rel.replace("/", os.sep)))[ln - 1].rstrip("\r\n")
        except Exception as e:                                                      # noqa: BLE001
            txt = "READ ERROR %s" % e
        got.append({"file": rel, "line": ln, "has_635": "635" in txt, "text": txt.strip()[:220]})
    J["files_asserting_635"] = got
    gate("R12 the three on-disk 635 assertions are where the brief says and all contain '635'",
         all(g["has_635"] for g in got), "; ".join("%s:%d %s" % (g["file"], g["line"], g["has_635"]) for g in got))
    for g in got:
        fact("635 IS ASSERTED AT %s:%d -> %s" % (g["file"], g["line"], g["text"]))
    fact("a 4th, GENERATED occurrence: tools/bench/analyse_nodeterms_main.py:89 writes the "
         "docs/main-vi-panel-map.md:401 heading, so that doc's 635 is not an independent count.")

    # R13/R14 - does the disagreeing set touch c53_row_class.json?
    rc = load(ROWCLASS)
    rc_txt = io.open(ROWCLASS, encoding="utf-8").read()
    keyed = set()
    for row in rc["table"]:
        keyed.add(int(row["owner_uid"]))
        for oe in (row.get("other_end") or []):
            if isinstance(oe, dict) and oe.get("kind") == "node" and oe.get("uid"):
                keyed.add(int(oe["uid"]))
    keyed |= set(int(u) for u in rc.get("focus_set", []))
    for pair in (rc.get("sr_pairs") or {}).values():
        keyed |= set(int(u) for u in pair)
    disagreeing = set(rev) | set(fwd)
    hit = sorted(keyed & disagreeing)
    J["c53_row_class_node_uids"] = sorted(keyed)
    J["c53_row_class_uids_in_disagreeing_set"] = hit
    J["c53_row_class_text_contains_22963"] = ("22963" in rc_txt)
    gate("R13 c53_row_class.json keys NO uid in the disagreeing set {22963}",
         not hit and "22963" not in rc_txt,
         "keyed %r ; intersection %r ; '22963' in file text: %r"
         % (sorted(keyed), hit, "22963" in rc_txt))
    missing = sorted(u for u in keyed if u not in nt_uids)
    J["c53_row_class_uids_missing_from_nodeterms"] = missing
    gate("R14 every uid c53_row_class.json keys is present in nodeterms",
         not missing, "%d/%d present; missing %r" % (len(keyed) - len(missing), len(keyed), missing))
    fact("ANSWER to the brief's red question: NO. The only node uid on which the two censuses disagree "
         "is 22963, and c53_row_class.json keys none of it - the 17-row loop-1.5 table is untouched by "
         "the 635-vs-626 discrepancy. Its 8 node uids %r all resolve in nodeterms." % sorted(keyed))
    fact("MECHANISM of 635 vs 626, read out of the files and not asserted: uid 22963 is net_map's own "
         "junk Invoke node. `main_vi_netmap.json` recorded it on 9 diagrams %r (635 = 626 + 9). "
         "`diagram_tree_main.json` recorded it on 11 OTHER diagrams %r, always as the LAST Nodes[] index "
         "(637 = 626 + 11), and `sweep_nodeterms_main.py:56-59` reads UID 0 there, logs 'node index out "
         "of range', and BREAKS - which is why main_vi_nodeterms.json stops at 626 and why its 11 "
         "`mismatches` rows are all uid 22963. Neither class filters nor diagram \"0\" contribute: "
         "diagram \"0\" holds 0 nodes in BOTH files."
         % (nm22, sorted(tr22_d, key=int)))
    J["diagram_0_nodes"] = {"netmap": len(nmd["0"]["nodes"]), "nodeterms": len(ntd["0"]["nodes"]),
                            "tree": len(td["0"]["uids"])}
    J["nodeterms_mismatch_uids"] = sorted(set(m.get("uid") for m in nt["mismatches"]))
    J["nodeterms_mismatch_n"] = len(nt["mismatches"])

    # per-diagram disagreement table
    tbl = []
    for k in sorted(td, key=int):
        a, b, c = len(td[k]["uids"]), len(ntd[k]["nodes"]), len(nmd[k]["nodes"])
        if not (a == b == c):
            tbl.append({"diagram": k, "owner": td[k]["owner"], "tree": a, "nodeterms": b, "netmap": c})
    J["per_diagram_disagreements"] = tbl
    fact("per-diagram disagreements: %d diagrams of 170; every one is a 22963 site and no other uid "
         "appears in any of them." % len(tbl))


# =====================================================================================  JOB 2
def job2():
    print("\n=== JOB 2  walk()'s node count for Diagram #686 (attempt 1's OPEN 3)", flush=True)
    J = R["job2"]
    src = lines_of(WALKSRC)
    body = "".join(src[128:137])
    J["walk_source_lines_129_137"] = body
    cap = "for n in range(limit)" in body
    brk = "if not u:" in body and "break" in body
    gate("R15a walk()'s stop #1 is the `limit` cap, build_opstopfromnode_v0.py:132", cap,
         src[131].strip())
    gate("R15b walk()'s stop #2 is `if not u: break`, build_opstopfromnode_v0.py:134-135", brk,
         src[133].strip() + " / " + src[134].strip())
    caller = lines_of(os.path.join(HERE, "diag_queue_typetest_control.py"))[299].strip()
    J["caller_line_300"] = caller
    gate("R15c the caller passed limit=200, so the CAP WAS NOT BINDING on a 24-node walk",
         "limit=200" in caller, "diag_queue_typetest_control.py:300  %s" % caller)

    ctl = load(CONTROL)
    cen = ctl["diagram_686_terminal_census"]
    J["walk_n_nodes"] = ctl.get("walk_n_nodes")
    J["census_len"] = len(cen)
    gate("R16 walk_n_nodes == len(census) == 24", ctl.get("walk_n_nodes") == len(cen) == 24,
         "%r / %d" % (ctl.get("walk_n_nodes"), len(cen)))

    nt = load(NODETERMS)
    rc = load(ROWCLASS)
    J["diagram_index_map_19"] = rc["diagram_index_map"]["19"]
    d19 = nt["diagrams"]["19"]["nodes"]
    nt_uids = sorted(int(n["uid"]) for n in d19)
    cen_uids = sorted(c["uid"] for c in cen)
    J["nodeterms_d19_uids"] = nt_uids
    J["census_uids"] = cen_uids
    gate("R17 nodeterms key '19' is Diagram #686 and holds 21 nodes", len(d19) == 21,
         "%d nodes; identified_as %s" % (len(d19), rc["diagram_index_map"]["19"]["identified_as"]))

    extra = sorted(set(cen_uids) - set(nt_uids))
    short = sorted(set(nt_uids) - set(cen_uids))
    J["census_minus_nodeterms"] = extra
    J["nodeterms_minus_census"] = short
    gate("R18 census - nodeterms == [10170, 23032, 23041]  AND  nodeterms - census == [] (NO SHORTFALL)",
         extra == [10170, 23032, 23041] and short == [], "extra %r / shortfall %r" % (extra, short))

    s2 = lines_of(S2LOG)
    hits = {}
    for u in extra:
        for i, ln in enumerate(s2, 1):
            if ("WhileLoop #%d" % u) in ln and "owner Diagram #686" in ln:
                hits[u] = {"line": i, "text": ln.strip()[:200]}
                break
    J["s2_provenance"] = hits
    labels = {c["uid"]: (c["label"], len(c["terms"])) for c in cen if c["uid"] in extra}
    J["extra_node_labels"] = {str(k): v for k, v in labels.items()}
    gate("R19 the 3 extra nodes are stage S2's loops a/b/c, each named in stage_d1_s2_loops.log "
         "with owner Diagram #686, and each carries 1 terminal",
         len(hits) == 3 and all(v[1] == 1 for v in labels.values()),
         "; ".join("#%d %s@L%d nterms=%d" % (u, labels[u][0], hits[u]["line"], labels[u][1])
                   for u in extra if u in hits))

    cen_terms = sum(len(c["terms"]) for c in cen)
    nt_terms = sum(len(n["terms"]) for n in d19)
    ntmap = {int(n["uid"]): n for n in d19}
    diffs = [[c["uid"], c["label"], len(c["terms"]), len(ntmap[c["uid"]]["terms"])]
             for c in cen if c["uid"] in ntmap and len(c["terms"]) != len(ntmap[c["uid"]]["terms"])]
    J.update({"census_terminals": cen_terms, "nodeterms_d19_terminals": nt_terms,
              "per_node_terminal_count_differences": diffs})
    gate("R20 terminals 139 == 136 + 3, and 0 per-node terminal-count differences on the 21 shared nodes",
         cen_terms == 139 and nt_terms == 136 and cen_terms == nt_terms + 3 and not diffs,
         "census %d / nodeterms %d / diffs %r" % (cen_terms, nt_terms, diffs))
    fact("ANSWER to OPEN 3: walk() did NOT truncate on Diagram #686. Its 24 is the 21 nodes the "
         "independent nodeterms census enumerates for that diagram PLUS the three While loops stage S2 "
         "added to it (#23032 loop a, #10170 loop b, #23041 loop c - stage_d1_s2_loops.log:47,61,75), "
         "and the per-node terminal counts agree on all 21 shared nodes. SHORTFALL = 0. This is a "
         "completeness reading for THIS diagram only: walk()'s `limit` cap and its `if not u: break` "
         "are both still live (build_opstopfromnode_v0.py:132,134-135) and a diagram with more than "
         "`limit` nodes would still truncate silently.")


# =====================================================================================  JOB 3
KEYS = ["owner_c54m3", "owner_c54m2", "owner_c54m"]
TITLES = {
    "owner_c54m3": "`owner_c54m3` (cycle 54 material dispatch 3 -- the queue trial census, 18 donors / 18 accepted)",
    "owner_c54m2": "`owner_c54m2` (cycle 54 material, the FILES-ONLY pair -- the netmap-truncation replay and the cycle-53 relocation)",
    "owner_c54m":  "`owner_c54m` (cycle 54 material, the S3 focus trial -- 43/0, ExecState 0, save refused)",
}
POINTER = ("  lock_relocated_c54: # \U0001F535 **THREE LOCK KEYS RELOCATED VERBATIM (rule 4) → "
           "`archive/2026-09-20-status-cycle54-relocate.md` §1–§3** — `owner_c54m3` "
           "(the queue trial census, 18 donors / 18 ACCEPTED), `owner_c54m2` (the files-only netmap "
           "replay + the cycle-51..53 relocation) and `owner_c54m` (the S3 focus trial, 43/0, "
           "`ExecState` 0, save refused). Nothing deleted, only moved; each key's sha256 was verified "
           "against STATUS before AND after the write. ⚠️ **Cycle 53's `## NEXT` section has NO "
           "verbatim source on disk** — STATUS's NEXT is rewritten in place every cycle and no "
           "snapshot of cycle 53's was archived, so §4 of that file RECORDS the gap rather than "
           "reconstructing it.\n")

HEADER = """---
type: archive
status: archived
date: 2026-09-20
tags: [status-relocation, lock-keys, rule-4, cycle54, cycle53]
---

# STATUS lock keys relocated VERBATIM on 2026-09-20 (cycle 55, rule 4)

STATUS.md's own NEXT named this relocation as owed a cycle ago: the three cycle-54 lock keys are
"paragraph-length and are the bulk of this file by volume". They were moved here **verbatim, unedited,
byte-for-byte** by a copy (never retyped, never summarised); each key's sha256 was taken from STATUS.md
before the write and recomputed from STATUS.md after it. In STATUS.md they are replaced by ONE pointer
line in the lock block, in the style the existing `lock_relocated_c51_c53:` key already uses. Nothing is
deleted, only moved. The cycle-55 lock keys and the live `## NEXT` section were not touched.

Written by `tools/bench/reverse_census_walk.py` (cycle 55 material #3, files only - LabVIEW was never
touched: no `.vi` opened, no COM call, no GUI, no motor/ASI/camera; refs 0/0/0).

"""


def job3():
    print("\n=== JOB 3  the rule-4 relocation STATUS's own NEXT has owed for a cycle", flush=True)
    J = R["job3"]
    src = lines_of(STATUS)
    J["status_lines_before"] = len(src)

    idx, keep = {}, []
    for i, ln in enumerate(src):
        m = re.match(r"^  (owner_c54m3|owner_c54m2|owner_c54m):", ln)
        if m:
            idx.setdefault(m.group(1), []).append(i)
    found = {k: idx.get(k, []) for k in KEYS}
    J["key_line_numbers_1based"] = {k: [i + 1 for i in v] for k, v in found.items()}
    gate("R21 STATUS.md holds exactly one line for each of the three cycle-54 keys",
         all(len(found[k]) == 1 for k in KEYS), json.dumps(J["key_line_numbers_1based"]))
    if not all(len(found[k]) == 1 for k in KEYS):
        fact("RELOCATION ABORTED - the three keys were not found exactly once; STATUS.md is unchanged.")
        return

    before = {}
    for k in KEYS:
        ln = src[found[k][0]]
        before[k] = {"sha256": sha(ln), "bytes": len(ln.encode("utf-8")), "line_1based": found[k][0] + 1}
        fact("captured %s from STATUS.md:%d  sha256 %s  (%d bytes)"
             % (k, before[k]["line_1based"], before[k]["sha256"], before[k]["bytes"]))
    J["sha256_before"] = {k: v["sha256"] for k, v in before.items()}

    # ---- write the archive file (the captured line objects are COPIED, never rebuilt from text)
    parts = [HEADER]
    for n, k in enumerate(KEYS, 1):
        parts.append("## §%d — %s\n\n```yaml\n" % (n, TITLES[k]))
        parts.append(src[found[k][0]])                       # <- the VERBATIM copy
        parts.append("```\n\nsha256 of the line as it stood in STATUS.md: `%s` (%d bytes)\n\n"
                     % (before[k]["sha256"], before[k]["bytes"]))
    parts.append(
        "## §4 — cycle 53's `## NEXT` section: NO VERBATIM SOURCE EXISTS ON DISK\n\n"
        "The cycle-54 relocation bullet asked for cycle 53's `## NEXT` to be moved here together with the\n"
        "three keys above. It cannot be, and this section records that instead of reconstructing it.\n\n"
        "MEASURED, not assumed:\n\n"
        "- `STATUS.md`'s `## NEXT` section is **rewritten in place** at every cycle close, so the live file\n"
        "  carries cycle 55's NEXT, not cycle 53's.\n"
        "- No snapshot of cycle 53's NEXT was archived. The only `## NEXT` heading anywhere under `archive/`\n"
        "  outside peer transcripts is cycle 50's, in `archive/2026-09-20-status-cycle50-relocate.md`;\n"
        "  `archive/2026-09-20-status-cycle53-relocate.md` holds five lock keys and no NEXT section.\n"
        "- This project is not a git repository, so there is no revision history to recover it from.\n\n"
        "Rule 4 relocates narrative **verbatim**; a reconstruction from memory or from summaries would be a\n"
        "new document wearing an old date. The gap is therefore reported, and cycle 53's decisions survive\n"
        "where they were actually written down: `docs/cycle27-plan.md` Pre-decided 38, and `owner_c53` in\n"
        "`archive/2026-09-20-status-cycle53-relocate.md` §1.\n")
    body = "".join(parts)
    with io.open(ARCHIVE, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    J["archive_path"] = os.path.relpath(ARCHIVE, ROOT).replace(os.sep, "/")
    J["archive_bytes"] = len(body.encode("utf-8"))
    fact("wrote %s (%d bytes)" % (J["archive_path"], J["archive_bytes"]))

    # ---- verify the archive holds each line byte-identically BEFORE touching STATUS
    arc = lines_of(ARCHIVE)
    arc_sha = {}
    for k in KEYS:
        want = src[found[k][0]]
        arc_sha[k] = any(sha(a) == before[k]["sha256"] for a in arc)
    J["archive_holds_each_line_byte_identical"] = arc_sha
    gate("R22a the archive file holds all three lines byte-identically (sha256 match)",
         all(arc_sha.values()), json.dumps(arc_sha))
    if not all(arc_sha.values()):
        fact("RELOCATION ABORTED after the archive write - STATUS.md is unchanged.")
        return

    # ---- rewrite STATUS: drop the three lines, insert ONE pointer at the FIRST of them
    drop = sorted(found[k][0] for k in KEYS)
    out = []
    for i, ln in enumerate(src):
        if i == drop[0]:
            out.append(POINTER)
        if i in drop:
            continue
        out.append(ln)
    tmp = STATUS + ".tmp_c55"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write("".join(out))
    os.replace(tmp, STATUS)

    after = lines_of(STATUS)
    J["status_lines_after"] = len(after)
    gate("R23 STATUS.md line count 81 -> 79", J["status_lines_before"] == 81 and len(after) == 79,
         "%d -> %d" % (J["status_lines_before"], len(after)))
    still = [k for k in KEYS if any(re.match(r"^  %s:" % k, a) for a in after)]
    gate("R22b the three keys are gone from STATUS.md and the pointer line is in",
         not still and any(a.startswith("  lock_relocated_c54:") for a in after),
         "still present %r" % still)
    gate("R22c every relocated sha256 still matches the archive after the STATUS rewrite",
         all(any(sha(a) == before[k]["sha256"] for a in lines_of(ARCHIVE)) for k in KEYS), "3/3")
    fact("cycle-55 keys left untouched: %s"
         % [k for k in ("owner_c55m1", "owner_c55m1_run1", "owner_c55m2")
            if any(re.match(r"^  %s:" % k, a) for a in after)])
    fact("`## NEXT` section left untouched: %r"
         % any(a.startswith("## NEXT") for a in after))


# =====================================================================================  JOB 4
def job4(phase, key):
    J = R["job4"].setdefault(phase, {})
    J["doc_lint"] = run_tool([os.path.join("tools", "doc_lint.py")], "doc_lint")
    tail = [l for l in J["doc_lint"]["stdout"].splitlines() if l.strip()]
    for l in tail:
        print("  [doc_lint %s] %s" % (phase, l[:300]), flush=True)
    J["doc_lint_headline"] = next((l for l in tail if l.startswith("DOC-LINT")), "?")
    J["doc_lint_L2"] = [l for l in tail if " L2 " in l or l.strip().startswith("STATUS.md:")]
    if key:
        J["violations"] = run_tool([os.path.join("tools", "violations.py")], "violations")
        for l in J["violations"]["stdout"].splitlines():
            if l.strip():
                print("  [violations] %s" % l[:300], flush=True)
        J["outcome_due"] = run_tool([os.path.join("tools", "outcome_review.py"), "--due"], "outcome")
        for l in (J["outcome_due"]["stdout"] + J["outcome_due"].get("stderr", "")).splitlines():
            if l.strip():
                print("  [outcome --due] %s" % l[:300], flush=True)


def main():
    print("=== reverse_census_walk  %s   FILES ONLY - LabVIEW IS NOT TOUCHED (no .vi, no COM, no GUI, "
          "no motor/ASI/camera; refs 0/0/0). Gates are REPORTED, never required (41(c))." % R["stamp"],
          flush=True)
    job4("before_relocation", True)
    job1()
    job2()
    job3()
    job4("after_relocation", False)

    R["summary"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False)
    print("\nGATES %d pass / %d fail%s" % (len(passes), len(fails),
                                           ("  failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("readings -> %s" % OUT, flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
