# g1-g4-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:22:29
- **outcome:** ANSWERED (52s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In Windows PowerShell 5.1, when the standard output of a native executable is captured inside PowerShell (for example $x = & prog.exe | Out-String), which setting determines the character encoding used to decode those bytes, and what do you set so that UTF-8 output is decoded correctly?

Search the web and cite the URL of every source you used.

## Answer

**`[Console]::OutputEncoding`** determines how PowerShell 5.1 decodes standard output captured from a native executable.

To decode UTF-8 output correctly, set it to:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Reasoning
When PowerShell captures standard output from an external program (e.g., `$x = & prog.exe`), it receives a stream of raw bytes. It uses the `.NET` class property `[Console]::OutputEncoding` to translate those bytes into PowerShell's internal strings. 

By default in PowerShell 5.1, this encoding is set to the system's legacy OEM code page (such as CP437). If the executable outputs UTF-8, PowerShell incorrectly decodes those bytes using the OEM code page, resulting in garbled text. Changing `[Console]::OutputEncoding` to UTF-8 forces PowerShell to parse the incoming byte stream properly. 

*(Note: The `$OutputEncoding` preference variable does the opposite; it controls the encoding PowerShell uses when **sending** data to an external program via the pipeline.)*

### Sources
- [Stack Overflow: How to get PowerShell to correctly capture UTF-8 output from a native executable](https://stackoverflow.com/questions/49476326)
- [Microsoft Learn: Console.OutputEncoding Property](https://learn.microsoft.com/en-us/dotnet/api/system.console.outputencoding)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
