# g5-g1-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.3596  in 14 / out 2715 / cache-create 15881 / cache-read 212256  (61s, 11 turn(s))
- **date:** 2026-09-30 19:55:33
- **outcome:** ANSWERED (64s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting (VI Server), which property of a Wire object reports whether that wire is broken, and what is that property's unique ID string (the hex ID used when the property is set with Allow Alternate Names = FALSE)? Also say what kinds of wire problems that property does and does not flag.

Search the web and cite the URL of every source you used.

## Answer

**Property:** The Wire class property is **Is Broken?** (short name **Broken?**). It is a read-only Boolean in the VI Scripting scope. It isn't available in the Run-Time Engine or on RT, and it isn't settable while the VI runs. The LabVIEW Wiki lists it as present as of LabVIEW 2018. — https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property

**Unique ID:** **6371004**. The Wire class list numbers its properties 6371000 through 637100E, including IDs like 637100A. That means these are hex strings, so the ID is the hex string "6371004". It is not a decimal number. The owning Wire class ID is 16439. — https://labviewwiki.org/wiki/Wire_class and https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property

I only found this on the community-run LabVIEW Wiki. I couldn't load NI's own Wire properties page (the fetch returned a navigation-only page), so NI's documentation didn't confirm the ID.

**What it does and does not flag: the evidence doesn't settle this.** The only description I found is one sentence: it "Returns TRUE if the wire is broken or in a bad state." The wiki's history note says "More info to come." — https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property

I found no source that lists which conditions set it to TRUE, and none that lists broken-diagram errors it misses. Examples of errors whose coverage I couldn't confirm either way:
- type conflicts
- wires with no source or with multiple sources
- loose ends
- class conflicts
- errors on nodes or VIs rather than on wires

NI's general material on why wires break (for example, incompatible data types) doesn't mention this property, so I can't tie it to any specific error:
- https://www.ni.com/docs/en-US/bundle/labview-nxg-g-programming-api-overview/page/troubleshooting-broken-wires.html
- https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019XS0SAM&l=en-US

To find the real coverage you would have to test it in LabVIEW, which I haven't done.

Sources:
- [Wire class/Is Broken? property – LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property)
- [Wire class – LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class)
- [Troubleshooting Broken Wires – NI](https://www.ni.com/docs/en-US/bundle/labview-nxg-g-programming-api-overview/page/troubleshooting-broken-wires.html)
- [Wire Class Conflict and Broken Wires in LabVIEW – NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019XS0SAM&l=en-US)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
