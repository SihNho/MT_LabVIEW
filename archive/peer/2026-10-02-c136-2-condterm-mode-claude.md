# c136-2-condterm-mode-claude

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **route:** fact chain step 2/2: FALLBACK - gemini step ended ERROR (incl. empty or content-empty answer / agy no output) (rc 4), archive\peer\2026-10-02-c136-2-condterm-mode-gemini.md
- **cost:** $0.4776  in 18 / out 3296 / cache-create 20437 / cache-read 290142  (78s, 14 turn(s))
- **date:** 2026-10-02 14:03:42
- **outcome:** ANSWERED (80s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API FACT question (LabVIEW 2026 VI Scripting / VI Server, no diagnosis):

A While Loop's conditional terminal can be in "Stop if True" or "Continue if True" mode. Which VI Scripting property READS that mode programmatically?

Known so far (measured here): WhileLoop class property "Loop End Ref" (data name LpEndRef, id 0x6362C00) returns a reference to the conditional terminal (a Terminal; Is Source? False). Terminal properties we use: UID 632A813, Is Source? 634A003, Connected Wire 634A000.

Please give, with a primary source (NI help page / ni.com KB / LabVIEW class browser documentation / vi.lib example) for each:
1. the exact property name as shown in the LabVIEW Class Browser, and its short (data) name;
2. which class it belongs to (WhileLoop itself, the loop-end terminal object's class, or another) and that class's name in the class hierarchy;
3. its type and value meaning (e.g. Boolean: TRUE = Continue if True), whether it is readable (and writable) through VI Scripting;
4. its numeric property id if any source lists it.
If no such property exists, say so and cite where you looked. Do not guess; mark any unsourced statement as unverified.



## Answer

The property you want is **WhileLoop › Stop If True?**. It is a property of the While Loop itself, not of the conditional terminal. My only source for its details is LabVIEW Wiki. I could not open the official ni.com page for it (details at the end).

**1. Name**
- Name in the Class Browser: **Stop If True?**
- Short (data) name: **StopIfTrue**
- Source: https://labviewwiki.org/wiki/WhileLoop_class/Stop_If_True%3F_property

**2. Class**
- It belongs to the **WhileLoop class** (class ID 16435). That is the same class as the "Loop End Ref" property you already use.
- Inheritance: Generic → GObject → Node → Structure → Loop → WhileLoop. TimedLoop is a child class of WhileLoop.
- The WhileLoop class lists three properties: Loop End Ref (6362C00, read only), Stop If True? (6362C01, read/write) and Iteration Terminal Hidden? (6362C02).
- No source I found shows a mode property on the Terminal object that Loop End Ref returns. That absence is unverified, because I did not search the Terminal class's property list.
- Source: https://labviewwiki.org/wiki/WhileLoop_class

**3. Type and meaning**
- Type: **Boolean**. Permissions: **Read/Write**. Scope: VI Scripting.
- Description: "Specifies whether the While Loop stops if you wire TRUE to the end terminal of the loop."
- So **TRUE = Stop if True** and **FALSE = Continue if True**. This is my reading of that description, and no source states it word for word.
- It cannot be set while the VI is running, and it is not available in the Run-Time Engine.
- The wiki gives the version as "LabVIEW 2018 or later" and adds "More info to come". Nothing I found confirms it for LabVIEW 2026 specifically.
- Source: https://labviewwiki.org/wiki/WhileLoop_class/Stop_If_True%3F_property

**4. Property ID**
- **0x6362C01**. It sits right after Loop End Ref (0x6362C00), which matches the id you measured.
- The For Loop has a separate property with the same name and data name, ForLoop › Stop If True? (ID 6362003, ForLoop class 16434), for its conditional terminal: https://labviewwiki.org/wiki/ForLoop_class/Stop_If_True%3F_property

**What isn't verified**
- **No primary NI source.** LabVIEW Wiki is a community wiki, not an NI page. The ni.com API reference loads its pages with JavaScript, so fetching them returned only the site navigation. I tried a guessed property page under `.../labview-api-ref/page/properties-and-methods/vi-server/...` and a guessed While Loop properties index next to the real [Loop Methods page](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop-m.html); both returned no content.
- **Checking it locally.** In LabVIEW's Class Browser, look under VI Scripting › WhileLoop for "Stop If True?". Or add a Property Node on a WhileLoop reference and read the property before and after switching the terminal's mode.

NI's general documentation on the two modes, not the scripting property itself: [Specifying Conditions for While Loops](https://www.ni.com/docs/en-AS/bundle/labview/page/specifying-conditions-for-while-loops.html), [While Loop (API reference)](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/structures/while-loop.html).

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
