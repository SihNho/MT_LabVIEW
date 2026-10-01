# g1-g5-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:22:55
- **outcome:** ANSWERED (26s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In Windows PowerShell 5.1, which character encoding does Get-Content use by default when it reads a text file that has no byte-order mark?

Search the web and cite the URL of every source you used.

## Answer

In Windows PowerShell 5.1, when `Get-Content` reads a text file that has no byte-order mark (BOM), it defaults to the system's active **ANSI code page** (often referred to as the "Default" encoding, typically Windows-1252 on US English systems). 

Because it falls back to ANSI, reading a BOM-less UTF-8 file that contains non-ASCII characters with `Get-Content` will result in corrupted text (mojibake). 

**Sources:**
* Microsoft Documentation on `Get-Content` (Windows PowerShell 5.1): [https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-content?view=powershell-5.1](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-content?view=powershell-5.1)
* "Understanding PowerShell Encoding" (2Pint Software): [https://2pintsoftware.com/understanding-powershell-encoding/](https://2pintsoftware.com/understanding-powershell-encoding/)
* StackOverflow - How to read/write a UTF8 without BOM file: [https://stackoverflow.com/questions/5596982/using-powershell-to-write-a-file-in-utf-8-without-the-bom](https://stackoverflow.com/questions/5596982/using-powershell-to-write-a-file-in-utf-8-without-the-bom)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
