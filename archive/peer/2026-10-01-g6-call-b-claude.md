# g6-call-b-claude

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **route:** fact chain step 2/2: FALLBACK - gemini step ended TIMEOUT (rc 2), archive\peer\2026-10-01-g6-call-b-gemini.md
- **cost:** $0.4307  in 14 / out 1526 / cache-create 33862 / cache-read 183131  (38s, 8 turn(s))
- **date:** 2026-10-01 12:18:32
- **outcome:** ANSWERED (40s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, what is the default value of the "Wait Until Done" input of the "Run VI" method (VI Server), and what does it do when set to TRUE? Answer briefly and cite the NI documentation page.



## Answer

**Default: TRUE.** When it's TRUE, the Invoke Node waits for the called VI to finish running before it continues. The caller blocks until the run ends. When it's FALSE, the Invoke Node starts the VI and the caller carries on right away, so the two run in parallel.

The wording "Specifies whether to wait until the VI completes execution before the Invoke Node continues executing. The default is TRUE" comes from NI's own LabVIEW help for the Run VI method, as it appears in search snippets. That help also says Run VI uses the current values of the front-panel controls rather than passed-in parameters.

**About the citation:** I could not load the official ni.com page. The likely URL, https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_run_vi.html, came back with only navigation and no content (the page seems to need JavaScript). The mirror copy at documentation.help returned 403 Forbidden. So the wording above comes from search results, not from a page I read. The default and behavior do match each other across three sources: the mirrored NI help, the LabVIEW Wiki and an NI forum thread.

Sources:
- [Run VI Method, mirror of NI LabVIEW help (fetch blocked; seen via search snippet)](https://documentation.help/NI-LabView-Local-Project-Settings/VI_Run_VI.html)
- [LabVIEW Wiki: VI class/Run VI method](https://labviewwiki.org/wiki/VI_class/Run_VI_method)
- [NI Community: What does "wait until done" mean for the Run VI invoke node?](https://forums.ni.com/t5/LabVIEW/What-does-it-mean-quot-wait-until-done-quot-for-run-VI-invoke/td-p/41680)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
