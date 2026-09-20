---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opreportnodes-execstate0

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (74s)
- **why asked:** See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
- **verdict:** see 'What was done with it' / STATUS.md 2026-09-14

## Question

LabVIEW 2026 VI Scripting. I have built the same transformation successfully TWICE and it fails the third time, and I do NOT have a confident explanation - attack whatever explanation seems likely and tell me what I am not considering. GOAL: turn a VI that reads ONE object's properties into one that loops over ALL of them and returns arrays. THE TRANSFORMATION, which worked twice: delete the Index Array that picks one element (freeing the array wire), delete the donor's per-element Property nodes, drop a For Loop, create new Property nodes INSIDE the loop body diagram, wire the array into the loop (auto-creates the input tunnel and supplies N), then erdosmiller 'Exit For Loop.vi' for auto-indexed OUTPUT tunnels, then an indicator on each tunnel. THIS WORKED on OpReport_v3 -> OpReportAll_v0 and the result is verified functionally (646 s -> 1.7 s on a 473 KB VI, rows identical). IT FAILS on donor OpSetLabel_v0 -> OpReportNodes_v0: every step reports success, the counts are right (ForLoop=1, LoopTunnel=3, Property=3, IndexArray=1, Wire=21, two array indicators created) but the VI stays at ExecState 0 (broken). DONOR LADDER (all on the top-level diagram): Open VI Reference(uid 43) -> Traverse for GObjects(124, Class Name='Diagram') -> Index Array(308) -> To More Specific Class(683, target class from a class constant 772) -> Property 'Nodes[]'(235) -> [deleted: Index Array 236, Property nodes 744 741 242 241 240 237]. ALSO PRESENT and untouched: node 243, an erdosmiller CREATOR subVI with terminals 'Diagram in'(wired), 'ID String'(wired), 'location (0,0)'(wired), 'Class Name'(wired), 'error in'(wired), and 'reference', 'reference out', 'Inputs', 'Outputs' ALL UNWIRED. Inside the loop body: Property(Node.Label 6359001, Node.Style 6359009) fed from the Nodes[] tunnel, and Property(Text.Text 632D800) fed from the first node's 'Label' output. QUESTIONS: (a) what makes a LabVIEW VI stay BROKEN when every wire I intended exists and remove-bad-wires has been run - what are the common causes I cannot see from object counts? (b) is leaving that creator subVI (243) with unwired 'reference'/'Inputs'/'Outputs' terminals a likely cause - are those REQUIRED terminals on erdosmiller creator VIs? (c) can a Property node whose output feeds an auto-indexed tunnel break if the property returns a REFNUM (Node.Label returns a Text refnum) rather than a value - is auto-indexing a refnum array illegal or problematic? (d) how do I READ LabVIEW's actual broken-VI error list by script (the VI method 'Get Errors' 452 is private and an earlier attempt to attach it failed)? That last one is what I actually need - I am debugging blind.

## Answer

The leading explanation is not the refnum tunnel or the untouched creator. It is a structural/compiler defect invisible to your counts?봢specially a tunnel with only one side connected, a required input on one of the newly created Property Nodes, or a node that is visually inside the loop but is not owned by the loop?셲 body diagram.

### Conclusions

**(a) Object counts do not establish diagram validity.** They miss:

