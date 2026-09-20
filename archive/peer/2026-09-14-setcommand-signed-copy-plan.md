---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# setcommand-signed-copy-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (65s)
- **why asked:** plan review before building SetCommand_signed.vi (the user-decided signed rotor read, on a copy)
- **verdict:** unverified

## Question

PLAN REVIEW (attack; one paragraph). GOAL (user decision): a signed-read COPY of the lab's Autonics rotor driver SetCommand.vi (instr.lib original untouched; the copy lives under claudeDev and only the NEW main VI will call it). MEASURED (tools/bench/probe_setcommand*.log): read frame = diagram 1 of a 4-case structure: VISA Write(query) -> VISA Read -> String Subset (substring wire 1183) -> Hexadecimal String To Number (default unwired = U32; number wire 2939) -> Multiply(x=number, y=const k) -> Subtract(x, y = Baseline*k') -> case output tunnel -> Pos_degree. A Type Cast (uid 622) hangs off the SUBSTRING (x=wire 1183, type=const 687 of unknown integer type) and feeds only a debug indicator via one Multiply. Protocol (Autonics PMC manual via codex): reply 'POS hhhhhhhh[CR]', 8 hex digits, 32-bit sign-extended. Two of your earlier answers disagree on whether an I32 default makes Hex String To Number return -10 for FFFFFFF6 (NI doc: out-of-range saturates to max) - so the design avoids it. PLAN (all scripted, proven primitives: delete Wire by uid, connect_terminals node->node, connect_ctl for panel objects, create_control): (1) delete wire 2939 (number -> Multiply.x) and wire 1183 (substring -> Hex.string / TypeCast.x / 'read buffer 2'); (2) reconnect substring -> Hex.string; Hex.number -> TypeCast.x; TypeCast.out -> Multiply.x (branch: the debug Multiply stays); substring -> 'read buffer 2' indicator; ExecState 1 -> save as SetCommand_signed.vi. (3) TEST copy: also delete wire 1251 (VISA Read.read buffer -> String Subset.string + 'read buffer' indicator) and create_control on String Subset.string -> a 'string' control; run with VISA resource '' (VISA errors, no hardware) for Ring = 0..3 injecting 'POS 00000064\r': the ring value whose Pos_degree != 0 is the read case (finds the Ring->case mapping without hardware; the other cases write to a nonexistent resource = harmless); then inject 'POS FFFFFFF6\r' -> expect Pos_degree = -10*k, 'POS 7FFFFFFF\r' -> +2147483647*k, with Baseline Startpoint = 0. ATTACK: (a) the unknown type of the Type Cast's 'type' constant 687: if it is not I32 the cast is wrong - is the injected-string test sufficient to detect it (I16 would give -1 for FFFFFFF6? DBL garbage), and what is the scripted fallback (create a control on the 'type' input? its default type?); (b) any LabVIEW subtlety in Type Cast U32 -> I32 (byte order is irrelevant for same-width integers - agree?); (c) risk in running a case with VISA resource '' (VISA Write error 1073807343? any dialog with auto error handling on: we set it off on the TEST copy only); (d) is the String Subset window (offset/length constants unreadable) likely [4,8] for 'POS hhhhhhhh' - the injection test will show; (e) anything that makes the copy differ from the original for POSITIVE replies (it must not).

## Answer

Conditional approve: the test is sufficient only as a behavioral gate, not as proof that constant 687 is I32. `FFFFFFFF`/`FFFFFFF6` alone is inadequate because an I16 cast can also retain the low 16 bits and produce ??/??0; your `7FFFFFFF ??+2147483647쨌k` vector distinguishes I16, while the negative vector distinguishes U32, so require all three vectors?봧ncluding `00000064`?봳o pass exactly. Type Cast reinterprets data rather than performing numeric conversion, so byte order is immaterial for equal-width U32?묲32 on the same LabVIEW target; nevertheless, inspect the resulting wire type if reporter output can expose it ([NI Type Cast distinction](https://www.ni.com/pdf/manuals/371780p.pdf)). Do not use `create_control(Type Cast.type)` as the fallback: it will inherit the existing unknown terminal type rather than establish I32; the scripted fallback should create or copy a demonstrably I32 numeric object, verify its representation via reporter output, then wire it to `type`, otherwise stop rather than guess. Running with an explicitly invalid/empty VISA resource should fail without hardware access?봏I identifies ??073807343 as ?쐇nsufficient location information or resource not present?앪봟ut it can still block or display something if an explicit error-handler/dialog exists, so disable automatic error handling on the test copy, confirm no dialog-producing handler in the executed cases, and impose a run timeout ([NI VISA error](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9IASA0&l=en-US), [NI automatic-error behavior](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)). `[4,8]` is the expected zero-based window for `POS hhhhhhhh`, but inject an actual CR byte?봭ot the two characters `\` and `r`?봞nd treat exact `read buffer 2 == hhhhhhhh` as a prerequisite. Finally, positive compatibility is not established by one value: inserting I32 can change coercion or overflow behavior if `k`, the Multiply output, tunnel, or Subtract path is integral, so regression-test at least `00000000`, `00000001`, `00000064`, `7FFFFFFE`, and `7FFFFFFF` against untouched-original results with identical controls; approve the production copy only if every positive output and indicator matches bit-for-bit, the three signed vectors pass, and the original remains untouched.

## Sources

(extract from answer)

## What was done with it

Built exactly this way; the injection test passed 16/16 (test_setcommand_signed.log) with the regression vectors the reviewer added. Verdict: correct.
