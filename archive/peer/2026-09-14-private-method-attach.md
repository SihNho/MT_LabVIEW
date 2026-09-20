---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# private-method-attach

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (125s)
- **why asked:** See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
- **verdict:** see 'What was done with it' / STATUS.md 2026-09-14

## Question

ATTACK this conclusion, do not confirm it. LabVIEW 2026 VI Scripting via ActiveX. CLAIM I am about to record as a permanent fleet limitation: 'our scripted Invoke-node builder cannot attach PRIVATE or SUPER-PRIVATE VI Server methods; only the GUI can, by right-click Select Method.' EVIDENCE: our builder op wraps erdosmiller lv-scripting's Create Invoke Node and takes a class string plus a method Unique ID. It WORKS for public methods - VI method 'Block Diagram:Remove Bad Wires' (ID 410) builds and runs fine, Terminal.Create Indicator (6349C02) likewise. It FAILS identically on two private ones: VI 'Get Errors' (0x452) and Control.Value (633200D). The failure shape is the same both times and is NOT an error: the Invoke/Property node IS created, but the METHOD DOES NOT ATTACH - the node comes up carrying only its generic terminals ('reference', 'reference out', 'error in', 'error out') with NO method-specific terminals at all (for Get Errors we expect 'Errors' and 'Details'). ExecState then goes to 0 once a reference is wired. Reproduced 2026-09-09 and again 2026-09-14, byte-identical output. The INI tokens SuperPrivateScriptingFeatureVisible, SuperPrivateSpecialStuff and SuperSecretPrivateSpecialStuff are all already True in this LabVIEW installation and LabVIEW has been restarted since. FIND WHY THIS CONCLUSION MIGHT BE WRONG: (a) is there a documented scripting-visible property or method that must be set on the Invoke node itself before the method name/ID takes - e.g. does one have to write 'Invoke Node Class Name' (6370402) FIRST and only then the method, and is ORDER significant? (b) does the method need a NAME string rather than a numeric ID, or a differently-formatted ID (decimal vs hex, with or without 0x)? (c) do private methods require the target VI reference to be opened with a specific option/access level (e.g. an app-instance or 'dangerous' flag) rather than a plain GetVIReference? (d) is there a scripted route that does NOT go through Create Invoke Node - for instance copying a typed node from a donor VI programmatically, or creating it with New VI Object and a style ring? (e) is 'Call Dangerously?' relevant to Get Errors specifically? Cite NI forums, labviewwiki, or the erdosmiller source. Note: I do NOT want a GUI answer; I want to know whether the SCRIPTED route is genuinely closed, because the project's rule is that GUI is permitted only where scripting is VERIFIED unreachable.

## Answer

Do not record that limitation. The evidence points to a missing private-node configuration call in the builder, not to a GUI-only boundary.

The decisive counterexample is that LabVIEW exposes separate scripting APIs specifically for attaching private members:

- Invoke nodes: `Set Method (Allow Private)`, method ID `6370003`.
- Property nodes: `Set Properties[] (Allow Private)`, method ID `636F406`.
- Individual property rows: `Set Property (Allow Private)`, method ID `6DE8D802`.

These are programmatic VI Server methods?봭ot GUI commands. [LabVIEW Wiki: Invoke class](https://labviewwiki.org/wiki/Invoke_class), [Property class](https://labviewwiki.org/wiki/Property_class), [Set Properties (Allow Private)](https://labviewwiki.org/wiki/Property_class/Set_Properties%28%29_%28Allow_Private%29_method), [Set Property (Allow Private)](https://www.labviewwiki.org/wiki/PropertyItem_class/Set_Property_%28Allow_Private%29_method).

Your failure signature is exactly compatible with calling ordinary `Set Method` (`6370002`) or ordinary property setters on a private member: object creation succeeds, but member selection is rejected or ignored, leaving the generic unconfigured node. Erdos Miller?셲 library being successful for public members does not establish that it invokes the `Allow Private` variants; its stated scope is a general VI Scripting code-generation wrapper. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting).

Answers to the proposed escape routes:

**(a) Class first, then member?**  
Yes?봳reat that order as required until disproved. `Invoke Node Class Name` (`6370402`) determines the node class, while `All Supported Methods` reports methods for the *current class*. Therefore the safe sequence is:

1. Create the generic node.
2. Set `Invoke Node Class Name`.
3. Invoke `Set Method (Allow Private)` on the node.
4. Read back `Method`, `Flags:Is Private`, and the terminal arrays.

