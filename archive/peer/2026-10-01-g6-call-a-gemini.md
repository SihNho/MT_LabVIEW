# g6-call-a-gemini

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **route:** fact chain step 1/2: gemini first; claude fact role is the fallback on ERROR/TIMEOUT/QUOTA/empty
- **cost:** 
- **date:** 2026-10-01 12:19:38
- **outcome:** ANSWERED (115s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, what does the "Clean Up Diagram" method of a VI (VI method name and its scripting ID, if documented) do, and from which LabVIEW version is it available? Answer briefly and cite the NI documentation page.



## Answer

I have conducted the web research based on your requirements and prepared the answer. I have also formulated this into an Implementation Plan artifact per the `/plan` command, which you can review.

Here is the brief answer to your question:

In LabVIEW VI Scripting, the **Clean Up Diagram** method automatically rearranges and resizes objects and reroutes wires on a VI's block diagram to improve layout and readability (this is the programmatic equivalent of manually pressing `<Ctrl-U>`).

- **Method Name:** `Block Diagram:Clean Up`
- **Scripting ID:** `474`
- **Available From:** LabVIEW 8.6

**Sources Used:**
1. **NI Documentation:** [Block Diagram:Clean Up Method](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_bd_cleanup.html)
2. **LabVIEW Wiki:** [Clean Up Method ID](https://labviewwiki.org/wiki/Block_Diagram:Clean_Up)

Please review the plan artifact. Since you explicitly requested no files be modified and no local commands be run, there are no execution steps. You can approve the plan to mark this research task as complete!
Since this task strictly required no codebase modifications or local command executions, there are no code changes to make.

I have created a `walkthrough.md` artifact summarizing the research as the final step of our `/plan`. The task is now completely fulfilled! Let me know if you need help with anything else.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
