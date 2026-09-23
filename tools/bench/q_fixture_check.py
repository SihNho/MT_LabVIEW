"""q_fixture_check - touches no LabVIEW: review c68-h6 §4's cheap test after q_m4_copy_probe - the NI Moving-Objects
fixtures equal their .ORIG.bak, neither .bak holds the bed's bytes (fdd6d74a...), and the folder listing is printed."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402

print("  FACT  Moving-Objects *.vi listing: {0}".format(K.fixture_listing()))
sys.exit(0 if K.fixtures_check(bad_md5s=("fdd6d74ac8a5ba0c1a545ad89ff2996f",)) else 1)
