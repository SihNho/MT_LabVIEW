# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_probe2 - card 146-a3-1 (OFFLINE, read-only): (1) the s04 and s05 READ items that are not L/C/SR (full raw +
detail + object) - do they name the VI / terminal?; (2) st0 'objs' entries for #5058, #29724, #29843 and every IndexArray node with
an unwired sink at the s05 start (which sinks are unwired); (3) the s05 base doc's fs_carried keys and the s05 plan's
finalized.rebase / base fields (does anything list the earlier sessions' created nodes or open items?); (4) the s04 pred's
errorlist.fixed open_at_end. PREDICTION CONTRACT: none (a census).
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_probe2.log -- py -u tools/bench/diag_c146_a2_1_probe2.py"""
import collections, glob, json, os, sys                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
from tools import elrule as ELR  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
for nm, f in (("s04", "tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json"),
              ("s05", "tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json")):
    for x in J(f).get("items") or []:
        t = "{0} {1}".format(x.get("raw", ""), x.get("detail", ""))
        if ELR.item_class(t) is None and ("unwired" in t.lower() or "required" in t.lower() or "reguired" in t.lower()):
            print("READ {0} #{1}: object={2!r} raw={3!r} detail={4!r} uid={5}".format(nm, x.get("index"), x.get("object"), x.get("raw"), str(x.get("detail"))[:300], x.get("uid")), flush=True)
p = J("tools/bench/plan_ring_p4_s05v18.json")
fz = p["finalized"]
st0 = J(fz["step_files"][0]["path"])["state"]
last = J(fz["step_files"][-1]["path"])["state"]
objs = st0.get("objs")
print("OBJS type {0} len {1}".format(type(objs).__name__, len(objs or [])), flush=True)
sample = (list(objs.items())[:2] if isinstance(objs, dict) else (objs or [])[:2])
print("OBJS sample {0}".format(json.dumps(sample)[:600]), flush=True)


def obj(u):
    if isinstance(objs, dict):
        return objs.get(str(u)) or objs.get(u)
    return [o for o in objs or [] if isinstance(o, dict) and int(o.get("uid", 0) or 0) == u]


rows = collections.defaultdict(list)
for r in st0.get("terminals") or []:
    rows[int(r["owner_uid"])].append(r)
for u in (5058, 29724, 29843):
    print("OBJ #{0}: {1}".format(u, json.dumps(obj(u))[:600]), flush=True)
for u, rs in sorted(rows.items()):
    if rs[0].get("owner_class") == "IndexArray":
        print("IA #{0}: unwired sinks start {1}; all rows {2}".format(u, [r.get("term_name") for r in rs if not r.get("is_source") and not r.get("wire_uid")],
              [(r.get("term_name"), r.get("is_source"), r.get("wire_uid")) for r in rs]), flush=True)
b = J((fz.get("base") or p.get("base"))["path"])
fc = b.get("fs_carried")
print("BASE fs_carried keys {0}: {1}".format(sorted(fc.keys()) if isinstance(fc, dict) else type(fc).__name__, json.dumps(fc)[:800]), flush=True)
print("PLAN keys {0}; finalized keys {1}; base {2}".format(sorted(p.keys()), sorted(fz.keys()), json.dumps(fz.get("base") or p.get("base"))[:400]), flush=True)
print("PLAN finalized.rebase {0}".format(json.dumps(fz.get("rebase"))[:1500]), flush=True)
for f in sorted(glob.glob(os.path.join(ROOT, "tools", "bench", "*p4*s04*pred*.json")) + glob.glob(os.path.join(ROOT, "tools", "bench", "*p4s04*pred*.json"))):
    try:
        d = J(f)
        fx = ((d.get("errorlist") or {}).get("fixed") or {})
        print("S04PRED {0}: total {1} open_at_end {2}".format(os.path.relpath(f, ROOT), fx.get("predicted_total"), fx.get("open_at_end")), flush=True)
    except Exception as e:                                                                   # noqa: BLE001
        print("S04PRED {0}: unreadable {1}".format(f, e), flush=True)
print(protocol.result_line(protocol.make_result(0, 0, None, [])), flush=True)
