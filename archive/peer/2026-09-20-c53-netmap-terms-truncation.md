# c53-netmap-terms-truncation

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.1620  in 26 / out 38662 / cache-create 137347 / cache-read 1548814  (526s, 22 turn(s))
- **date:** 2026-09-20 06:57:01
- **outcome:** ANSWERED (530s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session (correct for a read-only peer role), so the review is here in full rather than in a file.

# REFUTED on mechanism — and the conclusion is not a discovery. It was measured and written down on 2026-09-14; the two gates failed because the **gates** are mis-specified.

## 1. The single strongest reason the claim is wrong

**The `max_terms=40` cap explains #637 exactly — the one node the restructure depends on.**

`net_map`'s terminal loop is `for t in range(max_terms)` — `tools/gscript.py:2549`. It reads terminal indices **0–39 only**. For #637 (`main_vi_nodeterms.json:6424-7131`, 59 terminals) the unnamed terminals inside i0–i39 are i14, 17, 22, 23, 26, 27, 30, 31, 32, 33, 34, 37 = **12**, so named inside i0–i39 = 40 − 12 = **28** — exactly the netmap's length. Verified by direct probe of `main_vi_netmap.json`, not inferred:

| probe | is | meaning |
|---|---|---|
| `["error out", 6197]` = #637 **i39**, last index `range(40)` visits | **present** | the walk got there |
| `["# FD points", 9000]` = #637 **i42**, first dropped named terminal | **absent** | it stopped there |
| `["# slices in stack", 9649]` (i45), `["System no.", 16421]` (i49), `["# DT points", 29006]` (i50) | **absent** | everything past 39 is gone |

The brief's own measurement already said so: *"the cap model raises the match from 574 to 575"*, and #637 is the **only** one of the 52 with ≥40 terminals — so the one node the cap explained **is** #637. The brief then presents #637 as the unexplained worst case. "None is 40" counts the wrong quantity: `max_terms` bounds terminals **read**; the array length counts named terminals **written** (`sweep_netmap_main.py:64`).

The proposed mechanism is separately falsified by #637's own record: i2, i20, i24, i28 all carry `errs[3] = 1055` — [LabVIEW "Object reference is invalid"](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE), i.e. the wire read failed — and all four are **inside** the emitted 28. An errored property read demonstrably does not stop the walk.

## 2. Alternative explanation for the other 51 — a documented heuristic, not an error

`tools/gscript.py:2557-2560`: the walk breaks after **three consecutive terminals that are both unnamed and unwired** (`empties >= 3`). The comment states what it was built for — *"an unassigned connector-pane slot of a subVI (2026-09-07: those truncated the list)"*. Raising the threshold 1 → 3 narrowed the failure; it did not remove it.

The two violations your log actually printed (`c53_row_class.log:80`) are textbook cases: **#30804 and #4620**, 20 terminals / 6 named each, netmap drops exactly one trailing **named and wired** terminal — `error out` in both, the conventional bottom-right pane slot, reachable only past the unassigned middle slots.

So there are **two** mechanisms — cap (#637 alone) and `empties>=3` (the rest). The brief invented a third to cover both. Two more stops exist and are **invisible to any netmap↔nodeterms comparison keyed on nodes present in both files**: `MISS_LIMIT = 4` on the node loop (`:2525-2541`) and the junk-Invoke signature that breaks the **whole** walk (`:2564-2567`). Those drop entire nodes, so the 626 denominator is itself not a safe baseline.

## 3. It was already known, and G2b/G2c ask for something the record contradicts

`tools/bench/sweep_nodeterms_main.py:7`: *"the cache is 'at least' — **it truncated on some diagrams**"*. Its collection-time check (`:76`) was deliberately a **prefix** test, `mine_named[:len(theirs)] != theirs`, across all 626 nodes. Result — `sweep_nodeterms_main.log:189-200`: 626 checked, 11 mismatches, **all** of them `"node index out of range (UID 0)"` on uid 22963, and **zero** terminal-list disagreements.

G2b (`A == Bn`) and G2c (`shortfall == unnamed`) demand **equality** where the project's own record said **prefix**. The prior review's prediction contradicted a fact on disk; the FAILs are the gate's, and the "52 violations" are the documented truncation being rediscovered.

## 4. What was not reported, and is worse than a short count

`nets` is built inside the same truncated loop (`gscript.py:2570-2572`), so the netmap's **`wires`** table inherits every truncation. Diagram 19 is missing all of #637's i40–i58 wire ends — 9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392, 29081, 29106, 32583, 32344 — border wires of the loop being rebuilt.

And `c53_row_class.log:127-129` prints a **negative** claim straight off that table (`c53_row_class.py:366-371`): *"NO other node terminal on #686 carries either wire, so the SOURCE OBJECT of 4185 is UNMEASURED."* A truncated census cannot support "nothing else carries this wire". That must be re-derived from nodeterms before anything is built on it.

Your reassurance about the 17 rows does hold — but for a reason you didn't state: the five focus nodes have 6/7/1/1/1 netmap terminals (`c53_row_class.log:79`), far below both stops, and G6 confirms them independently. Not because they "fall in the 574-node complete set" — that set is defined by agreement with a file, not by completeness.

## 5. What would falsify my account

A node whose netmap array is shorter than the replay below predicts **while** (a) having no run of 3 consecutive unnamed+unwired terminals, (b) holding fewer than 40 terminals, and (c) showing clean `errs` on the first dropped terminal. That is the first real evidence of an unmodelled early stop. Symmetrically, mine dies if any of the 52 is not reproduced by cap-or-`empties3`.

## 6. Cheapest discriminating test — files only, ~25 lines, no LabVIEW, no COM

Replay `gscript.py:2548-2569` over `main_vi_nodeterms.json`, apply `sweep_netmap_main.py:64`'s `if t` filter, diff against `main_vi_netmap.json` for every node in both:

```python
JUNK = ["reference", "reference out", "error in (no error)", "error out", "Method", "Method"]
def replay(terms, max_terms=40):
    em, empties, stop = [], 0, "end-of-list"
    for t in terms[:max_terms]:
        if t["name"] == "" and t["wire"] == 0:
            empties += 1
            if empties >= 3: stop = "empties3@i%d" % t["i"]; break
            em.append(t); continue
        empties = 0; em.append(t)
        if len(em) == 6 and [x["name"] for x in em] == JUNK: return None, "junk"
    else:
        if len(terms) > max_terms: stop = "cap@40"
    while em and em[-1]["name"] == "" and em[-1]["wire"] == 0: em.pop()
    return [(x["name"], x["wire"]) for x in em if x["name"]], stop
```

Predictions, all machine-checkable: **626/626 reproduce**; `cap@40` holds **exactly #637**; `empties3` holds the other **51**, #30804 and #4620 among them; `unexplained` is **empty**. That is also your "do the 52 lengths correlate with anything readable" answer — they correlate with the index of the first 3-empty run, and with nothing else. Second lookup, one line, real consequence: build wire → ends from **nodeterms** for diagram 19 and resolve 4185 / 7506, so C1f's negative claim rests on the untruncated census.

**Do not re-sweep LabVIEW for this.** `main_vi_nodeterms.json` already *is* the complete census — 626 nodes, 3328 terminals, real indices, `is_source`, per-field error columns. Derive the wire table from it and retire `main_vi_netmap.json` as a census. A re-sweep at `max_terms=80` would spend ~74 min of LabVIEW time re-collecting what is on disk.

**What would change my mind:** the replay leaving any node in `unexplained`. Then the RuntimeError break at `:2554-2555` (a transient run failure, which files cannot distinguish from a deterministic stop) becomes the live hypothesis — and *that* is the point at which the measurement genuinely does not separate the two causes.

Sources: [NI — Error 1055 from a Property or Invoke Node](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE) · [NI Community — "Error 1055 at Property Node: Object reference is invalid"](https://forums.ni.com/t5/LabVIEW/quot-Error-1055-at-Property-Node-Object-reference-is-invalid/td-p/3365922) · [NI Community — Scripting: Terminal Information (`Terminals[]` usage)](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL — cycle 53 judgement session, 2026-09-20. It refutes the mechanism I had already
written into two documents, and one of its findings invalidates a disposition I wrote this same
morning.** This is the most consequential result of the cycle.

**THE MECHANISM, adopted, replacing the `if t` account.**
1. `net_map`'s terminal loop is `for t in range(max_terms)` with `max_terms=40` — `tools/gscript.py:2549`.
   It reads terminal indices **0–39 only**. `WhileLoop #637` has **59 terminals**
   (`tools/bench/main_vi_nodeterms.json:6424-7131`): 12 of i0–i39 are unnamed, so 40 − 12 = **28**
   named — exactly the netmap array's length, verified by direct probe rather than inferred. **The
   single node the entire seven-loop restructure turns on is the one the census truncates.**
2. The other 51 are the documented `empties >= 3` early stop (`:2557-2560`) — the walk breaks after
   three consecutive terminals that are both unnamed and unwired, built for unassigned connector-pane
   slots. `#30804` and `#4620` are textbook cases: 20 terminals, 6 named, and the one dropped row is
   the trailing **named and wired** `error out`, the conventional bottom-right pane slot sitting past
   the unassigned middle slots. Raising that threshold 1 → 3 in 2026-09-07 narrowed the failure and
   did not remove it.
3. The `if t` filter of `archive/peer/2026-09-20-c53-g2b-caseselector.md` is real but secondary. That
   review's disposition is amended by this one; both stay on file.

🔴 **THE FINDING THAT CHANGES WORK ALREADY DONE — `nets` is built inside the same truncated loop**
(`tools/gscript.py:2570-2572`), **so the netmap's `wires` table inherits every truncation.** Diagram 19
is missing all of `#637`'s i40–i58 wire ends — 9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392,
29081, 29106, 32583, 32344 — *the border wires of the loop being rebuilt*.

**CONSEQUENCE I AM OBLIGED TO RECORD AGAINST MYSELF.** `tools/bench/c53_row_class.log:127-129`
(`c53_row_class.py:366-371`) printed a **negative** claim straight off that table — *"no other node
terminal on `#686` carries either wire"* — and **I used exactly that claim this morning to REJECT the
P6 review's finding that `#48` t3's VISA session has a source on `#686`**
(`archive/peer/2026-09-20-movein-p6-diagram-misprediction.md`, "REJECTED — unsupported by the files it
cites"). A truncated census cannot support "nothing else carries this wire". **That rejection is
WITHDRAWN**: the P6 claim is not thereby proven, it is returned to UNRESOLVED and must be re-derived
from `main_vi_nodeterms.json` before anything is built on it. The measured count "sources on `#686` =
0" in Pre-decided 38(b) is likewise **UNSOUND** and is marked so in the plan.

This is the cleanest instance yet of the pattern the cycle has now met three times: a reader that
answers confidently with the wrong thing, and an argument built on it that looks fully measured. I
refuted a correct reviewer using a broken instrument, and only a second reviewer caught it. **A
negative claim — "nothing else X" — may never be drawn from a census whose completeness has not itself
been measured.** Written into Pre-decided 38(h).

**NOT A DISCOVERY, AND THAT IS ITS OWN FINDING.** The reviewer notes the cap and the early stop were
measured and written down on **2026-09-14**; the two gates failed because the *gates* were
mis-specified, not because the behaviour was unknown. Prior art existed and was not consulted.

**NOT DONE THIS CYCLE, carried to NEXT:** the reviewer's §6 discriminating test (files only, ~25 lines,
no LabVIEW, no COM) reproducing all 52 nodes from cap-or-`empties3`, and the re-derivation of every
netmap-sourced fact about `#637`'s border — `docs/frame-loop-wire-graph.md` is the document most
exposed.
