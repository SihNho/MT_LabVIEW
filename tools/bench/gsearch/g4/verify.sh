#!/bin/sh
# card chat-G4: the same three headless gemini-pro calls as G3 (tools/bench/gsearch/g3/verify.sh), unchanged except the
# slug (g4-verify-*), now that the user set deny command(*) in ~/.gemini/antigravity-cli/settings.json by hand.
# Prediction: a and c ANSWERED with >=1 URL; b returns an answer (e.g. "no local files") instead of an auto-deny abort.
# No LabVIEW.
cd "G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
echo "SETTINGS_MD5_BEFORE $(md5sum ~/.gemini/antigravity-cli/settings.json | cut -c1-32)"
for s in a b c; do
  f=a; [ "$s" = b ] && f=b
  powershell -NoProfile -ExecutionPolicy Bypass -File tools/peer.ps1 -Agent gemini -Kind fact -Model gemini-3.1-pro-high -Slug g4-verify-$s -TimeoutSec 300 -TaskFile tools/bench/gsearch/g2/verify_$f.txt
done
echo "SETTINGS_MD5_AFTER $(md5sum ~/.gemini/antigravity-cli/settings.json | cut -c1-32)"
n=$(ls -d "$TEMP"/peer_agy_cwd_* 2>/dev/null | wc -l)
echo "LEFTOVER_CWD_DIRS $n"
echo 'RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}'