The same logic applies to `Property Node Class Name` before `Set Properties[] (Allow Private)`. The sources do not explicitly document an order guarantee, so ?쐎rder is mandatory??remains an inference, but setting the member before its class is plainly an invalid test of the intended API. [Invoke class](https://labviewwiki.org/wiki/Invoke_class), [Property class](https://labviewwiki.org/wiki/Property_class).

**(b) ID representation/name?**  
The setter input is an **ID String**, not a numeric method ID. With `Allow Alternate Names? = FALSE`, it expects the Unique ID string returned by `All Supported Methods`; with that Boolean true, it can also match the data name, short name, or localized long name. [Set Method documentation](https://labviewwiki.org/wiki/Invoke_class/Set_Method_method).

Consequently, do not pass numeric `0x452`. Query `All Supported Methods` after selecting class `VI` and feed its returned Unique ID string back verbatim. The published table represents Get Errors as `452`, not `0x452`; likewise IDs such as `633200D` are hexadecimal-looking strings without a prefix. [VI class](https://labviewwiki.org/wiki/VI_class), [Control-class table](https://labviewwiki.org/wiki/Template%3AVIServerClassTables).

A second cheap test is `ID String = "Get Errors"` plus `Allow Alternate Names? = TRUE`. For the property case, use `"Value"` with the private property setter and alternate-name matching enabled. That separates ID-format failure from access filtering.

**(c) Special target-VI reference options?**  
I found no evidence that configuring a private Invoke/Property node requires opening the target VI using a dangerous/access-level option. The documented private bypass belongs to the *node?셲 setter* itself. Open-VI-reference option bits are documented for execution behavior such as preparing reentrant VIs, not for granting diagram-edit access to private VI Server members. [Run VI method](https://labviewwiki.org/wiki/VI_class/Run_VI_method).

Also distinguish three references: the VI containing the diagram being edited, the newly created node reference, and the eventual runtime reference wired into that node. Access filtering during `Set Method` concerns the node reference; changing how the eventual runtime VI reference is opened cannot create missing method-specific terminals.

**(d) Donor-node copying?**  
Yes, there is evidence for a fully scripted fallback. A reported VI Scripting solution uses VI `Create from Reference` to create a ?쐏erfect copy??of an existing object in another VI. [NI Community: Create from Reference](https://forums.ni.com/t5/LabVIEW/Using-scripting-to-copy-a-cluster-from-one-vi-to-another/m-p/1087774).

More specifically, an NI thread about `Get Errors` reports that the method was absent from the menu but ?쏧f I copy it, it works fine.??That proves a configured Get Errors node can survive programmatic/diagram copying; it undermines any claim that only interactive right-click selection can produce or transfer the node. [NI Community: Error list in VI scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/m-p/2268238).

Thus a donor VI plus `Create from Reference` is a credible scripted route even if LabVIEW 2026 has broken the private setter.

**(e) `Call Dangerously?`?**  
It is a parameter of the configured `Get Errors` call, so it affects execution of that method after attachment. It cannot explain why `Errors`, `Details`, and `Call Dangerously?` terminals never materialize?봳he method has not been attached yet. The historical thread shows a working Get Errors node with that optional input and separately discusses enabling private visibility. [NI Community: programmatically checking errors](https://forums.ni.com/t5/LabVIEW/how-to-programmatically-check-the-error-messages-of-a-broken-vi/m-p/3336655), [NI Community: Error list](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/m-p/2269168).

The cheapest decisive experiment for the manager is therefore:

1. Set class `VI`.
2. Read `All Supported Methods`; preserve the exact Get Errors ID string.
3. Call `Set Method (Allow Private)` (`6370003`), not `Set Method`.
4. Use the returned exact string, then retry with `"Get Errors"` and alternate names enabled.
5. Read back `Method`, `Flags:Is Private`, and terminal names.
6. Independently clone a known-good Get Errors node using `Create from Reference`.

For `Control.Value`, repeat with `Property Node Class Name` followed by `Set Properties[] (Allow Private)` or `PropertyItem.Set Property (Allow Private)`.

A defensible permanent statement today would be: **?쏷he current Erdos Miller-based builder path does not attach private members because it has not yet been shown to use LabVIEW?셲 explicit Allow Private setters with exact ID strings and correct class-first ordering.??* The stronger ?쐎nly the GUI can??conclusion is contradicted by the exposed scripting APIs and the scripted donor-copy route.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
