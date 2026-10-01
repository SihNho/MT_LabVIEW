# g5-l5-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.3433  in 14 / out 3848 / cache-create 13922 / cache-read 208640  (60s, 13 turn(s))
- **date:** 2026-09-30 20:08:04
- **outcome:** ANSWERED (62s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In the LabVIEW NI-IMAQdx palette, what are the DEFAULT values of the 'Buffer Number Mode' input of IMAQdx Get Image2.vi and of the 'Wait for Next Buffer?' input of IMAQdx Grab2.vi when those inputs are left unwired, and what does that default mean for a display loop that runs slower than the camera?

Search the web and cite the URL of every source you used.

## Answer

The defaults are **Next** for Buffer Number Mode on IMAQdx Get Image2.vi and **TRUE** for Wait for Next Buffer? on IMAQdx Grab2.vi. Both defaults do the same thing: the VI waits for a new frame instead of handing back one the camera already captured.

**Get Image2 → Buffer Number Mode: default is "Next"**
- A forum answer on NI's site says: "Use the default Buffer Number Mode, Next, for Get Image2. Do not wire Buffer Number In (it is 'required' for the Buffer Number Mode you chose, but is optional, and should be left unwired, for the 'Next' mode)." ([NI Forums](https://forums.ni.com/t5/LabVIEW/Buffers-output-in-IMAQdx/td-p/3644259))
- A search result for NI's official Get Image2 page said "Next" means "the driver waits for the next acquired buffer" ([NI docs](https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_get_image2.html)). I couldn't open that page (the fetch returned only site navigation), so I haven't confirmed the wording myself.

**Grab2 → Wait for Next Buffer?: default is TRUE**
- A forum answer says: "If you make it true(default) it waits for the next buffer to be ready before sending image, other case it returns the Last acquired buffer." ([NI Forums](https://forums.ni.com/t5/LabVIEW/Quick-question-about-grab-function-in-IMAQdx/td-p/3607125))
- The official Grab2 page ([NI docs](https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_grab2.html)) wouldn't load either, so this default rests on community sources only.

**What this means for a display loop slower than the camera**
- An NI employee's explanation (for the related Extract Image VI in LabVIEW NXG) gives this example: if you're taking buffer 5 while the camera has already reached buffer 10, "Next" waits for buffer 11. It doesn't return the frames already sitting in the buffer. ([NI Forums](https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556))
- So with the defaults, each loop pass:
  - **Skips frames:** every frame captured during the loop's work is dropped. The Grab thread also notes that a slow loop misses frames ([NI Forums](https://forums.ni.com/t5/LabVIEW/Quick-question-about-grab-function-in-IMAQdx/td-p/3607125)).
  - **Blocks:** it waits up to one camera frame period for the next new frame.
- The upside is that the loop never falls behind: the image shown is always fresh, never an old queued frame.
- The same thread describes the alternatives:
  - **"Last"** (or Wait for Next Buffer? = FALSE) returns the newest frame already captured without waiting.
  - **"Every"** returns the buffered frames in order so none are missed, which is what you'd use to process every frame instead of just displaying them.

**Caveats**
- NI's own reference pages didn't load for me (the ni.com pages rendered only navigation, and the documentation.help copies returned 403). The Next/TRUE defaults come from NI forum posts, plus a search-result summary of the Get Image2 page. The sources agree, but the Grab2 default isn't backed by an official page I could read.
- The worked example of "Next" behaviour is about Extract Image in LabVIEW NXG, not Get Image2 itself. It's the same NI-IMAQdx driver setting, but that thread doesn't directly confirm the two behave identically.

Sources:
- https://forums.ni.com/t5/LabVIEW/Buffers-output-in-IMAQdx/td-p/3644259
- https://forums.ni.com/t5/LabVIEW/Quick-question-about-grab-function-in-IMAQdx/td-p/3607125
- https://forums.ni.com/t5/Machine-Vision/Buffer-Mode-quot-Next-quot-and-quot-Every-quot-in-IMAQdx-Extract/td-p/4079556
- https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_get_image2.html (seen only as a search-result summary)
- https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_grab2.html (tried, content didn't load)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
