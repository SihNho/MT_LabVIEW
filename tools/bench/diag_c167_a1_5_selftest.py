# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_167-a1-5.md
# ---
r"""diag_c167_a1_5_selftest - card 167-a1-5 Part A (OFFLINE, json only, no LabVIEW): self-test of the SHARED Error List class function and
the SHARED JSON rewrite helpers, replaying recorded data (docs/script-writing.md rule 7).
Found before writing: the shared elcls ALREADY exists - tools/stagekit.py:2840 `el_class` ("the scratch recipes' elcls", self-test
tools/bench/selftest_t7_ring.py, synthetic data only) with `el_norm_ocr` (== errorlist_check.norm_ocr :331); no second one is added.
The JSON rewrite helpers were moved into tools/stagekit.py (json_text_like / json_newline_of / rewrite_json / json_changed_keys /
rewrite_json_selftest) from tools/bench/diag_c166_a1_1_lib.py:16-47.
The OLD inline elcls is CALLED, not pasted: its `norm_ocr` / `elcls` function definitions are taken from
tools/bench/diag_c165_a3_4_elexp.py (a script that runs on import) by `ast` and executed with that file's own OCR_ALIASES and elrule.
PREDICTION CONTRACT:
 E1 the read errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json (0c0664d8) has 47 items.
 E2 stagekit.el_class == the old inline elcls on every one of the 47 items (47 equal, 0 differ).
 E3 errorlist_check.class_counts(items) == the stored line tools/bench/diag_c166_a1_2_elexp.log:15 (brief's 'looseends 23, notconnected 21,
    unwiredinput 1, twotypes 1, other 1' - plain norm keys).
 E4 el_class counts == that stored line re-keyed mechanically (key -> 'input' if it holds 'unwiredorbadterminal', else 'other:'+norm_ocr(key),
    summed): predicted {other:wirewirehaslooseends 23, other:thiswireisnotconnectedtoanything 22 (anvthing folds into anything), input 1,
    other:youhayeconnectedtwoterminalsofdifferenttypes 1}.
 J  stagekit.rewrite_json_selftest on memory_model.json + plan_ring_p5s02e_pred.json (in %TEMP%, nothing in the tree written): [] failed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c167_a1_5_selftest.log -- py -u tools/bench/diag_c167_a1_5_selftest.py"""
import ast, collections, json, os, re, sys, tempfile                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K                                                                        # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
import elrule as ELR                                                                        # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
READ = os.path.join(B, "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
OLD = os.path.join(B, "diag_c165_a3_4_elexp.py")
STORED = os.path.join(B, "diag_c166_a1_2_elexp.log")
gate = L.Gate(fatal_default=False)


def old_inline():
    """The old script's norm_ocr / elcls / OCR_ALIASES, executed from its own source text (no copy here)."""
    tree = ast.parse(open(OLD, encoding="utf-8").read())
    keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in ("norm_ocr", "elcls"))
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "OCR_ALIASES" for t in n.targets))]
    ns = {"re": re, "ELR": ELR}
    exec(compile(ast.Module(body=keep, type_ignores=[]), OLD, "exec"), ns)
    print("FACT old inline taken from {0}: {1}".format(os.path.basename(OLD), ["{0}:{1}".format(getattr(n, "name", "OCR_ALIASES"), n.lineno) for n in keep]), flush=True)
    return ns["elcls"]


items = L.J(READ)["items"]
gate("E1 read {0} md5 {1}: {2} items == 47".format(os.path.basename(READ), L.md5(READ)[:8], len(items)), len(items) == 47)
old = old_inline()
new_c = [K.el_class(it) for it in items]
old_c = [old(it) for it in items]
diff = [(i, a, b) for i, (a, b) in enumerate(zip(new_c, old_c)) if a != b]
gate("E2 stagekit.el_class == old inline elcls per item: {0} equal, {1} differ".format(len(items) - len(diff), len(diff)), not diff, diff[:5])
line = next(x for x in open(STORED, encoding="utf-8").read().splitlines() if x.startswith("RECORD class counts of the read: "))
stored = json.loads(line.split(": ", 1)[1])
cc = EC.class_counts(items)
gate("E3 class_counts(items) == stored diag_c166_a1_2_elexp.log:15 {0}".format(stored), cc == stored, cc)
rekey = collections.Counter()
for k, n in stored.items():
    rekey["input" if "unwiredorbadterminal" in K.el_norm_ocr(k) else "other:" + K.el_norm_ocr(k)] += n
got = dict(collections.Counter(new_c))
gate("E4 el_class counts {0} == stored re-keyed {1}".format(json.dumps(got, sort_keys=True), json.dumps(dict(rekey), sort_keys=True)),
     got == dict(rekey))
bad = K.rewrite_json_selftest([os.path.join(B, "memory_model.json"), os.path.join(B, "plan_ring_p5s02e_pred.json")], tempfile.gettempdir())
gate("J stagekit.rewrite_json_selftest: failed {0}".format(bad), not bad)
sys.exit(gate.result([]))
