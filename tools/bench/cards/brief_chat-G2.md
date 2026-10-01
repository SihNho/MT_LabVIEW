# Brief chat-G2 - Gemini web-search RE-TEST after two fixes (user 2026-09-30: "제미나이는 재시험 진행")

Previous test: `tools/bench/gsearch/report_g1.md` (card chat-G1). gemini-3.1-pro-high answered 10/14 correct and lost
4/14 to agy's headless `command` auto-deny; one correct answer read OUR repo (agy cwd = project root,
`tools/peer.ps1` Set-Location). Opus (fact role, effort medium) was never wrong but only "partly" on all 6 LabVIEW /
IMAQdx answers. The user approved both fixes and a re-test focused on LabVIEW topics with an Opus HIGH arm added.

## Part A - two fixes, then verify
1. **agy user settings** (`~/.gemini/antigravity-cli/settings.json` or wherever agy actually reads them - find it from
   agy's help / the file on disk). FIRST copy the original to `tools/bench/gsearch/gemini_settings_backup_<ts>.json`
   and record its md5. Then change permissions so a headless run does not stall on `command`:
   SAFE DIRECTION ONLY - allow web reading/search tools; either keep shell commands denied explicitly, or allow only
   read-only fetch-like commands if agy's schema supports command patterns. NEVER a blanket allow of shell commands,
   file writes or edits. Record the exact diff.
2. **Neutral working directory** in `tools/peer.ps1`, gemini branch only: run agy from a fresh EMPTY temp directory
   (created per call, removed after), so it cannot read project files. Edit tool only; codex/claude branches untouched;
   no role default changed. The archive/output paths must still land in the project as before.
3. Verify with 3 headless calls: (a) a web question - URLs present, no denial; (b) "list the files in your current
   directory and quote the first line of STATUS.md" - must show an empty directory / no STATUS.md content;
   (c) repeat (a). If A fails within the failure budget, restore the backup, STOP, return FAIL with denial text.

## Part B - LabVIEW-focused comparison (only if A passes)
- Cases: keep G1-G3 from `tools/bench/gsearch/cases.json` and ADD 4-5 NEW known-answer cases on our narrow topics
  (LabVIEW VI Scripting / VI Server properties and methods, IMAQdx, NI-VISA serial, LabVIEW COM/ActiveX), each with
  verifying evidence file:line from `archive/peer/`, `docs/NAMES.md` or a measurement log. Neutral wording, no leaked
  answer. Store as `tools/bench/gsearch/cases_g2.json`.
- Arms, 2 repeats each, same question text: `gemini-pro` (-Model gemini-3.1-pro-high), `opus-medium` (current fact
  role as-is), `opus-high` (same fact role settings, effort high - use a peer.ps1 override if one exists, otherwise a
  direct call with the identical thin/web/plan settings; state which). Drop the gemini default model (8/14 timeouts).
- Blind scorer as in G1 (claude Sonnet, thin, question + known answer + anonymised answer).
- Report `tools/bench/gsearch/report_g2.md`: per case x arm table (grade / seconds / URLs / primary y/n), totals,
  failures by cause, Claude usd per arm, and any answer citing project files. Numbers only; the chat decides.

## Limits
Rig state 실험중: no LabVIEW, GUI or hardware. Runner stays stopped. Do not edit CLAUDE.md / STATUS.md. Keep the agy
settings change in place after the test (the user approved it) but report the exact diff and the backup path.
Return one result/1 JSON object.
