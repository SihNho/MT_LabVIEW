r"""diag_c91_step4_summary.py - print the compact per-cell / per-site table from tools/bench/t0_step4_91.json (no LabVIEW)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "t0_step4_91.json")))
print("rows:")
for r in J["rows"]:
    t = next(iter((r.get("tra") or {}).values()), {}) if isinstance(r.get("tra"), dict) else {}
    print(" %-22s reg_ok=%-5s tra=%s cal=%s bp=%s lost=%s frames=%s hz=%s rows_hdr=%s exact=%s dims=%s cap=%s secs=%s" % (
        r["leg"], r.get("registered_ok"), r.get("picks_registered_tra"), r.get("picks_registered_cal"), r.get("bandpass_answered"), r.get("lost_frames"),
        r.get("frames_delta"), r.get("measured_hz"), t.get("rows_hdr"), t.get("exact_for_target"), t.get("dims_prefix"), r.get("hwndCapture_nonzero"), r.get("secs")))
for grp, key in (("cells", "cells"), ("extra", "cells_extra_valid_reruns")):
    for cell, T in J.get(key, {}).items():
        print("%s %s (%s) lost=%s" % (grp, cell, T.get("leg"), T.get("lost_frames")))
        for ln, L in T["loops"].items():
            if "sites" not in L: print("   %s MISSING" % ln); continue
            print("   %-15s iters=%5d period med=%8.1f p95=%8.1f max=%9.1f us span=%.1fs" % (ln, L["iterations"], L["period_us"]["median"], L["period_us"]["p95"], L["period_us"]["max"], L["span_s"]))
            for s, S in L["sites"].items():
                if "delta_us" not in S: print("      site %s MISSING" % s); continue
                print("      site %-3s n=%5d per_iter med=%s max=%s  delta med=%8.1f p95=%8.1f max=%9.1f min=%7.1f us" % (
                    s, S["stamps"], S["stamps_per_iteration"]["median"], S["stamps_per_iteration"]["max"], S["delta_us"]["median"], S["delta_us"]["p95"], S["delta_us"]["max"], S["delta_us"]["min"]))
print("slope:", json.dumps(J.get("slope_15_vs_8"), indent=None)[:3000])
