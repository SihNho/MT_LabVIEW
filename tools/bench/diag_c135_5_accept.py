"""Card 135-5 (PD297): P3b-2 acceptance bookkeeping, OFFLINE (no LabVIEW, no COM).

Prior art checked: tools/errorlist_check.py already owns compare/_hit/reverdict/current_bed_text/class_counts; this
script only calls them. P3b-1's expected file was built the same way (card 131-6: P3a's entries, loose ends re-pinned
from the measured final read, PD274(b)).

Modes (one per card step):
  --measure  step 1: the recipe-written expected file's entries (norm_all + count, total) == P3b-1's 53 list.
             PREDICTION: equal (recipe b copied P3b-1's 53, stage_d1_ring_p3b2b.py:83-92).
  --write    step 2: keep the recipe file as *_recipe_stale.json; new expected = P3b-1's entries with every key-group
             count re-measured on the final read's raw items (130834). PREDICTION: 0 unmatched items, 0 items matching
             two keys, only `wirewirehaslooseends` changes 22 -> 20, total 51; reverdict with the new file = OK.
  --status   step 3: current_bed_text(STATUS.md) == ...\\D1_ring_p3b2b_20261002_130007.vi. PREDICTION yes.
  --delete   step 4: md5 of the two in-between files == 49cf7f77... / 6cc69221... -> delete; bed P3b-1, P3a still exist.
"""
import glob, hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as C  # noqa: E402  (lazy LabVIEW imports; nothing LabVIEW-side is bound)

B = os.path.join(ROOT, "tools", "bench")
CD = C.CLAUDEDEV
BED = os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi")
BED_MD5 = "395118775a52bc90073f4449b99f899d"
CUR = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
STALE = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007_recipe_stale.json")
P3B1 = os.path.join(B, "errorlist_expected_D1_ring_p3b1_20261002_060910.json")
READ = os.path.join(B, "errorlist_D1_ring_p3b2b_20261002_130007_20261002_130834.json")
READ_RAW = READ[:-5] + "_raw.json"
READ_MD5 = "7a17dad72388fc32de4a8ebbbd710c68"
DEL = {os.path.join(CD, "D1_ring_p3b2a_20261002_122043.vi"): "49cf7f77",
       os.path.join(CD, "scratch_c133_6_ring_p3b2a_20261002_093837.vi"): "6cc69221"}
KEEP = [os.path.join(CD, "D1_ring_p3b1_20261002_060910.vi"), os.path.join(CD, "D1_ring_p3a_20261001_180540.vi"), BED]
P, F, FIRST = 0, 0, None


def gate(label, ok, detail=""):
    global P, F, FIRST
    ok = bool(ok)
    P, F = P + ok, F + (not ok)
    if not ok and FIRST is None:
        FIRST = label
    print("GATE %s %s %s" % (label, "PASS" if ok else "FAIL", detail), flush=True)
    return ok


def load(p):
    return json.load(open(p, encoding="utf-8"))


def sig(d):
    return [(tuple(e.get("norm_all") or ()), tuple(e.get("norm_any") or ()), e.get("match"), int(e.get("count", 1)))
            for e in d.get("expected") or []]


def measure():
    a, b = load(CUR), load(P3B1)
    sa, sb = sig(a), sig(b)
    print("recipe file: total %s, %d entries, sum %d; P3b-1: total %s, %d entries, sum %d" % (
        a.get("total"), len(sa), sum(x[3] for x in sa), b.get("total"), len(sb), sum(x[3] for x in sb)))
    for i, (x, y) in enumerate(zip(sa, sb)):
        if x != y:
            print("  entry %d differs: recipe %s vs p3b1 %s" % (i, x, y))
    labels = [e.get("label") for e in a["expected"]] == [e.get("label") for e in b["expected"]]
    print("labels equal: %s; bed field %s" % (labels, os.path.basename(a.get("bed") or "")))
    return gate("S1_equal_53", sa == sb and a.get("total") == b.get("total") == 53, "labels_equal=%s" % labels)


