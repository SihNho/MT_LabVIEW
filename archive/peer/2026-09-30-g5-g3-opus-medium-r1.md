# g5-g3-opus-medium-r1

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.8224  in 22 / out 4218 / cache-create 26164 / cache-read 403974  (98s, 19 turn(s))
- **date:** 2026-09-30 19:58:29
- **outcome:** ANSWERED (99s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In NI-IMAQdx (C function IMAQdxGetImageData, or the LabVIEW IMAQdx Get Image2 VI), what numeric value does each buffer-number mode (Next, Last, BufferNumber, Every, LastNew) have, and which of these modes returns immediately without waiting for a new frame from the camera?

Search the web and cite the URL of every source you used.

## Answer

Only **Last** is confirmed to return right away without waiting for a new frame. I could confirm the numbers for three of the five modes; I could not find the numbers for Every and LastNew.

**Numeric values**

These come from a copy of NI's C header `NIIMAQdx.h` in WPILib's repo, which lists the enum with no explicit values. C numbers such members from 0, so the values follow from the order. pylablib's Python version of the enum writes the values out and they match.

| Mode | Value | Source |
|---|---|---|
| `IMAQdxBufferNumberModeNext` | 0 | header plus pylablib |
| `IMAQdxBufferNumberModeLast` | 1 | header plus pylablib |
| `IMAQdxBufferNumberModeBufferNumber` | 2 | header plus pylablib |
| Every | not found | — |
| LastNew | not found | — |

The enum also has a sentinel, `IMAQdxBufferNumberModeGuard = 0xFFFFFFFF`, which is not a real mode.

Neither source contains Every or LastNew, so that copy of the header predates them. I found no source that gives their values. You might expect 3 and 4 from the order, but nothing I found confirms that, so I'm not stating it. To settle it, look at the `IMAQdxBufferNumberMode` enum in the `NIIMAQdx.h` that ships with your NI-IMAQdx install, or wire a constant to that input of Get Image2 in LabVIEW and look at its numeric value.

**Which mode returns without waiting**

- **Last** returns right away. NI's documentation, as quoted in the NI forum, says "the driver does not wait for the next buffer but instead returns the last acquired buffer."
- **Next** is the default and waits: "the driver waits for the next acquired buffer."
- **BufferNumber** waits until the buffer number you asked for has been acquired, and "Buffer Number In" is ignored in the Last and Next modes.
- **Every** "returns all sequential images in memory." An NI employee explains that, unlike Next, it doesn't wait for a new frame when frames it hasn't returned yet are already in memory. I found nothing on what it does once it has caught up and no such frames are left.
- **LastNew:** NI has a support article on "Last" versus "Last New", but its page failed with a certificate error both times I tried, so I couldn't read its wording. I'm not making a claim about LastNew's waiting behaviour.

**Sources**
- https://github.com/wpilibsuite/nivision/blob/master/cpp/include/Vision/NIIMAQdx.h (read through https://raw.githubusercontent.com/wpilibsuite/nivision/master/cpp/include/Vision/NIIMAQdx.h)
- https://raw.githubusercontent.com/AlexShkarin/pyLabLib/main/pylablib/devices/IMAQdx/NIIMAQdx_defs.py
- https://pylablib.readthedocs.io/en/stable/_modules/pylablib/devices/IMAQdx/IMAQdx.html
- https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556
- https://natinst.public.imaq.general.narkive.com/OyB8ZFv2/quot-buffer-number-in-quot-confusion-with-imaqdx-get-image
- https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US (found in search, couldn't be read)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
