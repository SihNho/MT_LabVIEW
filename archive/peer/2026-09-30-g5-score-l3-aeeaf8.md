# g5-score-l3-aeeaf8

- **agent:** claude
- **role:** fact
- **model:** sonnet (effort low; pinned by -Model/-Effort (role fact))
- **kind:** fact
- **cost:** $0.0443  in 2 / out 87 / cache-create 9616 / cache-read 24715  (4s, 1 turn(s))
- **date:** 2026-09-30 20:05:35
- **outcome:** ANSWERED (6s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

You are grading ONE answer to a technical question against a known, machine-verified answer.
Do NOT search the web and do NOT use any tool; grade only from the text below.

QUESTION:
In LabVIEW VI Scripting, a program reads the Nodes[] property of a block diagram (Diagram / TopLevelDiagram class) to enumerate what is on it. Does that array include diagram constants, structure tunnels (for example loop tunnels or case selector tunnels) and shift registers? If some of them are missing, why, and how can a program enumerate them instead?

KNOWN ANSWER (verified on the machine / vendor files):
No. Nodes[] returns only objects of the Node class. A diagram Constant is a GObject but not a Node, so it never appears; loop tunnels, case-selector tunnels and shift registers are not in Nodes[] either (they belong to their structure). To enumerate them use a GObject-level traversal, e.g. vi.lib's Traverse for GObjects.vi by class name (or the diagram's AllObjs[] / the structure's own tunnel and shift-register properties).
KEY POINTS: constants are NOT in Nodes[] (Constant is a GObject, not a Node); tunnels and shift registers are NOT in Nodes[]; use Traverse for GObjects / AllObjs[] / structure properties

ANSWER AEEAF8 TO GRADE:
<<<
Based on the VI Server class hierarchy: **constants, tunnels and shift registers are all left out of `Nodes[]`**, because none of them belongs to the Node class. Structures are included. I found no test or official note that states this directly, so it is an inference from the documented classes. I couldn't settle the case selector tunnel either way.

**Why they are missing**

- `Nodes[]` "Returns references to all the nodes in the diagram." [1] The page doesn't list what it leaves out.
- **Constants:** the Constant class sits directly under GObject (Generic → GObject → Constant), not under Node [2][3]. Node's child classes don't include Constant, Tunnel or ShiftRegister [4]. So constants shouldn't appear in `Nodes[]`. One exception is ControlReferenceConstant, which is a Node subclass [4].
- **Tunnels:** Tunnel is also a direct child of GObject (Generic → GObject → Tunnel) [3][5]. On the NI forum, cbutcher wrote that "The LoopTunnel class is not a 'Node' or 'Control'", and the original poster could only get the tunnel by traversing for GObjects [6].
- **Shift registers:** LeftShiftRegister and RightShiftRegister are subclasses of Tunnel (Generic → GObject → Tunnel → LeftShiftRegister) [5][7]. So they are missing for the same reason as tunnels.
- **Structures are included:** Loops and other structures are Nodes (Generic → GObject → Node → Structure → Loop) [8][9].
- **Case selector: unresolved.** The Tunnel subclasses listed are ConditionalTunnel, LeftShiftRegister, LoopTunnel, RegionTunnel and RightShiftRegister [5]. None of them is clearly the selector, and I found no source saying which class the case selector belongs to or how to get a reference to it. "CaseSel" is the class name of the Case Structure itself, not of its selector [10].

**How to enumerate them instead**

1. **Ask each structure.** `Structure.Tunnels[]` returns the structure's tunnels [9]. `Loop.Shift Registers[]` returns the loop's shift registers [8]. From a left shift register, the `Right Shift Register` property gives its pair [7]. From a tunnel, `Inside Terminals[]` and `Outside Terminal` give its terminals [5].
2. **Use `All Objects[]` instead of `Nodes[]`.** It returns "all the top-level objects in the block diagram" [3], which should include constants because they are GObjects. It doesn't look inside structures [11]. So you have to read each structure's `Diagrams[]` [9] and repeat the call on each one. Whether tunnels on a structure's border count as objects of the diagram that holds the structure is not documented.
3. **Use `Traverse for GObjects.vi`.** It searches a VI recursively for every object of a given class [12][13]. Passing the class name "GObject" returns all block-diagram objects (Darren and Ajay_MV on the NI forum) [14]. You can also call it once per class, for example "Constant", "Tunnel", "LoopTunnel" or "LeftShiftRegister". Then use To More Specific Class to get the specific properties [6].

**Caveats:** NI's own docs pages loaded only as navigation menus when I fetched them, so the class hierarchy comes from the LabVIEW Wiki copy of the class reference. The wiki's descriptions of `Nodes[]` [1] and `Tunnels[]` [9] are brief. The wiki doesn't say whether `Nodes[]` looks inside structures; its sibling properties `All Objects[]` and `SubVIs[]` are described as returning top-level objects only [3]. A quick test on a small VI would confirm all of this for your LabVIEW version.

**Sources**
1. https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property
2. https://labviewwiki.org/wiki/Constant_class
3. https://labviewwiki.org/wiki/GObject_class (and https://labviewwiki.org/wiki/AbstractDiagram_class for the `All Objects[]` and `SubVIs[]` descriptions)
4. https://labviewwiki.org/wiki/Node_class
5. https://labviewwiki.org/wiki/Tunnel_class
6. https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392
7. https://labviewwiki.org/wiki/LeftShiftRegister_class
8. https://labviewwiki.org/wiki/Loop_class
9. https://labviewwiki.org/wiki/Structure_class
10. https://forums.ni.com/t5/LabVIEW/using-vi-scripting-to-create-a-case-structure-switched-on/td-p/3739408
11. http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html
12. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html (found by search; its content didn't load)
13. https://forums.ni.com/t5/LabVIEW/LV-Scripting-how-to-get-all-diagram-object-references/td-p/2742296
14. https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133
>>>

Grade: correct = every key point right and nothing contradicting the known answer; partly = the main point right
but a key point missing or wrong; wrong = the main point wrong, or no usable answer.
Reply with exactly two lines:
GRADE: correct|partly|wrong
REASON: <one sentence>

## Answer

GRADE: correct
REASON: All key points match (constants/tunnels/shift registers excluded as non-Node GObjects, structures included, enumeration via Traverse for GObjects/AllObjs/structure properties) with nothing contradicting the known answer.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
