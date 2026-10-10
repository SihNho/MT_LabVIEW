---
name: main-vi-diagram-was-cleaned-up-so-position-means-nothing
description: "The main VI's block diagram was rearranged by LabVIEW's Clean Up Diagram, so node positions carry NO functional meaning — never infer that nearby nodes belong together — and restoring that lost organisation is one of the user's main reasons for this project"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-13T08:15:20.627Z
type: decision
status: in-force
date: 2026-09-13
source: memory/diagram_was_cleaned_up_position_means_nothing.md
---

# Position means nothing in this VI: the diagram was Cleaned Up

The user ran LabVIEW's **Clean Up Diagram** (다이어그램 정리) on the main VI during an earlier version bump:

> "이전에 내가 버전 개량하면서 랩뷰 다이어그램 정리 눌러버렸거든. 그러니까 기능과는 무관하게 싹 다 섞여버렸어.
> 내가 클로드 사용하는 가장 큰 이유 중 하나가 그거기도 해"

Clean Up re-lays the whole diagram out algorithmically. It changes **positions only** — but it destroyed the spatial
grouping a human had built, so code that does one job is now scattered and interleaved with unrelated code.

## What this forbids

**Never infer function from proximity in this VI.** "These nodes are near each other, so they are one feature" is
false here by construction. Three separate searches in one session (2026-09-13) leaned on spatial reasoning and each
had to be thrown away — ranking diagrams by array-node density, picking a subVI extraction seam by visual clustering,
and reading a coordinate band as if it were a functional region.

It also means a **subVI extraction cannot be chosen by drawing a box around a screen region.** Whatever box is drawn
will cut through several unrelated features at once.

## What still survives, and is therefore what to use

Clean Up moved nodes; it did not rewire anything. So:

- **Diagram membership is intact.** A node inside the frame loop is still inside the frame loop — the diagram index
  from a Traverse is structural, not positional. `diagram 43 = the frame loop's body` remains exactly true.
- **Wire topology is intact.** The functional grouping still exists in the graph, it is just no longer visible on
  screen. It can be **recovered computationally** — connected components, reachability from a known anchor such as the
  tracking kernel call, which wires cross which structure boundary.

So: group by **graph structure**, never by coordinates.

## Why this matters beyond tooling

Restoring that lost organisation is, in the user's own words, one of the main reasons they are using Claude on this
project. The restructuring work is therefore not only about frame rate — a deliverable that is fast but still
unreadable only solves half of what was asked. Functional grouping is part of the goal, not a side effect.
