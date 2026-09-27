r"""diag_c110_cut - card 110-1 P1/P3 OFFLINE: print a stagesim run's per-step cut/reconnect rows, rule rows, bare deletions and the
end cdiff rows (no LabVIEW). Arg: the sim step directory (tools/bench/sim/.../<stage>).
    py tools/bgrun.py --material --max-min 3 --log <log> -- py -u tools/bench/diag_c110_cut.py <stepdir>"""
import glob, json, os, sys                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                                # noqa: E402
D = sys.argv[1]
for f in sorted(glob.glob(os.path.join(D, "step_*.json"))):
    st = json.load(open(f, encoding="utf-8"))
    a, e = st.get("action") or {}, st.get("effect") or {}
    print("STEP {0} {1} {2} keys={3}".format(st.get("n"), a.get("op"), a.get("id"), sorted(e.keys())), flush=True)
    for r in e.get("reconnect") or []:
        print("   RC {0}".format(json.dumps(dict((k, r.get(k)) for k in ("key", "side", "cut_wire", "how", "direct", "effective", "chain", "partners_now")))[:700]), flush=True)
    for k in ("rule_rows", "only_sink", "only_source", "bare_deleted", "tunnel_flips", "cut_set"):
        if e.get(k):
            print("   {0} {1}".format(k.upper(), json.dumps(e.get(k))[:900]), flush=True)
    if st.get("cdiff") or st.get("cdiff_rows"):
        print("   CDIFF {0}".format(json.dumps(st.get("cdiff_rows") or st.get("cdiff"))[:3000]), flush=True)
c = os.path.join(D, "candidates.json")
if os.path.exists(c):
    for r in json.load(open(c, encoding="utf-8")) if isinstance(json.load(open(c, encoding="utf-8")), list) else json.load(open(c, encoding="utf-8")).get("candidates", []):
        print("CAND {0}".format(json.dumps(r)[:600]), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
