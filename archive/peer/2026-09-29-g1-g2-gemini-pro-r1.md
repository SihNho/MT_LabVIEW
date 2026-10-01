# g1-g2-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:18:32
- **outcome:** ANSWERED (38s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

Yes, the 'Enable automatic error handling' option can be switched off programmatically for a specific VI. 

- **Class:** `VI`
- **Property:** `Execution:Automatic Error Handling` (Short Name: `Auto Err Handling`)

Setting this Boolean property to `False` disables the feature for the referenced VI. 

**Is there a global switch?**
No, there is no global application-level property in VI Server to toggle this for all VIs at once. The setting is strictly a per-VI property. To apply it globally across a project, you must write a script that iterates through all VI references (e.g., using `Application:All VIs in Memory`) and sets this property on each one individually. 

Furthermore, this property is primarily a development environment feature and is **not supported in the LabVIEW Run-Time Engine** (built executables ignore it).

**Sources:**
- NI Documentation for `Auto Err Handling` property: [VI Properties: Execution: Automatic Error Handling](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_auto_err_handling.html) (derived from NI support material)
- NI Forums discussing the lack of a global programmatic toggle and iterating over VIs: [Turning off automatic error handling on multiple VIs](https://forums.ni.com/t5/LabVIEW/Turning-off-automatic-error-handling-on-multiple-VIs/td-p/1126744)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
