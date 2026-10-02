# Brief chat-E1 - refuse a material agent's exit while its own LabVIEW run is still alive (user 2026-10-02)

Decision D-2026-10-02-01, answered by the user: *"재료 에이전트는 중간에 갑자기 종료되지 않도록 장치 넣을 것."*
What happened (three times: 2026-10-02 card 129-2, and twice on 2026-09-17): a material agent launched a LabVIEW run
under `tools/bgrun.py` in the background, wrote a final message like "Waiting for the scratch run to finish" and ended
its turn; ending the agent killed the child, so the run died mid-way (10-35 min lost each time plus a LabVIEW
clean-up). The written rule ("wait in-turn") did not stop it.

## Build (offline only - NO LabVIEW, GUI or hardware; the runner is live, do not touch its LabVIEW)
1. A hook script `tools/hooks/guard_agent_exit.py` for Claude Code's **SubagentStop** event (verify the event name,
   its JSON input fields and the "block = exit code 2 + stderr reason, the agent continues" behaviour against the
   official Claude Code hooks docs first - cite the URL). It must REFUSE the stop (exit 2, short reason telling the
   agent to wait for its run's `BGRUN END` line, e.g. with Monitor/until-loop, then report) when THIS agent still has a
   live `bgrun.py` child it launched: a bgrun log with `BGRUN START`, no `BGRUN END`, and its `BGRUN PID` alive.
   Attribute runs to the agent with data that exists today (e.g. `tools/bench/cards/launches.jsonl` written by
   guard_bash at launch, the agent's transcript path / session or agent id in the hook input, the log paths named in
   the agent's own Bash calls). Never block on runs started by other agents or by the runner itself.
2. Fail OPEN on any read error (a broken guard must never trap an agent forever) and add a loop breaker: after N
   (e.g. 3) refusals for the same run within one agent, allow the stop and log it, so it can never deadlock.
3. Exempt the chat session and runner judgement sessions if they are not subagents (SubagentStop should already
   scope this - confirm).
4. Self-test `tools/bench/selftest_guard_agent_exit.py`: live child -> refuse; child ended (BGRUN END) -> allow; dead
   PID without END -> allow (and say so); run owned by another agent -> allow; unreadable input -> allow; loop
   breaker -> allow on the 4th. Use fake logs and a real short-lived dummy process; no LabVIEW.
5. Do NOT edit `.claude/settings.json`. Return the exact JSON snippet to add under "hooks" (forward-slash path,
   `py "<abs path>"`, timeout) in the result's facts.

Return one result/1 JSON object (facts: docs URL + event semantics, attribution method, self-test counts, snippet).
