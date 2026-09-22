r"""jev_contradict.py - insertion #7 of the SECOND WAVE table in docs/jev-integration-plan.md:
PRE-DECIDED CONTRADICTIONS.

    py tools/jev_contradict.py [--plan docs/cycle27-plan.md] [--pairs 400] [--samples 3] [--controls]

`docs/cycle27-plan.md`'s `## Pre-decided` list has grown past 120 numbered items written over five days, and
several of them exist ONLY to withdraw, supersede, amend or correct an earlier one. A material session applies
them by number; nothing mechanical tells it that item 88 has already withdrawn item 81. This script pairs the
items that could plausibly collide and asks Jev, per pair, whether they contradict.

METHOD
  1. parse every top-level numbered item (`12.` / `111a.`) and its body
  2. for each item, pair it with the EIGHT earlier items sharing the most UNCOMMON tokens (>= 2 shared), where
     "uncommon" means the token appears in at most 15 % of items - shared boilerplate ("measured", "review")
     pairs everything with everything, so it is excluded by construction
  3. keep the highest-scoring pairs up to --pairs (<= 600)
  4. ask the noul question --samples times per pair and use the MEAN (3-sample consensus, second-wave #6)
  5. print the pairs at p >= 0.80, highest first

IT NEVER EDITS THE PLAN. The output is a list of pairs for a judgement session to read; deciding which of two
decisions stands is exactly the call CLAUDE.md reserves for judgement.

PRIOR ART CHECKED before writing: tools/doc_ingest.py (the model-read consistency audit this assists - it
reads CHANGED FILES as prose, it does not pair decisions); tools/doc_lint.py (mechanical: paths, line counts,
dispositions - no semantics); tools/jev.py (transport). No LabVIEW, no COM.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402

PLAN = os.path.join(ROOT, "docs", "cycle27-plan.md")
ITEM_RE = re.compile(r"^(\d{1,3}[a-z]?)\.\s+(.*)$")
HEAD_RE = re.compile(r"^#{1,6}\s")
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}|\b\d{3,6}\b")
STOP = set("""this that with from have been will must shall they them their when what which
where because there these those into over under only also very such than then else more most
item items line lines file files path paths plan cycle cycles session sessions user users rule rules
measured measure measurement review reviewed build built builds still does done make made same other
about after before again would could should never always every each both none said says
docs tools bench archive status claude""".split())

CONTRADICT_Q = {
    "type": "noul",
    "instructions": (
        "`a` and `b` are two numbered standing decisions from one long-running engineering project's plan "
        "document, written days apart; `b` is the EARLIER one. Decide whether they CONTRADICT: whether one "
        "orders, permits or asserts something the other forbids, withdraws, supersedes, corrects or asserts "
        "the opposite of - so that a worker applying both would be pulled two ways and one of them has to be "
        "the one that stands. Two decisions about the same subject that fit together do NOT contradict, and "
        "neither do two about different subjects that share vocabulary. An item that explicitly withdraws, "
        "supersedes, amends or corrects the other IS a contradiction for this purpose, even though it resolves "
        "it, because the earlier text still stands in the document."),
    "criteria": {
        "true": ("They cannot both be applied as written: one withdraws, supersedes, amends, corrects, "
                 "forbids or reverses what the other orders, permits or asserts."),
        "false": ("They can both be applied as written - they concern different things, or they concern the "
                  "same thing and agree, refine each other, or address different stages of it."),
    },
}


def parse_items(path=PLAN):
    """[{'id','title','body','text'}] - every top-level numbered item in the document, in order."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []
    items, cur = [], None
    for ln in lines:
        m = ITEM_RE.match(ln)
        if m:
            if cur:
                items.append(cur)
            cur = {"id": m.group(1), "title": m.group(2).strip(), "body": []}
            continue
        if cur is None:
            continue
        if HEAD_RE.match(ln) or (ln and not ln[0].isspace() and not ln.startswith(("-", "*", ">", "|", "`"))):
            items.append(cur)
            cur = None
            continue
        cur["body"].append(ln.strip())
    if cur:
        items.append(cur)
    for it in items:
        it["text"] = (it["title"] + " " + " ".join(it["body"])).strip()
        it.pop("body", None)
    return items


def _tokens(text):
    return {t.lower() for t in TOKEN_RE.findall(text)} - STOP


