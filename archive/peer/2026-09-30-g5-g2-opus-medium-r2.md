# g5-g2-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.3479  in 14 / out 2863 / cache-create 15806 / cache-read 212731  (56s, 13 turn(s))
- **date:** 2026-09-30 19:56:37
- **outcome:** ANSWERED (58s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

**Yes, you can switch it off per VI through VI Server.**

- **Class:** VI (VI Server → VI class)
- **Property:** `Automatic Error Handling`. The documentation page also lists it as `Execution:Automatic Error Handling`, and its short name is `Auto Err Handling`.
- **Type and access:** Boolean, read/write, remote access supported. Setting it to FALSE turns off automatic error handling for the VI the reference points to.
- **Limits:** you can't set it while the VI is running. It isn't supported on real-time targets or in the LabVIEW Run-Time Engine, and it doesn't apply to control VIs, global VIs, polymorphic VIs or strict type definitions.
- **What it maps to:** this is the same setting as the "Enable automatic error handling" checkbox on the Execution page of VI Properties.
- **How to use it:** open a VI reference to the target VI, then write FALSE to this property with a Property Node. If you leave the Property Node's reference input unwired, it acts on the VI it's placed in.

Sources: [NI – Automatic Error Handling property](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/automaticerrorhandling.html) (NI's page didn't load for me, so the details come from its search snippet and the wiki mirror), [LabVIEW Wiki – VI class/Automatic Error Handling property](https://labviewwiki.org/wiki/VI_class/Automatic_Error_Handling_property)

**Global switch: yes, but it's a checkbox in the LabVIEW environment's settings. I found nothing documented that sets it from code.**

Both global options are under **Tools » Options » Block Diagram**:

1. **"Enable automatic error handling dialogs"** is the actual global switch. If you uncheck it, LabVIEW won't pause the VI or show the error dialog, even in VIs that still have automatic error handling turned on. It is checked by default. ([NI – Block Diagram Page, Options dialog](https://www.ni.com/docs/en-US/bundle/labview-2021/page/lvdialog/block_diagram_options.html); I got this from the search-result summary and couldn't open the page to read it directly.)
2. **"Enable automatic error handling in new VIs"** only sets the default for new blank VIs. It doesn't change existing VIs. ([LabVIEW Wiki – Automatic Error Handling](https://labviewwiki.org/wiki/Automatic_Error_Handling))

**Not settled by my sources:**
- I found no documented Application-class property or LabVIEW.ini setting that changes either option from code. That doesn't prove none exists.
- For built applications, Build Specifications → Source File Settings has a per-VI "Enable automatic error handling" option, which defaults to "Use VI Property". Users also report that built executables don't show these dialogs anyway. Both points come from blog comments, not NI documentation. ([LabVIEW Artisan blog](http://labviewartisan.blogspot.com/2009/02/my-tools-options-settings.html))

Separately from both switches, wiring a node's error out to another node or to an indicator turns off automatic handling for that one node. ([LabVIEW Wiki](https://labviewwiki.org/wiki/Automatic_Error_Handling))

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
