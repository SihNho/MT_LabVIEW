"""Card 137-P3 (offline, no LabVIEW): plan_ring_p4_v5.json = v4 + an explicit loop-input tunnel on base While #10170
for each crossing of its border, in the form of v3's pool crossing (plan_ring_p4_v4.json:1069-1095:
tunnel p4_t_pool -> wire src -> TP1.outer -> wire TP1.inner -> dst).

Prior art checked: tools/bench/prep_c137_p2_facts.md (v4 maker, same json.dump indent=1 as stagesim.py:2409-2410);
no existing tool adds tunnel actions to a plan (plan file edit only, per the card).

Prediction contract:
  - p4_x_fd and p4_x_dt are #10170 border crossings (src on 686, dst on body 23166) -> each gets +2 actions
    (tunnel before the wire, inner wire after the wire's RLE); the wire's dst becomes new:<T>.outer.
  - p4_x_n2_out: src IAN1 on FS4.f0, dst EQ2 on 23166 (plan_ring_p4_v4.json:622-705) - NOT a #10170 crossing;
    left unchanged and reported.
  - v4 has 163 actions (checked below) -> v5 has 167; diff = 4 inserted + 2 dst changes + 2 why changes.
"""
import copy, hashlib, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from tools import protocol  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
V4 = os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v4.json")
V5 = os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v5.json")
META = os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v3_meta.json")