def write():
    gate("S2_read_md5", C.md5(READ) == READ_MD5, C.md5(READ))
    gate("S2_bed_md5", C.md5(BED) == BED_MD5)
    src, raw, base = load(READ), load(READ_RAW), load(P3B1)
    items = raw.get("items") or []
    gate("S2_items_51", len(items) == 51 == src.get("n_reported"), "%d / n_reported %s" % (len(items), src.get("n_reported")))
    keys, order = {}, []
    for e in base["expected"]:
        k = tuple(e["norm_all"])
        if k not in keys:
            keys[k] = 0
            order.append(k)
    unmatched, multi = [], []
    for it in items:
        txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
        hits = [k for k in order if C._hit({"norm_all": list(k)}, txt)]
        if not hits:
            unmatched.append(it.get("raw"))
            continue
        if len(hits) > 1:
            multi.append((it.get("raw"), hits))
        keys[hits[0]] += 1
    gate("S2_unmatched_0", not unmatched, repr(unmatched)[:300])
    gate("S2_multi_0", not multi, repr(multi)[:300])
    oldsum = {k: sum(e["count"] for e in base["expected"] if tuple(e["norm_all"]) == k) for k in order}
    changed = {"".join(k): (oldsum[k], keys[k]) for k in order if oldsum[k] != keys[k]}
    print("key groups P3b-1 -> final read: %s" % {"+".join(k): (oldsum[k], keys[k]) for k in order})
    gate("S2_only_loose_22_20", changed == {"wirewirehaslooseends": (22, 20)}, repr(changed))
    if F:
        return False
    new = dict(base)
    new["expected"] = []
    for e in base["expected"]:
        e = dict(e)
        k = tuple(e["norm_all"])
        if oldsum[k] != keys[k]:
            if sum(1 for x in base["expected"] if tuple(x["norm_all"]) == k) != 1:
                return gate("S2_single_entry_group", False, "+".join(k))
            e["count"] = keys[k]
            e["label"] = "Wire: Wire has loose ends. (measured, card 135-4 final read)"
            e["cite"] = ("card 135-5 (PD297): re-pinned from the measured final read %s (md5 %s), class 22 -> 20; "
                         "P3b-1's value was 22 (card 131-6)" % (os.path.relpath(READ, ROOT), READ_MD5))
        new["expected"].append(e)
    new["bed"], new["bed_md5"], new["total"] = BED, BED_MD5, sum(e["count"] for e in new["expected"])
    new["decided_by"] = ("card 135-5 (PD297, PD291(d)): P3b-1's 53 entries with each key group re-counted on the launch's "
                         "full final read (card 135-4); only loose ends changed 22 -> 20 (PD292(b) class level). The recipe's "
                         "auto-written copy of P3b-1's 53 is kept as %s, not used." % os.path.basename(STALE))
    new["measured_from"] = os.path.relpath(READ, ROOT)
    new["per_class_p3b1"] = base.get("per_class_read")
    new["per_class_read"] = C.class_counts(items)
    new["per_class_delta"] = {k: new["per_class_read"].get(k, 0) - v for k, v in (base.get("per_class_read") or {}).items()
                              if new["per_class_read"].get(k, 0) != v}
    for k in ("r2_delta",):
        new.pop(k, None)
    gate("S2_total_51", new["total"] == 51, str(new["total"]))
    if F:
        return False
    shutil.copy2(CUR, STALE)
    gate("S2_stale_kept", C.md5(STALE) == C.md5(CUR), C.md5(STALE))
    with open(CUR, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=1, ensure_ascii=False)
    print("WROTE %s md5 %s" % (CUR, C.md5(CUR)))
    v, out = C.reverdict(BED, READ, READ_RAW, expected_path=CUR)
    r = load(out)
    return gate("S2_reverdict_OK", v == "OK", "%s extra %s missing %s -> %s" % (v, r["extra"], r["missing"], out))


def status():
    p = C.current_bed(os.path.join(ROOT, "STATUS.md"))
    return gate("S3_current_bed", p and os.path.normcase(p) == os.path.normcase(BED), str(p))


def delete():
    for p, pre in DEL.items():
        ok = os.path.exists(p) and C.md5(p).startswith(pre)
        if not gate("S4_md5 " + os.path.basename(p), ok, C.md5(p) if os.path.exists(p) else "absent"):
            return False
    for p in DEL:
        os.remove(p)
        gate("S4_gone " + os.path.basename(p), not os.path.exists(p))
    for p in KEEP:
        gate("S4_kept " + os.path.basename(p), os.path.exists(p), C.md5(p) if os.path.exists(p) else "absent")
    return not F


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--measure"
    {"--measure": measure, "--write": write, "--status": status, "--delete": delete}[mode]()
    import protocol
    print("mode %s" % mode)
    print(protocol.result_line(protocol.make_result(P, F, first_fail=FIRST)))
