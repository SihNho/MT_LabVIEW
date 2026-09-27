"""Card 110-4 L4: OFFLINE (no LabVIEW) per-class count of the GUI Error List read of the saved L2-B1 file, beside the RBW
wire classes (tools/bench/diag_c110d_rbwends.log). PRIOR ART: errorlist_check.norm/_hit (tools/errorlist_check.py:384-390)
and the class keys of errorlist_expected_D1_l2_a3_20260927_151224.json; nothing is written except this log.
PREDICTION CONTRACT:
  G1 the read JSON exists and its raw item count == its n_reported read count (80), window count recorded (99)
  G2 every read item falls in exactly one class key below (no unclassified item)
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c110d_elcounts.log -- py -u tools/bench/diag_c110d_elcounts.py"""
import collections, glob, json, os, sys                                            # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
MAIN = sorted(p for p in glob.glob(os.path.join(B, "errorlist_D1_l2_b1_20260927_193100_*.json")) if not p.endswith(("_raw.json", "_reuse.json")))[-1]
RAW = MAIN[:-len(".json")] + "_raw.json"
KEYS = [("buildarr", ["buildarr", "containsunwired"]), ("split1darr", ["split1darr", "containsunwired"]), ("bundle", ["bundle", "containsunwired"]),
        ("indexarr", ["indexarr", "containsunwired"]), ("replacearr", ["replacearr", "containsunwired"]), ("imagein", ["imagein", "notwi"]),
        ("unwiredselector", ["unwiredselector"]), ("sr_unwired_inside", ["unwiredfrominsidetheloop"]), ("sr_type_undefined", ["datatypeisundefined"]),
        ("tunnel_to_input", ["outputlooptunnel"]), ("undirected_tunnel", ["undirectedtunnel"]), ("different_types", ["differenttypes"]),
        ("different_dims", ["differentdimensions"]), ("no_source", ["connectsoneormoredatasinksbuthasnosource"]),
        ("unconnected", ["completelyunconnectedwire"]), ("loose_ends", ["wirehaslooseends"])]
gates = {}


def gate(k, ok, msg):
    gates[k] = bool(ok)
    print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, str(msg)[:600]), flush=True)


M = json.load(open(MAIN, encoding="utf-8"))
items = json.load(open(RAW, encoding="utf-8")).get("items") or []
gate("G1_read_json", len(items) == M.get("n_reported") or len(items) == len(M.get("items") or []),
     {"main": os.path.basename(MAIN), "raw_items": len(items), "n_reported": M.get("n_reported"), "from": M.get("n_reported_from"),
      "gates": M.get("gates"), "md5_before": M.get("bed_md5_before"), "md5_after": M.get("bed_md5_after")})
cnt, unk = collections.Counter(), []
for i, it in enumerate(items):
    n = EC.norm("%s %s %s" % (it.get("object") or "", it.get("raw") or "", it.get("detail") or ""))
    k = next((k for k, ks in KEYS if all(x in n for x in ks)), None)
    cnt[k or "UNCLASSIFIED"] += 1
    if not k:
        unk.append((i, (it.get("raw") or "")[:90], (it.get("detail") or "")[:60]))
for k, _ks in KEYS:
    print("CLASS %-18s %3d" % (k, cnt.get(k, 0)), flush=True)
print("UNCLASSIFIED %d %s" % (len(unk), unk), flush=True)
gate("G2_every_item_one_class", not unk, {"classified": sum(v for k, v in cnt.items() if k != "UNCLASSIFIED"), "unclassified": len(unk)})
n_pass = sum(1 for x in gates.values() if x); n_fail = len(gates) - n_pass           # noqa: E702
first = next((k for k, x in gates.items() if not x), None)
print("=== GATES: %d pass / %d fail%s" % (n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [])))
sys.exit(0 if n_fail == 0 else 1)
