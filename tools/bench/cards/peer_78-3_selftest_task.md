ATTACK this claim about a failed prediction in an OFFLINE Python self-test (no LabVIEW involved).

Script: tools/bench/m8b_replay_compare.py (new, card 78-3). Log: tools/bench/m8b_replay_selftest78.log.
Prediction: gate "G1 both tra parse" PASS when the script reads a tra file (tools/bench/m8_out/s1_20260925_063401/tra001-000)
as: text header ending at b"not in z!)", then two I32 dims, then f64 row-major data, with dims product == data length.
Observed: G1 FAIL; dims read as [-1207107584, 201326592] (tools/bench/m8b_replay_selftest78.json).

Claim: the dims (and the f64 data) are LITTLE-endian, not big-endian as the first version assumed.
-1207107584 = 0xB80D0000 whose byte-reversal is 0x00000DB8 = 3512, and 201326592 = 0x0C000000 -> 12; 3512 rows x 12
cols matches the tra header "actual data points/nominal: 3512/2000000" and drive_m8.tra_rows' earlier count
(tools/bench/m8_s1_p3.json:110-112: data_bytes 337160 = 3512*96 + 8). The fix is "<ii" and "<f8".

Already ruled out: file truncation (size matches 3512*96+8 exactly); a different column count (12 = time,trans,rot + 3 beads x xyz).
Question: is there any reason the DATA block could be big-endian while the dims are little-endian (LabVIEW's
Write to Binary File defaults to big-endian, so a little-endian dims prefix is itself surprising)? What is the cheapest
check that distinguishes "<f8" from ">f8" for the data block, e.g. the time column being monotonic and finite?
