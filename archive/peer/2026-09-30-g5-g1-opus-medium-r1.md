# g5-g1-opus-medium-r1

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.3687  in 16 / out 3181 / cache-create 16725 / cache-read 241557  (70s, 11 turn(s))
- **date:** 2026-09-30 19:55:41
- **outcome:** ANSWERED (72s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting (VI Server), which property of a Wire object reports whether that wire is broken, and what is that property's unique ID string (the hex ID used when the property is set with Allow Alternate Names = FALSE)? Also say what kinds of wire problems that property does and does not flag.

Search the web and cite the URL of every source you used.

## Answer

The property is **Wire › Is Broken?** (short name **Broken?**), and its ID is **6371004**. I'm fairly confident that ID is hex, but it comes from a community wiki, not NI's own documentation. I found no source that says which wire problems the property does or doesn't flag.

**1. The property**
- It belongs to the Wire class (class ID 16439) and is part of VI Scripting. It is a read-only Boolean.
- Its description is: *"Returns TRUE if the wire is broken or in a bad state."*
- It isn't available on Real-Time or in the Run-Time Engine. Remote access is allowed.
- Source: https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property (the page's raw wikitext gives `propertyid = 6371004`: https://labviewwiki.org/w/index.php?title=Wire_class/Is_Broken%3F_property&action=raw)

**2. The ID: 6371004 (probably `0x6371004`)**
- I couldn't find this ID on any NI page.
- The wiki's ID field is hex. Another page on the same wiki lists the ID `636F80E`, which contains hex letters: https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property
- The wiki's page template shows the ID as written, with no conversion: https://labviewwiki.org/w/index.php?title=Template:VIServerProperty&action=raw
- If you read 6371004 as decimal it would be 0x6136BC, which doesn't match the wiki's hex format. That makes `0x6371004` the likely reading, but this is an inference.
- I also found nothing that describes "Allow Alternate Names" or ties it to this ID. The only official-looking statement is that the Unique ID string "is consistent across all versions and locales of LabVIEW" (same All Supported Properties page above).
- To confirm the ID, you could read the Property class's All Supported Properties list for a Wire reference in your own LabVIEW install.

**3. What it flags and doesn't flag: not settled**
- The only description I found is "broken or in a bad state." The wiki doesn't list which conditions set it, such as type mismatch, loose ends, multiple sources, no source, or broken wire branches.
- Forum threads cover broken wires in general. For example, Ctrl+B removes loose ends and wires broken by type mismatches together: https://forums.ni.com/t5/LabVIEW-Idea-Exchange/broken-wires-hotkey-to-remove-only-broken-wires-with-no/idi-p/951765
- None of them say whether `Is Broken?` returns TRUE for each of those cases, so I can't say which problems it catches. You would need to test it: script VIs with each wire problem and read the property.

Sources:
- [Wire class/Is Broken? property – LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property)
- [Raw wikitext of that page](https://labviewwiki.org/w/index.php?title=Wire_class/Is_Broken%3F_property&action=raw)
- [Template:VIServerProperty](https://labviewwiki.org/w/index.php?title=Template:VIServerProperty&action=raw)
- [Property class/All Supported Properties – LabVIEW Wiki](https://labviewwiki.org/wiki/Property_class/All_Supported_Properties_property)
- [NI Forums – Access any property by name](https://forums.ni.com/t5/LabVIEW/Access-any-property-of-any-class-BY-NAME/td-p/3994503)
- [NI Idea Exchange – remove only broken wires](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/broken-wires-hotkey-to-remove-only-broken-wires-with-no/idi-p/951765)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
