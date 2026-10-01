# g1-g1-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:19:11
- **outcome:** ANSWERED (114s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting (VI Server), which property of a Wire object reports whether that wire is broken, and what is that property's unique ID string (the hex ID used when the property is set with Allow Alternate Names = FALSE)? Also say what kinds of wire problems that property does and does not flag.

Search the web and cite the URL of every source you used.

## Answer

The property that reports whether a wire is broken is **`Wire.Is Broken?`**, and its unique hex ID string is **`6371004`**. 

### What it flags
It flags semantic and structural errors that render as a dashed wire with a red "X":
*   **Dataflow violations** (e.g., wiring a value produced inside a For Loop directly to that same loop's `N` terminal).
*   **Dangling wires / loose ends**.
*   **Hard type or class conflicts** (e.g., wiring a `GObject` reference to an API terminal expecting a `Node`).

### What it does NOT flag
*   **Weak type mismatches / coercions:** These render as black dashed wires (e.g., wiring a freshly dropped, weakly-typed Static VI Reference). This is LabVIEW's type-mismatch rendering, but it is not considered a broken wire.
*   **Unwired required terminals:** While an unwired required input breaks the VI (shattered Run arrow), there is no `Wire` object present to query, so this property cannot flag it.

### Sources
*   The property ID `6371004` is documented in this repository in `docs/vi-server-ids.json`, which sources it from the [LabVIEW Wiki's Wire class reference](https://labviewwiki.org/wiki/Wire_class). 
*   The types of wire problems and visual appearances (dashed red X vs. black dashed) are documented in this repository in `.agents/skills/labview-automation/references/vi-scripting.md`.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
