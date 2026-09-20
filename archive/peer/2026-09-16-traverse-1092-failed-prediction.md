# traverse-1092-failed-prediction

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (112s)
- **why asked:** a FAILED PREDICTION — `report_all(MAIN, "PropertyNode")` raised error 1092 where I predicted a
  list of property nodes (`tools/bench/diag_autofocus_border.log`). Dispatched to attack my explanation before it
  drove a recipe fix. **Outcome: H1 (wrong class-name string) survived the attack**; codex supplied the VI Server
  hierarchy showing `Property` (ID 16419) and no `PropertyNode` anywhere in it, and correctly noted that 1092
  literally means "Invalid Class Operator VI", so the code alone does not prove a bad name. My own 2×2 grid
  (`diag_autofocus_panel.log`) then separated name from VI empirically. Follow-up exchange with the grid result:
  `2026-09-16-traverse-1092-grid-result.md`.
- **verdict:** unverified

## Question

FAILED PREDICTION, LabVIEW 2026 VI Scripting through ActiveX/COM. I predicted that a traverse-based reporter would return the PropertyNode objects of a large VI; it raised error 1092 instead, and I want my explanation attacked before it drives any build.

OBSERVATION. Our op VI OpReportAll_v0 wraps 'VI Scripting - Traverse.lvlib:Traverse for GObjects.vi' with a class-name string control. Called with class name 'PropertyNode' on a large top-level VI (626 nodes, 170 diagrams, ~5000 wires) it raised: 'error 1092: Invoke Node in TRef Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReportAll_v0.vi'. The same op with other class names ('Node', 'Wire', 'CaseStructure', 'ControlTerminal') has worked on this same VI for weeks.

MY LEADING EXPLANATION (H1), which I want refuted: the class name is wrong. In the same run, a different op that casts an object reference and reads its class reported the owner class of the property node uid 30146 as 'Property', not 'PropertyNode' - so I think the traverse wants 'Property' and rejects 'PropertyNode' with 1092.

ALTERNATIVE (H2): the class name is fine and the failure belongs to this VI or to a particular object inside it - a property node whose reference class cannot be resolved, a locked or password-protected subVI diagram, or a size limit in the traverse.

ALREADY RULED OUT: (a) not a stale reference - the same op run succeeded on other classes seconds earlier in the same LabVIEW session; (b) not the VI being dirty or modified - its md5 was identical before and after; (c) not a timeout - the error returned in under a second.

WHAT I AM ACTUALLY AFTER, and the second question: I want the front-panel control that an IMPLICIT property node (its 'reference' terminal unwired) is linked to. Is there a scripting property that exposes that link - and if so what is it called and on which class does it live? If there is no such property in LabVIEW 2026, say so and name the route people actually use.

Please give: what error 1092 means in LabVIEW scripting; the exact legal class-name strings for a property node in a traverse; the strongest reason H1 is wrong; and the cheapest experiment that separates H1 from H2.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason to doubt H1 is that error 1092 does **not** literally mean ?쐇nvalid class-name string.??It means **?쏧nvalid Class Operator VI.??* `Traverse for GObjects` ultimately invokes the VI Server `Class Operator:Traverse` mechanism, so 1092 can also mean that the selected traversal operator is missing, unregistered, malformed, or incompatible?봭ot necessarily that an encountered GObject is corrupt. [LabVIEW error table](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family), [Class Operator:Traverse documentation](https://labviewwiki.org/wiki/Generic_class/Class_Operator.Traverse_method)

That attack does not survive the class-hierarchy evidence, however.

1. Exact class name

The most-specific VI Server class of a property node is:

```text
Property
```

It is class ID `16419`, under:

```text
GObject
  Node
    Function
      GrowableFunction
        ObjectFunction
          Property
```

Consequently, these ancestor strings can also select a property node as part of a broader traversal:

```text
GObject
Node
Function
GrowableFunction
ObjectFunction
Property
```

`PropertyNode` is not present in the published VI Server hierarchy. The traverse input requires the VI Server class name, specifically the unlocalized class name?봭ot the palette/object?셲 descriptive English name. [VI Server hierarchy showing `Property`](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [Traverse input definition](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html)

The reported `ClassName = "Property"` result therefore agrees with the hierarchy; it is not merely an odd owner-class label.

2. Alternative explanation

The credible alternative is a class-operator registration or compatibility failure: `PropertyNode` might conceivably be a recognized alias whose corresponding traversal operator is unavailable or malformed in that LabVIEW installation. Error 1092 permits that interpretation because it identifies an invalid operator VI rather than explicitly saying ?쐕nknown class.??[Application class operator registration methods](https://labviewwiki.org/wiki/Application_class), [error 1092 definition](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family)

The proposed object-specific H2 explanations are much weaker:

- A locked VI and a password-protected VI have their own errors, 1044 and 1040 respectively?봭ot 1092. [LabVIEW error table](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family)
- Traversing a top-level VI walks that VI?셲 GObject/container hierarchy; a SubVI node does not imply opening and traversing the called VI?셲 separate block diagram. [Traverse for GObjects details](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html)
- Failure during immediate traverse initialization fits operator lookup better than a limit reached after examining thousands of wires. This last point is an inference from the reported timing and call chain, not a documented guarantee.

3. Observation that would falsify H1

H1 would be falsified if either:

- `PropertyNode` appears in LabVIEW 2026?셲 `ClassSpecifierConstant.AllTypes[]` output as an unlocalized VI Server class name; that property is the programmatic source of the legal class names, [VI Server hierarchy?봯rogrammatic access](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy); or
- `Traverse for GObjects` with `PropertyNode` succeeds on a minimal VI containing one ordinary property node in the same LabVIEW process.

Absent either result, the published hierarchy says `PropertyNode` is simply the wrong string.

4. Implicitly linked control

Yes?봳here is a direct scripting property:

```text
Owning class: Property
Long name:    Linked Control
Data name:    LinkedControl
Type:         Control reference
Access:       Read-only
```

It returns the front-panel control referenced by an implicitly linked property node. If the property node has no static link?봲uch as an explicitly referenced node?봧t returns a null reference and an error. [Property.Linked Control reference](https://labviewwiki.org/wiki/Property_class/Linked_Control_property)

NI material independently confirms the API name `LinkedControl` and recommends reading it separately before reading something like `LinkedControl.ClassName`, because `LinkedControl` can error when no link exists. [NI LabVIEW known issue and workaround](https://www.ni.com/en/support/documentation/bugs/18/labview-2018-known-issues.html)

Verdict: after attacking it, H1 still holds and is substantially better supported than H2. What would change my mind is `PropertyNode` appearing in LabVIEW 2026?셲 `AllTypes[]`, or succeeding on a one-node control case.

The cheapest discriminating test is therefore: use the same reporter, session, and large target but change only the input from `PropertyNode` to `Property`. Success immediately separates H1 from the proposed target/object/size explanations; if `Property` also produces 1092, repeat those two strings on the smallest already-available VI containing one property node to distinguish target-specific failure from a broken class-operator installation.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