- A loop tunnel whose inner or outer terminal is unwired. NI specifically identifies an undefined/black loop tunnel as a cause of a broken VI that may even produce an empty Error List. [NI: No Errors Listed When Clicking the Broken Run Arrow](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DdHkSAK&l=en-US)
- An unwired required input. ?쏳emove Bad Wires??removes invalid wires; it does not satisfy required terminals. [NI: Debugging Tools in LabVIEW](https://www.ni.com/getting-started/labview-basics/debug.htm)
- A broken subVI or a stale subVI instance whose connector pane changed after placement. [NI: Debugging Tools in LabVIEW](https://www.ni.com/getting-started/labview-basics/debug.htm)
- A wire that exists but terminates on the wrong terminal.
- A type mismatch hidden behind a wire that LabVIEW has marked broken.
- A Property Node with an inappropriate reference class, wrong property direction, or an unwired required reference input.
- Incorrect ownership: the scripting operation positioned the Property Node inside the loop rectangle, but its actual owner remains the top-level diagram.
- A tunnel created by an unsuccessful or partially successful crossing-wire operation.
- A stale compilation state or internal compiler error. NI recommends forcing a recompile when the Error List is missing or stale. [NI: Troubleshooting LabVIEW Code Module Issues](https://www.ni.com/docs/en-AS/bundle/teststand/page/troubleshooting-labview-code-module-issues.html)

Your counts are particularly weak evidence here: `LoopTunnel=3` says three tunnel objects exist, not that each has valid inner and outer connections. My first attack would therefore be:

1. Report every tunnel?셲 owner, index mode, inner-terminal connection, outer-terminal connection, and connected terminal/node identities.
2. Report every terminal of nodes `6359001`, `6359009`, and `632D800`, including direction, connected state, and connected peer.
3. Confirm all three Property Nodes??`Owner` is the For Loop?셲 body diagram, not merely that their coordinates lie inside the loop.
4. Temporarily reason from a minimal build ladder: loop plus input tunnel only, then one Property Node, then its output tunnel, then the second chain. ExecState after each mutation is more diagnostic than final counts.

Also inspect whether both output tunnels were explicitly set to indexing mode. For Loops normally auto-index new output crossings, but relying on a creator library?셲 behavior is weaker than reading the resulting tunnel mode. NI describes the bracketed indexing mode and resulting one-element-per-iteration array behavior here: [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG).

**(b) Node 243 is unlikely to be the cause.** LabVIEW connector-pane outputs cannot be marked Required at all. Only inputs can be Required; unwired recommended or optional terminals do not break the caller. [NI: Setting Required, Recommended, and Optional Inputs and Outputs](https://www.ni.com/docs/ar-IQ/csh?context=lvcore_lvhowto_specifying_required_recomm)

Therefore:

- Unwired `reference out`, `Inputs`, and `Outputs` cannot themselves break the caller merely because they are outputs.
- An input named `reference` could be Required, but that must be checked from the actual connector pane/Context Help; its name alone proves nothing.
- More decisively, if donor `OpSetLabel_v0` was executable with node 243 in exactly that wiring state, node 243 cannot independently explain why the transformed caller became broken.

The caveat is that your deletion may have removed a wire that previously satisfied a required input on 243, even if the subVI itself was ?쐕ntouched.??Compare node 243?셲 terminal connectivity before and after?봭ot just the node?셲 presence. The Erdos Miller project describes itself as a general VI Scripting code-generation library, but its public README does not document that creator?셲 terminal requiredness. [Erdos Miller LV-Scripting repository](https://github.com/erdosmiller/lv-scripting)

**(c) Auto-indexing a refnum is legal.** A refnum is a LabVIEW data value, and a loop output tunnel can build an array from the value produced on each iteration. NI?셲 rule is data-type-general: an indexed output receives one element from every iteration. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

So an array of Text refnums is not intrinsically illegal. Possible problems are instead:

- the refnum?셲 exact class is incompatible with the downstream indicator type;
- the tunnel is not truly indexing;
- one side of the tunnel is undefined;
- the reference becomes invalid later at runtime.

The last item would be a runtime semantic problem, not a broken-arrow cause. In your described chain, `Node.Label` feeds `Text.Text` inside the same iteration, so the Text refnum apparently does not even cross the loop boundary. That makes ?쐒efnum auto-indexing broke compilation??an especially poor hypothesis unless your actual wiring differs from the description.

**(d) The practical route to the real list is the private `VI:Get Errors` method, using a known-good prebuilt Invoke Node?봭ot constructing it by guessing method metadata.** Community evidence confirms the method exists but is hidden/private, provides incomplete details in some cases, and can be exposed with private scripting INI tokens. [NI Community: Error list in VI scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/td-p/2263216/highlight/true), [NI Community: programmatically check broken-VI messages](https://forums.ni.com/t5/LabVIEW/how-to-programmatically-check-the-error-messages-of-a-broken-vi/td-p/3336258)

Recommended diagnostic tool design:

1. Obtain or recreate a tiny donor containing a functioning `VI:Get Errors` Invoke Node.
2. Copy that already-typed node into an Op VI.
3. Feed it the target VI reference.
4. Wire every returned field to indicators and read those through your existing ActiveX pipeline.
5. Initially leave `Call Dangerously?` false. Only test true if the normal call demonstrably omits the needed information; the private method is undocumented.
6. Force compilation immediately before querying, because Error List contents can be stale. NI documents forcing a recompile from the broken Run arrow when errors are absent. [NI: Troubleshooting LabVIEW Code Module Issues](https://www.ni.com/docs/en-AS/bundle/teststand/page/troubleshooting-labview-code-module-issues.html)

If attaching method ID `452` failed, do not yet conclude the method is unusable in LabVIEW 2026. Plausible alternatives are:

- `452` is not the full class-qualified method identifier expected by your `Set Method` mechanism;
- the Invoke Node was created for the wrong VI Server class;
- private/super-private visibility was unavailable when the node was configured;
- the method?셲 interface changed;
- your attachment operation silently declined.

The cheap fallback is GUI-assisted but still deterministic: open the target?셲 diagram and invoke **View ??Error List / Ctrl+L**, then capture the Error List. NI explicitly identifies that window as the authoritative source and says double-clicking an entry locates the offending object. [NI: LabVIEW Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)

My probability ranking is:

1. **Half-connected/undefined loop tunnel or wrong tunnel peer**
2. **Required reference input unwired on a newly built Property Node**
3. **Wrong diagram ownership despite correct visual position**
4. **Stale compiler state**
5. **Node 243 lost an existing required-input connection during deletion**
6. **Refnum auto-indexing** ??very unlikely

The single most valuable reporter now is not another count reporter. It is a terminal-level edge list for the For Loop, its tunnels, the three Property Nodes, and node 243, including owner UID and both endpoints of every connection.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
