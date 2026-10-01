# g5-l2-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:06:36
- **outcome:** ANSWERED (105s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

With NI-IMAQdx and a USB3 Vision camera, a program opens a camera session, writes new values to attributes such as Width/Height (ROI), ExposureAuto/ExposureTime or the acquisition frame rate, confirms them by reading back, and then closes the session. When the next IMAQdxOpenCamera (or IMAQdx Open Camera VI) call opens the same camera, what values do those attributes have, and why?

Search the web and cite the URL of every source you used.

## Answer

I have completed the web research regarding your question about NI-IMAQdx, USB3 Vision cameras, and attribute persistence across sessions. 

I've created an implementation plan artifact containing the detailed findings, the underlying mechanics, and the sources used. 

**Brief Summary of Findings:**
When the next `IMAQdxOpenCamera` call opens the same camera, the attributes will **revert to their previous, original values** (the values they had before the first program modified them). They will not retain the new values written during the first session. 

This happens because modifying attributes programmatically only changes the camera's volatile memory and the current software session, but it does not automatically save those changes to the host's `.icd` configuration file. When `IMAQdxOpenCamera` is called again, the driver locates the unchanged `.icd` file and explicitly applies those saved settings back to the camera, overriding the camera's hardware state and effectively erasing your modifications.

Please review the [Research Findings Plan](file:///C:/Users/KimLab/.gemini/antigravity-cli/brain/4d1fb85b-b380-4967-8b78-393a248eb475/research_plan.md) artifact for a more detailed breakdown and the cited sources. Let me know if you would like me to proceed with any further research on this topic!
I have finalized the research and created a [Walkthrough](file:///C:/Users/KimLab/.gemini/antigravity-cli/brain/4d1fb85b-b380-4967-8b78-393a248eb475/walkthrough.md) artifact to summarize the completion of this task. Since this was a read-only research task with no local system changes required, the task is now fully complete! Let me know if you have any follow-up questions.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
