---
name: gui-click-optimization-first
description: "The user's ordering (2026-09-04): first make GUI clicking as fast, accurate and efficient as possible; build the LabVIEW toolkit WITH that optimized GUI tool; minimize clicks only after clicking itself is cheap — and benchmark the clicking methods, not the models, first"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-04T07:11:54.301Z
type: decision
status: in-force
date: 2026-09-04
source: memory/gui_click_optimization_first.md
---

# Optimize GUI clicking first; the toolkit is built with the optimized clicker

Stated 2026-09-04 after the user watched a day of screenshot→read→click round-trips and the
tenth "I'll script it next time": *"GUI 클릭 최적화부터 우선 들어가야해. 다른 판단은 필요 없이 GUI
클릭을 가장 빠르고 정확하게, 그리고 효율 높게 진행할 방법을 찾아. 이후 툴킷 개발은 최적화 GUI 도구로
시작해야하고 (GUI 클릭은 최소화하는게 맞지만, 그 이전에 GUI 클릭 효율을 높이는 것이 최선) 그 다음
개발로 들어가야겠어."*

This is an ORDERING, not a reversal of "script first". The user's reasoning: clicks are
unavoidable while the toolkit is being built (every new op needs a few), so the cheapest path to a
click-free toolkit runs through a fast, accurate, cheap clicker — not through more promises to
avoid clicking. Priorities, in order:

1. **Make the clicker fast and exact.** Coordinates from data, not from vision: the COM reporter
   gives every object's diagram position; with one known screen↔diagram offset per viewport the
   click target is arithmetic. Vision (Claude reading screenshots, or the local UI-TARS grounder)
   is the fallback for what data cannot give (menus, dialogs), never the default.
2. **Package proven click sequences as single verbs** with COM self-verification (place-from-
   palette, change-to-write, create-control, pick-method) so the expensive model issues one
   command and does not narrate each step.
3. **Then** build the toolkit ops with that clicker, and only then push clicks toward zero.

Measured baseline to beat (this session, Claude-reads-screenshot method): ~143 gated GUI actions
and ~560 screenshots over ~3.5 h of GUI work — roughly 1.5 min and 4 screenshots per action, with
recurring failure modes (menu-mode from the focus Alt-tap, submenus that open only on real cursor
motion, wrong palette row, foreground stolen by another app, COM/GUI contention hangs).

Benchmarking follows the same order: measure **clicking methods** (vision vs grounder vs
coordinate-from-data macros) on small recurring GUI micro-ops — time, screenshots, clicks,
retries, tokens, verified success — before measuring which model should run them.
