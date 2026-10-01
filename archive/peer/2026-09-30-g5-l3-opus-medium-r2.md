# g5-l3-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.7026  in 22 / out 6367 / cache-create 23253 / cache-read 390624  (106s, 23 turn(s))
- **date:** 2026-09-30 20:04:36
- **outcome:** ANSWERED (108s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, a program reads the Nodes[] property of a block diagram (Diagram / TopLevelDiagram class) to enumerate what is on it. Does that array include diagram constants, structure tunnels (for example loop tunnels or case selector tunnels) and shift registers? If some of them are missing, why, and how can a program enumerate them instead?

Search the web and cite the URL of every source you used.

## Answer

**Answer: no, `Nodes[]` leaves all three out.** Diagram constants, tunnels (loop tunnels, case selector tunnels) and shift registers are not Node objects in the VI Server class hierarchy, and `Nodes[]` returns only Node objects. I found no NI page that states this directly. It follows from the class hierarchy, and an NI forum thread about tunnels confirms it.

**Why they are missing**
- `AbstractDiagram.Nodes[]` is documented only as "Returns references to all the nodes in the diagram." Nothing on that page says what is excluded. [labviewwiki: Nodes() property](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property)
- The Node branch of the hierarchy is `Generic → GObject → Node`. Its children include Function, SubVI, Structure, FeedbackNode and ControlReferenceConstant. Constant, Tunnel and Terminal are not among them. [labviewwiki: Node class](https://labviewwiki.org/wiki/Node_class)
- Constant, Tunnel, Terminal, Wire and Decoration are each separate direct children of GObject, alongside Node. [labviewwiki: GObject class](https://labviewwiki.org/wiki/GObject_class), [Constant class](https://labviewwiki.org/wiki/Constant_class), [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)
- The hierarchy table places LoopTunnel under Tunnel, and LeftShiftRegister and RightShiftRegister under Tunnel → LoopTunnel. So shift registers are tunnels, not nodes. Selector and conditional tunnels also appear as Tunnel classes in the table. Two caveats: the rows for the shift-register classes are a little garbled, and I could not confirm the exact parent of SelectorTunnel. [labviewwiki: VI Server Class Hierarchy Table](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy_Table)
- In an NI forum thread about tunnels, LoopTunnel is described as something that "is not a 'Node' or 'Control'". [NI forum: change tunnel mode via scripting](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392)
- A related limit: the diagram-level arrays cover only the top level. `All Objects[]` is documented as returning "all the top-level objects in the block diagram", and it does not recurse into structures. [labviewwiki: AbstractDiagram class](https://labviewwiki.org/wiki/AbstractDiagram_class), [LabVIEW Artisan scripting tip](http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html)

**How to enumerate them instead**
1. **Traverse for GObjects.vi:** pass a class name such as `GObject`, `Constant` or `LoopTunnel`. It returns matching objects throughout the diagram, including those inside structures. Then use To More Specific Class to get the exact type. [NI forum: reference all objects (traverse)](https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133), [NI forum: tunnel mode](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392), [NI docs: Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html) (the NI page did not load for me, so I could not read its text).
2. **Walk the structure properties yourself:**
   - `Structure.Tunnels[]` returns a structure's tunnels. [labviewwiki: Structure class](https://labviewwiki.org/wiki/Structure_class)
   - `Loop.Shift Registers[]` returns "an array of references to the shift registers of the loop." [labviewwiki: Loop Shift Registers() property](https://labviewwiki.org/wiki/Loop_class/Shift_Registers()_property)
   - `Structure.Diagrams[]` returns the subdiagrams. Recurse into each one to reach nested objects. [labviewwiki: Structure class](https://labviewwiki.org/wiki/Structure_class)
3. **Constants:** `All Objects[]` on each diagram or subdiagram should include them, because it returns all top-level objects and not just nodes. This is an inference from the wording; no source I found shows it explicitly. Traversing with class `Constant` is the documented alternative. [labviewwiki: AbstractDiagram class](https://labviewwiki.org/wiki/AbstractDiagram_class), [NI forum: reference all objects](https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133)

**What the evidence does not settle:** I found no official NI statement that `Nodes[]` excludes these objects. The conclusion rests on the class hierarchy, mostly from the community-maintained LabVIEW Wiki, plus that forum quote. A quick test on a sample VI would confirm it.

Sources:
- https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property
- https://labviewwiki.org/wiki/AbstractDiagram_class
- https://labviewwiki.org/wiki/Node_class
- https://labviewwiki.org/wiki/GObject_class
- https://labviewwiki.org/wiki/Constant_class
- https://labviewwiki.org/wiki/Tunnel_class
- https://labviewwiki.org/wiki/Terminal_class
- https://labviewwiki.org/wiki/Structure_class
- https://labviewwiki.org/wiki/Loop_class
- https://labviewwiki.org/wiki/Loop_class/Shift_Registers()_property
- https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy_Table
- https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392
- https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133
- http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html
- https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html (did not load)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
