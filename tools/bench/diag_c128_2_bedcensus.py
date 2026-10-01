r"""diag_c128_2_bedcensus - card 128-2 (B) file 1, OFFLINE (no LabVIEW): node-class census of the P3a bed graph
tools/bench/graph_ring_p3a_20261001_190155.json (and the S1 copy-of-original graph tools/bench/graph_s1_20260924.json when present).
EXISTING FIRST: graph files are written by diag_c125_graph_p3a.py (terminal table = allterms rows + term_class); no reader of
PrimIndex exists in tools/ (grep PrimIndex: 0 hits), so primitives are identified by owner_class + terminal-name signature.
PREDICTION: bed terminals > 5000 (not an empty read); NamedUnbundler owners == 16 (result_127-5 facts[0]); Select-signature
owners: MEASUREMENT (127-5 said 0 in the P2b graph). Writes tools/bench/diag_c128_2_bedcensus.json.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c128_2_bedcensus.log -- py -u tools/bench/diag_c128_2_bedcensus.py"""
import collections, json, os, sys                                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = [("bed_p3a", "graph_ring_p3a_20261001_190155.json"), ("s1_copy_of_original", "graph_s1_20260924.json")]
# run 1 (00:02) FAILED 2 gates; review archive/peer/2026-10-02-c128-2-bedcensus.md: graph_s1 carries a per-object class map `cls`
# (uid -> class) of D1_s1_copy.vi, not a terminal table -> read `cls`; "16" was never measured (12 NamedUnbundler + 3 Unbundler).
SEL_NAMES = {"s", "t", "f", "s? t: f"}
OUT, fails, passes = {}, [], []
def gate(label, ok, got=""):
    (passes if ok else fails).append(label); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(got)[:400]), flush=True)
