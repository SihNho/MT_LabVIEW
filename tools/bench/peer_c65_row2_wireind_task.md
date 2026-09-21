# REFUTE THIS ROUTE: feeding an existing panel indicator from an `Index Array` primitive with `wire_indicators`

You are the adversary. Your job is to find the strongest reason the route below is WRONG, name an
alternative explanation, say what would falsify it, and name the cheapest discriminating test. Do
not confirm. Do not summarise. If the route is sound, say so only after you have tried hardest to
break it — and then still give the falsifier and the test.

You may read any file under the project directory. Do not modify anything.

---

## 0. Context in four sentences

The project is refactoring one LabVIEW VI (a magnetic-tweezers bead tracker) so that a data path
that today crosses a loop boundary as a plain wire is instead carried by an **indicator write +
Local read** pair. One such transport is being built one "row" at a time. Row 1 is BUILT and saved.
Row 2's first half (the Local → sink connect) is BUILT and saved. Row 2's second half — feeding the
indicator from its source terminal — is what this review is about.

All verification in this project is **STRUCTURAL** (`ExecState`, censuses, `Wire.Is Broken?`),
never functional. No VI is ever run.

---

## 1. THE PREDICTION I MADE, AND THE MEASUREMENT THAT KILLED IT

**My prediction (cycle 65 material #2):** the `'index'` indicator's *block-diagram terminal* would
be addressable as an entry in `Diagram #639`'s `Nodes[]` array, so the verb `connect_nested_v1`
— whose only addressing scheme is `Diagram[d].Nodes[n].Terminals[t]` (`tools/gscript.py:1342-1343`)
— could wire it directly from `#10757`'s `'element'` source terminal.

**The measurement, `tools/bench/diag_c65_s3b_row2b.log:208`:**

```
FACT  [B1] (iii) *** THE WHOLE-VI ControlTerminal CENSUS (116 uids, census error '')
      INTERSECTED WITH Diagram #639's Nodes[] LIST (75 uids) = 0 uid(s): [] ***
FAIL  A4c (iii) MEASURED: the ControlTerminal census and Diagram #639's Nodes[] list
      intersect at all  ->  0 common uid(s): []
```

So: **116 ControlTerminal uids in the whole VI, 75 `Nodes[]` uids on `Diagram #639`, intersection
= 0.** A front-panel control's terminal is class `ControlTerminal`, and on this machine a
`ControlTerminal` never appears in a `Diagram`'s `Nodes[]` list. The prediction is dead and the
`connect_nested_v1` route to an indicator is dead with it. The run aborted by design; nothing was
built, nothing saved, all md5 pins byte-unchanged.

The indicator itself is fine and reads, off the machine:
`{'label': 'index', 'indicator': True, 'uid': 23525, 'is_source': False, 'wire': 0, 'wire_err': 1055}`
— i.e. it EXISTS on the front panel and its terminal is **BARE**.

---

## 2. THE ROUTE THAT WILL NOW BE RUN — ATTACK THIS

A different verb, `wire_indicators`, which does NOT use `Nodes[]` addressing for the indicator at
all: it names the indicator by **label** and selects the source node by **index within a traversed
class census**.

```python
g.wire_indicators(
    target,
    node_index      = <index of uid 10757 in report_all(target, 'IndexArray')>,
    src_terms       = ['element'],
    indicator_names = ['index'],
    diagram_index   = 46,          # Diagram #639
    node_class      = 'IndexArray',
)
```

### 2.1 The wrapper, verbatim (`tools/gscript.py:1781-1798`)

```python
    ensure_loaded(target)
    vi = op(OP_WIREIND)                      # claudeDev\OpWireInd_v0.vi
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", node_class)      # 'IndexArray'
    vi.SetControlValue("index", node_index)
    vi.SetControlValue("Names", list(src_terms))      # ['element']
    vi.SetControlValue("Class Name 2", "Diagram")
    vi.SetControlValue("index 2", diagram_index)      # 46
    vi.SetControlValue("Names 2", list(indicator_names))   # ['index']
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"wire_indicators: {err}")
    if exec_state(target) != 1:
        raise RuntimeError("wire_indicators: target BROKEN after wiring - ...")
    return dt
```

`OpWireInd_v0.vi` wraps erdosmiller's **`Wire Indicators.vi`**, whose contract this project
recorded as: *"It selects EXISTING indicators by label ('indicators selected with Indicator Names
on **Diagram in**') and branches each onto the wire already attached to the source terminal."*
(`.claude/skills/labview-automation/references/com-driving.md:155-170`)

### 2.2 The bed, every number read off the machine

File `claudeDev\D1_s3b_row2_20260921_151221.vi`, md5 `7a11818387fe44a764c2ff169b1dd6f7`, 476,690 B.

| fact | value |
|---|---|
| `ExecState` COLD | **1** |
| `Wire` / `Node` / `ControlTerminal` / `Local` | 1906 / 632 / 116 / 10 |
| `#10757` | class **`IndexArray`**, label `'Index Array'`, `Diagram #639 Nodes[27]` |
| `#10757` terminals | t0 `'array'` (sink), **t1 `'element'` SOURCE, wire 0 = BARE**, t2 `'index'` (sink) |
| the target indicator | panel control uid **23525**, label `'index'`, indicator, **wire 0 = BARE** |
| the Local built by row 2's first half | `#23523`, on **`Diagram #639` `Nodes[74]`**, its terminal ALSO labelled **`'index'`**, source, on wire **23540** |
| `#10407` (the Case structure, the Local's sink) | t2 still on wire **23540** |

### 2.3 The precedent I am leaning on

`tools/bench/cycle59_s3a_recipe.log:119-131` — the SAME verb, the SAME node `#10757`, the SAME
terminal `'element'`, the SAME indicator label `'index'`, the SAME `diagram_index=46`, on an
ancestor of this very file:

```
FACT  N2 LIVE: diag_index(#639) = 46, #10757 class membership
      [{'class': 'IndexArray', 'index': 20, 'members': 47}]
FACT  N2 wire_indicators(IndexArray[20], ['element'] -> ['index'], diagram_index=46) error VERBATIM ''
FACT  N2 the indicator's wire uid 0 -> 10990 ; whole-VI Wire count 1905 -> 1905 (delta 0 ...)
FACT  ExecState [N2 AFTER wire_indicators] = 1
```

And `tools/bench/diag_c64_s3b_row1.log:299-313` — ROW 1, the same shape, built and saved:

```
FACT  [8] CALL: g.wire_indicators(target, node_index=102, src_terms=['x .and. y?'],
        indicator_names=['Automatic Error Handling'], diagram_index=46, node_class='Function')
FACT  [8] wire_indicators returned 0.088... ; raised ''
FACT  ExecState [08 [8] after wire_indicators] = 1
PASS  H wire_indicators left a NON-ZERO wire on the source #10686 t0  wire 23526
FACT  [8] T3 SEPARATOR - the net of wire 23526 (74 nodes scanned on #639, 116 panel rows):
      [{'where': 'Diagram #639 Nodes[25] = #10686', 'terminal': 0, 'name': 'x .and. y?', 'is_source': True},
       {'where': 'panel control uid 23555', 'name': 'Automatic Error Handling', 'is_source': False}]
PASS  I EXACTLY ONE source on wire 23526, and control 23555 is among its sinks
```

---

## 3. THE TWO HAZARDS I WANT YOU TO ATTACK SPECIFICALLY

### HAZARD 1 — LABEL COLLISION

Row 2's first half created a **Local, `#23523`, on the SAME `Diagram #639`, at `Nodes[74]` of 75,
whose terminal is ALSO named `'index'`** (a Local inherits the label of the control it references —
here, control 23525 itself). `indicator_names=['index']` is resolved BY LABEL against objects
reachable from `Diagram in` = `Diagram #639`. So `wire_indicators` may bind the **Local** instead
of the panel indicator.

That would be a silent wrong build: `ExecState` could still read 1 while the wire goes
`#10757 t1 → Local #23523`, which is a data-source collision with the Local's existing source role
on wire 23540 — or, worse, a legal-looking but semantically wrong topology.

What I have as counter-evidence is ONE precedent: in ROW 1 the very same collision existed (the
Local created from control 23555 also carried the label `'Automatic Error Handling'`, also sat on
`Diagram #639`, at `Nodes[73]`), and the net census afterwards found the sink to be **panel control
uid 23555**, with the Local NOT on the net. Row 1's T3 census scanned all 74 nodes of `#639` and
all 116 panel rows and returned exactly two net members.

**Attack that.** Is one precedent enough? Is there a reason row 1's resolution order would not
repeat here (different node class — `Function` vs `IndexArray`; different `Nodes[]` position — 73
vs 74; different label length; the row-1 indicator was ALREADY WIRED at the start while row 2's is
BARE)? Is there a reading of erdosmiller's `Wire Indicators.vi` under which the choice between a
co-labelled Local and a co-labelled panel indicator is order-dependent, or dependent on which one
appears first in `Get Controls.vi`'s output? Can a `Local` even appear in `Get Controls.vi`'s
`Control Names` array at all, and if it can, at what index relative to a `ControlTerminal`?

### HAZARD 2 — THE WRAPPER'S ABSOLUTE `exec_state` TEST IS A MEASURED DEFECT

`tools/gscript.py:1794-1797` raises whenever `exec_state(target) != 1` after the call. This project
MEASURED, in cycle 62, that the same shape of test raised a **false failure while the machine had
in fact made a real wire**. Related measurements: cycle 64 material #4 (`diag_c64_junkpurge.log`)
showed that several of this fleet's ops leave a **junk `Invoke` node with six terminals and zero of
them wired**, which is itself genuinely broken — `ExecState` goes 1 → 0 on the connect and back to
**1** the moment that junk node is deleted by uid.

So the run will treat a raise as a **READING, not a verdict**: catch it, print it verbatim, then
measure the machine (census diff, panel row 114's wire uid, `#10757` t1's wire uid), purge any new
unwired `Invoke` node by uid, and only then read `ExecState`.

**Attack that too.** Is "catch the raise and keep measuring" ever unsafe here — can the wrapper's
raise leave the target in a state where the subsequent measurement is itself misleading? Is the
junk-`Invoke` purge the right response for `wire_indicators` specifically, given that row 1's
census diff after `wire_indicators` was `Node 631 -> 631 ; 0 new uid(s): []` (i.e. this verb left
NO junk node at all)? If `wire_indicators` leaves no junk, what else could drive `ExecState` to 0,
and would purging be an error?

### A third thing I have NOT got a precedent for — say whether it matters

In cycle 59 the source `#10757 t1` was **WIRED** (wire 10990) and the indicator bare, so
`wire_indicators` **BRANCHED** (Wire delta 0). In row 1 BOTH ends were bare and it **MINTED** a new
wire (Wire 1905 → 1906). Row 2 is the row-1 case: both ends bare. My gate therefore expects the
final cold `Wire` census to be **1907** (1906 + 1). Is that arithmetic right, and is "mint on a
bare source" reliable, given that `tools/gscript.py:1765-1770` says an unwired source makes the
verb *"extend an unrelated wire instead → 'This wire connects more than one data source' and the
target breaks"*? Row 1 contradicts that docstring. Which is right, and how would the run tell the
difference at the moment it happens rather than three steps later?

---

## 4. ALREADY RULED OUT — do not propose these

- `connect_nested_v1` / any `Diagram[d].Nodes[n].Terminals[t]` addressing of the indicator's
  terminal: MEASURED impossible on this machine (§1, intersection = 0).
- Creating a second indicator, a cast, a splice, `allow_broken`, `gui_save`, any GUI action, any
  new op or new `gscript` verb, editing `tools/gscript.py`, or running the VI. All forbidden by
  the dispatch.
- Moving the indicator's `ControlTerminal` onto `Diagram #639` with `move_in`: this run's script
  does not call `move_in` at all, by design.

## 5. WHAT I WANT BACK

1. The strongest reason the §2 route is wrong.
2. An alternative explanation for row 1's success that does NOT generalise to row 2.
3. What would falsify the route — stated as something the run can OBSERVE.
4. The cheapest discriminating test, expressible as extra measurement inside the single
   diagnostic script that is already going to run (no second LabVIEW session, no second file).
5. Anything in §3 you think my gates would MISS — in particular, a gate that would pass while the
   build is semantically wrong.
