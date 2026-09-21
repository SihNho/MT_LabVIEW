# ATTACK this claim about a NEW STATIC GATE we just added to a checker we own

## The claim (attack it; do not confirm it)

`tools/bench/c60c_astcheck.py` gained **gate 10**, a `%`-format ARITY check, and its first run over
`tools/recipes/build_d1_m3a2.py` (log `tools/bench/c74_gate10_m3a2.log`) reported:

    NOTE  10 MISMATCH   build_d1_m3a2.py:354  'ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s) - N'
                        wants 5 arg(s), the tuple supplies 4
    FAIL  10 ... 145 checked OK, 1 MISMATCH, 0 unresolved

THE CLAIM: *the gate counts `%`-format arity correctly for Python source of this shape; the one site it
names is a real defect and the 145 it passed are really correct; therefore this gate is fit to stand as
the fleet's pre-launch arity check, and after that one site is repaired the file carries no further
`%`-arity defect.*

## What the gate actually does (read it: `tools/bench/c60c_astcheck.py`, `SPEC_RE`, `_spec_count`, `percent_format_sites`)

- It walks `ast.BinOp(op=Mod)` nodes whose LEFT is a literal `str`/`bytes` constant.
- Spec regex: `%(?:\((?P<key>[^)]*)\))?(?P<flags>[-+ #0]*)(?P<width>\*|\d+)?(?:\.(?P<prec>\*|\d+))?(?P<len>[hlL])?(?P<conv>[diouxXeEfFgGcrsa%])`
  Each match consumes `1 + (width == '*') + (prec == '*')` arguments; `conv == '%'` consumes none;
  a `%(name)s` mapping key is collected and the site is then declared UNRESOLVED, never counted.
- RIGHT operand: a literal `ast.Tuple` without `Starred` is counted by `len(elts)` and a mismatch FAILS.
  A non-tuple right operand passes when exactly one spec is wanted, FAILS when zero are wanted, and is
  reported UNRESOLVED when two or more are wanted (it may be a tuple at run time).
- UNRESOLVED sites are printed with `file:line`, never silently passed, and never failed.

## Context this comes out of (facts, not argument)

- The run this replaces died in phase 1 of a 45-minute LabVIEW build at what is now `:354`, with
  `TypeError: not enough arguments for format string`. 1,062 hand-written lines had been launched at
  LabVIEW with no static read of any kind.
- The same helper stands CORRECT with five arguments in the sibling recipe `tools/recipes/build_d1_m3a1.py`;
  the copy desynchronised when prose was hand-appended to the format string.
- This gate is a REPAIR of an existing checker. No new harness was built (a standing user order forbids
  new devices). The alternative remedy - executing `main()` against a stubbed LabVIEW wrapper - would catch
  strictly more and is deliberately NOT built; it is recorded as an open item.

## Already ruled out (do not spend the answer on these)

- "Run the recipe and see" - the recipe drives LabVIEW VI Scripting for ~45 min per attempt; that is the
  cost this gate exists to avoid paying.
- "Use a linter instead" - adding a third-party linter is a new device and is forbidden by the same order.
- "The mismatch is a false positive" as a bare assertion - `%02d %s %r %.1f %.2f` against a four-element
  tuple is the exception CPython actually raised in `tools/bench/build_d1_m3a2.log`.

## What an answer that is worth its cost looks like

1. The strongest concrete reason the claim is WRONG: name a `%`-format shape that exists in Python and that
   this counter gets wrong - over-counting (a false FAIL that would block a correct recipe) or, worse,
   under-counting (a defect it passes). Be specific about the source text, not the category.
2. An alternative explanation for the 145 "checked OK" sites reading clean - e.g. a reason the walk never
   reaches some sites at all, so "clean" means "unvisited".
3. What observation would FALSIFY the claim.
4. The cheapest discriminating test, runnable with no LabVIEW, that separates 1/2 from the claim.
