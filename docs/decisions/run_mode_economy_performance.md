---
name: usage-controlled-manually-no-self-imposed-limits
description: "The user's 2026-09-29 rule — no self-imposed usage limits: the weekly 50 % economy/performance run mode, 5-hour and weekly gates, and ultracode caps are all retired; the user watches usage in real time and controls it by hand (supersedes the 2026-09-28 run-mode rule)"
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-29T09:36:20.768Z
type: decision
status: in-force
date: 2026-09-29
source: memory/run_mode_economy_performance.md
---

# Usage is controlled manually by the user (2026-09-29); the run mode is retired

On 2026-09-29, after a benchmark day pushed weekly usage from 13 % to 34 % and I proposed ultracode limits, the user
ruled: "5시간 한도 및 주간 사용량 제한은 폐기하도록 하자. (이전에 주간 사용량 관련해서 50% 숫자를 한계로 뒀는데 이것도
없애는게 좋을 것 같음. 생각해보면 어차피 이제 LabVIEW 사용을 종종 할거라 그 동안에는 사실상 하네싱에 한계가 생김.)
사용량은 내가 실시간으로 체크하고 매뉴얼하게 통제하는게 좋아보임." Their reason: once LabVIEW is used by the experiments
often, the harness is idle much of the time anyway, so automatic throttling mostly costs speed.

History: on 2026-09-28 they had set a two-mode rule (weekly usage above a fixed 50 % = economy, one card at a time;
at/below = performance, pipeline on), refreshed by the chat every 30 min. That rule is now OFF:
`tools/bench/run_mode_config.json` has `disabled: true` (threshold logic kept in `tools/run_mode.py`, self-test 7/7, so
the user can switch it back).

## How I apply it

- Do not add or propose automatic usage gates (5-hour, weekly, per-run token caps, ultracode agent caps or
  one-at-a-time rules). Report spend facts when asked or when something runs far above my estimate — and when a
  job I launched is burning usage much faster than I told the user, stop it and report, as I did with B4.
- Estimate a job's cost honestly before launching it, and say the number; the user controls from that.
- The PLATFORM usage-limit protocol still applies: when a real limit is hit, schedule resume at renewal + 2 min and
  rerun any interrupted benchmark from the start.
- The chat no longer writes `run_mode.json` every 30 min.
