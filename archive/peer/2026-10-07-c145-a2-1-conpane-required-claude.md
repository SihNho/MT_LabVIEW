# c145-a2-1-conpane-required-claude

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **route:** fact chain step 2/2: FALLBACK - gemini step ended ERROR (incl. empty or content-empty answer / agy no output) (rc 4), archive\peer\2026-10-07-c145-a2-1-conpane-required-gemini.md
- **cost:** $0.7647  in 20 / out 4672 / cache-create 27615 / cache-read 362510  (103s, 21 turn(s))
- **date:** 2026-10-07 22:30:13
- **outcome:** ANSWERED (105s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 (also valid for 2019+) VI Server / VI Scripting API fact question. No opinion wanted, only the exact API names with a primary source (ni.com docs, labviewwiki.org class pages, or NI forum posts quoting the property/method help).

Question: Given a VI reference to a subVI file (e.g. Open VI Reference on RingPickSlot_v0.vi), how do I READ, for each connector-pane terminal, its usage setting Required / Recommended / Optional ("This Connection Is" in the editor)?

Please give, for each route that exists:
1. The exact class and property/method name (e.g. on the ConnectorPane class reached by VI property "Connector Pane:Reference" (ID 23E), whose known members are Controls[] (239A8403), Number of Connection Terminals (239A8401), Pattern (239A8400), method Assign Control To Terminal (239A8000)). Is there a ConnectorPane member that returns terminal requirement / "Required" / "Recommended" (e.g. something like "Get Terminal Requirement", "Terminal Requirements", "Set Terminal Requirement" / "Get Terminal Settings")? Its inputs, outputs, the enum values (which integer = Required/Recommended/Optional/Dynamic), and the LabVIEW version that introduced it.
2. Alternatively, on a SubVI node placed on a block diagram (class SubVI / Node, Terminals[] -> Terminal class): is there a Terminal property that says the terminal is Required (e.g. "Required", "Is Required?", "Terminal Requirement")?
3. Alternatively, a VI class method such as "Get Conpane Terminal info" or similar scripting method names.
If none exists in public VI Server, say so explicitly and name the nearest documented workaround (e.g. Context Help bold labels, a private method, or reading it from the .vi file binary - which resource holds it).



## Answer

Yes, this exists in public VI Scripting, on the ConnectorPane class. Everything below comes from labviewwiki.org class pages. I found no ni.com help page for these members; NI's own scripting how-to only says scripting can set whether a terminal is required, optional or recommended ([rajsite mirror of NI help](https://rajsite.github.io/unofficial-lvdocs/lvhowto/scripting_configuring_connector_panes.html)).

## Route 1: ConnectorPane class (from VI property "Connector Pane:Reference")

The [ConnectorPane class page](https://labviewwiki.org/wiki/ConnectorPane_class) lists two ways to read the setting, alongside the members you already know.

**a) Property `WiringRules[]`, ID 239A8405** ([page](https://labviewwiki.org/wiki/ConnectorPane_class/WiringRules()_property))
- Returns one value per connector-pane terminal: "an array of the wiring rules for each terminal on a connector pane."
- Type: Enum U16 array. Read/Write. Not available in the Run-Time Engine.
- Loads the front panel into memory, not the block diagram. Can't be written while the VI is running.
- Enum values:

| Integer | Meaning |
|---|---|
| 0 | Invalid Wire Rule |
| 1 | Required |
| 2 | Recommended |
| 3 | Optional |
| 4 | Dynamic Dispatch |

**b) Method `Wiring Rule:Get`, ID 239A8007, data name `GetWiringRule`** ([page](https://labviewwiki.org/wiki/ConnectorPane_class/Wiring_Rule.Get_method))
- Input: `Terminal Index` (U32, required). The wiki's description of this input is copied from Assign Control To Terminal.
- Output: Enum U16 return value with the same five values as above.
- Not available in the Run-Time Engine. Loads the front panel.

**Setter for reference: `Wiring Rule:Set`, ID 239A8001, data name `SetWireRule`** ([page](https://labviewwiki.org/wiki/ConnectorPane_class/Wiring_Rule.Set_method))
- Inputs: `Terminal Index` (U32) and `Rule` (Enum U16). No return value.

An NI forum answer confirms the property's purpose: "you can use the Wiring Rules property so make inputs required\optional\dynamic dispatch" ([NI forum](https://forums.ni.com/t5/LabVIEW/Scripting-Set-connector-pane-error-1-if-source-terminals-are/td-p/3685361)).

**Version: not settled.** The wiki pages say "LabVIEW 2018" with the history section marked "More info to come." That reads as the first version the wiki documented, not necessarily when NI added the members. I found no source giving the real introduction version. It is at least 2018, so it covers your 2019+ requirement.

**Index order: inferred, not confirmed.** I found no source saying that `WiringRules[]` uses the same terminal order as `Controls[]` and `Terminal Index`. Scripting terminal order is documented as right to left, bottom to top ([labviewwiki Connector pane](https://labviewwiki.org/wiki/Connector_pane)). I'd check the alignment once against a VI whose settings you know.

**Lifetime caveat:** closing the VI reference also invalidates the ConnectorPane reference, so read the property before closing the VI ref ([NI forum, paul_cardinale](https://forums.ni.com/t5/LabVIEW/Script-to-Change-All-Input-Terminals-in-a-Project-to-Required/td-p/4078696)).

## Route 2: Terminal class on a placed SubVI node

**No such property exists.** The [Terminal class page](https://labviewwiki.org/wiki/Terminal_class) lists only these properties: Connected Wire, Type Descriptor, Diagram, Is Source?, Name, Caption, Coercion Dot?, Type Descriptor (Full), Data Type, Is Hidden?, Has Buffer Allocation. None of them is a Required/Recommended/Optional setting. To use a placed node, get the subVI's VI reference and apply Route 1.

## Route 3: a VI class method like "Get Conpane Terminal info"

**Not found.** I searched for a VI-class method with that kind of name and found nothing documented. Route 1 makes it unnecessary, so there's no need for a private-method or .vi-binary workaround. I did not research which resource inside the .vi file stores the setting.

## Sources

(extract from answer)

## What was done with it

Card 145-a2-1 (material). Taken as the API to read requiredness: `ConnectorPane.WiringRules[]` 239A8405 (U16 enum array: 1 Required,
2 Recommended, 3 Optional, 4 Dynamic Dispatch) or `Wiring Rule:Get` 239A8007 (`Terminal Index` -> enum). NOT yet measured: the fleet has no
op VI carrying either member (grep `WiringRule|239A8405|239A8007` over tools/docs = 0 hits), and the card forbids saving any VI outside the
adopt path, so no reader was built. The read is left to judgement (tools/bench/diag_c145_a2_1_facts.md). Index alignment with Controls[] is
the peer's inference, to be checked once on a VI with a known setting before any number is trusted.
