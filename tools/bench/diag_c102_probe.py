r"""probe102 - firefighter cycle 102, offline only (no LabVIEW).
(1) plan_disp.json 7c432e1b (disk) vs the committed b535071e / 8a96086f: which keys differ (provenance vs content).
(2) the tunnel-flip seed defect (PD214(d)): re-apply op 12 (move_in #11310) on the OLD step-11 state with the
    refuted node:delete rule and print what flips and what happens to edge 11369 -> 11270.
"""
import copy, json, os, subprocess, sys
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS  # noqa: E402

PO = os.path.join(ROOT, "tools/bench/sim/disp/plan_disp.json")
cur = json.load(open(PO, encoding="utf-8"))


def git_json(rev):
    out = subprocess.run(["git", "show", rev + ":tools/bench/sim/disp/plan_disp.json"], cwd=ROOT, capture_output=True).stdout
    import hashlib
    return json.loads(out.decode("utf-8")), hashlib.md5(out).hexdigest()


def walk(a, b, path=""):
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                diffs.append(path + "/" + k + " (one side only)")
            else:
                diffs += walk(a[k], b[k], path + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(path + " len {0} vs {1}".format(len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diffs += walk(x, y, path + "[{0}]".format(i))
    elif a != b:
        diffs.append(path + ": {0!r} vs {1!r}".format(str(a)[:60], str(b)[:60]))
    return diffs


for rev in ("1bd3d74", "98e716b"):
    old, m = git_json(rev)
    d = walk(old, cur)
    print("PLAN {0} md5 {1} vs disk {2}: {3} differing leaves".format(rev, m, SS.md5_file(PO), len(d)))
    for x in d[:40]:
        print("   ", x)

# (2) the flip seed defect
st = json.load(open(os.path.join(ROOT, "tools/bench/sim/disp/step_11_move_in.json"), encoding="utf-8"))["state"]
a = next(x for x in cur["actions"] if x.get("id") == "mv_11310")
for label, rule in (("PROVISIONAL keep", SS.PROVISIONAL["move_in"]["params"]["only_source"]),
                    ("node:delete (refuted, exposes the seed bug)", {"constant": "delete", "node": "delete", "default": "keep"})):
    s_ = copy.deepcopy(st)
    P = dict(SS.PROVISIONAL["move_in"]["params"], only_source=rule)
    e, _c = SS.op_move_in(s_, a, P, None, {})
    w = dict((r["term_uid"], (r["wire_uid"], r["is_source"])) for r in s_["terminals"])
    print("RULE", label)
    print("   only_source", e["only_source"])
    print("   tunnel_flips", e["tunnel_flips"])
    print("   cleared", e["cleared_term_uids"], "bare_deleted", e["bare_deleted"])
    print("   11365", w.get(11365), "11369", w.get(11369), "11270", w.get(11270), "11316", w.get(11316))
