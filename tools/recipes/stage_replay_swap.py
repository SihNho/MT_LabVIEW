r"""stage_replay_swap - card 78-3 (m8 plan PD13(d), PD14(c), PD15, PD22(d)): the replay SWAP stage.
FOUND FIRST: gscript.replace_object (gscript.py:2974, accepted PD15 on swap_verb_75.json 21/0 - new uid per swap, so every
check is remapped new->old); diag_replay_lib census/edges/tail (the same readers stage_replay_standins.py G2 used);
wiki_build.read_live (whole-VI terminals). Nothing new is built here; rows/uids/paths come from
tools/bench/plans/plan_replay_swap_78.json (decision 8).
Two dated byte copies land in claudeDev\replay\ (S1 and S3 callees are absolute G: paths, the replay VIs sit beside).
PREDICTION per copy (s1, s3): A1 copy md5 == source; A2 BEFORE census: each swap uid calls its old callee, ES 1;
A3 each replace_object: no error, a new uid; A4 callee diff == exactly the two swaps -> the replay VIs (path read back);
A5 wire-edge diff(before, after) == 0 after new->old remap; A6 ES 1 -> scripted save; COLD (fresh LabVIEW): C1 ES 1,
C2 census == warm; H pins: S1, S3, 3 replay VIs, original md5 unchanged; LabVIEW gone. No VI is run.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_replay_swap_78.log -- py -u tools/recipes/stage_replay_swap.py
CARD 95-6 (PD202(d)3): PLAN SELECTION by `--plan <tag>` (argv) or env REPLAY_SWAP_PLAN; default "78" = the plan above,
unchanged. Only plans listed in PLANS load (named literals, so stage_prerun keys the records on every plan's md5). A plan
WITHOUT `second_input` makes ONE copy (the input's). Optional plan keys (defaults = plan 78's behaviour): input_tag "s3",
second_tag "s1", input_pin "S3", stage_name "stage_replay_swap_78", task "78-3", out_json "stage_replay_swap_78.json".
    py tools/bgrun.py --material --max-min 45 --log tools/bench/replay_c95_swap.log -- py -u tools/recipes/stage_replay_swap.py --plan 95"""
import json, os, shutil, sys, time                                                       # noqa: E401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench"))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
PLANS = {"78": "plans/plan_replay_swap_78.json", "95": "plans/plan_replay_swap_95.json"}
PLAN_TAG = sys.argv[sys.argv.index("--plan") + 1] if "--plan" in sys.argv else (os.environ.get("REPLAY_SWAP_PLAN") or "78")
P = json.load(open(os.path.join(K.BENCH, PLANS[PLAN_TAG]), encoding="utf-8"))
cd = lambda rel: os.path.join(K.CLAUDEDEV, rel)                                          # noqa: E731
IN, IN_MD5 = cd(P["input"]["vi"].split("\\", 1)[1]), P["input"]["md5"]            # plan 78: S3, the only dry-shape graph
TAG1, TAG2 = P.get("input_tag", "s3"), P.get("second_tag", "s1")
S2, S2_MD5 = (cd(P["second_input"]["vi"].split("\\", 1)[1]), P["second_input"]["md5"]) if "second_input" in P else (None, None)
SW = [(int(r["uid"]), r["old_callee"], cd(r["new"]), r["new_md5"]) for r in P["swaps"]]
WB, TS = K.mod("wiki_build"), time.strftime("%Y%m%d_%H%M%S")
H = lambda p: "dry" if L.DRY else K.md5(p)                                               # noqa: E731  (dry: no copy on disk)


