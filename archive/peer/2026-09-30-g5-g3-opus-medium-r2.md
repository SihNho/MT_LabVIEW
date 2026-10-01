# g5-g3-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.5373  in 24 / out 4562 / cache-create 19971 / cache-read 393969  (90s, 20 turn(s))
- **date:** 2026-09-30 19:58:15
- **outcome:** ANSWERED (91s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In NI-IMAQdx (C function IMAQdxGetImageData, or the LabVIEW IMAQdx Get Image2 VI), what numeric value does each buffer-number mode (Next, Last, BufferNumber, Every, LastNew) have, and which of these modes returns immediately without waiting for a new frame from the camera?

Search the web and cite the URL of every source you used.

## Answer

I found three of the five values. Nothing I could reach online gives the numbers for Every and LastNew, so I've left those as unknown rather than guess.

**Numeric values**

| Mode | Value | Source |
|---|---|---|
| Next (`IMAQdxBufferNumberModeNext`) | 0 | NIIMAQdx.h and pylablib |
| Last (`IMAQdxBufferNumberModeLast`) | 1 | NIIMAQdx.h and pylablib |
| BufferNumber (`IMAQdxBufferNumberModeBufferNumber`) | 2 | NIIMAQdx.h and pylablib |
| Every | not found | — |
| LastNew | not found | — |

- The copy of NIIMAQdx.h in the wpilibsuite/nivision repo lists Next, Last and BufferNumber in that order with no values assigned, so C numbers them 0, 1 and 2. The only other member is `IMAQdxBufferNumberModeGuard = 0xFFFFFFFF`. https://github.com/wpilibsuite/nivision/blob/master/cpp/include/Vision/NIIMAQdx.h
- pylablib's definitions file sets the same values explicitly: Next = 0, Last = 1, BufferNumber = 2. https://raw.githubusercontent.com/AlexShkarin/pyLabLib/main/pylablib/devices/IMAQdx/NIIMAQdx_defs.py
- Neither header has Every or LastNew. They are probably newer additions, and both headers predate them. NI's own pages (the Get Image2 VI reference and the documentation.help mirrors) either didn't load or returned 403, so I couldn't check the official list. It would be a guess to say they are 3 and 4. To settle it, open `NIIMAQdx.h` from your installed NI-IMAQdx, or right-click the mode ring on IMAQdx Get Image2 and look at its item values.

**Which mode returns immediately**

**Last** is the one documented as not waiting. NI's text, quoted in the NI forum: "Default value is **Next**, which specifies that the driver waits for the next acquired buffer." and "**Last** specifies that the driver does not wait for the next buffer but instead returns the last acquired buffer." https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556

How the other modes behave:
- **Next** always waits for a new frame (same source as above).
- **BufferNumber** "specifies an exact buffer number to wait for". If that buffer hasn't been acquired yet, the call blocks until it is. https://forums.ni.com/t5/Machine-Vision/quot-buffer-number-in-quot-confusion-with-IMAQdx-get-image/td-p/688948 and https://natinst.public.imaq.general.narkive.com/OyB8ZFv2/quot-buffer-number-in-quot-confusion-with-imaqdx-get-image
- **Every** "returns all sequential images in memory". An NI engineer says it hands back an already-acquired buffer "without waiting", but it still waits when you have caught up with the camera. https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556
- **LastNew**: NI has a knowledge article on how Last and LastNew differ, but the page wouldn't load (certificate error), so I can't confirm how LastNew behaves. https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US

**Sources**
- https://github.com/wpilibsuite/nivision/blob/master/cpp/include/Vision/NIIMAQdx.h
- https://raw.githubusercontent.com/AlexShkarin/pyLabLib/main/pylablib/devices/IMAQdx/NIIMAQdx_defs.py
- https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556
- https://forums.ni.com/t5/Machine-Vision/quot-buffer-number-in-quot-confusion-with-IMAQdx-get-image/td-p/688948
- https://natinst.public.imaq.general.narkive.com/OyB8ZFv2/quot-buffer-number-in-quot-confusion-with-imaqdx-get-image
- https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US (found by search, couldn't open)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
