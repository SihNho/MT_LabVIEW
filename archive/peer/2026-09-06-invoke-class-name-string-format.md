---
type: peer-review
status: historical
date: 2026-09-06
tags: [peer-review]
---

# invoke-class-name-string-format

- **agent:** codex
- **date:** 2026-09-06
- **outcome:** ANSWERED (49s)
- **why asked:** OpBuildInvoke_v0 created App-class nodes with no method although Class Name and ID String were wired; needed the exact string formats.
- **verdict:** accepted (consistent with the creator's diagram: Class Name -> Method Class Name verbatim; Set Method with AllowAlternateNames=F): use 'VI Server:<Class>' and Unique-ID method strings (6349C02/6349C03 known). Not yet machine-verified in the op (control conflict to fix first).

## Question

LabVIEW VI Scripting fact question (LabVIEW 2026). The erdosmiller LV-Scripting Create Invoke Node.vi (installed under vi.lib\Erdos Miller\LV-Scripting in the project machine; you can read its exported strings if useful) creates an Invoke Node with New VI Object, then in a case selected by its Class Name string input writes the Invoke class property named MethClassName (i.e. Invoke.Method Class Name), then calls Invoke.Set Method (IDString, AllowAlternateNames=F). We passed Class Name="Diagram" and ID String="Connect Wire" and got an Application-class node with no method. Question 1: what EXACT string does the writable property "Method Class Name" (Invoke node) / "Property Node Class Name" (Property node) expect? Give the documented format and concrete examples for the classes Diagram, VI, Control, Terminal, Generic, GObject (e.g. "VI Server:Generic:GObject:Diagram"?). Cite NI docs or labviewwiki pages. Question 2: for Set Method, is the method ID string the display name ("Connect Wire") or an internal ID (e.g. "ConnectWire"), and does AllowAlternateNames=T accept display names? Cite. Question 3: is there a way to READ the list of valid class-name strings from LabVIEW (e.g. Application property "VI Server Classes" or Invoke.All Supported Methods) that our reporter could call? Answer compactly with sources.

## Answer

1. The class string format is:

`<server class>:<node class>`

For ordinary VI Server nodes, use exactly:

- `VI Server:Diagram`
- `VI Server:VI`
- `VI Server:Control`
- `VI Server:Terminal`
- `VI Server:Generic`
- `VI Server:GObject`

Do **not** encode the inheritance path; therefore, not `VI Server:Generic:GObject:Diagram`. The documentation explicitly gives `VI Server:Generic` as its example. The same format applies to both `MethClassName` and `PropClassName`. [Invoke Node Class Name](https://labviewwiki.org/wiki/Invoke_class/Invoke_Node_Class_Name_property), [Property Node Class Name](https://labviewwiki.org/wiki/Property_class/Property_Node_Class_Name_property)

Your call failed for an additional reason: **Connect Wire belongs to Terminal, not Diagram**. Its owning class is Terminal and its method ID is `6349C03`. Thus the relevant class is `VI Server:Terminal`. [Terminal.Connect Wire](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

2. With `Allow Alternate Names? = FALSE`, `Set Method` expects the method?셲 **Unique ID string**, not its display name. For Terminal.Connect Wire, that is:

`6349C03`

With `Allow Alternate Names? = TRUE`, LabVIEW may match any of:

- Unique ID string
- Data name
- Localized short name
- Localized long name

Consequently, `"Connect Wire"` should work with `TRUE`, provided the node class is `VI Server:Terminal`. `"ConnectWire"` is not documented as this method?셲 ID or data name. [Set Method documentation](https://labviewwiki.org/wiki/Invoke_class/Set_Method_method), [Terminal.Connect Wire metadata](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

3. Yes. The reporter can discover both classes and methods:

- Create or locate a **Class Specifier Constant**, then read `All Types[]`. It returns every VI Server class with Unique ID, Parent ID, unlocalized name, and localized name. This is the best programmatic class inventory; I found no documented Application property named `VI Server Classes`. [All Types[]](https://labviewwiki.org/wiki/ClassSpecifierConstant_class/All_Types%28%29_property), [programmatic class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)
- After setting an Invoke Node?셲 class, read `Invoke.All Supported Methods`. It returns each supported/inherited method?셲 Unique ID, data name, localized short name, and localized long name. [All Supported Methods](https://labviewwiki.org/wiki/Invoke_class/All_Supported_Methods_property)

Therefore the immediate correction is:

`Class Name = "VI Server:Terminal"`  
`ID String = "6349C03", AllowAlternateNames = FALSE`

or:

`Class Name = "VI Server:Terminal"`  
`ID String = "Connect Wire", AllowAlternateNames = TRUE`

## Sources

(extract from answer)

## What was done with it

recorded in docs/NAMES.md and docs/keystone-op-spec.md §13 (plan v5).