def one(s, tag, path):
    """R02-R06 on one dated copy; returns its record (new uids, census, edges count, md5)."""
    s.head("[{0}] {1}".format(tag.upper(), os.path.basename(path))); g.ensure_loaded(path)
    c0 = L.census(path)
    s.gate("A2 {0} BEFORE: {1}".format(tag, ", ".join("#%d calls %s" % (u, o) for u, o, _n, _m in SW)),
           all(os.path.basename(str(c0.get(u, ""))) == o for u, o, _n, _m in SW), dict((u, c0.get(u)) for u, _o, _n, _m in SW), fatal=True)
    s.gate("A2 {0} ExecState 1 before the swap".format(tag), s.es(tag + " before", path) == 1, fatal=True)
    E0 = L.edges(WB.read_live(path, fs_pairs=[]), {}); remap = {}
    for u, _o, new, _m in SW:
        r = g.replace_object(path, u, new); s.fact("{0} replace_object #{1} -> {2}: {3}".format(tag, u, os.path.basename(new), r))
        s.gate("A3 {0} replace #{1}: no error, new uid".format(tag, u), not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
        remap[r["new_uid"]] = u
    c1 = L.census(path); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    want = set(remap) | set(remap.values())
    ok4 = set(dd) == want and all(os.path.normcase(str(c1.get(nu))) == os.path.normcase(dict((u, n) for u, _o, n, _m in SW)[ou])
                                  for nu, ou in remap.items())
    s.gate("A4 {0} callee diff == exactly the two swaps -> replay VIs".format(tag), ok4, dd)
    E1 = L.edges(WB.read_live(path, fs_pairs=[]), remap)
    s.gate("A5 {0} wire-edge diff 0 after remap ({1} edges before, {2} after)".format(tag, len(E0), len(E1)), E0 == E1,
           (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]))
    s.gate("A6 {0} ExecState 1 after the swaps".format(tag), s.es(tag + " after", path) == 1, fatal=True)
    g.save(path); g.reset(); m = H(path); s.fact("SAVED {0} md5 {1}".format(path, m))
    return {"path": path, "md5": m, "remap": dict((str(k), v) for k, v in remap.items()), "census_after": dict((str(k), v) for k, v in c1.items()),
            "edges": len(E0), "callee_diff": dict((str(k), v) for k, v in dd.items())}


def body(s):
    s.start(); R = s.R; ts = TS
    cp = {TAG1: s.work}                                                                 # beside the replay VIs
    if S2:
        cp[TAG2] = cd(P["copies"][TAG2].format(ts=ts)); shutil.copyfile(S2, cp[TAG2])
    s.gate("A1 copies md5 == sources", L.DRY or (H(cp[TAG1]) == IN_MD5 and (not S2 or H(cp[TAG2]) == S2_MD5)), cp, fatal=True)
    R["copies"] = {}
    for tag in (TAG1, TAG2) if S2 else (TAG1,):
        R["copies"][tag] = one(s, tag, cp[tag]); s.dump()
    s.head("[C] COLD: fresh LabVIEW"); s.restart()
    for tag, rec in R["copies"].items():
        s.gate("C1 {0} ExecState 1 COLD".format(tag), g.exec_state(rec["path"]) == 1)
        cc = dict((str(k), v) for k, v in L.census(rec["path"]).items())
        s.gate("C2 {0} COLD callee census == warm".format(tag), cc == rec["census_after"],
               dict((k, (rec["census_after"].get(k), cc.get(k))) for k in set(cc) | set(rec["census_after"]) if cc.get(k) != rec["census_after"].get(k)))
        s.gate("C3 {0} md5 unchanged by the cold load".format(tag), H(rec["path"]) == rec["md5"])
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + ((P.get("input_pin", "S3"), IN, IN_MD5),) + ((("S1", S2, S2_MD5),) if S2 else ()) + tuple(
        (os.path.basename(n), n, m) for _u, _o, n, m in SW) + tuple((a, cd(b), c) for a, b, c in P["extra_pins"])
    st = St(IN, IN_MD5, P.get("stage_name", "stage_replay_swap_78"), preload=False, deadline_min=40, work_dir=L.RP,
            work_name=os.path.basename(P["copies"][TAG1]).format(ts=TS), pins=pins,
            task=P.get("task", "78-3"), out_json=os.path.join(K.BENCH, P.get("out_json", "stage_replay_swap_78.json")))
    sys.exit(K.run(body, st))
