ATTACK the explanation below. It is a diagnosis formed under pressure after TWO gates failed in
`tools/bench/c53_row_class.log` (script `tools/bench/c53_row_class.py`). Do not confirm it. Find the
strongest reason it is WRONG, give an alternative explanation, say what would falsify it, and name the
cheapest FILE-ONLY discriminating test (no LabVIEW, no COM — this session may not open a VI for this).

## What was predicted and what was measured

These two gates were written to run a discriminating test proposed by a previous adversarial review
(`archive/peer/2026-09-20-c53-g2b-caseselector.md`), which established that
`tools/bench/sweep_netmap_main.py:63-64` writes

    rec["nodes"][str(uid)] = {"label": lbl, "terms": [[t, w] for _ti, t, w in terms if t]}

i.e. an unnamed-terminal filter, discarding the real terminal index `_ti`. That review predicted the
netmap `terms` array would equal the NAMED SUBSET, in order, for EVERY node, and that each node's
shortfall would equal its unnamed-terminal count.

    FAIL  G2b(rewritten)  netmap `terms` == the NAMED SUBSET, in order, for EVERY node
                          MEASURED 574/626 nodes match
    FAIL  G2c             per-node shortfall == that node's unnamed-terminal count
                          MEASURED 574/626 ; 130 nodes have a shortfall at all

So the previous review's own predicted rule holds for 574 of 626 nodes and fails for 52.

## Measured shape of the 52 violations (files only: main_vi_netmap.json + main_vi_nodeterms.json)

* In **52 of 52** the netmap `terms` array is a strict **PREFIX** of the named subset — never a
  reordering, never a gap in the middle, always a truncation at the end.
* The truncation point is NOT the writer's `max_terms=40` cap (`sweep_netmap_main.py:55`,
  `g.net_map(MAIN, i, max_nodes=200, max_terms=40)`). Measured netmap array lengths among the 52:
  `[0, 1, 2, 3, 4, 5, 6, 11, 28]` — none is 40. Node total-terminal counts among the 52:
  `[10, 11, 12, 16, 20, 23, 27, 59]`; only ONE of the 52 has 40 or more terminals.
* Applying the cap as a model (`named(first 40 terminals)`) raises the match from 574 to **575** of
  626 — it explains exactly one node, not the other 51.
* Among the 574 matching nodes the maximum terminal count is 28, and none exceeds 40.
* Worst case, and it is the node being restructured: **WhileLoop #637, diagram index 19** —
  59 terminals total, 41 named, 18 unnamed, and the netmap `terms` array holds **28**. Examples:
    `{'d': '19',  'uid': 637,   'n_total': 59, 'n_named': 41, 'n_netmap': 28, 'unnamed': 18}`
    `{'d': '161', 'uid': 24170, 'n_total': 27, 'n_named': 17, 'n_netmap': 11, 'unnamed': 10}`
    `{'d': '3',   'uid': 30804, 'shortfall': 15, 'unnamed': 14}`  (drops a trailing NAMED, WIRED
      terminal `('error out', 32594)`)

## The explanation I formed (ATTACK THIS)

"`g.net_map` stops enumerating a node's terminals EARLY, at a per-node point that is not the
`max_terms` cap — probably the first terminal whose property read errors or returns out-of-range,
after which the loop breaks and the node's remaining terminals are never emitted. The unnamed-filter
of `sweep_netmap_main.py:64` is real but is only the SECOND filter; an earlier truncation inside
`net_map` is the dominant one. Therefore `main_vi_netmap.json` is not a complete terminal census for
52 of 626 nodes, WhileLoop #637 among them, while the 17 cut rows of the 1.5 FOCUS set are unaffected,
because all five focus uids (10407, 48, 3529, 3560, 3447) fall in the 574-node complete set and are
independently confirmed by `main_vi_nodeterms.json` (gate G6 PASS, 17/17 on name+wire+is_source)."

## Already ruled out

* Not the `max_terms=40` cap: it models exactly one of the 52 (575 vs 574).
* Not a reordering or a middle gap: prefix-consistent in 52/52.
* Not a stale file: both censuses name the same source VI and the same 170-diagram traverse.
* Not the 17-row count: G2 (netmap `wires` table), G3 (wire uids) and G6 (third census,
  `main_vi_nodeterms.json`, taken with a different op) all agree on 17 for the five focus uids.

## What I need from you

1. The single strongest reason my "net_map truncates early" story is WRONG.
2. At least one ALTERNATIVE explanation — consider: `main_vi_nodeterms.json` being the file that
   OVER-reports (duplicated or phantom terminals); the two censuses having been taken at different
   times against different VI states; `net_map` deduplicating terminals that share a wire; a
   node-class-dependent terminal enumeration; or a second cap elsewhere in `gscript.net_map`.
3. The observation that would FALSIFY my story.
4. The cheapest file-only discriminating test, naming the files or source lines to read. Candidates:
   `tools/gscript.py` (`net_map` and whatever it calls), `tools/bench/sweep_netmap_main.py`,
   `tools/bench/sweep_netmap_main.log`, `tools/bench/main_vi_nodeterms.json`,
   `tools/bench/sweep_nodeterms_main.log`, `tools/bench/main_vi_netmap.json`.
   Say specifically whether the 52 truncation lengths correlate with anything readable in those files.

Why it matters: if `main_vi_netmap.json` truncates #637's terminal list at 28 of 41 named, then any
count or boundary taken from that file for the loop under restructure is short, silently.
