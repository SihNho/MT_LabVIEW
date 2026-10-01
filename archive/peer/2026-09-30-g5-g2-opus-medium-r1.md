# g5-g2-opus-medium-r1

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.3245  in 14 / out 2655 / cache-create 14413 / cache-read 209417  (54s, 11 turn(s))
- **date:** 2026-09-30 19:56:44
- **outcome:** ANSWERED (56s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

**Yes, per VI.** Use the **VI class** property **Automatic Error Handling** (short name **Auto Err Handling**). It's a Boolean, readable and writable. Open a VI reference to the target VI with Open VI Reference, then write FALSE to the property with a Property Node. This is the same checkbox as File » VI Properties » Execution » "Enable automatic error handling".

- The LabVIEW Wiki property page lists it as **not settable while the VI is running**, and **not available in the Run-Time Engine**. So do it at edit time, or from a separate tool VI while the target VI is idle.
- NI's own page for this property turned up in search, but I couldn't read its contents, so the details above come from the LabVIEW Wiki.
- On a declined NI Idea Exchange post, users say you can script this property to batch-change many VIs. NI pointed to JKI's Property Inspector toolkit for that job instead of adding a project-wide switch.

**Global switch: only partly.**
- **Tools » Options » Block Diagram » "Enable automatic error handling in new VIs"** only sets the default for newly created VIs. Existing VIs keep their own setting.
- **"Enable automatic error handling dialogs"** is also named as a global option in the Idea Exchange thread. My sources don't say exactly what it covers, for example whether it hides the dialogs for all VIs while leaving each VI's setting alone. I can't settle that.
- **The `EnableAutomaticErrorHandling` ini token** is mentioned in the same thread, but only as something that "might" affect built executables. It isn't confirmed.
- **No project-wide or global VI Server property** turned up. The request for a project-level on/off control was declined by NI, and that thread is the evidence for this point.

Sources:
- [LabVIEW Wiki – VI class/Automatic Error Handling property](https://labviewwiki.org/wiki/VI_class/Automatic_Error_Handling_property)
- [NI docs – Automatic Error Handling (VI Server property)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/automaticerrorhandling.html) (found by search; its contents didn't load)
- [LabVIEW Wiki – Automatic Error Handling](https://labviewwiki.org/wiki/Automatic_Error_Handling)
- [LabVIEW Artisan – My Tools > Options Settings](http://labviewartisan.blogspot.com/2009/02/my-tools-options-settings.html)
- [NI Idea Exchange – Enable/disable Automatic Error Handling for all project items (Declined)](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Ability-to-enable-or-disable-Automatic-Error-Handling-for-all/idi-p/4392260)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
