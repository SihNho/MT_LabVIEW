#!/bin/sh
# card 142-5: the new rebind self-test + the old rebind/rebase self-tests + c125_1, each under bgrun (offline, no LabVIEW).
cd "G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop" || exit 9
for t in selftest_rebind_c142_5 selftest_rebind_c132_5 selftest_rebase_c132_6 selftest_rebase_c133_3 c125_1_offline_measure; do
  py tools/bgrun.py --material --max-min 6 --log tools/bench/${t}_c142_5.log -- py -u tools/bench/${t}.py
  echo "== $t: $(grep -h '^RESULT\|BGRUN END\|BGRUN TIMEOUT' tools/bench/${t}_c142_5.log | tr '\n' ' ' | cut -c1-400)"
done
