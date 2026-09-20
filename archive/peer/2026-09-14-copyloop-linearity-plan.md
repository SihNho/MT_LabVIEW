---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# copyloop-linearity-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (37s)
- **why asked:** plan review before the linearity bench (second N = X Resolution 1280) that the earlier copy-loop review requested
- **verdict:** unverified

## Question

PLAN REVIEW (attack; one paragraph). Result just measured (tools/bench/run_copyloop_bench.log): HARNESS_copyloop (For loop N = IMAQ GetImageSize 'Y Resolution' = 1024, IMAQ Copy A->B 1280x1024 U8 inside) median 54.2 / 55.1 ms per Run vs HARNESS_copyloop0 (same loop, inner Copy deleted) 2.39 / 2.35 ms -> steady-state copy = 0.0506 / 0.0515 ms per copy (~26 GB/s, buffer cache-resident); cold single copy in the same session 0.42 / 0.36 ms; empty 1024-iteration loop 0.16 ms. Your earlier review asked for linearity in N (N=0/50/200) - N here is fixed by the image height. PLAN: build the same harness with N = 'X Resolution' (1280) as a second point (HARNESS_copyloopX / copyloopX0, same recipe with an argv switch), bench all four loop cells plus copy0/copy1 in one session, A-B-A-B, 5 warm + 60 timed Runs per cell, two passes; PREDICTION: (T1280 - T0X)/1280 within 5 percent of (T1024 - T0)/1024, and T1280 - T1024 = 256 x 0.05 = 12.8 +- 1 ms. ATTACK: (a) is a 26 GB/s copy of a 1.3 MB buffer plausible for a memcpy-class IMAQ Copy on a desktop (L2/L3-resident), or does it suggest the copy is being skipped (same src/dst each iteration; LabVIEW cannot elide an external IMAQ call - agree?); (b) a better cheap check that the pixels are really copied each iteration (e.g. compare B's pixel sum after the loop to A's; or deliberately modify B inside the loop) - is it worth adding, given ExecState and NI docs say IMAQ Copy copies unconditionally; (c) anything in the two-N design that confounds (both N share the same warm state).

## Answer

Proceed, but tighten the interpretation: 26?츶B/s payload bandwidth?봞bout 52?츶B/s counting source reads plus destination writes?봧s plausible for a hot 1.31?츼B copy whose combined A+B footprint is ~2.62?츼B and may reside in last-level cache; Intel explicitly treats cache and DRAM bandwidth as distinct regimes, and optimized `memcpy` aims to saturate cache bandwidth ([Intel MLC](https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html), [Intel memcpy optimization](https://www.intel.com/content/www/us/en/developer/articles/technical/performance-optimization-of-memcpy-in-dpdk.html)). It therefore does not itself suggest skipping, but I would not assert that ?쏬abVIEW cannot elide it?? the compiler likely preserves the call, yet only NI?셲 implementation determines possible alias/fast-path behavior; NI does document image buffers as mutable referenced memory and Copy as actually transferring data into another buffer, which argues strongly against legal elimination ([NI execution-order note](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8khSAC), [NI Copy description](https://www.ni.com/en/support/documentation/supplemental/06/ring-acquisitions.html)). A final pixel sum proves only the last iteration, not all 1,024 copies; the best cheap check is a separate untimed correctness harness that changes a sentinel pixel in A each iteration, copies, immediately reads that pixel from B, and accumulates mismatches?봡o not contaminate the timing harness with it. The two-N design is otherwise sound and shared warmth is desirable, provided `copyloopX0` retains the 1,280-iteration empty loop and cell order is counterbalanced; compare baseline-subtracted slopes and the ratio, expected near 1280/1024????.25. One correction: ?쐓lopes within 5%??does not mathematically guarantee the stronger `12.8 짹 1 ms` difference?봧ndependent 짹5% slope errors permit roughly 짹3.3?칖s in that difference?봲o make the ratio/slope criterion primary and the 짹1?칖s figure an empirical secondary prediction.

## Sources

(extract from answer)

## What was done with it

Followed: the slope agreement became the primary criterion and the ±1 ms difference a secondary, non-gating
prediction in run_copyloop_bench.py. Measured (run_copyloop_bench.log 14:37): slopes 0.0508 / 0.0501 and
0.0506 / 0.0518 ms per copy at N = 1024 / 1280 → PASS both passes; the secondary held once and missed by 1.5 ms once,
inside the spread the reviewer derived. The cache-bandwidth reading (26 GB/s payload ≈ 52 GB/s traffic, LLC-resident)
is recorded in the report. The sentinel-pixel correctness harness was not built. Verdict: correct and useful.
