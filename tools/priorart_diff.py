# ---
# labview: none
# hardware: none
# ---
"""PRIOR-ART ON WHAT CHANGED ONLY, for a repeated session script (card chat-E3 item 5, user 2026-10-04).

A ring-step session script (stage_d1_ring_p4_s03v18.py) is a COPY of the previous session's script (s02v18) with names
changed - 143-P1's docstring says so - yet each copy bought a full prior-art review (3 dispatches in 143-1 alone). Here:

  sibling(recipe)   the last APPROVED script of the same pattern: same file name with every digit run masked
                    (stage_d1_ring_p#_s##v## ), in the same folder, whose prior-art stop record is released or novel FOR
                    THE BYTES ON DISK (stop_record.sha256_of, header-blind) - i.e. a review answered for exactly that text.
  scope(recipe)     a line diff (difflib, header block stripped) against that sibling. A changed line is PARAMETER-ONLY
                    when it equals its counterpart after masking string literals, numbers and digit runs in names (plan
                    path, file names, card ids, memory numbers); anything else is SUBSTANTIVE.
                    + plan side: stage_prerun.new_structure_classes(recipe) - op kinds / create classes no clean stage ran.
  -> review_needed False: no substantive line and no new structure class: guard_cycle allows (logged PRIORART-DIFF).
  -> review_needed True : the review is asked about the substantive lines + new classes only
                          (prior_art_review.py --diff-from <sibling> builds that narrowed task).
No sibling -> None: the full review rule applies unchanged.
"""
import difflib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

STR_RE = re.compile(r"(?:[rbuRBU]{0,2})(\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')")
NUM_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
DIGITS_RE = re.compile(r"\d+")


def pattern_key(path):
    return DIGITS_RE.sub("#", os.path.basename(path).lower())


def norm_line(s):
    s = STR_RE.sub('"S"', s)
    s = NUM_RE.sub("N", s)
    s = DIGITS_RE.sub("#", s)
    return re.sub(r"\s+", " ", s).strip()


def _text(path):
    """The CODE lines (header block stripped; comments and docstrings blanked by protocol.code_only, line numbers kept):
    prose in a copied script's docstring is not what a prior-art review is about."""
    import scope_header
    import protocol
    with open(path, "rb") as f:
        src = scope_header.canonical_bytes(f.read()).decode("utf-8", "replace")
    return [ln.rstrip() for ln in protocol.code_only(src).splitlines()]


def approved(path, records=None):
    """True when a stop record for `path` is released or novel for the bytes on disk now."""
    import stop_record as S
    recs = S.load_records() if records is None else records
    cur = S.sha256_of(path)
    keys = S.keys_for(os.path.relpath(path, ROOT))
    for r in recs:
        if not (S.keys_for(r.get("recipe_path")) & keys):
            continue
        rel = r.get("released") or {}
        if rel.get("sha256") and rel["sha256"] == cur:
            return True
    return False


def sibling(recipe, records=None):
    ap = os.path.abspath(recipe)
    d, key = os.path.dirname(ap), pattern_key(ap)
    cands = []
    for n in os.listdir(d):
        p = os.path.join(d, n)
        if os.path.normcase(p) == os.path.normcase(ap) or pattern_key(p) != key or not n.endswith(".py"):
            continue
        try:
            if approved(p, records):
                cands.append((os.path.getmtime(p), p))
        except Exception:                      # noqa: BLE001
            continue
    return max(cands)[1] if cands else None


def diff_lines(old, new):
    """(parameter_only_count, [(new line no, old text, new text)] substantive)."""
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    param, subst = 0, []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        a, b = old[i1:i2], new[j1:j2]
        if op == "replace" and len(a) == len(b):
            for k, (x, y) in enumerate(zip(a, b)):
                if norm_line(x) == norm_line(y):
                    param += 1
                else:
                    subst.append((j1 + k + 1, x, y))
            continue
        for k, y in enumerate(b):
            if y.strip() and not y.strip().startswith("#"):
                subst.append((j1 + k + 1, "", y))
        for x in a:
            if x.strip() and not x.strip().startswith("#"):
                subst.append((j1 + 1, x, ""))
    return param, subst


def scope(recipe, records=None, new_classes=None):
    sib = sibling(recipe, records)
    if not sib:
        return None
    param, subst = diff_lines(_text(sib), _text(recipe))
    if new_classes is None:
        try:
            import stage_prerun
            new_classes = stage_prerun.new_structure_classes(recipe)
        except Exception:                      # noqa: BLE001 - unknown -> review the plan side too
            new_classes = ["(new_structure_classes unavailable)"]
    return {"sibling": os.path.relpath(sib, ROOT).replace("\\", "/"), "param_only": param,
            "substantive": subst, "new_classes": list(new_classes),
            "review_needed": bool(subst or new_classes)}


def task_text(sc):
    """The narrowed review subject for prior_art_review.py --diff-from."""
    out = ["=== DIFF-ONLY REVIEW (card chat-E3): this script is a copy of %s, whose prior-art review was answered "
           "for its current bytes. %d parameter-only line(s) changed (names, paths, numbers) and are NOT under review. "
           "Review ONLY the lines and structure classes below. ===" % (sc["sibling"], sc["param_only"])]
    for ln, old, new in sc["substantive"][:120]:
        out.append("L%d  - %s\n      + %s" % (ln, old.rstrip(), new.rstrip()))
    if sc["new_classes"]:
        out.append("NEW structure classes (no clean stage ran them): " + ", ".join(sc["new_classes"]))
    return "\n".join(out)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print("usage: priorart_diff.py <recipe>")
        return 2
    sc = scope(a[0])
    print(json.dumps(sc, indent=1) if sc else "no approved sibling - the full review rule applies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
