# peerps1-bomless-cp949-parse

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (165s)
- **why asked:** Mandatory review of a FAILED PREDICTION — peer.ps1 stopped parsing after the `-Kind review` block
  was added, and three dispatches died rc=1 in one second (verification run 1, tests B, C, F).
- **verdict:** PARTIALLY REFUTED, and accepted. The broad diagnosis (BOM-less UTF-8 decoded through the legacy ANSI
  page) stands, but my specific mechanism does not: `0x27` is not a valid CP949 trail byte, so the closing quote was
  never "consumed". The peer's alternative — mojibake producing a typographic quote (U+2018–U+201B), which
  PowerShell treats as a string delimiter — is unrefuted. The repair is also CONFOUNDED: the escapes and the BOM
  were applied together, so neither is shown necessary. Its discriminating test (insert an ASCII `A` before the
  closing quote and parse only) is deliberately NOT run — the same day's outcome review says to freeze
  non-delivery tooling work. Logged as an open, low-stakes unknown; the fix is functional either way (all tests pass).

## Question

CLAIM UNDER TEST, attack it. tools/peer.ps1 stopped parsing on 2026-09-15 with "Unexpected token" at `if ($Kind -eq 'review') {`, and three dispatches died with rc=1 in 1 second. MY DIAGNOSIS: the file was UTF-8 WITHOUT a BOM, so Windows PowerShell 5.1 decoded it as the system ANSI code page (cp949), and a Korean literal at the END of a single-quoted regex (...|GEOMTO\s*BUTAK') had its closing quote consumed as the trail byte of a double-byte sequence, so the string ran on and the next statement became garbage. EVIDENCE: the parser error quotes the rest of the file as if it were inside that string; an em-dash elsewhere rendered as ?? in the error text; the same file parsed fine BEFORE the Korean literal was added, although it already contained em-dashes in COMMENTS. FIX APPLIED: Korean moved to \uXXXX escapes and a UTF-8 BOM prepended. ALSO EXPLAIN: why did em-dashes in comments survive for weeks while this broke immediately?

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The specific ?쏿postrophe became a CP949 trail byte??mechanism is wrong.

1. **Strongest objection:** `0x27` is not a valid CP949 trail byte. Microsoft?셲 CP949 mapping preserves it as ASCII U+0027 and contains no two-byte mapping ending in `27`. At most, an implementation-specific invalid-sequence fallback could replace multiple bytes; that is different from valid trail-byte decoding. [Microsoft CP949 mapping](https://unicode.org/Public/MAPPINGS/VENDORS/MICSFT/WINDOWS/CP949.TXT), [.NET decoder fallback behavior](https://learn.microsoft.com/en-us/dotnet/api/system.text.decoderfallback)

2. **Alternative explanation:** CP949 mojibake may have introduced a Unicode typographic quote *inside* the regex, prematurely terminating the string. PowerShell treats U+2018?밬+201B as single-quote delimiters, not ordinary string content. Another possibility is an independently missing or transformed quote during the edit. The parser then reports the next recognizable statement??if`?봢ven though the defect is earlier. [PowerShell lexical grammar](https://learn.microsoft.com/en-us/powershell/scripting/lang-spec/chapter-15?view=powershell-7.6)

   The BOM evidence establishes only the broader encoding hazard: Windows PowerShell reads BOM-less source using the active ANSI code page. It does not establish which decoded character broke tokenization. Moreover, escapes and a BOM were applied together, so the repair is causally confounded. [PowerShell encoding documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-7.6)

3. **Falsifying observation:** Decode the exact original bytes through the same Windows PowerShell 5.1 source-loading path. If the final ASCII `0x27` remains U+0027 and appears as the closing delimiter in the parser?셲 token extent, then the claimed ?쐁onsumed closing quote??mechanism is falsified?봢ven if encoding corruption elsewhere still caused the error.

4. **Why comments survived:** PowerShell ignores everything after `#` through the newline. Thus a mojibaked em dash in a comment can display as `??` for weeks without changing tokenization. The same corruption in executable string text can create a recognized quote character or disturb decoding near a delimiter. [PowerShell comments](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comments?view=powershell-7.6)

The broader diagnosis?볿OM-less UTF-8 misread through the legacy ANSI code page?봱emains likely, but the asserted CP949-trail-byte mechanism does not hold without decoder-level evidence.

**Cheapest discriminating test:** On disposable copies containing only the exact problematic line, parse?봭ot execute??A) the original and (B) a version with ASCII `A` inserted immediately before the closing apostrophe. `0x41` is a valid CP949 trail byte. If A fails and B parses, boundary consumption is supported; if both fail, inspect the decoded text for an injected typographic quote or ordinary syntax corruption.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
