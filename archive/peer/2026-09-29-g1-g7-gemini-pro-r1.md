# g1-g7-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:24:35
- **outcome:** ANSWERED (56s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In Windows PowerShell 5.1, if a string variable that contains embedded double-quote characters and spaces is passed as a single argument to a native executable (for example & prog.exe $s), does the program receive it as one intact argument?

Search the web and cite the URL of every source you used.

## Answer

**No.** The native executable will not receive it as one intact argument; it will be split into multiple mangled arguments and the quotes will likely be stripped.

### Reasoning

When you pass a variable to a native executable (using `&`), Windows PowerShell 5.1 must reconstruct your arguments into a single raw command-line string before handing it to the OS. If your string contains spaces, PowerShell automatically wraps the entire argument in double quotes. 

However, PowerShell 5.1 fails to properly escape any double quotes that are *already* inside your string. This results in an invalidly quoted command line (e.g., passing `a "b c" d` becomes `"a "b c" d"`). When the target native executable parses this raw string (typically via the Windows `CommandLineToArgvW` API), it treats your unescaped inner quotes as structural delimiters. The parser then splits the string at the spaces, destroying the single argument.

To successfully pass the string as one argument in PowerShell 5.1, you must manually escape the inner quotes (often with a backslash `\"` or backtick-backslash `` `\" `` depending on the target), or use the `--%` stop-parsing symbol if you don't need variable expansion.

### How to check this cheaply

You can verify exactly how your string is being mangled by passing your variable to the `echoargs.exe` utility (often found in PowerShell Community Extensions). It simply echoes back the exact `argv` array that the native process receives, allowing you to iterate on your escaping until it forms one intact argument.

### Sources
*   StackOverflow: [PowerShell stripping double quotes from command line arguments](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKryCOy8SzU0_UhWWP52OcZhFp7hxDjIIIy4EVPqfLr5_pCW5BzwOTX_4k2QD6MXsQCLDxBHxQ98E-wfwoA7LmVKu7w376CXZN9in3-a-5FFWxDcE3rjWcngc9t10zAVHmvJyZVFZmILezScPhADer07ygeWu0vWpqZlyisSHjTRPudIbmYH-W_EpWwm68_vv9ecBygBkDb3eDBocEpKWG)
*   Microsoft: [about_Parsing (Stop-parsing token)](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEafmf6Cx-PR8YmZBLaG53rkOfVw2ayHjAQ3wEmLKEU3uUgy8caI6qXkYu7VDYU7xlsP7H6BGWziagPUS8FbuOXsPiyGJkW-qrJqdzlRY2mNQCVFnNrcSH9QRQ-u7u49Sp8wF5ribxYFUe8-r5eyBxF7o8S1C3A19hpWHi9heVrA4jOhBOZsvTnCtbZE58N7UmdyPDbLtTxmIIm2p9JvMyt9H7ufO4svwQxi6c=)
*   PowerShell Magazine: [How to pass arguments to a command or an executable](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED_ElaiU70gcpiXwzBPOQclZqF1YxW80q4wxUYgHYP3C_VpES2WHfn079EdX9qApOp2dGxNgKsDH8_NXzTKx_DiQ_pphABuVtOJMCJp1Tcjh8q0148wUo8mGSznGDXrXrc_D04pS6DHyP5MHesJWOV_lVgVvk6LNfx9KNUBTYwhTPZbI-DPFqM)
*   StackOverflow: [Using EchoArgs to debug PowerShell argument passing](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcZx4Kq9lJRLYzrjRLaIRvuoco_U_NhKrPvyYKuJ_iJRutK5qI7i-V3tgFWRYHkq98dgiHgoZEGLwajqSIDGB3FPcvHvKKRriUATVDDa7ieKDouiFX9zPZ-hVbFoaKiasyXtkS9THColhsE4BOZuHUms3a5UCOrX2bgcHtINcuBsRVEW2Vy9xeeJc_n5CTa0NRdHSHIcCtfQIhFXbyEBqpf1yElWNDHzAU009Tfg==)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