POOL_CITE = "plan_ring_p4_v4.json:1069-1095 (p4_t_pool/p4_x_pool/p4_w_pool_in, PD298(b))"
X = [  # (crossing wire id, tunnel id, tunnel symbol, inner wire id, CT label)
    ("p4_x_fd", "p4_t_fd", "TFD1", "p4_w_fd_in", "'# FD points' t8936"),
    ("p4_x_dt", "p4_t_dt", "TDT1", "p4_w_dt_in", "'# DT points' t28844"),
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    gates = {"pass": 0, "fail": 0}
    first_fail = None

    def gate(ok, label):
        nonlocal first_fail
        gates["pass" if ok else "fail"] += 1
        if not ok and first_fail is None:
            first_fail = label
        print("GATE {0} | {1}".format("PASS" if ok else "FAIL", label))

    print("v4 md5", md5(V4))
    v4 = json.load(open(V4, encoding="utf-8"))
    acts = copy.deepcopy(v4["actions"])
    n4 = len(acts)
    print("v4 actions", n4)
    ids = [a.get("id") for a in acts]
    # n2_out shape check (prediction: not a #10170 crossing)
    a_n2 = acts[ids.index("p4_x_n2_out")]
    diag = {a.get("as"): a.get("diagram") for a in acts if a.get("op") == "create"}
    print("p4_x_n2_out", a_n2["src"], "->", a_n2["dst"], "| IAN1 diagram", diag.get("IAN1"), "| EQ2 diagram", diag.get("EQ2"))
    gate(diag.get("IAN1") == "new:FS4.f0" and diag.get("EQ2") == 23166, "p4_x_n2_out is FS4 frame -> body 23166 (no #10170 border)")

    diffs = []
    for xid, tid, sym, wid, lab in X:
        i = [a.get("id") for a in acts].index(xid)
        w = acts[i]
        dst0 = copy.deepcopy(w["dst"])
        gate(isinstance(w["src"], dict) and w["src"].get("uid") == w["src"].get("term_uid"), xid + " src is a CT uid form")
        gate(acts[i + 1].get("op") == "wire_remove_loose_ends" and acts[i + 1].get("of") == xid, xid + " followed by its RLE")
        tun = {"op": "tunnel", "id": tid, "loop": 10170, "body": 23166, "parent": 686, "dir": "in", "as": sym,
               "why": "ROUTE tunnel | PRECEDENT | card 137-P3 (PD305(a)/PD298(b) precedent): explicit loop-input tunnel on "
                      "base While #10170 (body 23166, parent 686) for {0} {1}, same form as {2}".format(xid, lab, POOL_CITE)}
        w["dst"] = "new:{0}.outer".format(sym)
        old_why = w["why"]
        w["why"] = ("ROUTE branch | PRECEDENT | card 137-P3: #686 control {0} (wired) -> {1} outer: same-diagram BRANCH on 686 "
                    "(was connect_term_uid across the #10170 border, stagesim.py:1366-1368); form of p4_x_pool").format(lab, sym)
        inner = {"op": "wire", "id": wid, "src": "new:{0}.inner".format(sym), "dst": dst0,
                 "why": "ROUTE connect | PRECEDENT | card 137-P3: {0} inner -> {1} (same pattern as p4_w_pool_in)".format(sym, dst0)}
        acts.insert(i, tun)                 # tunnel before the crossing wire
        acts.insert(i + 3, inner)           # after wire (i+1) and its RLE (i+2)
        diffs.append((xid, "insert", i + 1, tid))
        diffs.append((xid, "dst", i + 2, json.dumps(dst0), w["dst"]))
        diffs.append((xid, "why", i + 2, old_why[:60], w["why"][:60]))
        diffs.append((xid, "insert", i + 4, wid))

    v5 = copy.deepcopy(v4)
    v5["actions"] = acts
    with open(V5, "w", encoding="utf-8") as f:
        json.dump(v5, f, indent=1, default=str)
    print("v5 actions", len(acts))
    gate(len(acts) == n4 + 4, "v5 = v4 + 4 actions")

    # every other action unchanged: drop inserted, compare remaining except the two changed wires' dst/why
    new_ids = {t for _, t, _, _, _ in X} | {w for _, _, _, w, _ in X}
    rest = [a for a in acts if a.get("id") not in new_ids]
    same = 0
    other_changes = []
    for a4, a5 in zip(v4["actions"], rest):
        if a4 == a5:
            same += 1
            continue
        keys = sorted(k for k in set(a4) | set(a5) if a4.get(k) != a5.get(k))
        other_changes.append((a4.get("id"), keys))
    print("unchanged actions", same, "changed", other_changes)
    gate(same == n4 - 2 and all(k == ["dst", "why"] for _, k in other_changes), "only dst/why of the 2 crossing wires changed")
    top = sorted(k for k in set(v4) | set(v5) if k != "actions" and v4.get(k) != v5.get(k))
    gate(not top, "no top-level key changed ({0})".format(top))
    for d in diffs:
        print("DIFF", d)

    # per-build-step counts, from the v3 meta's per-action step (new actions take their crossing's step)
    meta = json.load(open(META, encoding="utf-8"))
    stepof = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "step" in o and "unit" in o:
                stepof[o["id"]] = (o["step"], o.get("unit"), o.get("session"))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(meta)
    xstep = {}
    for xid, tid, sym, wid, lab in X:
        xstep[tid] = xstep[wid] = stepof.get(xid)
    counts4, counts5, missing = {}, {}, []
    for a in v4["actions"]:
        s = stepof.get(a.get("id"))
        if s is None:
            missing.append(a.get("id"))
            continue
        counts4[s[0]] = counts4.get(s[0], 0) + 1
    for a in acts:
        s = stepof.get(a.get("id")) or xstep.get(a.get("id"))
        if s is None:
            continue
        counts5[s[0]] = counts5.get(s[0], 0) + 1
    print("meta step of crossings", {x: stepof.get(x) for x, *_ in X}, "n2_out", stepof.get("p4_x_n2_out"))
    print("ids without meta step", missing)
    print("step counts v4", dict(sorted(counts4.items())), "v5", dict(sorted(counts5.items())))
    gate(all(c <= 40 for c in counts5.values()), "v5 per-build-step counts <= 40 (v3 meta cut)")
    print("v5 md5", md5(V5))
    print(protocol.result_line(protocol.make_result(gates["pass"], gates["fail"], first_fail,
                                                    [{"path": "tools/bench/plan_ring_p4_v5.json", "md5": md5(V5)}])))


if __name__ == "__main__":
    main()
