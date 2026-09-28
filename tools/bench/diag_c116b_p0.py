"""diag_c116b_p0 - card 116-2 STEP 0b table (offline): B3 vs R1 differences from NI's comparison report (tools/bench/diag_c116b_cmp.xml, LabVIEWCLI
CreateComparisonReport, -nobdcosm, written by diag_c116b_props.py) plus that script's direct reads (diag_c116b_props.json G2/G3). PREDICTION: the report
holds 0 front-panel, 0 VI-attribute changes and block-diagram changes of three types only - 'deleted' Shift Register x12 (the retired pairs),
'wiring changes' (nets that lost a sink) and 'loose ends' - i.e. no changed or added object; props G1-G4 PASS. Writes tools/bench/diag_c116b_p0.json."""
import collections, json, os, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
root = ET.parse(os.path.join(B, "diag_c116b_cmp.xml")).getroot()
nc = dict((e.get("type"), int(e.get("num"))) for e in root.iter("numChanges"))
ch = [dict(e.attrib) for e in root.iter("funcChanges")]
kinds = collections.Counter((c["diffType"], c["objType"]) for c in ch)
PJ = json.load(open(os.path.join(B, "diag_c116b_props.json"), encoding="utf-8"))
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:900]), flush=True)


gate("P0a front panel 0, FP position 0, VI attribute 0 changes", nc.get("Front Panel") == 0 and nc.get("Front Panel Position/Size") == 0 and nc.get("VI Attribute") == 0, nc)
gate("P0b block-diagram changes only of type deleted/Shift Register x12, wiring changes, loose ends ({0} changes)".format(len(ch)),
     set(kinds) <= {("deleted", "Shift Register"), ("wiring changes", ""), ("loose ends", "")} and kinds[("deleted", "Shift Register")] == 12
     and len(ch) == nc.get("Block Diagram Functional"), dict((" / ".join(k), v) for k, v in kinds.items()))
g = PJ["gates"]
gate("P0c direct reads: diag_c116b_props.json 18/0 (G1 tunnels 151, G2 IndexMode/faces equal, G3 302 constants byte-equal, G4 dump)", g["pass"] == 18 and not g["fail"], g)
tab = {"report": {"path": "tools/bench/diag_c116b_cmp.xml", "numChanges": nc, "by_type": dict((" / ".join(k), v) for k, v in kinds.items()),
                  "deleted_uids_in_image_names": sorted(int(os.path.basename(c["imagePath1"]).split("_")[2]) for c in ch if c["diffType"] == "deleted")},
       "direct": "diag_c116b_props.json: 151 LoopTunnels (IndexMode + faces) and 302 Constants (flattened bytes) equal per uid",
       "kept_object_differences": [] if all(c for _n, c in ok) else "see FAIL lines"}
json.dump(tab, open(os.path.join(B, "diag_c116b_p0.json"), "w", encoding="utf-8"), indent=1)
print("  FACT TABLE " + json.dumps(tab), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
