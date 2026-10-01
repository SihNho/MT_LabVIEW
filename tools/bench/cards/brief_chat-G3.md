# Brief chat-G3 - web-only brief for Gemini, then re-verify (user 2026-09-30: "가 적용 후 확인해보도록")

Previous card chat-G2 (result_chat-G2.json, archive/peer/2026-09-30-g2-verify-*.md): with the empty working directory
in place, 3/3 headless agy calls still aborted on `command permission ... auto-denied`. Two causes were read from agy's
trajectories: (1) after `read_url_content` failed, agy tried `Invoke-WebRequest` via run_command; (2) the brief
peer.ps1 inlines for gemini (AGENTS.md, which says to read STATUS.md first, AGENTS.md:57) made agy run `cat STATUS.md`
/ `Get-ChildItem`. The user approved fixing (2) on our side; the agy settings file is NOT to be touched (the permission
classifier refused it; the user may change it by hand later).

## Do
1. In `tools/peer.ps1`, gemini branch only: replace the inlined AGENTS.md brief with a short WEB-ONLY brief: answer
   from web search and web page reading only; there are no local files and no shell - do not try to list, read or run
   anything locally; if a page cannot be read, try another source or search result instead of fetching it another way;
   cite URLs. Keep the read-only guarantees, the empty-cwd change, archive format and every other branch unchanged.
   Edit tool only. Record the before/after md5 and the exact new brief text.
2. Re-run the same 3 verification calls as G2 (`tools/bench/gsearch/g2/verify.sh` or equivalent, gemini-3.1-pro-high):
   (a) the web question, (b) the "list files / quote STATUS.md" probe, (c) the web question again. Record per call:
   ANSWERED/ERROR, seconds, URL count, any run_command attempt read from agy's trajectory (what command), denial text.
3. No Part B comparison in this card. Write `tools/bench/gsearch/g3/verify.log` and a 10-line summary.

## Limits
Rig 실험중: no LabVIEW/GUI/hardware; runner stays stopped; do not touch ~/.gemini; do not edit CLAUDE.md, STATUS.md or
AGENTS.md itself (only what peer.ps1 inlines for gemini). Return one result/1 JSON object.