for tag, fn in FILES:
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        print("  FACT  %s missing: %s" % (tag, fn)); continue                                  # noqa: E702
    d = json.load(open(p, encoding="utf-8"))
    print("  FACT  %s top-level keys %s" % (tag, sorted(d.keys()) if isinstance(d, dict) else type(d)), flush=True)
    rows = d.get("terminals") or [] if isinstance(d, dict) else []
    own = collections.defaultdict(list)
    for r in rows:
        own[int(r["owner_uid"])].append(r)
    cls = collections.Counter(rs[0]["owner_class"] for rs in own.values())
    nu = {u: sorted(str(r["term_name"]) for r in rs) for u, rs in own.items() if rs[0]["owner_class"] in ("NamedUnbundler", "Unbundler")}
    sel = {u: (rs[0]["owner_class"], sorted(str(r["term_name"]) for r in rs)) for u, rs in own.items()
           if len({str(r["term_name"]).strip() for r in rs} & SEL_NAMES) >= 3 or any("?" in str(r["term_name"]) and ":" in str(r["term_name"]) for r in rs)}
    sigs = collections.Counter((rs[0]["owner_class"], tuple(sorted(str(r["term_name"]) for r in rs))) for rs in own.values()
                               if rs[0]["owner_class"] not in ("Terminal",) )
    prim_like = {c: n for c, n in cls.items() if c.lower() in ("function", "prim", "primitive", "node", "builtin", "primitivenode")}
    other_keys = {k: (len(v) if hasattr(v, "__len__") else v) for k, v in d.items() if k not in ("terminals",)} if isinstance(d, dict) else {}
    OUT[tag] = {"terminal_rows": len(rows), "owners": len(own), "owner_class_counts": dict(cls.most_common()),
                "named_unbundlers": {str(u): v for u, v in sorted(nu.items())}, "select_like": {str(u): v for u, v in sorted(sel.items())},
                "prim_like_classes": prim_like, "other_keys": other_keys}
    print("  FACT  %s terminal rows %d, owners %d" % (tag, len(rows), len(own)), flush=True)
    print("  FACT  %s owner classes %s" % (tag, dict(cls.most_common())), flush=True)
    print("  FACT  %s other keys %s" % (tag, other_keys), flush=True)
    print("  FACT  %s NamedUnbundler/Unbundler owners %d: %s" % (tag, len(nu), json.dumps({str(u): v for u, v in sorted(nu.items())})[:1500]), flush=True)
    print("  FACT  %s Select-like owners %d: %s" % (tag, len(sel), json.dumps({str(u): v for u, v in sorted(sel.items())})[:1500]), flush=True)
    objs = d.get("objs") if isinstance(d, dict) else None
    ov = list(objs.values()) if isinstance(objs, dict) else (objs or [])
    oc = collections.Counter(str(o.get("class") or o.get("cls")) if isinstance(o, dict) else str(o) for o in ov)
    OUT[tag]["objs_class_counts"] = dict(oc.most_common())
    print("  FACT  %s objs %d, NamedUnbundler %d, Unbundler %d, classes %s" % (tag, len(ov), oc.get("NamedUnbundler", 0), oc.get("Unbundler", 0), dict(oc.most_common(60))), flush=True)
    fsig = collections.Counter(tuple(sorted(str(r["term_name"]) for r in rs)) for rs in own.values() if rs[0]["owner_class"] in ("Function", "Comparison"))
    OUT[tag]["function_signatures"] = [[list(k), n] for k, n in fsig.most_common()]
    print("  FACT  %s Function/Comparison terminal-name signatures %d: %s" % (tag, len(fsig), [(list(k), n) for k, n in fsig.most_common(45)]), flush=True)
    st = [u for u, v in nu.items() if "status" in v]
    print("  FACT  %s Unbundle owners with a 'status' terminal: %s" % (tag, st), flush=True)
    cm = d.get("cls") if isinstance(d, dict) else None
    if isinstance(cm, dict):
        cc = collections.Counter(str(v) for v in cm.values())
        OUT[tag]["cls_counts"] = dict(cc.most_common())
        OUT[tag]["cls_unb_uids"] = sorted(int(u) for u, v in cm.items() if v in ("NamedUnbundler", "Unbundler"))
        print("  FACT  %s cls map %d objects, NamedUnbundler %d, Unbundler %d, uids %s; classes %s" % (tag, len(cm), cc.get("NamedUnbundler", 0),
              cc.get("Unbundler", 0), OUT[tag]["cls_unb_uids"], dict(cc.most_common())), flush=True)
        gate("%s vi is D1_s1_copy and cls map not empty" % tag, "D1_s1_copy" in str(d.get("vi")) and len(cm) > 1000, (d.get("vi"), len(cm)))
    else:
        gate("%s not an empty read (terminal rows > 1000)" % tag, len(rows) > 1000, len(rows))
b = OUT.get("bed_p3a") or {}
bu = sorted(int(u) for u in (b.get("named_unbundlers") or {}))
gate("bed_p3a NamedUnbundler == 12 and Unbundler == 3", (b.get("owner_class_counts") or {}).get("NamedUnbundler") == 12 and (b.get("owner_class_counts") or {}).get("Unbundler") == 3,
     b.get("owner_class_counts", {}).get("NamedUnbundler"))
gate("bed Unbundle uid set == D1_s1_copy cls Unbundle uid set", bu == (OUT.get("s1_copy_of_original") or {}).get("cls_unb_uids"), bu)
json.dump(OUT, open(os.path.join(HERE, "diag_c128_2_bedcensus.json"), "w", encoding="utf-8"), indent=1)
print("=== GATES: %d pass / %d fail; failing: %s" % (len(passes), len(fails), "; ".join(fails)))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS", "gates": {"pass": len(passes), "fail": len(fails)},
                              "first_fail": fails[0] if fails else None, "artefacts": [{"path": "tools/bench/diag_c128_2_bedcensus.json"}]}))
sys.exit(1 if fails else 0)
