# chatS1-opmodels-b2-fsit-c1

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3578  in 30 / out 13123 / cache-create 95755 / cache-read 1410645  (152s, 23 turn(s))
- **date:** 2026-09-24 22:46:32
- **outcome:** ANSWERED (155s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the two failed gates in tools/bench/opmodels_measure_B2.log (script tools/bench/opmodels_measure.py,
group B2): "C1 fs_inner_tunnel_connect_1 / _2 op returned without raising and without an error string".

CLAIM: both failures are a bug in OUR gate, not a failed connect. The gate read the result dict's `err` key, which for
OpFsInnerTunnelConnect_v1 is the POISON value that build_d1_m3a3b_d3.fsit_call pre-loads into every readout
(build_d1_m3a3b_d3.py:281-296, Pre-decided 125) and that this op never overwrites: the same string
"error 999999: POISON - not overwritten by the run" is on every ACCEPTED call of that op (build_d1_m3a3b_d3.log G2 calls
1-20, diag_c86_norbw.log). The op's real error columns (invoke_err, err_uidvi, err_fsit, err_termuid, err_uidback) are all ''
in both calls; term_uid/uid_back echo the addressed FSIT (25075/25059 and 5260/5183); `Is Broken?` False; wire_delta 1;
and the independent terminal-level diff (allterms.read_terms before/after) shows 6 edges added per call. So the connect
succeeded and the measured diff is valid data; the fix is to gate on invoke_err + err_* (already patched) and rerun B2.

Already ruled out: a LabVIEW-side failure of the connect (the before/after terminal tables differ, and the readback columns
echo the right uids); a stale readout from a previous call (the two calls address different FSITs and read back different
uids, 25075 vs 5260).

My reading of the extra edges (attack it too): each connect adds exactly ONE Wire object (23508 / 23487) from the source to
the FSIT terminal; the other 5 "added" edges are RESTORED edges - the setup delete_wire had left a sourceless chain, the
downstream FS inner/outer, Selector and Loop tunnels had lost their direction (their terminals now read is_source True again:
terms_changed is_source False -> True on #24984, #25059, #43605 / #2992, #5129, #5183), and the half-wires 25003, 25045, 25066,
25497, 44089 / 628, 3148, 3513, 5174, 5194 are whole again.

Also look at the recorded diffs in tools/bench/opmodels/raw/fs_inner_tunnel_connect_1.json and _2.json: edges_added is 6
per call and terms_added 6 / objs_added 8 including one Invoke - is that plausibly ONE connect plus the known stray Invoke
(the OpConnect* family mints one zero-wired Invoke per call), or evidence that the op did something else (e.g. auto-routing
through extra tunnels)? Name what would falsify the claim and the cheapest discriminating test.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim holds for this run.** Both C1 failures came from our gate reading a column that never changes. But three parts of the argument are weaker than they are stated, and one check the claim depends on was never measured.

**1. Strongest reason it could be wrong: the VI was still broken after each connect, and nothing shows that was only the stray Invoke.**
- The bed opened with ExecState 1 (`opmodels_measure_B2.log:46`). Both connects ended at ExecState 0 (`:174`, `:196`).
- The claim says the connect succeeded and the stray Invoke is harmless junk. But nobody read ExecState after the purge, so "the connect left a whole VI" is inferred, not measured.
- The correlation does support the claim. ExecState is 0 after exactly the ops that create a stray Invoke (tunnel, connect_from_wire, fs_inner) and 1 after the ops that create none (wire_sr, const) (`:55-237`, census diffs at `:61-237`).
- The web does not say whether an unconfigured Invoke breaks a VI. NI's docs only say an unwired `reference` falls back to the current VI or Application for those classes ([LabVIEW Wiki: Invoke Node](https://labviewwiki.org/wiki/Invoke_Node), [Invoke Node reference](https://rajsite.github.io/unofficial-lvdocs/glang/Invoke_Node.html)).

**2. Alternative explanations of the same evidence.**
- **(a) Errors are dropped with no trace.** The op runs with automatic error handling OFF (`build_d1_m3a3b_d3.log:45`). Any node in the op whose error output goes to no indicator loses its error without a dialog ([Automatic Error Handling](https://labviewwiki.org/wiki/Automatic_Error_Handling), [NI: Prevent Error Dialog](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019SFfSAM)). So a clean `invoke_err` plus `err_*` covers only the nodes wired to those indicators.
- **(b) The `err_*` columns are not fresh evidence.** `fsit_call` pre-loads the poison value only into `error out 7` and `error out` (`build_d1_m3a3b_d3.py:293-298`). `err_uidvi`, `err_fsit`, `err_termuid` and `err_uidback` are never pre-loaded, so their `''` could be a default or left over from an earlier run.
  - The fresh positive evidence is the poisoned columns: `term_uid`, `uid_back` and `sink_wire_uid` came back non-zero, `is_broken` came back False although it was pre-set True, and `invoke_err` came back `''` although it was pre-set to the poison error. The patched gate leans on the unpoisoned columns.
- **(c) The cited precedent is weak.** The G2 calls cited as "accepted" had `wire_delta=0` and `is_broken=True`, which is the untouched poison value (`build_d1_m3a3b_d3.log:58-60`). Those calls did not connect anything.
  - This supports "`err` is constant": it reads the poison string whether the op connects or not.
  - It does not show that the op's `error out` indicator is unwired. That was never read from the op's own diagram. `keystone-op-spec.md:255` says so for a different op.

**3. Your edge reading is confirmed by the raw files, and the auto-routing alternative is ruled out.** In both `fs_inner_tunnel_connect_1.json` and `_2.json`:
- `objs_added` is 8: one Invoke (#1756), its 6 terminals, and one Wire (23508 or 23487). No tunnel or other structure object was added.
- `wire_objs` goes from 1912 to 1913, one new wire.
- The other 5 added edges reuse the exact wire uids listed in `half_wires_before`, and `half_wires` goes from 5 to 0.
- The counts balance across the two calls on one scratch copy. After call 1 plus the purge (−1 Invoke, −6 terminals) and call 2's setup (−1 wire, −6 edges), call 2's before-counts equal call 1's exactly (5801 / 10101 / 2238 / 1912).

**4. What would falsify the claim.**
- ExecState stays 0 after the purge. That would mean the connect itself left something broken.
- Or the after-op edge set differs from the untouched bed's edge set on the affected terminals, apart from the one renamed wire (25092→23508, 5297→23487). For example, a restored chain feeds a different sink, or an edge from the bed is missing.

**5. Cheapest test that separates the claim from these alternatives.**
- **Offline, no LabVIEW:** compare the `edges_added` rows in each raw file with the same terminals in `tools/bench/opmodels/bed_s4_loop17.json`. Every source/sink pair must match the bed, with only the one wire uid different.
- **Next B2 rerun, one line:** read ExecState after each purge and require it to be 1.
- **Tighten C1 for this op:** gate on the fresh values (`wire_delta==1`, `is_broken is False`, `uid_back==fsit`, `term_uid==fsit_term`). Pre-load the poison into `err_*` in the caller before `fsit_call`; it reuses the same VI object and does not reset those indicators.
- **Optional:** LabVIEW 2025 Q3 added a "Log Unwired Errors" option that would record the dropped errors in (a) ([NI forum](https://forums.ni.com/t5/LabVIEW-Public-Beta-Program-in/2025-Q3-Feature-Log-Unwired-Errors/td-p/4434830)).

**What would change my mind:** either falsifier in section 4. If ExecState is 1 after the purge and the edges match the bed, the claim holds and the B2 rerun with the patched gate is valid.

Sources:
- [LabVIEW Wiki – Invoke Node](https://labviewwiki.org/wiki/Invoke_Node)
- [Invoke Node (unofficial LV docs)](https://rajsite.github.io/unofficial-lvdocs/glang/Invoke_Node.html)
- [LabVIEW Wiki – Automatic Error Handling](https://labviewwiki.org/wiki/Automatic_Error_Handling)
- [NI – Prevent LabVIEW Error Dialog Box](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019SFfSAM)
- [NI – 2025 Q3 Feature: Log Unwired Errors](https://forums.ni.com/t5/LabVIEW-Public-Beta-Program-in/2025-Q3-Feature-Log-Unwired-Errors/td-p/4434830)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
