# g5-score-l4-faebf6

- **agent:** claude
- **role:** fact
- **model:** sonnet (effort low; pinned by -Model/-Effort (role fact))
- **kind:** fact
- **cost:** $0.0399  in 2 / out 58 / cache-create 8592 / cache-read 24715  (3s, 1 turn(s))
- **date:** 2026-09-30 20:15:59
- **outcome:** ANSWERED (5s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

You are grading ONE answer to a technical question against a known, machine-verified answer.
Do NOT search the web and do NOT use any tool; grade only from the text below.

QUESTION:
In LabVIEW VI Scripting, a program enumerates the objects on a block diagram and reads each object's class name (for example with Traverse for GObjects.vi or the ClassName property of a GObject reference). What class name does a VISA Write function node report, is there a VISA-specific scripting class for it, and how would a program pick out only the VISA Write nodes?

KNOWN ANSWER (verified on the machine / vendor files):
It reports the generic class 'Function' - the same class as Add, Multiply or Divide; there is no VISA-specific scripting class. VISA Write nodes are singled out by their name/label text ('VISA Write'), not by class.
KEY POINTS: class = Function (generic); no VISA-specific class; identify by name/label 'VISA Write'

ANSWER FAEBF6 TO GRADE:
<<<
I have completed the web research regarding the LabVIEW VI Scripting class name for the "VISA Write" node. Here are the answers to your questions based on the documentation and community forums (NI and LAVAG):

1. **What class name does a VISA Write function node report?**
   In LabVIEW VI Scripting, a "VISA Write" function is a built-in primitive node. When queried for its class name (e.g., via the `ClassName` property of a VI Server reference), it does not report a special VISA-related class name. Instead, it belongs to the standard LabVIEW object hierarchy and reports its class as **`Function`** (which inherits from the `Generic » GObject » Node » Function` hierarchy).

2. **Is there a VISA-specific scripting class for it?**
   **No**, there is no VISA-specific scripting class (such as `VisaWriteNode` or `VisaNode`). The scripting engine treats "VISA Write" as a generic primitive function node. Note that the term "class" in the context of VISA usually refers to the **VISA Resource Class** (e.g., `Instr` or `Serial Instr`), which dictates hardware interface compatibility, not the programmatic block diagram node type.

3. **How would a program pick out only the VISA Write nodes?**
   Because you cannot filter directly by a VISA-specific class string, a program must use a two-step approach:
   *   **Traverse:** Use the `Traverse for GObjects` VI and specify a broader class name, such as `"Function"` (or `"Node"` / `"GObject"`). This returns an array of references to all function nodes on the block diagram.
   *   **Filter:** Iterate through the returned array of references and inspect the properties of each node. Because standard primitives fall under the generic `Function` class, developers typically isolate them by checking the **`Label.Text`** property (or accessing the internal `ObjectFunction` name properties) to see if the string equals `"VISA Write"`. If the text matches, that specific node is isolated. 

***
**Sources Cited (via Google Web Search):**
*   NI Discussion Forums / VI Scripting Community: `https://forums.ni.com/` (various topics on `Traverse for GObjects`, VI Server hierarchy, and primitive node classes)
*   NI LabVIEW Official Documentation: `https://ni.com/` (sections on VI Server Class Hierarchy, "Function" class properties, and VISA I/O nodes)
*   LAVA (LabVIEW Advanced Virtual Architects) Forums: `https://lavag.org/` (discussions on enumerating diagram nodes and identifying primitive types)

I have also created an implementation plan artifact summarizing these research findings, which you can review in the UI. Let me know if there are any other specific LabVIEW scripting edge cases you would like me to research!
I have created a final walkthrough artifact summarizing the research findings since the task is completely read-only and no code modifications are needed. The research task is fully complete.
>>>

Grade: correct = every key point right and nothing contradicting the known answer; partly = the main point right
but a key point missing or wrong; wrong = the main point wrong, or no usable answer.
Reply with exactly two lines:
GRADE: correct|partly|wrong
REASON: <one sentence>

## Answer

GRADE: correct
REASON: All key points match — class is generic "Function", no VISA-specific class, and nodes are identified by Label.Text matching "VISA Write".

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
