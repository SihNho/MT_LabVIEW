# g1-g5-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:23:44
- **outcome:** ANSWERED (30s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In Windows PowerShell 5.1, which character encoding does Get-Content use by default when it reads a text file that has no byte-order mark?

Search the web and cite the URL of every source you used.

## Answer

In Windows PowerShell 5.1, `Get-Content` defaults to the system's active **ANSI code page** (e.g., Windows-1252 on US English systems) when reading a text file without a byte-order mark (BOM).

**Reasoning:**
If a file lacks a BOM, PowerShell 5.1 cannot automatically detect its encoding. In this scenario, `Get-Content` falls back to the `-Encoding Default` value, which corresponds to the system's active ANSI code page. This is distinct from newer versions of PowerShell (Core 6 and above), which default to UTF-8 without a BOM.

**Reference:**
[Microsoft Documentation: about_Character_Encoding (PowerShell 5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
