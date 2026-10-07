# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_2_classdiff - card 145-a2-5 (retry of 145-a2-2), OFFLINE. Classes EVERY item of EVERY recorded Error List file
(tools/bench/**/errorlist*.json; the selftests' recordings are among them) twice: with the classifier as it was before this card
(the three regexes of tools/elrule.py md5 50f29adc, copied verbatim below as OLD) and with the current elrule.item_class (NEW),
both on "raw detail" (the text errorlist_check.py:423/512 builds). Prints one CHANGED line per item whose class differs.
Existing tools checked first: diag_c145_a2_2_insp.py diffs one s03/s04 pair only; no all-file class table exists.
PREDICTION CONTRACT: exactly ONE distinct item text changes class, None -> 'local', and it is the empty-raw item whose detail is
'This local or global variable is not wired ...' (gate C1); the s04 recording 5e53096a holds it once (gate C2). Any other change
= gate C1 FAIL.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c145_a2_2_classdiff.log -- py -u tools/bench/diag_c145_a2_2_classdiff.py"""
import collections, glob, json, os, re, sys                                                 # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from tools import protocol                                                                  # noqa: E402
from tools import elrule as ELR                                                             # noqa: E402

OLD = [("local", re.compile(r"local\s*variable.*not\s*connected", re.I | re.S)),
       ("cond", re.compile(r"while\s*loop.*conditional\s*terminal.*not\s*wired", re.I | re.S)),
       ("sr", re.compile(r"shift\s*register.*unwired\s*from\s*inside", re.I | re.S))]


def old_class(t):
    for c, rx in OLD:
        if rx.search(str(t or "")):
            return c
    return None


files = sorted(set(p.replace("\\", "/") for p in glob.glob("tools/bench/**/errorlist*.json", recursive=True)))
n_items = n_files = skipped = 0
changed = collections.Counter()
per_file = []
tot_old, tot_new = collections.Counter(), collections.Counter()
for p in files:
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:                                                                  # noqa: BLE001
        print("SKIP {0} unreadable {1}".format(p, type(e).__name__), flush=True)
        skipped += 1
        continue
    its = d.get("items") if isinstance(d, dict) else None
    if not isinstance(its, list):
        print("NOITEMS {0} {1} keys {2}".format(p, type(d).__name__, sorted(d)[:8] if isinstance(d, dict) else len(d)), flush=True)
        skipped += 1
        continue
    n_files += 1
    nch = 0
    for x in its:
        if not isinstance(x, dict):
            continue
        t = "{0} {1}".format(x.get("raw", "") or "", x.get("detail", "") or "")
        a, b = old_class(t), ELR.item_class(t)
        tot_old[a] += 1
        tot_new[b] += 1
        n_items += 1
        if a != b:
            nch += 1
            changed[(a, b, t.strip()[:150])] += 1
            print("CHANGED {0} | {1} -> {2} | raw={3!r} | detail={4!r}".format(p, a, b, (x.get("raw") or "")[:60],
                                                                              (x.get("detail") or "")[:80]), flush=True)
    if nch:
        per_file.append((p, nch))
print("FILES {0} classified, {1} without an items list/unreadable; ITEMS {2}".format(n_files, skipped, n_items), flush=True)
print("TOTALS old {0}".format(dict(tot_old)), flush=True)
print("TOTALS new {0}".format(dict(tot_new)), flush=True)
for (a, b, t), n in sorted(changed.items(), key=lambda kv: -kv[1]):
    print("DISTINCT x{0} | {1} -> {2} | {3}".format(n, a, b, t), flush=True)
for p, n in per_file:
    print("FILE-CHANGES {0} {1}".format(n, p), flush=True)
only = list(changed)
ok1 = (len(only) == 1 and only[0][0] is None and only[0][1] == "local"
       and re.match(r"^this local or global variable is not wired", only[0][2], re.I) is not None)
print("GATE {0} | C1 exactly one distinct item text changes class, None -> local, the empty-raw 'local or global variable is not "
      "wired' item | {1}".format("PASS" if ok1 else "FAIL", [(a, b, t[:60], n) for (a, b, t), n in changed.items()]), flush=True)
s04 = "tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json"
ok2 = dict(per_file).get(s04) == 1
print("GATE {0} | C2 the s04 recording 5e53096a holds that item once | {1}".format("PASS" if ok2 else "FAIL",
                                                                                  dict(per_file).get(s04)), flush=True)
np_, nf = int(ok1) + int(ok2), 2 - int(ok1) - int(ok2)
print(protocol.result_line(protocol.make_result(np_, nf, None if nf == 0 else ("C1" if not ok1 else "C2"), [])), flush=True)
sys.exit(0 if nf == 0 else 1)
