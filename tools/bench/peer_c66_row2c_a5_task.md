# ATTACK THIS CLAIM — D1 S3b row 2's saved artefact is a sound bed for stage M3

You are the adversary. Your job is to REFUTE the claim below, or to show precisely where it is
under-evidenced. Do not restate it back to me, do not endorse it, do not soften. If after attacking it
you cannot break it, say what specifically survived and what remains unmeasured.

## Context you need

This is a LabVIEW VI Scripting project. We are restructuring a copy of a large tracking VI stage by
stage; each stage must leave a saved `.vi` on disk that the next stage starts FROM. All verification
here is STRUCTURAL (object censuses, `ExecState`, `Broken?`), never functional — nothing has been run
with data.

The run under discussion: `tools/bench/diag_c65_s3b_row2c.py` (1,368 lines, 60 gate sites), whose log
`tools/bench/diag_c65_s3b_row2c.log` ended `BGRUN END rc=1 after 415s` with **57 pass / 1 fail**. That
log is currently this project's newest failing log.

## THE CLAIM TO REFUTE

> S3b row 2's saved artefact `claudeDev\D1_s3b_row2_20260921_160311.vi` (md5
> `26c54ff784cb5cea21edbd214d2cc3a0`, 476,759 B) is **structurally correct** and is a **sound bed** on
> which to run the next stage M3 (five `move_in` calls of the loop-1.5 nodes into `Diagram #23058`,
> then a re-wire of nine internal rows).
>
> The evidence offered for it:
> - cold `ExecState` **1**
> - cold `Wire` **1907** = bed 1906 + 1
> - `Node` **632** — zero new nodes, i.e. the verb `wire_indicators` left no junk `Invoke` behind
> - `ControlTerminal` **116**
> - `Local` **10**
> - `LoopTunnel` **135**, unchanged (no loop boundary was crossed)
> - node `#637` back at position **(59,48)**
> - the Wire **uid-set** diff was `minted [23556] ; vanished []` — a MINT, not the extension of an
>   existing net
> - a cold REVERSE census over all **75** nodes of `Diagram #639` and all **116** panel rows found
>   exactly **one source** (`#10757` terminal 1, `'element'`) and **one sink** (panel control uid
>   **23525**), with the rival Local `#23523` proven NOT on that net

## ALREADY RULED OUT — do not spend your answer re-deriving these

1. **The single failing gate `A5` refuted its own premise.** `A5` assumed that the index into
   `report_all('ControlTerminal')` equals the front-panel row index. Row `i=114` returned uid **34982**,
   whose `owner_of` is `('Diagram', 26117)` — outside the 23xxx band this VI's objects occupy. So the
   gate measured the WRONG terminal; nothing in the artefact depended on it, and the gate was
   non-fatal by construction.
2. **Consequence, recorded as a measurement gap:** the indicator's own `ControlTerminal` uid therefore
   remains UNIDENTIFIED. We know the panel control uid (23525); we do not know the uid of its
   block-diagram terminal object.
3. **An ordered `Broken?` read on the new wire is MEASURED UNREACHABLE.** Both ordered readers this
   fleet owns address their sink as `Diagram[d].Nodes[n].Terminals[t]`, and this net's only sink is a
   panel `ControlTerminal`, which does not appear in that diagram's `Nodes[]` list. Gate `L` therefore
   ran on a different wire (23540) and read `Broken?` = False — a reading about the wrong wire.

## THE STANDING QUESTION — answer this explicitly

**Does the unidentified `ControlTerminal` uid, or the unreachable ordered `Broken?` on the new wire,
leave any way for row 2's net to be WRONG in a manner that every gate listed above would still PASS?**

Construct the concrete failure mode if one exists — name the object, the property, and why each listed
gate would be blind to it. Consider at least: a wire that is present and counted but type-broken; a
sink that is the wrong terminal of the right control; a source terminal that is not the one intended;
an object owned by a diagram other than `#639`; and anything a pure COUNT plus a uid-set diff cannot
distinguish.

Then name the **cheapest discriminating test** that our EXISTING verbs can actually execute. Our verbs
address objects as: whole-VI class censuses (`report_all('<Class>')` → uid lists), per-node terminal
tables (`node_terms(uid)` → label / is_source / wire uid / error code per terminal), a 116-row
front-panel census (label / indicator / uid / is_source / wire / wire_err), `owner_of(uid)`,
`count('<Class>')`, `exec_state`, and diagram-indexed node addressing
`Diagram[d].Nodes[n].Terminals[t]`. A test that requires a verb we do not have is not cheap — say so
and rank what we could build instead.

## Output contract

⚠️ **BUDGET: answer in AT MOST ~900 words, and do not restate the context or the claim back to me.**
A previous dispatch of this exact question ran out of wall-clock before writing anything. Go straight to
the five numbered items below; a short sharp answer is worth more here than an exhaustive one. Do not
read more of the repository than you need — everything load-bearing is already quoted above.

1. The strongest reason the claim is WRONG.
2. An alternative explanation of the evidence that is consistent with a BAD artefact.
3. What would falsify your alternative.
4. The cheapest discriminating test, expressed in the verbs listed above.
5. Anything in the "already ruled out" block that you think is itself wrong, with the reason.
