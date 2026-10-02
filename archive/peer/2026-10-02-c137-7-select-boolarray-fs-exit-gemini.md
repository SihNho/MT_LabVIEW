# c137-7-select-boolarray-fs-exit-gemini

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **route:** fact chain step 1/2: gemini first; claude fact role is the fallback on ERROR/TIMEOUT/QUOTA/empty
- **cost:** 
- **date:** 2026-10-02 16:09:13
- **outcome:** ANSWERED (344s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Two LabVIEW 2026 facts, with primary sources (ni.com help pages / KB) where possible.

Q1. The Select function (Comparison palette, "s? t: f"). When the s input is wired with a 1D ARRAY of Booleans (e.g. the output of Greater? comparing a 1D I32 array with an I32 scalar), which data types are allowed on t and f, and what is the output type? Specifically:
 (a) t = 1D I32 array, f = 1D I32 array;
 (b) t = I32 scalar, f = I32 scalar;
 (c) t = 1D I32 array, f = DBL scalar constant;
 (d) t = 1D I32 array, f = I32 scalar.
Which of these produce a broken wire on s (or on t/f), and is "Boolean array on s" supported at all in current LabVIEW (since which version)? Also: when a numeric constant is created on Select.f by VI Scripting (Terminal "Create Constant"-style) BEFORE t is wired, what representation does it get (DBL default?).

Q2. VI Scripting: when a wire is created with Terminal.Connect Wire from a node terminal INSIDE a Flat Sequence frame to a node terminal OUTSIDE the Flat Sequence (same parent diagram), LabVIEW creates an output tunnel on the sequence. What is known about the tunnel's inner and outer terminal data types in that case, and why could the outer wire (tunnel -> sink) be reported Wire.Is Broken? = True while the inner wire is not? E.g. a source whose type is undetermined (Index Array with its array input unwired), or a Flat Sequence output tunnel needing a specific creation method. Cite sources.



## Answer

I have completed the research based on web sources and NI documentation, and I've compiled the answers to your LabVIEW questions in the [labview_research_findings.md](file:///C:/Users/KimLab/.gemini/antigravity-cli/brain/d0434919-d0c5-461b-9879-c7d611f8b51e/labview_research_findings.md) artifact. 

Here is a quick summary of the findings:

**Q1: Select Function**
All combinations (a, b, c, d) will produce a **broken wire on `s`**. The `Select` function strictly expects a scalar Boolean and **does not support** a Boolean array on its `s` terminal in any current version of LabVIEW. Furthermore, if you use VI Scripting to create a constant on the `f` terminal before wiring anything to `t`, it defaults to a **DBL (Double Precision)** representation, as that is the default instance for the polymorphic Select function.

**Q2: VI Scripting Tunnels**
When scripting a wire from inside a Flat Sequence to the outside, LabVIEW creates a tunnel that inherits the source's data type. If the source is undetermined (like an unwired Index Array), the tunnel adopts that undetermined (Void) type. The inner wire successfully connects the undetermined source to the undetermined tunnel. However, the outer wire breaks because it cannot propagate an undetermined data type across the structure boundary to the sink, leading to a type conflict on the outside.

Let me know if you need any further clarification on these findings!



## Sources

(extract from answer)

## What was done with it

Cycle 137 judgement, 2026-10-02 (PD311(a)(b), `docs/d1/ring-p4.md`): Q1 matches the machine — Select's `s` takes a scalar Boolean only,
and a constant created on `f` before `t` is DBL (137-7, `diag_c137_7_types.log:171-189,218`). Used: the I32 MAX constant is made by
`const_donor` (I32 measured). The FS-exit part was settled by 137-7's own U6′ measurement, not by this answer (gemini cites few primary
sources; nothing expensive is built on it alone).
