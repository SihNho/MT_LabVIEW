#!/bin/sh
# card chat-G2 Part A step 3: three headless gemini-pro calls through peer.ps1 (neutral cwd); no LabVIEW.
cd "G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
for s in a b c; do
  f=a; [ "$s" = b ] && f=b
  powershell -NoProfile -ExecutionPolicy Bypass -File tools/peer.ps1 -Agent gemini -Kind fact -Model gemini-3.1-pro-high -Slug g2-verify-$s -TimeoutSec 300 -TaskFile tools/bench/gsearch/g2/verify_$f.txt
done
n=$(ls -d "$TEMP"/peer_agy_cwd_* 2>/dev/null | wc -l)
echo "LEFTOVER_CWD_DIRS $n"
echo 'RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}'
