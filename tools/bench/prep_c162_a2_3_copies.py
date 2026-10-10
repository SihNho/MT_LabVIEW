# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-3.md
# ---
r"""prep_c162_a2_3_copies - card 162-a2-3 step 1 (OFFLINE): list EVERY copy of the three PD392(e) blocks under tools/**/*.py and say, per copy,
whether it is byte-identical to the brief's reference site or how it differs. A block is found by its START anchor and kept only when it holds the
block's distinctive line; it ends at its END anchor. 'argument-only' = equal after every string literal is replaced by <S> and whitespace is folded
(the licence `why` text and the one-line / two-line `own, wr` form are the only expected differences).
Reference sites (brief): L prep_c156_a1_1_licence.py:49-60, P prep_c156_a1_1_pred.py:78-82, S selftest_c160_regface.py:73-79.
Prior art: no copy-finder exists (glob tools/**/*cop*y*.py: none); md5 / Gates CALLED from tools/invcheck.py.
PREDICTION CONTRACT (grep before the run): L 8 copies (c150_a3_1, c150_a3_6, c152_b2_1, c154_a3_2b, c155_a2_1, c155_a4_1, c156_a1_1, c160_c3_1);
P 5 copies (c154_a3_2b, c155_a2_1, c155_a4_1, c156_a1_1 identical; c160_c3_1 + an `ids` field); S 2 copies (regface; prep_c160_b3_1_mk with a
FRESH_IDS rewrite in the same loop).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c162_a2_3_copies.log -- py -u tools/bench/prep_c162_a2_3_copies.py"""
import glob
import io
import os
import re
import sys
import tokenize

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402

B = "tools/bench/"
BLOCKS = {
    "L": {"ref": B + "prep_c156_a1_1_licence.py", "start": re.compile(r"^own(, wr)? = collections\.defaultdict"),
          "mark": 'own[int(r["owner_uid"])].add(int(r["term_uid"]))', "end": "for o in sorted(own)]", "want": 8},
    "P": {"ref": B + "prep_c156_a1_1_pred.py", "start": re.compile(r"^cpe = \[\]"), "mark": 'an = max(ops[k - 1]["acts"]) if k else 0',
          "end": 'x.get("md5")})', "want": 5},
    "S": {"ref": B + "selftest_c160_regface.py", "start": re.compile(r"^acts = \[\]"), "mark": '"dw_" + a["id"][2:]',
          "end": re.compile(r'^\w+\["actions"\] = acts'), "want": 2},
}
SELF = os.path.basename(__file__)


def find(lines, spec):
    """[(first line no, last line no, text)] of every block in one file."""
    out = []
    for i, ln in enumerate(lines):
        if not spec["start"].match(ln):
            continue
        for j in range(i, min(i + 20, len(lines))):
            e = spec["end"]
            if (e.match(lines[j]) if hasattr(e, "match") else e in lines[j]):
                txt = "\n".join(lines[i:j + 1])
                if spec["mark"] in txt:
                    out.append((i + 1, j + 1, txt))
                break
    return out


def shape(txt):
    """The block with every string literal -> <S>, comments dropped, whitespace folded; `own, wr` one-line form == two-line form."""
    toks = []
    for t in tokenize.generate_tokens(io.StringIO(txt + "\n").readline):
        if t.type == tokenize.STRING:
            toks.append("<S>")
        elif t.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
            continue
        else:
            toks.append(t.string)
    s = " ".join(toks)
    s = s.replace("own , wr = collections . defaultdict ( set ) , collections . defaultdict ( list )",
                  "own = collections . defaultdict ( set ) wr = collections . defaultdict ( list )")
    s = re.sub(r"\.format \( <S> \)", ".format(<S>)", s)
    return re.sub(r"(<S> )+<S>", "<S>", s)     # adjacent literal concatenation == one literal


g = IC.Gates()
files = sorted(p for p in glob.glob(os.path.join(ROOT, "tools", "**", "*.py"), recursive=True) if os.path.basename(p) != SELF)
found = dict((k, []) for k in BLOCKS)
for p in files:
    try:
        lines = open(p, encoding="utf-8").read().splitlines()
    except UnicodeDecodeError:
        lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    for k, spec in BLOCKS.items():
        for a, b, txt in find(lines, spec):
            found[k].append((os.path.relpath(p, ROOT).replace("\\", "/"), a, b, txt))
for k, spec in BLOCKS.items():
    ref = [x for x in found[k] if x[0] == spec["ref"]]
    g("{0} reference site {1} found once".format(k, spec["ref"]), len(ref) == 1, [(x[1], x[2]) for x in ref])
    rtxt = ref[0][3] if ref else ""
    print("BLOCK {0}: {1} cop(y/ies)".format(k, len(found[k])), flush=True)
    for f, a, b, txt in found[k]:
        if txt == rtxt:
            how = "IDENTICAL (byte)"
        elif shape(txt) == shape(rtxt):
            how = "ARGUMENT-ONLY (string literals / own-wr line form differ)"
        else:
            rt, tt = shape(rtxt).split(" "), shape(txt).split(" ")
            extra = [t for t in tt if t not in rt][:12]
            how = "DIFFERS: tokens not in the reference {0}".format(extra)
        print("COPY {0} | {1}:{2}-{3} | md5 {4} | {5}".format(k, f, a, b, IC.md5(os.path.join(ROOT, f)), how), flush=True)
    g("{0} copies found {1} == grep prediction {2}".format(k, len(found[k]), spec["want"]), len(found[k]) == spec["want"], len(found[k]))
print(g.result([]), flush=True)
sys.exit(1 if g.failed else 0)
