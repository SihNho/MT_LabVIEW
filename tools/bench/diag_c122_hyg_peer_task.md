ATTACK this claim about the failed prediction in tools/bench/diag_c122_hyg.log (script tools/bench/diag_c122_hyg.py, card 122-4).

Observed: 57 gates PASS, 1 FAIL at tools/bench/diag_c122_hyg.log:114:
  "FAIL H6 the files left on disk == [] and nothing was removed  added ['DonorRingConst_v0.vi'] removed []"
The H6 gate is stagekit's leftover-file check at Stage close (tools/stagekit.py:1161-1170): it lists claudeDev before and after and
expects the "added" set to equal the files the script declares it saved.

CLAIM: this is a script premise error, not a LabVIEW or op fault. diag_c122_hyg.py deliberately saved the donor
claudeDev\DonorRingConst_v0.vi (md5 d8dc30136c197bef836cd4622bbce61d, log lines 24-30: DBL[20] 0.0 #101, I32[20] -1 #130, I32 -1 #249,
read back equal) as an INTENDED artefact, but never declared it to stagekit's leftover gate, so H6 reported it as an unexpected file.
Every measurement gate (2,000 hygiene calls, 0 errors, handles max dev 17, refs 53/53, donor read-back) passed. The judgement session
accepted the donor and the hygiene record (docs/d1-loop12-17-split-plan.md:2348-2354, PD243(a)).

Already ruled out: no other file was added or removed (removed []); the donor md5 matches its record tools/bench/diag_c122_donor.json.

Question: is there any reading of this FAIL under which the donor file is NOT what the script intended (e.g. a stray save of a scratch,
a wrong path, a partial write), or under which something else left on disk would be hidden by this explanation? Name the cheapest
offline check that would falsify the claim.
