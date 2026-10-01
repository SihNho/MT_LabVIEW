# g5-l3-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:11:13
- **outcome:** ANSWERED (112s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, a program reads the Nodes[] property of a block diagram (Diagram / TopLevelDiagram class) to enumerate what is on it. Does that array include diagram constants, structure tunnels (for example loop tunnels or case selector tunnels) and shift registers? If some of them are missing, why, and how can a program enumerate them instead?

Search the web and cite the URL of every source you used.

## Answer

I have conducted web research to answer your questions about the LabVIEW VI Scripting `Nodes[]` property.

I have summarized all of the answers and cited my sources in the plan artifact (see `labview_research_plan.md`). Here is a quick summary of the findings:

*   **Are they included?** No, the `Nodes[]` array does not include diagram constants, structure tunnels, or shift registers.
*   **Why are they missing?** LabVIEW's VI Scripting categorizes diagram objects strictly by class hierarchy. The `Nodes[]` property only returns objects that inherit from the `Node` class. Constants inherit from the `Constant` class. Furthermore, tunnels and shift registers are not independent diagram nodes; they are structural components of the specific loops or case structures they belong to.
*   **How to enumerate them?** The most common and robust way is to use the **`TRef Traverse for GObjects.vi`** utility (found in `vi.lib\Utility\traverseref.llb`). By specifying the exact class string (e.g., `"Constant"`, `"Tunnel"`, `"Shift Register"`, or `"GObject"` for everything), you can recursively search and gather references to them across the entire diagram. Alternatively, you can cast loop nodes to their specific structure classes and access their internal properties, like `Tunnels[]` and `Shift Registers[]`.

Please review the implementation plan artifact for the full details and citations! Since no local changes or execution steps are necessary for this research task, you can simply approve the plan if it looks good.
I've completed the workflow by generating a final `walkthrough.md` artifact summarizing our research. Since no code changes were needed, everything is finalized. Let me know if there's anything else you need!



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
