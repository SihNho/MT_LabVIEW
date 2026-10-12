# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_166-a1-4.json
# ---
r"""selftest_c166_pbtight - card 166-a1-4 (docs/d1/ring-p5c.md PD397(e)), OFFLINE on STORED data (no LabVIEW).
Shared functions under test (stagekit): pb_record_lines, pb_provenance (class-3 provenance, PD397(e)(1)), pb_frame_coverage (per-frame
coverage in classes 2 and 3, PD397(e)(2)), pb_inherit_ctx (chain_tunnel_case newest-wins + chain_logs, PD397(e)(3)), pb_inherited_row and
pb_386 which call them. OLD = the pre-change byte copy tools/bench/diag_c166_a1_4_stagekit_pre.txt (md5 dd57c1ca), loaded as a module.
Stored PB inputs of an adopted step (adopted_scratch.jsonl line n, as selftest_c161_pbinherit.py R1-R3 builds them): the plan
(plan_md5s), its finalized base graph and last step file (sim end), the scratch json (`real_end_rows`, `stagexec` bindings), <plan>_pred.json
(cdiff_rows) and <plan>_licence.json; the stored verdict = the scratch log's `PASS  PB` / `FAIL  PB` line and its `RECORD PB` lines.
PREDICTION (gates):
 U1  pb_record_lines(diag_c161_p5s02b_scratch.log): error in -> [(158, {3934, 4965})], total data array in -> [(161, {1842, 3954})].
 P   p5s02c / p5s02d / p5s02e (lines 13-15): NEW pb_386 ok, recorded sinks + classes == the stored log's RECORD PB lines, blocked [];
     pb_provenance of the two #376 class-3 rows = diag_c161_p5s02b_scratch.log:[158] / [161] (the RECORD text itself is unchanged).
 S   stricter only, every adopted line 1-15: NEW recorded subset of OLD recorded, OLD blocked subset of NEW blocked, OLD ok -> NEW ok
     (a line both versions cannot score raises the same exception: listed, gate on equality). Any OLD-ok -> NEW-not-ok = RETURN.
 N1  class-3 row without provenance (chain_logs empty) -> None; OLD (no provenance rule) -> 3.
 N1b provenance line with another S1 set (temp log, 4965 -> 4966) -> None.   N1c log without the sink's line -> None.
 N2  missing frame on the p5s02b CLASS-2 rows (stored line 12): the entries carried through frame 31517 dropped -> None (NEW); OLD -> 2
     (the review's hole). N2b the class-3 rows (line 15): pb_frame_coverage on the same mutation -> not ok; the whole row is then taken by
     CLASS 1 (unchanged by PD397(e), which names classes 2 and 3) - printed as a fact, not gated.
 N3  doubled frame: an entry carried through 31517 duplicated -> None.   N3b one 31506 entry replaced by a 31517 entry (count still
     2 per uid) -> None (NEW); OLD -> 3.
 N4  chain_tunnel_case newest-wins: a temp adopted chain where p5s02b's record (newest) and a byte copy of it under a temp plan path (older)
     both create tunnels 31593/31598/31628/31640 -> NEW ctx maps them to the real (newest) plan and the row is class 3; OLD ctx maps them to
     the older copy and the same row (NEW function) is None.
 F   stored files unchanged (adopted_scratch.jsonl and the three scratch logs md5 before == after).
Usage: py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_c166_pbtight.log -- py -u tools/bench/selftest_c166_pbtight.py"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


PRE = os.path.join(HERE, "diag_c166_a1_4_stagekit_pre.txt")
gate("B0 pre-change copy md5 == dd57c1ca", md5(PRE).startswith("dd57c1ca"), md5(PRE))
KO = types.ModuleType("stagekit_pre")
KO.__file__ = os.path.join(ROOT, "tools", "stagekit.py")
sys.modules["stagekit_pre"] = KO
exec(compile(open(PRE, encoding="utf-8").read(), PRE, "exec"), KO.__dict__)

V, SX, JC = K.pure("vigraph"), K.pure("stagexec"), K.pure("jev_candidates")
LAB = JC.node_labels_default()
S1f = K.s1_frame_graph(LAB)
ADOPT = os.path.join(HERE, "adopted_scratch.jsonl")
RECS = [json.loads(x) for x in open(ADOPT, encoding="utf-8") if x.strip()]
LOGB = "tools/bench/diag_c161_p5s02b_scratch.log"
WATCH = [ADOPT] + [os.path.join(ROOT, RECS[i - 1]["log"].replace("\\", "/")) for i in (12, 13, 14, 15)]
M0 = [md5(p) for p in WATCH]

# ---- U1 ----------------------------------------------------------------------------------------------------------------------------
rl = K.pb_record_lines(LOGB)
gate("U1 pb_record_lines(p5s02b scratch log): error in -> [(158, {3934,4965})], total data array in -> [(161, {1842,3954})]",
     rl.get("376|Terminal|error in|0") == [(158, frozenset([3934, 4965]))]
     and rl.get("376|Terminal|total data array in|0") == [(161, frozenset([1842, 3954]))],
     dict((k, [(i, sorted(s) if s else s) for i, s in v]) for k, v in rl.items()))


def inputs(ln):
    """The stored PB inputs of adopted line ln (as selftest_c161_pbinherit.py R1-R3)."""
    r = RECS[ln - 1]
    pp = list(r["plan_md5s"])[0]
    Pq = K.jload(K.ROOT, pp)
    D = K.jload(K.ROOT, r["log"].replace("\\", "/")[:-4] + ".json")
    Bq = K.jload(K.ROOT, Pq["finalized"]["base"]["path"])
    Lq = K.jload(K.ROOT, Pq["finalized"]["step_files"][-1]["path"])["state"]
    Fq = K.run_bind(report=D["stagexec"])
    real, _al = K.real_rows_from_record(D["real_end_rows"], Lq["terminals"], Fq)
    PRq = K.jload(K.ROOT, pp.replace(".json", "_pred.json"))
    REN = K.licence_renames(K.jload(K.ROOT, pp.replace(".json", "_licence.json")))
    objs = SX.bind_state(Lq, {"obj": Fq, "term": {}, "diag": {}})[0].get("objs") or []
    FSq = Bq.get("fs_tunnel_pairs", Bq.get("fs_pairs"))
    return dict(r=r, pp=pp, P=Pq, B=Bq, L=Lq, F=Fq, real=real, PR=PRq, REN=REN, objs=objs, FS=FSq)


def score(mod, I):
    return mod.pb_386(I["B"]["terminals"], I["L"], I["real"], I["objs"], I["F"], I["P"], I["PR"]["cdiff_rows"], I["P"]["open_rows"], LAB, I["FS"],
                      I["REN"], S1f, V)


def stored(I):
    lp = os.path.join(K.ROOT, I["r"]["log"].replace("\\", "/"))
    ls = open(lp, encoding="utf-8", errors="replace").read().splitlines()
    pb = [x.strip()[:4] for x in ls if x.strip().startswith(("PASS  PB ", "FAIL  PB "))][-1:]
    cls = {}
    for x in ls:
        if "RECORD PB " in x:
            s = x.split("RECORD PB ", 1)[1].split(": ", 1)
            cls[s[0]] = s[1].split(" (")[0]
    return pb, cls


# ---- P + S --------------------------------------------------------------------------------------------------------------------------
cls_name = {1: "class 1", 2: "class 2", 3: "class 3"}
RET = []
I15 = R15 = I12 = R12 = None
for ln in range(1, len(RECS) + 1):
    stem = RECS[ln - 1]["stage"].replace("stage_d1_ring_", "").replace(".py", "")
    try:
        I = inputs(ln)
    except Exception as e:                                                         # noqa: BLE001
        print("FACT S line {0} {1}: stored PB inputs not loadable: {2}: {3}".format(ln, stem, type(e).__name__, str(e)[:160]), flush=True)
        continue
    out = []
    for mod in (KO, K):
        try:
            out.append(score(mod, I))
        except Exception as e:                                                     # noqa: BLE001
            out.append("EXC {0}: {1}".format(type(e).__name__, str(e)[:200]))
    o, n = out
    if isinstance(o, str) or isinstance(n, str):
        gate("S line {0} {1}: both versions raise the same (not scorable)".format(ln, stem), o == n, (o if isinstance(o, str) else "ok",
                                                                                                         n if isinstance(n, str) else "ok"))
        continue
    rs = lambda x: set(y["sink"] for y in x["recorded"])                           # noqa: E731
    bs = lambda x: set(y["sink"] for y in x["blocked"])                            # noqa: E731
    ok = rs(n) <= rs(o) and bs(o) <= bs(n) and (n["ok"] or not o["ok"])
    if o["ok"] and not n["ok"]:
        RET.append({"line": ln, "step": stem, "blocked": [(y["sink"], y["why"][-300:]) for y in n["blocked"]]})
    pb, scl = stored(I)
    gate("S line {0} {1}: stricter only - ok old {2} / new {3}; recorded {4} -> {5}; blocked {6} -> {7}; stored PB {8}".format(
        ln, stem, o["ok"], n["ok"], len(rs(o)), len(rs(n)), len(bs(o)), len(bs(n)), pb), ok,
        {"newly_blocked": sorted(bs(n) - bs(o)), "no_longer_recorded": sorted(rs(o) - rs(n))})
    if ln in (13, 14, 15):
        got = dict((y["sink"], cls_name.get(y.get("class"), "tag only")) for y in n["recorded"])
        want = dict((k, v.split(" (")[0] if v.startswith("class") else "tag only") for k, v in scl.items())
        cx = K.pb_inherit_ctx(I["P"], I["F"], labels=LAB, fs_pairs=I["FS"], S1f=S1f, V=V)
        pv = dict((y["sink"].split("|")[2], K.pb_provenance(y["sink"], [int(u) for u in y["why"].split("S1 source uids [", 1)[1].split("]")[0].split(", ")],
                                                            cx["chain_connects"][(376, y["sink"].split("|")[2])][0], cx)[1][:60])
                  for y in n["recorded"] if y.get("class") == 3)
        gate("P line {0} {1}: NEW pb_386 ok, blocked [], recorded rows + classes == the stored log's RECORD PB lines; stored PB {2}; "
             "class-3 provenance {3}".format(ln, stem, pb, pv),
             n["ok"] and not n["blocked"] and got == want and pb == ["PASS"]
             and pv.get("error in", "").startswith("diag_c161_p5s02b_scratch.log:[158]")
             and pv.get("total data array in", "").startswith("diag_c161_p5s02b_scratch.log:[161]"), {"got": got, "want": want})
    if ln == 15:
        I15, R15 = I, n
    if ln == 12:
        I12, R12 = I, n
print("FACT RETURN rows (old PASS -> new not ok): {0}".format(RET or "none"), flush=True)

# ---- N: negatives on the P5 final's stored PB inputs (line 15, p5s02e) ------------------------------------------------------------
I, r = I15, R15
ctx = K.pb_inherit_ctx(I["P"], I["F"], labels=LAB, fs_pairs=I["FS"], S1f=S1f, V=V)
G1 = r["G1"]
by = dict((y["sink"], y) for y in r["old"]["cd"]["rows"])
fm = K.frame_tag_map(G1)
RB = K.pb_bound_rows(r["old"]["cd"], G1, V)
SK = dict((s.split("|")[2], s) for s in by if s.startswith("376|"))
res0 = lambda nm: [K.frame_src_resolve(x, fm) for x in by[SK[nm]]["after"]]      # noqa: E731
NM = ("error in", "total data array in")


def row(nm, res=None, c=None, mod=K):
    s = SK[nm]
    return mod.pb_inherited_row(s, by[s], res if res is not None else res0(nm), G1, S1f, RB.get(s), c or ctx)


def short(x):
    return (x[0], x[1][-260:])


pos = [row(nm) for nm in NM]
gate("N0 p5s02e stored: both #376 rows class 3 (NEW, ctx chain_logs has p5s02b)", [x[0] for x in pos] == [3, 3], [short(x) for x in pos])
n1 = [row(nm, c=dict(ctx, chain_logs={})) for nm in NM]
o1 = [row(nm, c=dict(ctx, chain_logs={}), mod=KO) for nm in NM]
gate("N1 class-3 row without provenance (chain_logs empty) -> None; OLD -> 3", all(x[0] is None for x in n1) and [x[0] for x in o1] == [3, 3]
     and all("(v) provenance" in x[1] for x in n1), [short(x) for x in n1])
TMP = tempfile.mkdtemp(prefix="c166_pbtight_")
src = open(os.path.join(ROOT, LOGB), encoding="utf-8", errors="replace").read()
lg_b = os.path.join(TMP, "diag_alt_uids.log")
open(lg_b, "w", encoding="utf-8").write(src.replace("S1 source uids [3934, 4965]", "S1 source uids [3934, 4966]")
                                        .replace("S1 source uids [1842, 3954]", "S1 source uids [1842, 3955]"))
pp_b = [k for k in ctx["chain_logs"] if k.endswith("plan_ring_p5s02b.json")]
n1b = [row(nm, c=dict(ctx, chain_logs=dict(ctx["chain_logs"], **{pp_b[0]: lg_b}))) for nm in NM] if pp_b else []
gate("N1b provenance line with another S1 source set (temp log, 4965->4966 / 3954->3955) -> None", n1b and all(x[0] is None for x in n1b),
     [short(x) for x in n1b])
lg_c = os.path.join(TMP, "diag_no_line.log")
open(lg_c, "w", encoding="utf-8").write("\n".join(x for x in src.splitlines() if "RECORD PB 376|Terminal|error in|0" not in x
                                                  and "RECORD PB 376|Terminal|total data array in|0" not in x))
n1c = [row(nm, c=dict(ctx, chain_logs=dict(ctx["chain_logs"], **{pp_b[0]: lg_c}))) for nm in NM] if pp_b else []
gate("N1c adopted log without the sink's RECORD PB line -> None", n1c and all(x[0] is None for x in n1c), [short(x) for x in n1c])
F17 = 31517
drop = lambda rs_: [e for e in rs_ if F17 not in set(f for _t, f in e[1])]        # noqa: E731
# N2 on the CLASS-2 rows of p5s02b's stored inputs (line 12): class 1 cannot take them (base after [] -> R0 != end), so the class-2 code judges
Gb12 = R12["G1"]
by12 = dict((y["sink"], y) for y in R12["old"]["cd"]["rows"])
fm12, RB12 = K.frame_tag_map(Gb12), K.pb_bound_rows(R12["old"]["cd"], Gb12, V)
ctx12 = K.pb_inherit_ctx(I12["P"], I12["F"], labels=LAB, fs_pairs=I12["FS"], S1f=S1f, V=V)
sk12 = lambda nm: "376|Terminal|{0}|0".format(nm)                                  # noqa: E731
r12 = lambda nm: [K.frame_src_resolve(x, fm12) for x in by12[sk12(nm)]["after"]]  # noqa: E731
n2 = [K.pb_inherited_row(sk12(nm), by12[sk12(nm)], drop(r12(nm)), Gb12, S1f, RB12.get(sk12(nm)), ctx12) for nm in NM]
o2 = [KO.pb_inherited_row(sk12(nm), by12[sk12(nm)], drop(r12(nm)), Gb12, S1f, RB12.get(sk12(nm)), ctx12) for nm in NM]
p2 = [K.pb_inherited_row(sk12(nm), by12[sk12(nm)], r12(nm), Gb12, S1f, RB12.get(sk12(nm)), ctx12)[0] for nm in NM]
gate("N2 missing frame, p5s02b class-2 rows (stored line 12; unmutated NEW {0}): entries carried through 31517 dropped ({1} -> {2}) -> None; "
     "OLD -> {3}".format(p2, len(r12(NM[0])), len(drop(r12(NM[0]))), [x[0] for x in o2]),
     p2 == [2, 2] and all(x[0] is None for x in n2) and all("coverage" in x[1] for x in n2), [short(x) for x in n2])
# N2b the class-3 rows (line 15): the coverage function the class-3 code calls, on the same mutation
own = ctx["frames"].get(376, set())
cfr = ctx["cases"].get(31308) or []
tu1 = lambda b: K._iv((G1["rows"].get(b) or {}).get("term_uid"))                   # noqa: E731
su_ = dict((nm, sorted(K._iv((S1f["rows"].get(b) or {}).get("term_uid")) for b in by[SK[nm]]["before"])) for nm in NM)
c2b = [K.pb_frame_coverage(drop(res0(nm)), [tu1(b) for b, _t in drop(res0(nm))], su_[nm], own, cfr, True) for nm in NM]
c2p = [K.pb_frame_coverage(res0(nm), [tu1(b) for b, _t in res0(nm)], su_[nm], own, cfr, True)[0] for nm in NM]
n2c = [row(nm, res=drop(res0(nm))) for nm in NM]
gate("N2b class-3 rows (line 15): pb_frame_coverage unmutated {0}, 31517 entries dropped -> not ok; FACT the whole row then goes to CLASS 1 "
     "(NEW {1}, unchanged class, PD397(e) scope = classes 2/3)".format(c2p, [x[0] for x in n2c]),
     c2p == [True, True] and all(not x[0] for x in c2b), [x[1][:200] for x in c2b])
via17 = lambda nm: [e for e in res0(nm) if F17 in set(f for _t, f in e[1])]      # noqa: E731
n3 = [row(nm, res=res0(nm) + via17(nm)[:1]) for nm in NM]
gate("N3 doubled frame: one entry carried through 31517 duplicated -> None", all(x[0] is None for x in n3), [short(x) for x in n3])


def swap(nm):
    rs_, v = res0(nm), via17(nm)
    i = [k for k, e in enumerate(rs_) if F17 not in set(f for _t, f in e[1])][0]
    j = [e for e in v if e[0] == rs_[i][0]] or v[:1]                                # the same source's 31517 entry
    return rs_[:i] + j[:1] + rs_[i + 1:]


n3b = [row(nm, res=swap(nm)) for nm in NM]
o3b = [row(nm, res=swap(nm), mod=KO) for nm in NM]
gate("N3b doubled frame, count unchanged: a 31506 entry replaced by the same source's 31517 entry -> None; OLD -> {0}".format(
    [x[0] for x in o3b]), all(x[0] is None for x in n3b), [short(x) for x in n3b])

# ---- N4: chain_tunnel_case newest-wins --------------------------------------------------------------------------------------------
rb = RECS[11]                                                                       # adopted_scratch.jsonl:12 = p5s02b
ppb = list(rb["plan_md5s"])[0]
cp_plan = os.path.join(TMP, "plan_ring_p5s02b_copy.json")
shutil.copyfile(os.path.join(ROOT, ppb), cp_plan)
cp_log = os.path.join(TMP, "diag_copy_scratch.log")
shutil.copyfile(os.path.join(ROOT, rb["log"].replace("\\", "/")), cp_log)
shutil.copyfile(os.path.join(ROOT, rb["log"].replace("\\", "/"))[:-4] + ".json", cp_log[:-4] + ".json")
newer = dict(rb, artefact={"md5": "N"}, input={"md5": "O"})
older = dict(rb, artefact={"md5": "O"}, input={"md5": "Z"}, plan_md5s={cp_plan: md5(cp_plan)}, log=cp_log)
ad = os.path.join(TMP, "adopted.jsonl")
open(ad, "w", encoding="utf-8").write(json.dumps(newer) + "\n" + json.dumps(older) + "\n")
cn = K.pb_inherit_ctx(I["P"], I["F"], base_vi_md5="N", labels=LAB, fs_pairs=I["FS"], S1f=S1f, V=V, adopt_path=ad)
co = KO.pb_inherit_ctx(I["P"], I["F"], base_vi_md5="N", labels=LAB, fs_pairs=I["FS"], S1f=S1f, V=V, adopt_path=ad)
TUN = (31593, 31598, 31628, 31640)
tn_ = dict((u, cn["chain_tunnel_case"].get(u)) for u in TUN)
to_ = dict((u, co["chain_tunnel_case"].get(u)) for u in TUN)
c4n = dict(ctx, chain_connects=cn["chain_connects"], chain_tunnel_case=cn["chain_tunnel_case"], chain_logs=cn["chain_logs"])
c4o = dict(c4n, chain_tunnel_case=co["chain_tunnel_case"])
n4n, n4o = [row(nm, c=c4n) for nm in NM], [row(nm, c=c4o) for nm in NM]
gate("N4 newest-wins: NEW ctx tunnels -> (newest {0}, 31308), OLD ctx -> (older temp copy); row class 3 with NEW ctx, None with OLD ctx".format(ppb),
     all(v == (ppb, 31308) for v in tn_.values()) and all(v == (cp_plan, 31308) for v in to_.values())
     and [x[0] for x in n4n] == [3, 3] and all(x[0] is None for x in n4o) and cn["chain_connects"].get((376, "error in"), ("",))[0] == ppb,
     {"new": tn_, "old": to_, "rows_new": [x[0] for x in n4n], "rows_old": [short(x) for x in n4o][:1]})
shutil.rmtree(TMP, ignore_errors=True)
gate("F stored files unchanged (adopted_scratch.jsonl + scratch logs of lines 12-15)", [md5(p) for p in WATCH] == M0, [m[:8] for m in M0])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
