# g5-l3-opus-medium-r1

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.9460  in 26 / out 6421 / cache-create 28580 / cache-read 500712  (132s, 24 turn(s))
- **date:** 2026-09-30 20:04:57
- **outcome:** ANSWERED (134s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, a program reads the Nodes[] property of a block diagram (Diagram / TopLevelDiagram class) to enumerate what is on it. Does that array include diagram constants, structure tunnels (for example loop tunnels or case selector tunnels) and shift registers? If some of them are missing, why, and how can a program enumerate them instead?

Search the web and cite the URL of every source you used.

## Answer

## Answer

**Short version:** No. `Nodes[]` returns only objects of the **Node** class. Diagram constants, tunnels and shift registers are not Nodes; they sit in separate class branches directly under GObject. NI's own one-line description ("Returns references to all the nodes in the diagram") never says this outright, so part of the conclusion below comes from the class hierarchy and a forum post rather than a direct NI statement.

### 1. What `Nodes[]` returns
`AbstractDiagram` is the parent of `Diagram` and `TopLevelDiagram`. Its `Nodes[]` property is documented only as "Returns references to all the nodes in the diagram." A sibling property, `All Objects[]`, "Provides an array of references to all the **top-level** objects in the block diagram." ([AbstractDiagram class](https://labviewwiki.org/wiki/AbstractDiagram_class), [Nodes() property](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property))

### 2. Why constants, tunnels and shift registers are left out
In the VI Server class hierarchy, these are siblings of `Node`, not children of it:
- **Constant** is a direct child of GObject (Generic → GObject → Constant). NumericConstant, StringConstant and the other typed constants inherit from it. ([Constant class](https://labviewwiki.org/wiki/Constant_class), [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy))
- **Tunnel** is a direct child of GObject. Its children are LoopTunnel, **LeftShiftRegister**, **RightShiftRegister**, ConditionalTunnel and RegionTunnel. So shift registers are Tunnels, not Nodes. ([Tunnel class](https://labviewwiki.org/wiki/Tunnel_class))
- **Terminal** is also a direct child of GObject. ([VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy))
- **Node** (Generic → GObject → Node) has children such as Function, SubVI, Structure, Global, Local and FeedbackNode. None of the classes above are among them. ([Node class](https://labviewwiki.org/wiki/Node_class))

An NI forum thread confirms that the distinction matters in practice. Asking Traverse for GObjects for class "Node" "will only give GObjects that are a 'Node' in the GObjects Class Hierarchy." VI Analyzer's Node Count, by contrast, also counts "Constant" and "ControlTerminal" objects. ([NI forum: Programmatic VI Metric: Node Count](https://forums.ni.com/t5/LabVIEW/Programmatic-VI-Metric-Node-Count/td-p/1042729))

One more thing: tunnels belong to the structure's border, not to a diagram's contents. The Tunnel class has `Outside Terminal` and `Inside Terminals[]`, with "one reference for each frame of the structure." ([Tunnel class](https://labviewwiki.org/wiki/Tunnel_class))

**Case selector:** I could not settle this one. The hierarchy page lists a `SelectorTunnel` class (Tunnel → ConditionalTunnel → SelectorTunnel), but none of the sources say whether that class is the Case structure's selector terminal. So I can't say from the evidence where the case selector sits. ([VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy))

### 3. How to enumerate them instead
- **Tunnels:** read the structure's `Structure.Tunnels[]` property ("Returns an array of references to the tunnels of the loop"). ([Structure class](https://labviewwiki.org/wiki/Structure_class))
- **Shift registers:** read `Loop.Shift Registers[]` ("Returns an array of references to the shift registers of the loop"). ([Loop Shift Registers() property](https://labviewwiki.org/wiki/Loop_class/Shift_Registers()_property))
- **Constants and anything else on one diagram level:** read `All Objects[]` and cast each reference with *To More Specific Class*. This does not look inside structures. For nested code, get each structure's subdiagrams through `Structure.Diagrams[]` and repeat. ([AbstractDiagram class](https://labviewwiki.org/wiki/AbstractDiagram_class), [Structure class](https://labviewwiki.org/wiki/Structure_class), [NI forum: get all diagram object references](https://forums.ni.com/t5/LabVIEW/LV-Scripting-how-to-get-all-diagram-object-references/td-p/2742296))
- **The whole diagram, recursively:** use `Traverse for GObjects.vi` (vi.lib\Utility\traverseref.llb) with a class name such as "Constant", "LoopTunnel" or "Tunnel". It handles the recursion into containers for you. Users recommend it for getting LoopTunnel references, followed by *To More Specific Class*. ([NI API ref: Traverse for GObjects](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html), [LabVIEW Artisan: The Power of Traverse](http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html), [NI forum: change tunnel mode](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392))

**Limits of this answer:** NI's own reference pages would not render when fetched, so the class and property descriptions come from the LabVIEW Wiki, which mirrors NI's property descriptions and class IDs. No source I found shows a direct test of `Nodes[]` on a diagram containing constants. The exclusion is inferred from the class hierarchy and the forum statement about the "Node" class.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
