<#
    peer.ps1 — dispatch a read-only research question to a peer agent (Codex or Gemini/Antigravity).

    Per CLAUDE.md rule 5: peers are read-only advisers; Claude keeps all judgement and is the only
    execution path that touches LabVIEW. This wrapper enforces the operational half of that rule:

      * READ-ONLY, MECHANICALLY. Codex runs under `--sandbox read-only`; agy runs in `--mode plan`
        without `--dangerously-skip-permissions`, so neither can edit files or run commands.
      * NEVER BLOCKS THE WORK. A hard timeout (default 180 s) bounds every call. The user runs both
        peers on cheap subscriptions that can cut out mid-session; waiting on an answer that will
        never come is the worst case, not a slow answer.
      * CLASSIFIES THE OUTCOME as ANSWERED / TIMEOUT / QUOTA / ERROR. On QUOTA, stop calling that
        agent for the rest of the session (the next call fails the same way) — the caller checks
        the marker file this script writes.
      * ARCHIVES EVERY EXCHANGE to archive/peer/YYYY-MM-DD-<slug>.md (question, answer, outcome,
        and WHICH MODEL ANSWERED). Claude fills in the verdict and sources afterwards; see
        archive/peer/README.md.
      * RECORDS THE MODEL (added 2026-09-15). Until then the archive named only the agent, so none
        of the 216 earlier exchanges can be attributed to a model after the fact — and since this
        script passes no model flag by default, the answer came from whatever the CLI's own config
        happened to hold that day. The effective model is now read at dispatch time (codex: the
        top-level `model` / `model_reasoning_effort` in ~\.codex\config.toml) and written into the
        archive header. `-Model` / `-Effort` pin it explicitly instead.

    Usage (from the project root):
      .\tools\peer.ps1 -Agent codex  -Slug style-codes -Task "question text ..."
      .\tools\peer.ps1 -Agent gemini -Slug style-codes -Task "question text ..." -Image shot.png
      .\tools\peer.ps1 -Agent codex  -Task "..."            # slug defaults to a timestamp
      .\tools\peer.ps1 -Agent codex  -Task "..." -Model gpt-5.6-sol -Effort high
      .\tools\peer.ps1 -Agent gemini -Task "..." -Model gemini-3.1-pro-high   # `agy models` lists them
      .\tools\peer.ps1 -Agent claude -Task "..."                     # sonnet; -Model opus if it earns it
      .\tools\peer.ps1 -Agent claude -Role hypothesis -Slug x -Task "..."  # FAILED-PREDICTION reviewer:
                                                                           # opus / effort max, WEB SEARCH ALLOWED
      .\tools\peer.ps1 -Kind fact  -Slug x -Task "..."      # no -Agent => claude / role fact  (opus-5-5, medium, thin)
      .\tools\peer.ps1 -Kind prose -Slug x -TaskFile f.md   # no -Agent => claude / role prose (opus-5-5, medium, thin)
      .\tools\peer.ps1 -Dual -Slug x -TaskFile q.md   # the SAME task to codex AND the hypothesis role,
                                                      # archived as <date>-x-codex.md and <date>-x-opus.md
      .\tools\peer.ps1 -Agent codex  -Kind prose -Slug x -TaskFile fact-list.md  # codex AUTHORS the report from
                                                                                 # a fact list; archives to archive\prose\
      .\tools\peer.ps1 -Kind fact -Slug x -Task "..." -DryRun   # resolve agent/model/effort/tools, print, dispatch NOTHING
      .\tools\peer.ps1 -CheckQuota                          # report which agents are marked out

    THE THREE PEERS (rule 5's ladder; one peer per question, both others only to cross-check):
      codex  - reads the project dir (read-only sandbox) and the web. Pinned: gpt-5.6-sol / medium.
               STILL SELECTABLE, never a default any more (see below).
      gemini - web only; the brief is inlined because agy does not scan AGENTS.md. Unchanged fallback.
      claude - reads the project dir; NO web unless the role's own tool list allows it. Added 2026-09-15
               so the review structure survives an external quota outage.

    2026-09-18 - CODEX'S ROLES MOVE TO CLAUDE SUB-SESSIONS (user, TRIAL: "Codex 잔여량이 생각보다 얼마 남지
    않음. 주간 한도 9% 남았음. 아무래도 Codex가 수행중인 역할을 fable로 구동하는게 어떨까 싶음." +
    "우선은 지금 말한 방법으로 몇 번 돌려보자"). The role -> model table for -Agent claude:

      role        model / effort   web   prompt                         who dispatches it
      ----------  ---------------  ----  -----------------------------  ----------------------------------
      audit       sonnet           no    AGENTS.md brief + CLAUDE.md    -Agent claude, no -Role
      priorart    opus / high      no    AGENTS.md brief + CLAUDE.md    prior_art_review.py
      ingest      sonnet           no    AGENTS.md brief + CLAUDE.md    doc_ingest.py
      hypothesis  opus-5-5 / high  YES   AGENTS.md brief + CLAUDE.md    failed-prediction reviews (SINGLE arm)
      fact        opus-5-5 / med   YES   THIN (task only)               -Kind fact with no -Agent
      outcome     fable / medium   YES   THIN (task only)               outcome_review.py; the retrospective
                                                                        uses this role pinned -Model claude-opus-5-5
                                                                        -Effort high (user table 2026-09-27)
      prose       opus-5-5 / med   no    THIN (REPORT WRITER preamble)  -Kind prose with no -Agent
    (fact/prose were fable/low 2026-09-18 .. 2026-09-27; moved by the user's model table, card chat-N4.)

    THIN = the cell runs with `--safe-mode`, which skips CLAUDE.md auto-discovery, skills, plugins, hooks and
    MCP servers while leaving auth, model selection, built-in tools and permissions normal (claude --help).
    That is the whole point of the three fable roles: the measured FIXED cost of loading this project's context
    into a peer cell is ~158,000 cache-creation tokens - $1.86 on the opus/max arm of the 2026-09-17 -Dual
    self-test - before the cell reads a single file. A pure API fact, an outcome question and a report do not
    need the project's rules in the system prompt.

    Exit codes: 0 answered · 2 timeout · 3 quota exhausted · 4 error · 5 agent marked out earlier
#>
[CmdletBinding()]
param(
    [ValidateSet('codex', 'gemini', 'claude')]
    [string]$Agent,

    [string]$Task,

    # The task body read from a UTF-8 FILE instead of -Task. Needed because a prose block is long and full of
    # quotes, backticks and newlines - exactly the argv content PowerShell 5.1 mangles (see the stdin note below).
    # -Task still works; -TaskFile wins if both are given.
    [string]$TaskFile = '',

    [string]$Slug = (Get-Date -Format 'HHmmss'),

    [string]$Image = '',

    [int]$TimeoutSec = 180,

    # Pin the peer's model / reasoning effort. Empty = the CLI's own default, which is what every
    # call before 2026-09-15 used. The value is recorded either way.
    [string]$Model = '',

    [string]$Effort = '',

    # 'review' = anything whose answer will drive work: a diagnosis, a plan, a claim under test. The
    # peer is then MADE adversarial (see below) and confirm-bait is refused. 'fact' = a pure API/tool
    # fact with no framing to attack. Default is the strict one, so forgetting the flag is safe.
    # 'prose' = REPORT AUTHORING, not research and NOT proofreading (user, 2026-09-16: "보고는 검수를 받는게
    # 아니라 그냥 chatgpt cli에 의존하는게 좋을 것 같은데? 그냥 클로드와 코덱스는 문체가 달라"). The task body is
    # a FACT LIST - bullets, numbers, paths, headings - and codex WRITES the user-facing report from it. The
    # earlier proofreading variant was rejected the same day: rewriting Claude's sentences keeps Claude's
    # sentence shapes. It is not a claim under test, so the adversarial suffix and the confirm-bait check are
    # both OFF, and it archives to archive\prose\ so it never feeds guard_peer / prior-art / violations
    # counting - those all glob archive\peer\ only (verified 2026-09-16). See .claude/agents/reporter.md.
    [ValidateSet('review', 'fact', 'prose')]
    [string]$Kind = 'review',

    # Which claude-peer job this is. The two read almost disjoint file sets, so they are separate sessions
    # (user's decision, 2026-09-15): `audit` reads CLAUDE.md and the current docs; `priorart` reads the logs, the
    # code and the ARCHIVE. Ignored for codex and gemini.
    # 'ingest' added 2026-09-16 (CLAUDE.md section 4, "Documents are LINTED by code and INGESTED by a model every
    # cycle"). A ROLE, not a new -Kind: the prior-art review of docs/doc-lint-plan.md fired `helper-exists` on the
    # grounds that -Role already distinguishes claude-peer jobs (prior_art_review.py passes -Role priorart), so a
    # fourth -Kind would be a second mechanism for the same distinction. The dispatch stays -Kind fact.
    # Its archive goes to archive\ingest\ for the same reason -Kind prose goes to archive\prose\: guard_peer.py,
    # guard_cycle.py, violations.py, outcome_review.py AND audit_cycle.py (A3 at :165 and A4 at :134) all glob
    # archive\peer\ only. The prior-art review caught what the plan had missed: an ingest pass landing in
    # archive\peer\ would satisfy A3 for EVERY failing log in the window - "a peer exchange was archived after it" -
    # and would then be demanded a disposition by A4. It must be invisible, and it is, by directory.
    # 'hypothesis' added 2026-09-17 (CLAUDE.md rule 5, "Hypothesis reviews are being moved to an Opus/max Claude
    # peer"). The FAILED-PREDICTION reviewer, run under codex's exact constraints - read-only, adversarial preamble
    # (-Kind review's suffix), bounded timeout, archived to archive\peer\ so every gate sees it - with two
    # differences the user asked for: OPUS at effort MAX ("opus는 high 보다 더 높게 잡아도 문제 없을 것 같은데"),
    # and WEB SEARCH ALLOWED, which no other claude role gets. Rule 5's ladder says the claude peer has no web; this
    # role is the measured exception, because a failed-prediction review that cannot search is exactly the "false
    # confidence from local evidence" the external-search rule exists to stop.
    # NOTE: this role does NOT by itself amend D3 ("the claude peer cannot discharge a failed prediction") -
    # guard_peer.py still requires codex/gemini. That is why -Dual exists: the next five failed predictions go to
    # BOTH, and the archive's cost lines are the comparison data.
    # 'fact', 'outcome' and 'prose' added 2026-09-18 (user's trial: codex's roles move to claude sub-sessions).
    # They are the THIN roles - fable, --safe-mode, no AGENTS.md brief, no CLAUDE.md - and they are resolved
    # AUTOMATICALLY from -Kind when no -Agent is given, so the callers do not have to know the table.
    [ValidateSet('audit', 'priorart', 'ingest', 'hypothesis', 'fact', 'outcome', 'prose')]
    [string]$Role = 'audit',

    # Dispatch the SAME task to codex AND the hypothesis role, archiving both under <slug>-codex / <slug>-opus.
    # One call, two exchanges, so the comparison is on identical wording (a re-typed question is a different
    # question). Exit code is codex's, because guard_peer.py still only counts codex/gemini.
    [switch]$Dual,

    # Resolve agent / role / model / effort / tools / archive path, PRINT them, dispatch NOTHING and exit 0.
    # Added 2026-09-18 so a routing change can be checked without spending a call (the thing the -Dual
    # self-test could not do). Not -WhatIf: that name needs SupportsShouldProcess, which would also attach
    # -Confirm semantics to a script that has no state to confirm.
    [switch]$DryRun,

    # SESSION PROTOCOL v1, C4/C5 (docs/session-protocol.md, user-approved 2026-09-24): a review/1 card
    # (tools/bench/cards/review_<id>.json). It is validated (an invalid card is REFUSED, nothing dispatched), rendered
    # in front of the task, and the VERDICT CONTRACT is appended at the end; the peer's last line must then be
    # `VERDICT {verdict/1 json}`, which is parsed into tools/bench/cards/verdict_<id>.json. The archive keeps the full
    # prose exchange as before and records the parse result on its `verdict-card:` line.
    [string]$ReviewCard = '',

    [switch]$CheckQuota
)

$ErrorActionPreference = 'Stop'
# This script's own stdout is captured by bgrun and read back as UTF-8. Without this, Write-Output of a Korean
# answer reaches the log as cp949 mojibake (measured 2026-09-16 on the first -Kind prose run).
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$root = Split-Path -Parent $PSScriptRoot
$peerDir = Join-Path $root 'archive\peer'
$proseDir = Join-Path $root 'archive\prose'
$ingestDir = Join-Path $root 'archive\ingest'
$quotaDir = Join-Path $env:TEMP 'peer_quota_markers'
if (-not (Test-Path $quotaDir)) { New-Item -ItemType Directory -Force $quotaDir | Out-Null }

if ($CheckQuota) {
    $markers = Get-ChildItem $quotaDir -Filter '*.out' -ErrorAction SilentlyContinue
    if (-not $markers) { Write-Output 'all agents available' }
    else { $markers | ForEach-Object { Write-Output ("OUT: $($_.BaseName) since $($_.LastWriteTime)") } }
    return
}

if ($TaskFile) {
    if (-not (Test-Path $TaskFile)) { throw "-TaskFile not found: $TaskFile" }
    $Task = Get-Content -Path $TaskFile -Raw -Encoding UTF8
}

# C4: the review/1 card, rendered by tools/protocol.py (ONE renderer; this script does not restate the schema).
$verdictId = ''
$verdictContract = ''
if ($ReviewCard -and -not $Dual) {
    $protoPy = Join-Path $PSScriptRoot 'protocol.py'
    $cardBlock = (& py $protoPy render-review $ReviewCard --part card | Out-String)
    if ($LASTEXITCODE -ne 0) { throw "REFUSED by peer.ps1: -ReviewCard $ReviewCard is not a valid review/1 card: $cardBlock" }
    $verdictContract = (& py $protoPy render-review $ReviewCard --part contract | Out-String)
    $verdictId = ((Get-Content $ReviewCard -Raw -Encoding UTF8) | ConvertFrom-Json).id
    $Task = $cardBlock + "`n" + $Task
}

# --- DEFAULT ROUTING (user's decision, 2026-09-18, TRIAL) -------------------------------------------------
# codex is at 9 % of its weekly quota, so the roles it held move to claude sub-sessions and codex stops being
# a default. Only -Kind decides, and only when the caller named no -Agent: an explicit -Agent codex (or gemini)
# is still honoured exactly as before, which is what keeps the ladder's fallback usable.
#   -Kind fact  -> claude / role fact  (fable, low,    thin)
#   -Kind prose -> claude / role prose (fable, low,    thin)
#   -Kind review-> NOT defaulted: a review's reviewer is a judgement call (hypothesis vs audit vs gemini).
# $PSBoundParameters is how "the caller passed -Role" is distinguished from "the parameter has its default
# value 'audit'" - prior_art_review.py and doc_ingest.py both pass -Role explicitly and are untouched by this.
$roleExplicit = $PSBoundParameters.ContainsKey('Role')
if (-not $Agent -and -not $Dual -and -not $CheckQuota) {
    if ($Kind -eq 'fact' -or $Kind -eq 'prose') { $Agent = 'claude' }
}
if ($Agent -eq 'claude' -and -not $roleExplicit) {
    if ($Kind -eq 'fact') { $Role = 'fact' } elseif ($Kind -eq 'prose') { $Role = 'prose' }
}
# A thin role is meaningless for codex/agy (they have no CLAUDE.md to skip); say so rather than silently
# dispatching a claude-shaped call to another CLI.
if ($Agent -and $Agent -ne 'claude' -and $roleExplicit -and $Role -in @('fact', 'outcome', 'prose')) {
    throw "-Role $Role is a claude-only role (peer.ps1's role table). Drop -Role for -Agent $Agent."
}
# -Dual: ONE question, TWO reviewers, identical wording. Re-invokes this same script twice so every mechanism
# below (read-only flags, confirm-bait refusal, adversarial suffix, timeout, outcome classification, archiving,
# cost line) applies to both arms unchanged - a second copy of the dispatch logic would drift from this one.
# The task always travels as a FILE to the children: argv quoting is what -TaskFile exists to avoid.
if ($Dual) {
    if (-not $Task) { throw '-Dual needs -Task or -TaskFile.' }
    $dualFile = Join-Path $env:TEMP ("peer_dual_{0}.txt" -f (Get-Random))
    Set-Content -Path $dualFile -Value $Task -Encoding utf8
    # HASHTABLE splat, not an array one: an array splat passes its elements POSITIONALLY, so '-Kind' landed on
    # $Agent and 'fact' on $TaskFile (measured on the first self-test run, `peer_dual_selftest.log`).
    $common = @{ Kind = $Kind; TimeoutSec = $TimeoutSec; TaskFile = $dualFile }
    if ($Image) { $common['Image'] = $Image }
    if ($ReviewCard) { $common['ReviewCard'] = $ReviewCard }

    Write-Output "=== DUAL ARM 1/2: codex -> $Slug-codex ==="
    & $PSCommandPath -Agent codex -Slug "$Slug-codex" @common
    $rcCodex = $LASTEXITCODE

    Write-Output "=== DUAL ARM 2/2: claude/hypothesis (opus, effort max, web) -> $Slug-opus ==="
    & $PSCommandPath -Agent claude -Role hypothesis -Slug "$Slug-opus" @common
    $rcOpus = $LASTEXITCODE

    Remove-Item $dualFile -Force -ErrorAction SilentlyContinue
    Write-Output "=== DUAL DONE: codex rc=$rcCodex, opus rc=$rcOpus  (archive\peer\$(Get-Date -Format 'yyyy-MM-dd')-$Slug-codex.md, -$Slug-opus.md) ==="
    exit $rcCodex
}

if (-not $Agent -or -not $Task) { throw 'Both -Agent and -Task are required (or use -CheckQuota, or -TaskFile).' }

$marker = Join-Path $quotaDir "$Agent.out"
if (Test-Path $marker) {
    Write-Output "SKIPPED: $Agent was marked quota-exhausted at $((Get-Item $marker).LastWriteTime). Delete $marker to retry."
    exit 5
}

# THE PEER MUST BE ASKED TO REFUTE (user, 2026-09-15, after cycle 7's retrospective found several
# prompts that said "BRIEF CONFIRM" — the exact opposite of rule 5). Two mechanisms, because either
# alone is weak: the adversarial instruction is APPENDED by the script so it cannot be forgotten, and
# confirm-bait in the question itself is REFUSED, because a leading question survives any suffix.
# Kept ASCII deliberately: this file is read by PowerShell 5.1, which decodes a BOM-less script as the
# system ANSI page (cp949 here). A Korean literal at the END of a string swallowed the closing quote and
# broke the parser on 2026-09-15 - measured, not guessed. The file now carries a UTF-8 BOM as well, but
# the regex stays in \u escapes so it survives any later re-save that loses the BOM.
$confirmBait = 'brief(ly)?\s+confirm|please\s+confirm|confirm\s+(that|this|my|the)|sanity[- ]?check|' +
               'do you agree|am i right|validate my|' +
               '확인\s*(만|좀|부탁)|검토\s*부탁'
if ($Kind -eq 'review') {
    if ($Task -match $confirmBait) {
        throw ("REFUSED by peer.ps1: the task asks the peer to CONFIRM (matched '$($Matches[0])'). " +
               "Rule 5: a peer used as adversary must be asked to REFUTE. Rewrite the question as an " +
               "attack on your own claim — or pass -Kind fact if this is a pure API/tool fact with no " +
               "framing to attack.")
    }
    $Task = $Task + @"


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.
"@
}
if ($verdictContract) { $Task = $Task + $verdictContract }

# Peers must not be steered into the archive; AGENTS.md already forbids it, repeat it per-call.
$preamble = 'You are a read-only research assistant. Never run or modify anything. ' +
            'Cite a URL for every external claim. '

# Codex loads AGENTS.md natively (verified). agy does NOT scan it (verified: zero mentions in its
# log) and headless mode auto-denies its file tools, so for agy the brief is inlined into the prompt.
if ($Agent -eq 'gemini') {
    $brief = Get-Content (Join-Path $root 'AGENTS.md') -Raw
    $preamble = "Your project brief follows between the markers; obey it.`n--- BRIEF ---`n$brief`n--- END BRIEF ---`n"
}
# A claude cell loads CLAUDE.md automatically - which addresses the SESSION that owns the work, not
# a reviewer. Say plainly which role this cell holds, or it will try to take the lock and build.
if ($Agent -eq 'claude' -and $Role -eq 'priorart') {
    $brief = Get-Content (Join-Path $root 'AGENTS.md') -Raw
    $preamble = "You are this project's PRIOR-ART REVIEWER. You are not judging whether the plan is good - other " +
                "reviews do that. You answer ONE question: HAS THIS ALREADY BEEN DONE HERE? Already built under " +
                "another name, already measured and written down, already tried and failed, already provided by an " +
                "existing helper, or contradicted by something else in these files.`n" +
                "**READING `archive/` IS YOUR JOB.** CLAUDE.md rule 4 tells ordinary work not to read it; that rule " +
                "does NOT apply to you. The archive is where failed attempts and superseded decisions live, and " +
                "missing one is the exact failure you exist to prevent. Read archive/peer/ and archive/*.md freely, " +
                "along with tools/bench/*.log, tools/recipes/, tools/gscript.py and docs/.`n" +
                "Cite a FILE and LINE for every finding - a verdict with no citation cannot be acted on, and the " +
                "only way this review is ever released is by someone opening your citation and showing in writing " +
                "that it does not cover their case. Your citations are therefore the whole product.`n" +
                "Do NOT take the LabVIEW lock, build, edit or run anything. Your brief follows.`n" +
                "--- BRIEF ---`n$brief`n--- END BRIEF ---`n"
}
elseif ($Agent -eq 'claude' -and $Role -eq 'ingest') {
    # THE MODEL HALF OF THE DOCUMENT LINT (CLAUDE.md section 4). It is the SAME rule/consistency auditor role as
    # below - the prior-art review's `helper-exists` finding says so explicitly ("peer.ps1:181 already defines the
    # RULE AND CONSISTENCY AUDITOR preamble and :250 already pins it to sonnet for this exact role") - narrowed to
    # one question and forbidden to recommend anything. Resolving a contradiction is judgement work; this layer
    # only finds them.
    $brief = Get-Content (Join-Path $root 'AGENTS.md') -Raw
    $preamble = "You are this project's RULE AND CONSISTENCY AUDITOR, running the per-cycle DOCUMENT INGEST. " +
                "You answer exactly one question about the files listed below: WHICH STATEMENTS CONTRADICT EACH " +
                "OTHER, or contradict CLAUDE.md or STATUS.md?`n" +
                "Report contradictions ONLY. No recommendations, no ranking, no opinion about which side is " +
                "right - the judgement session decides that, and a recommendation from you is a decision taken " +
                "in the wrong place. Cite file:line for BOTH sides of every pair; a pair without two citations " +
                "is not reportable. A summary line that contradicts its own section 40 lines earlier counts, and " +
                "has happened here.`n" +
                "Do NOT take the LabVIEW lock, do not build, do not edit, do not run anything. Your brief " +
                "follows between the markers.`n" +
                "--- BRIEF ---`n$brief`n--- END BRIEF ---`n"
}
elseif ($Agent -eq 'claude' -and $Role -eq 'hypothesis') {
    # THE FAILED-PREDICTION REVIEWER (user, 2026-09-17). Same job codex has held: attack the framing of a
    # diagnosis formed under pressure. -Kind review appends the four-part adversarial instruction set after this,
    # so this preamble does NOT repeat it; it states the role, and the one capability no other claude role has.
    $brief = Get-Content (Join-Path $root 'AGENTS.md') -Raw
    $preamble = "You are this project's FAILED-PREDICTION REVIEWER. Something was predicted and something else " +
                "was observed, and the explanation you are about to read was written AFTER the observation, under " +
                "pressure, by the session that chose the failing experiment. Your job is to attack that framing - " +
                "not to check arithmetic, and not to be helpful.`n" +
                "**WEB SEARCH IS PART OF YOUR JOB, and you are the one claude role that has it.** Use WebSearch " +
                "and WebFetch on every factual claim about a tool, an API, an error code or a capability - " +
                "including claims about LabVIEW VI Scripting property/method IDs and about what this project's " +
                "own tools can or cannot do. CLAUDE.md: absence in what you happen to be looking at is not " +
                "evidence of absence. Cite a URL for every external claim.`n" +
                "You may also read this project's files (docs/, tools/, tools/bench/*.log, archive/) to check the " +
                "claim against what the machine actually recorded. Cite file:line for every local claim.`n" +
                "Say plainly when the evidence does not settle the question - 'the measurement does not " +
                "distinguish these two causes' is a more useful answer than a confident wrong one.`n" +
                "Do NOT take the LabVIEW lock, do not build, do not edit, do not run anything. Your brief " +
                "follows between the markers.`n" +
                "--- BRIEF ---`n$brief`n--- END BRIEF ---`n"
}
elseif ($Agent -eq 'claude' -and $Role -eq 'fact') {
    # THIN. No AGENTS.md, no CLAUDE.md (--safe-mode below): a pure API/tool/error fact has no project framing to
    # attack and needs no project rules to answer. The generic read-only preamble set above is the whole prompt.
    $preamble = $preamble + "You have WebSearch and WebFetch. Answer the question below and nothing else. " +
                "If the evidence does not settle it, say so instead of guessing.`n"
}
elseif ($Agent -eq 'claude' -and $Role -eq 'outcome') {
    # THIN. The outcome review's SEVEN QUESTIONS travel in the task (tools/outcome_review.py), together with the
    # counted output and the paths to read - so the question set is identical to the one codex answered, and the
    # only thing removed is the project context the cell would otherwise load before reading anything.
    $preamble = "You are this project's OUTCOME REVIEWER. You judge RESULTS, not process: the cycles have already " +
                "been reviewed for how they were run. You are the one reviewer whose job is to say that work was " +
                "not worth doing, so do not soften it.`n" +
                "Read the files the task names - they are in the current directory - and cite the file or log " +
                "behind every judgement. WebSearch and WebFetch are available; cite a URL for any external claim.`n" +
                "Do NOT build, edit or run anything. Answer the numbered questions in order and end with the " +
                "machine-readable lines the task specifies.`n"
}
elseif ($Agent -eq 'claude' -and $Role -eq 'prose') {
    # THIN, and the REPORT WRITER preamble below ($Kind -eq 'prose') replaces this entirely. Named here only so a
    # `-Role prose` cell can never fall through to the audit branch and load the brief it must not have.
    $preamble = ''
}
elseif ($Agent -eq 'claude') {
    $brief = Get-Content (Join-Path $root 'AGENTS.md') -Raw
    $preamble = "You are this project's RULE AND CONSISTENCY AUDITOR — a peer reviewer, not the session " +
                "doing the work. Your specific job, the one the other two peers cannot do: check the claim " +
                "against what THIS project's own files actually say. Does it match the logs, docs/NAMES.md " +
                "and the archived reviews? Does the plan violate a rule in CLAUDE.md (rule 1 originals, " +
                "rule 1a computation-preserving, the GUI-only-when-scripting-is-impossible gate, the " +
                "verification-level rule)? Quote the file and line you are relying on. You are NOT the " +
                "framing adversary — codex and agy hold that role.`n" +
                "CLAUDE.md is loaded for context only: do NOT take the LabVIEW lock, do not build, do not " +
                "edit, do not run anything. Read files and answer. Your brief follows between the markers.`n" +
                "--- BRIEF ---`n$brief`n--- END BRIEF ---`n"
}
# REPORT AUTHORING, not research and not proofreading. Overrides every role preamble above: a prose cell is not a
# reviewer, it does not read the project, and it must not judge the content - it writes the report the user reads.
# Kept ASCII for the same reason as $confirmBait - a Korean literal in this file broke PowerShell 5.1's parser once
# already (2026-09-15, measured).
if ($Kind -eq 'prose') {
    $preamble = @"
You are the REPORT WRITER. What follows is a FACT LIST - bullets, numbers, file paths, headings - collected by
someone else. Write the report from it. Do not proofread it, do not rewrite it sentence by sentence: the fact
list is raw material, the report is yours to compose. Rules, all mandatory:
 1. Write in plain, natural Korean for the person who runs this lab. If the facts are written in English, write
    the report in plain, natural English instead.
 2. Keep every number, file path, file name, code span, identifier, command line, quoted sentence and technical
    term EXACTLY as given, character for character. Do not translate them and do not "correct" them.
 3. Add no facts that are not in the list. Drop no facts that are in it.
 4. No hedges, no praise, no preamble, no commentary about what you did.
 5. Keep the caller's section order and headings.
 6. If the fact list ends with a question for the user, end the report with that question.
 7. Output ONLY the report. No explanation, no code fence around the whole answer.
--- FACT LIST ---
"@
}
$prompt = $preamble + $Task

$outFile = Join-Path $env:TEMP ("peer_{0}_{1}.txt" -f $Agent, (Get-Random))
$npmDir = Join-Path $env:APPDATA 'npm'
$agyDir = Join-Path $env:LOCALAPPDATA 'agy\bin'
$claudeDir = Join-Path $env:USERPROFILE '.local\bin'
$env:Path = "$env:Path;$env:ProgramFiles\nodejs;$npmDir;$agyDir;$claudeDir"

# The prompt travels via STDIN, never argv: PowerShell 5.1 mangles native-command arguments that
# contain double quotes (AGENTS.md has plenty), silently splitting the prompt into stray arguments.
$promptFile = Join-Path $env:TEMP ("peer_prompt_{0}.txt" -f (Get-Random))
Set-Content -Path $promptFile -Value $prompt -Encoding utf8

# WHICH MODEL IS ABOUT TO ANSWER. Read it, never assume it: with no -Model the answer comes from
# the CLI's own config, which the user can change between sessions (and did, on 2026-09-15 14:48).
# Top-level TOML keys precede the first [table], so the scan stops there.
$usedModel = ''; $usedEffort = ''; $modelSrc = ''
if ($Agent -eq 'codex') {
    $cfgModel = ''; $cfgEffort = ''
    $cfgPath = Join-Path $env:USERPROFILE '.codex\config.toml'
    if (Test-Path $cfgPath) {
        foreach ($line in (Get-Content $cfgPath)) {
            if ($line -match '^\s*\[') { break }
            if ($line -match '^\s*model\s*=\s*"([^"]+)"') { $cfgModel = $Matches[1] }
            elseif ($line -match '^\s*model_reasoning_effort\s*=\s*"([^"]+)"') { $cfgEffort = $Matches[1] }
        }
    }
    # PINNED HERE, not inherited. The user chose gpt-5.6-sol at medium effort for peer work on
    # 2026-09-15. ~\.codex\config.toml is the user's own interactive Codex setting and it changed
    # mid-session once already; a review must not silently switch model because of that.
    $usedModel = if ($Model) { $Model } else { 'gpt-5.6-sol' }
    $usedEffort = if ($Effort) { $Effort } else { 'medium' }
    $modelSrc = if ($Model -or $Effort) { 'pinned by -Model/-Effort' } else { 'peer.ps1 default (user, 2026-09-15)' }
    if ($cfgModel -and $cfgModel -ne $usedModel) {
        Write-Output "NOTE: ~\.codex\config.toml says model=$cfgModel/$cfgEffort; this dispatch uses $usedModel/$usedEffort."
    }
} elseif ($Agent -eq 'claude') {
    # `audit` (rule/consistency): SONNET, and NOT the model the asking session runs - a reviewer that is a copy of
    # the asker mostly agrees with it, and this peer draws on the SAME subscription as the main session.
    # `priorart`: OPUS at high effort (user, 2026-09-15). That job reads the logs, the code and 345 archive files
    # looking for what we already did; a shallow read misses exactly what it exists to catch, and one missed hit
    # costs a whole build cycle - the first run found four defects, one a repeat of a recorded failure.
    # 2026-09-23 (user): Opus 5.5 pinned by id for priorart and hypothesis; the alias 'opus' resolved to claude-opus-5.
    # hypothesis moves max -> xhigh (max = +4 index points at 3.3x cost, news.hada.io/topic?id=34142).
    if ($Role -eq 'priorart') {
        $usedModel = if ($Model) { $Model } else { 'claude-opus-5-5' }
        $usedEffort = if ($Effort) { $Effort } else { 'medium' }
    } elseif ($Role -eq 'hypothesis') {
        # OPUS at effort MAX, not high (user, 2026-09-17). This role replaces codex on the one review layer where
        # being wrong costs a whole rebuild, so it gets the ceiling.
        $usedModel = if ($Model) { $Model } else { 'claude-opus-5-5' }
        $usedEffort = if ($Effort) { $Effort } else { 'high' }
    } elseif ($Role -eq 'fact' -or $Role -eq 'prose') {
        # OPUS 5.5 at MEDIUM, still THIN (user model table 2026-09-27, card chat-N4; weekly Fable at 75 %). Was
        # fable/low from 2026-09-18. A pure fact lookup and a report written from a fact list are the two jobs
        # where the cell's own reasoning is cheapest to buy - the cost that mattered was the fixed context load,
        # and --safe-mode removes that, not the effort dial.
        $usedModel = if ($Model) { $Model } else { 'claude-opus-5-5' }
        $usedEffort = if ($Effort) { $Effort } else { 'medium' }
    } elseif ($Role -eq 'outcome') {
        # FABLE at MEDIUM (user, 2026-09-18): one notch up from fact, because this reviewer has to weigh a whole
        # project's output against the user's requirements, and it is the layer that stopped the work twice.
        $usedModel = if ($Model) { $Model } else { 'fable' }
        $usedEffort = if ($Effort) { $Effort } else { 'medium' }
    } else {
        $usedModel = if ($Model) { $Model } else { 'sonnet' }
        $usedEffort = $Effort
    }
    $modelSrc = if ($Model -or $Effort) { "pinned by -Model/-Effort (role $Role)" } else { "peer.ps1 default for role $Role" }
} else {
    # agy keeps no model key in ~\.gemini\settings.json; without -Model its default is not readable.
    # `agy models` lists what can be pinned (gemini-3.1-pro-high, claude-opus-4-6-thinking, ...).
    $usedModel = if ($Model) { $Model } else { '(agy default, not readable)' }
    $modelSrc = if ($Model) { 'pinned by -Model' } else { 'agy built-in default' }
}
$modelLine = if ($usedEffort) { "$usedModel (effort $usedEffort; $modelSrc)" } else { "$usedModel ($modelSrc)" }

if ($Agent -eq 'codex') {
    # '-' = read instructions from stdin, and it must stay LAST.
    $exeArgs = @('exec', '-s', 'read-only', '--skip-git-repo-check', '-o', $outFile)
    $exeArgs += @('-m', $usedModel, '-c', "model_reasoning_effort=$usedEffort")
    if ($Image) { $exeArgs += @('-i', (Resolve-Path $Image).Path) }
    $exeArgs += '-'
    $exe = 'codex.cmd'
} elseif ($Agent -eq 'claude') {
    # A Claude sub-session as a peer (user, 2026-09-15: "claude 하위 세션도 peer review에 참여").
    # READ-ONLY MECHANICALLY, two ways: plan mode cannot edit, and the acting tools are denied
    # outright - which also means this project's PreToolUse/PostToolUse Bash hooks never fire
    # inside the cell, so it cannot be steered by them either. Prompt arrives on stdin, like the
    # others. The variadic --disallowedTools stays LAST so it cannot swallow another flag.
    # json, not text: the result envelope carries `total_cost_usd` and `usage`, which is the only way this project
    # can see what a review actually costs. Measured 2026-09-15 on a one-word answer: 69,048 cache-creation input
    # tokens and $0.276 on sonnet BEFORE reading anything - that is the price of loading the project context into
    # the cell. The user made cost tracking the condition for letting this peer read archive/.
    $exeArgs = @('-p', '--model', $usedModel, '--permission-mode', 'plan', '--output-format', 'json')
    if ($usedEffort) { $exeArgs += @('--effort', $usedEffort) }    # levels: low medium high xhigh max
    # THE THIN ROLES (2026-09-18). --safe-mode: "all customizations (CLAUDE.md, skills, plugins, hooks, MCP
    # servers, custom commands and agents, ...) disabled ... Auth, model selection, built-in tools, and
    # permissions work normally" (claude --help, read on this machine 2026-09-18). It is the only documented
    # flag that drops CLAUDE.md auto-discovery without also dropping OAuth: --bare would do it too, but --bare
    # requires ANTHROPIC_API_KEY (not set here - measured), so it cannot authenticate at all.
    # This is what makes a fable role cheap: the project context, not the model, is the fixed cost.
    if ($Role -eq 'fact' -or $Role -eq 'outcome' -or $Role -eq 'prose') { $exeArgs += '--safe-mode' }
    # WEB FOR THE HYPOTHESIS ROLE ONLY. plan mode permits read-only tools but prompts for network ones, and a
    # headless cell that is prompted simply does not search - so the two web tools are named explicitly. Both are
    # read-only: they fetch, they do not act. Every other claude role keeps rule 5's "claude peer has no web".
    # --allowedTools is variadic like --disallowedTools, so it goes BEFORE it and the disallow list stays last;
    # a tool named in both is denied, and none of these six is in the allow list.
    if ($Role -eq 'hypothesis') {
        $exeArgs += @('--allowedTools', 'WebSearch', 'WebFetch', 'Read', 'Glob', 'Grep')
    }
    elseif ($Role -eq 'fact') {
        # Web only. A `fact` cell answers about a tool, an API or an error code; it is not given the project
        # files, because a thin cell that starts reading this repository re-acquires the cost it exists to avoid.
        $exeArgs += @('--allowedTools', 'WebSearch', 'WebFetch')
    }
    elseif ($Role -eq 'outcome') {
        # Web AND the project files: questions 1-7 are answered from project-requirements/, STATUS.md and the
        # logs. The saving here is the SYSTEM PROMPT, not the reading - the cell reads what it chooses to read.
        $exeArgs += @('--allowedTools', 'WebSearch', 'WebFetch', 'Read', 'Glob', 'Grep')
    }
    # $Role 'prose' gets NO allow list: a report written from a fact list needs no tool at all, and the
    # disallow list below already removes every acting one.
    $exeArgs += @('--disallowedTools', 'Bash', 'PowerShell', 'Edit', 'Write', 'NotebookEdit', 'Agent')
    $exe = 'claude.exe'
} else {
    # agy: plan mode = no edits; no --dangerously-skip-permissions = tool use stays blocked.
    # Piped stdin is a documented prompt source; -p with an argv prompt is the quoting trap.
    $exeArgs = @('--mode', 'plan', '--print-timeout', "${TimeoutSec}s")
    if ($Model) { $exeArgs += @('--model', $Model) }
    $exe = 'agy.exe'
}

# --- DRY RUN: print the resolved routing and stop. No call, no archive, no cost. ------------------------
if ($DryRun) {
    $dateP = Get-Date -Format 'yyyy-MM-dd'
    $archP = if ($Kind -eq 'prose') { "archive\prose\$dateP-$Slug.md" }
             elseif ($Agent -eq 'claude' -and $Role -eq 'ingest') { "archive\ingest\$dateP-$Slug.md" }
             else { "archive\peer\$dateP-$Slug.md" }
    Write-Output "DRYRUN agent      : $Agent"
    Write-Output "DRYRUN role       : $Role$(if ($Agent -ne 'claude') { '  (ignored for this agent)' })"
    Write-Output "DRYRUN kind       : $Kind"
    Write-Output "DRYRUN model      : $modelLine"
    Write-Output "DRYRUN exe        : $exe"
    Write-Output "DRYRUN args       : $($exeArgs -join ' ')"
    Write-Output "DRYRUN thin       : $(if ($exeArgs -contains '--safe-mode') { 'YES (--safe-mode: no CLAUDE.md, no skills/plugins/hooks/MCP)' } else { 'no (project context loaded)' })"
    Write-Output "DRYRUN preamble   : $($preamble.Length) chars"
    Write-Output "DRYRUN prompt     : $($prompt.Length) chars"
    Write-Output "DRYRUN archive    : $archP"
    Write-Output "DRYRUN timeout    : ${TimeoutSec}s"
    Write-Output "DRYRUN reviewcard : $(if ($verdictId) { "id $verdictId, card block + verdict contract ($($verdictContract.Length) chars) in the prompt, verdict -> tools\bench\cards\verdict_$verdictId.json" } else { '(none)' })"
    Remove-Item $promptFile -Force -ErrorAction SilentlyContinue
    exit 0
}

$t0 = Get-Date
$job = Start-Job -ScriptBlock {
    param($exe, $exeArgs, $wd, $path, $promptFile)
    # DECODE THE CELL'S OUTPUT AS UTF-8. PowerShell decodes a native program's stdout using the CONSOLE code page,
    # which is cp949 here. On 2026-09-15 a claude review quoted Korean from STATUS.md, came back mojibaked, and the
    # JSON envelope broke at character 5520 - the answer was unreadable and its citations unverifiable. Same
    # encoding family that broke peer.ps1's own parsing earlier the same day. The job runs in its own runspace, so
    # this has to be set HERE, not in the caller.
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    $env:Path = $path
    Set-Location $wd
    Get-Content $promptFile -Raw | & $exe @exeArgs 2>&1 | Out-String
} -ArgumentList $exe, $exeArgs, $root, $env:Path, $promptFile

$done = Wait-Job $job -Timeout $TimeoutSec
$elapsed = [int]((Get-Date) - $t0).TotalSeconds

if (-not $done) {
    Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue
    $outcome = 'TIMEOUT'; $answer = "(no answer within ${TimeoutSec}s — job stopped)"
} else {
    $stdout = (Receive-Job $job | Out-String)
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    # -Encoding UTF8, MEASURED 2026-09-16: codex writes its -o answer file as UTF-8, and PowerShell 5.1's
    # Get-Content defaults to the system ANSI page (cp949 here), so a Korean answer was archived as mojibake -
    # the first `-Kind prose` test came back unreadable. English answers hid the bug for 217 exchanges. Same
    # encoding family as the two failures already recorded in this file's comments.
    $answer = if ($Agent -eq 'codex' -and (Test-Path $outFile)) { Get-Content $outFile -Raw -Encoding UTF8 } else { $stdout }
    # The claude cell answers in a JSON envelope. Pull the answer out of `result` and keep the cost line; the
    # stream may carry permission warnings ahead of the JSON, so take the outermost brace pair rather than assume
    # the whole of stdout parses.
    $costLine = ''
    if ($Agent -eq 'claude') {
        # The CLI writes the envelope as ONE line. Taking first-brace-to-last-brace swept up whatever braces the
        # permission warnings contained; take the last line that parses instead.
        $cand = @($stdout -split "`r?`n" | Where-Object { $_.TrimStart().StartsWith('{') })
        $line = if ($cand.Count) { $cand[-1] } else { '' }
        $s = if ($line) { 0 } else { $stdout.IndexOf('{') }
        $e = if ($line) { $line.Length - 1 } else { $stdout.LastIndexOf('}') }
        if (-not $line -and $s -ge 0 -and $e -gt $s) { $line = $stdout.Substring($s, $e - $s + 1) }
        if ($line) {
            try {
                $j = $line | ConvertFrom-Json
                if ($j.result) { $answer = $j.result }
                $u = $j.usage
                $costLine = ("`$" + ('{0:N4}' -f $j.total_cost_usd) +
                             "  in $($u.input_tokens) / out $($u.output_tokens) / " +
                             "cache-create $($u.cache_creation_input_tokens) / cache-read $($u.cache_read_input_tokens)" +
                             "  ($([int]($j.duration_ms/1000))s, $($j.num_turns) turn(s))")
            } catch {
                $costLine = "(cost not parsed: $($_.Exception.Message))"
            }
        } else { $costLine = '(no JSON envelope found in the cell output)' }
    }
    # QUOTA detection must match the AGENT's own refusal, never words inside an ANSWER.
    # The first version matched a bare '429' and fired on a LabVIEW method-ID table
    # ('Transaction:Redo | 429'), discarding a perfect answer and falsely benching codex
    # for the session (2026-08-28). So: require quota phrases to carry their own context,
    # anchor 429 to an HTTP error, and ignore anything that only appears in the answer body.
    $quotaSignals = @(
        'quota (exceeded|exhausted|reached)',
        'out of (quota|credits)',
        'rate limit(ed|s)? (exceeded|reached|hit)',
        'usage limit (exceeded|reached)',
        'RESOURCE_EXHAUSTED',
        'HTTP (status )?429',
        'status code 429',
        'error 429',
        'too many requests',
        'no longer supported'
    ) -join '|'
    # Look only at what the agent printed OUTSIDE its answer where possible.
    $envelope = if ($Agent -eq 'codex' -and (Test-Path $outFile)) {
        $stdout.Replace($answer, '')   # answer file holds the reply; the rest is envelope
    } else { $stdout }

    if ($envelope -match $quotaSignals) {
        # CONFIRM before benching an agent for the session. There is no CLI that reports
        # remaining quota (codex doctor shows auth mode only), but a trivial prompt is a
        # definitive liveness test and costs ~6 s. Benching a healthy agent on one
        # ambiguous string is far more expensive than this probe.
        $probeOut = Join-Path $env:TEMP ("peer_probe_{0}.txt" -f (Get-Random))
        $probeIn = Join-Path $env:TEMP ("peer_probe_in_{0}.txt" -f (Get-Random))
        Set-Content -Path $probeIn -Value 'Reply with exactly the word: alive' -Encoding utf8
        $probeArgs = if ($Agent -eq 'codex') {
            @('exec', '-s', 'read-only', '--skip-git-repo-check', '-o', $probeOut, '-')
        } elseif ($Agent -eq 'claude') {
            @('-p', '--model', $usedModel, '--permission-mode', 'plan', '--output-format', 'text',
              '--disallowedTools', 'Bash', 'PowerShell', 'Edit', 'Write', 'NotebookEdit', 'Agent')
        } else { @('--mode', 'plan', '--print-timeout', '60s') }
        $probeJob = Start-Job -ScriptBlock {
            param($exe, $a, $wd, $path, $inFile)
            $env:Path = $path; Set-Location $wd
            Get-Content $inFile -Raw | & $exe @a 2>&1 | Out-String
        } -ArgumentList $exe, $probeArgs, $root, $env:Path, $probeIn
        $probeOk = $false
        if (Wait-Job $probeJob -Timeout 60) {
            $pOut = (Receive-Job $probeJob | Out-String)
            if ($Agent -eq 'codex' -and (Test-Path $probeOut)) { $pOut += (Get-Content $probeOut -Raw) }
            $probeOk = $pOut -match 'alive'
        }
        Stop-Job $probeJob -EA SilentlyContinue; Remove-Job $probeJob -Force -EA SilentlyContinue
        Remove-Item $probeOut, $probeIn -Force -EA SilentlyContinue

        if ($probeOk) {
            Write-Output "NOTE: quota-looking text appeared, but a liveness probe succeeded - NOT benching $Agent."
            $outcome = if ([string]::IsNullOrWhiteSpace($answer)) { 'ERROR' } else { 'ANSWERED' }
        } else {
            $outcome = 'QUOTA'
            New-Item -ItemType File -Force $marker | Out-Null
        }
    } elseif ($Agent -eq 'gemini' -and $stdout -match 'jetski: no output produced') {
        # agy headless: a tool hit the permission wall and the run produced no real answer.
        # (Matched narrowly on agy's own marker - an ANSWER that merely quotes the error
        # text must not be classified ERROR; that false positive happened on 2026-08-28.)
        $outcome = 'ERROR'
    } elseif ([string]::IsNullOrWhiteSpace($answer)) {
        $outcome = 'ERROR'; $answer = "(empty answer)`n$stdout"
    } else {
        $outcome = 'ANSWERED'
    }
}

# Archive the exchange (rule 5: every exchange, useful or not).
# A PROSE PASS IS NOT A PEER REVIEW. It goes to archive\prose\, because guard_peer.py, prior_art_review.py and
# violations.py all glob archive\peer\*.md (verified 2026-09-16) - a proofreading exchange landing there would
# lift a failed-prediction gate and be counted as a review by the audit, for work it never looked at.
# C5: parse the peer's VERDICT line into tools/bench/cards/verdict_<id>.json (gates read that; the archive keeps prose).
# card 106-4 (cycle-99 NEXT): the retrospective contract asks for `loss_usd=<n or ?>`, and peers carry the `?` into the
# VERDICT JSON ("loss_usd":"?"), which verdict/1 rejects ("expected number/null, got str" - 16 archived answers, e.g.
# archive/peer/2026-09-25-retrospective-cycle74.md:10,370). "Unknown" IS null in verdict/1, so on VERDICT lines only a
# quoted `?` for loss_usd / loss_min becomes null before the parse. Any other string still fails validation; the
# archived answer keeps the peer's own text. Test: tools/bench/selftest_c106d_tools.py H4 (extracts this function by AST).
function ConvertTo-VerdictNulls([string]$Text) {
    $eval = { param($m) $m.Value -replace '("loss_(?:usd|min)"\s*:\s*)"\?"', '${1}null' }
    return [regex]::Replace($Text, '(?m)^.*\bVERDICT\s+\{.*$', $eval)
}
$verdictLine = ''
if ($verdictId) {
    if ($outcome -eq 'ANSWERED') {
        $ansFile = Join-Path $env:TEMP ("peer_answer_{0}.txt" -f (Get-Random))
        Set-Content -Path $ansFile -Value (ConvertTo-VerdictNulls $answer) -Encoding utf8
        $vOut = Join-Path $PSScriptRoot ("bench\cards\verdict_{0}.json" -f $verdictId)
        $verdictLine = (& py (Join-Path $PSScriptRoot 'protocol.py') parse-verdict $ansFile --id $verdictId --out $vOut | Out-String).Trim()
        Remove-Item $ansFile -Force -ErrorAction SilentlyContinue
    } else { $verdictLine = "NO-VERDICT: outcome $outcome" }
}
$date = Get-Date -Format 'yyyy-MM-dd'
# THE FRONTMATTER NOW CARRIES A TIME (2026-09-17, OPEN 31). The archive FILENAME stays date-only - violations.py
# and the audit key off it - but the `- **date:**` line gets `yyyy-MM-dd HH:mm:ss`, because a re-archived slug is
# otherwise undatable: MEASURED on this NTFS volume, deleting a file and writing the same name back KEEPS THE OLD
# CREATION TIME (tunneling), so guard_cycle.stamp()'s min(ctime, mtime) returns the slug's FIRST EVER write, hours
# or days stale. The file's own text is the only stamp a re-archive updates and a bulk frontmatter pass does not.
# guard_cycle.review_time()'s docstring already anticipated this: "If peer.ps1 ever writes a time too, the finer
# comparison is used automatically."
$dateStamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$archDir = if ($Kind -eq 'prose') { $proseDir } elseif ($Agent -eq 'claude' -and $Role -eq 'ingest') { $ingestDir } else { $peerDir }
if (-not (Test-Path $archDir)) { New-Item -ItemType Directory -Force $archDir | Out-Null }
$archRel = if ($Kind -eq 'prose') { "archive\prose\$date-$Slug.md" } elseif ($Agent -eq 'claude' -and $Role -eq 'ingest') { "archive\ingest\$date-$Slug.md" } else { "archive\peer\$date-$Slug.md" }
$archFile = Join-Path $archDir "$date-$Slug.md"
@"
# $Slug

- **agent:** $Agent
- **role:** $(if ($Agent -eq 'claude') { $Role } else { '(n/a)' })
- **model:** $modelLine
- **kind:** $Kind
- **cost:** $costLine
- **date:** $dateStamp
- **outcome:** $outcome (${elapsed}s)
- **verdict-card:** $(if ($verdictId) { $verdictLine } else { '(no -ReviewCard)' })
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

$Task

## Answer

$answer

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
"@ | Set-Content -Encoding utf8 $archFile

Write-Output "OUTCOME: $outcome (${elapsed}s)  model: $modelLine  archived: $archRel"
if ($costLine) { Write-Output "COST: $costLine" }
if ($verdictId) { Write-Output "VERDICT-CARD: $verdictLine" }
if ($outcome -eq 'ANSWERED') { Write-Output '--- ANSWER ---'; Write-Output $answer }

Remove-Item $outFile, $promptFile -Force -ErrorAction SilentlyContinue
switch ($outcome) {
    'ANSWERED' { exit 0 }
    'TIMEOUT'  { exit 2 }
    'QUOTA'    { exit 3 }
    default    { exit 4 }
}