def build_pairs(items, per_item=8, min_shared=2, cap=400, df_frac=0.15):
    """[(score, i, j)] with j < i: the most-overlapping earlier item for each item, capped and sorted."""
    toks = [_tokens(it["text"]) for it in items]
    n = len(items)
    df = {}
    for s in toks:
        for t in s:
            df[t] = df.get(t, 0) + 1
    limit = max(2, int(df_frac * n))
    rare = [{t for t in s if df.get(t, 0) <= limit} for s in toks]
    pairs = []
    for i in range(n):
        scored = []
        for j in range(i):
            sh = len(rare[i] & rare[j])
            if sh >= min_shared:
                scored.append((sh, i, j))
        scored.sort(reverse=True)
        pairs.extend(scored[:per_item])
    pairs.sort(reverse=True)
    return pairs[:cap]


def ask_pair(a_text, b_text, samples=3, timeout=25, retries=0, purpose="contradict"):
    """(mean p, [samples], err). 3-sample consensus by default (second-wave #6).

    Uses `jev.ask_n` when that module offers it - it is the project's ONE consensus implementation since
    2026-09-22 and reports the spread the same way everywhere - and falls back to a local loop otherwise, so
    this file keeps working whichever version of jev.py it is imported beside."""
    if hasattr(jev, "ask_n"):
        mean, spread, err = jev.ask_n({"a": a_text[:1400], "b": b_text[:1400]},
                                      {"contradict": CONTRADICT_Q}, n=samples, purpose=purpose,
                                      timeout=timeout, retries=retries)
        if mean is None:
            return None, [], err or "no noul in response"
        vals = (spread or {}).get("values") if isinstance(spread, dict) else None
        return mean, list(vals or []), None
    ps, err = [], None
    for _ in range(max(1, samples)):
        resp, e = jev.ask({"a": a_text[:1400], "b": b_text[:1400]}, {"contradict": CONTRADICT_Q},
                          purpose=purpose, timeout=timeout, retries=retries)
        if e:
            err = e
            continue
        p = jev.noul(resp, "contradict")
        if p is not None:
            ps.append(p)
    if not ps:
        return None, [], err or "no noul in response"
    return sum(ps) / len(ps), ps, None


def main(argv=None):
    for _s in (sys.stdout, sys.stderr):      # plan titles carry emoji; this console is cp949
        try:
            _s.reconfigure(errors="backslashreplace")
        except Exception:      # noqa: BLE001
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=PLAN)
    ap.add_argument("--pairs", type=int, default=400)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--threshold", type=float, default=0.80)
    ap.add_argument("--out", default=os.path.join(BENCH, "jev_contradict.json"))
    a = ap.parse_args(argv)
    path = a.plan if os.path.isabs(a.plan) else os.path.join(ROOT, a.plan)
    items = parse_items(path)
    print("=== %d numbered items parsed from %s" % (len(items), os.path.basename(path)))
    pairs = build_pairs(items, cap=min(a.pairs, 600))
    print("=== %d pairs (<=8 earlier items each, >=2 shared uncommon tokens, cap %d)" % (len(pairs), a.pairs))
    out, t0 = [], time.time()
    for k, (score, i, j) in enumerate(pairs):
        p, ps, err = ask_pair(items[i]["text"], items[j]["text"], samples=a.samples)
        if p is None:
            continue
        out.append({"a": items[i]["id"], "b": items[j]["id"], "p": p, "samples": ps, "shared": score,
                    "a_title": items[i]["title"][:120], "b_title": items[j]["title"][:120]})
        if (k + 1) % 25 == 0:
            print("    ... %d/%d pairs, %.0f s" % (k + 1, len(pairs), time.time() - t0))
            sys.stdout.flush()
    out.sort(key=lambda r: -r["p"])
    hits = [r for r in out if r["p"] >= a.threshold]
    print("\n=== %d pair(s) at p >= %.2f ; top %d" % (len(hits), a.threshold, a.top))
    for r in out[:a.top]:
        print("  %5.2f  %-5s vs %-5s  shared=%-2d | %s || %s" % (
            r["p"], r["a"], r["b"], r["shared"], r["a_title"][:70], r["b_title"][:70]))
    try:
        json.dump({"plan": os.path.basename(path), "n_items": len(items), "n_pairs": len(pairs),
                   "samples": a.samples, "rows": out}, open(a.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\n=== readings -> %s" % a.out)
    except OSError as e:
        print("(could not write %s: %s)" % (a.out, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
