---
name: search-the-web-when-troubleshooting
description: External web search is MANDATORY before answering a question or diagnosing an error - whether a peer agent does it or Claude does it alone
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-29T08:23:38.444Z
type: decision
status: in-force
date: 2026-08-29
source: memory/search_the_web_when_troubleshooting.md
---

# External search is mandatory — for questions as much as for errors

The user has now had to give this instruction three times, each time wider than the last, and the
third time out of visible frustration:

1. *"이제는 에러 찾고 트러블슈팅 할때 커뮤니티하고 웹 검색은 꼭 해보자"* — always search when
   hunting an error.
2. *"좀 검색을 해봐라... 그냥 질문을 하면 외부 검색을 기본으로 해보자"* — search by default for any
   question, after Claude declared a CLI had no way to show remaining quota, reasoning only from
   its `--help` output, when the tool in fact has a `/status` command.
3. *"도저히 안되겠다. 멀티 에이전트 활용을 하던 아니면 너 혼자 답변을 하던 외부 검색 세션을 필수로
   넣도록"* — make an external search session **mandatory**, whether it is delegated to a peer agent
   or Claude runs it alone.

So: **before answering a factual question about a tool, an API, an error, or a capability, run an
external search.** Delegating it to a peer agent counts; doing it with Claude's own web tools
counts; skipping it does not. If both peers are out of quota, Claude runs the search itself — the
obligation belongs to the task, not to any particular agent.

The failure mode being corrected is not laziness but **false confidence from local evidence**. A
`--help` listing does not enumerate interactive slash commands. A config schema does not describe
runtime behaviour. An API surface does not reveal a vendor's known bugs. Concluding "there is no
way to do X" because the material at hand did not mention X is the specific error to stop making:
**absence in what you happen to be looking at is not evidence of absence.** One search costs
seconds; a wrong conclusion costs the user a correction and costs Claude its credibility.

**The concrete trigger, added after breaking this rule hours after codifying it:** the moment a
sentence forms that says *"X is not possible"*, *"our tools cannot reach that"*, or *"so we have to
fall back to <slower method>"* — **that is the trigger**. Do not treat it as settled knowledge
about your own toolkit; it is a factual claim about a capability and needs a search or a peer
before it drives any work.

The incident: Claude concluded that a LabVIEW terminal could not be wired by script (the fleet's
wiring op only reaches Node objects) and switched to GUI clicking, burning a dozen-plus calls and
provoking a hang. The library in use had a VI named `Conditionally Connect Wire.vi` built for
exactly that, **and its name was already sitting in a directory listing Claude had printed earlier
in the same session.** The rule did not fire because the question was misfiled as "a known limit of
my own tools" rather than "a factual question about a capability". That distinction is not real —
your own toolkit is exactly the thing you are most likely to be wrong about, because nobody has
written its limits down.

Two earlier incidents make the cost concrete: a LabVIEW error code chased through five experiments
and hundreds of parameter values when one forum query held the answer, and a claim that quota could
not be inspected when the CLI has a documented command for exactly that.

The search result is still only a hypothesis. Confirm it against the machine or the vendor's own
files before acting — searching first and verifying after are both required, and neither replaces
the other.
