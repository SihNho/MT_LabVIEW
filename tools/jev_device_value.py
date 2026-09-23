r"""jev_device_value.py - DEVICE VALUE survey: how much recorded loss would a proposed device have removed? (user 2026-09-24
03:3x "해당 장치를 통해서 얼마만큼의 성능을 보일지 확인 ... 만들도록 해"). Per item Jev answers prevented / reduced / unrelated for
ONE device sentence (5-sample consensus, jev.ask_n); code sums loss. ADVISORY (docs/jev-integration-plan.md "## Device value").
PRIOR ART: tools/jev.py ask_n + normalise (used unchanged); tools/cycle_runner.py BGRUN_START_RE/BGRUN_FAIL_RE/GATE_FAIL_RE
(imported) + its bookkeeping exclusion; tools/stagekit.py checked - LabVIEW stage helpers only, none fits a text survey.
v1 retrospectives (bare `VIOLATION: <slug>`, no loss, saturated) contribute nothing; Findings are read only where sectioned.
  --device "<s>" [--since D] [--slug s] [--dry]   pre-build expected saving -> tools/bench/device_value_<slug>.json
  --device "<s>" --after D [--slug s]             post-build: same menu over items dated >= D; prints the prior json too
Labelled-set measurement of this menu: tools/bench/jev_device_value_labels.py (labels in jev_device_value_labels.json).
Loss per item: VIOLATION = its loss_min/loss_usd; failing log = that failed run's bgrun wall-clock; finding = none."""
import argparse, datetime, glob, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); BENCH = os.path.join(HERE, "bench")
sys.path.insert(0, HERE)
import jev  # noqa: E402
import cycle_runner as CR  # noqa: E402
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
CLASSES = ("prevented", "reduced", "unrelated")
Q = {"type": "choice", "instructions": (
    "A LabVIEW VI-scripting project records its failures: failing build logs (first failing gate line), and "
    "retrospective VIOLATION lines and FINDINGS paragraphs. `device` describes ONE proposed tool. `item` is ONE "
    "recorded failure or finding. Decide what the device, had it existed then, would have done to THIS item. Judge the "
    "item's actual cause, not shared vocabulary: an item that merely mentions the same node or terminal but failed "
    "for another reason is unrelated."), "criteria": {
    "prevented": "The device removes this item's cause: with it, this failure or finding would not have happened.",
    "reduced": ("The device addresses part of the cause or shortens the diagnosis/repair, but the item would still "
                "have occurred in some form."),
    "unrelated": "The item's cause is outside what the device does; the item would have happened unchanged."}}
LOSS_RE = re.compile(r"^VIOLATION:\s*([\w-]+)\s*\|\s*loss_min=([\d.?]+)\s*\|\s*loss_usd=([\d.?]+)[^\n]*", re.M)
DUR_RE = re.compile(r"^BGRUN (?:END rc=\d+ after|TIMEOUT killed after) (\d+)s", re.M)
SKIP_CMD = re.compile(r"doc_lint|audit_cycle|violations\.py|retrospective|doc_ingest|outcome_review|prior_art_review|"
                      r"selftest|peer\.ps1", re.I)
num = lambda s: float(s) if re.fullmatch(r"\d+(\.\d+)?", s or "") else None


def corpus(since=None):
    items, seen = [], set()
    def add(kind, text, cycle, date, lm, lu, src):
        t = jev.normalise(text)
        if (kind, t[:400]) not in seen:
            seen.add((kind, t[:400])); items.append({"id": len(items), "kind": kind, "text": t[:900], "cycle": cycle,
                                                    "date": date, "loss_min": lm, "loss_usd": lu, "src": src})
    for p in sorted(glob.glob(os.path.join(ROOT, "archive", "peer", "*retrospective*.md"))):
        fn = os.path.basename(p); date = fn[:10]; cyc = (re.search(r"cycle(\w+)", fn) or [None, "?"])[1]
        txt = open(p, encoding="utf-8", errors="replace").read()
        if (since and date < since) or "\n## Answer" not in txt: continue
        ans = txt.split("\n## Answer", 1)[1].split("\n## What was done with it", 1)[0]
        for m in LOSS_RE.finditer(ans):
            add("violation", ans[max(0, m.start() - 700):m.start()].strip() + "\n" + m.group(0), cyc, date,
                num(m.group(2)), num(m.group(3)), fn)
        f = re.search(r"^##\s+findings\b.*?$(.*?)(?=^##\s|\Z)", ans, re.M | re.S | re.I)
        for para in re.split(r"\n(?=\s*(?:\*\*)?\d+\.\s)", f.group(1)) if f else []:
            if len(para.strip()) > 40: add("finding", para.strip(), cyc, date, None, None, fn)
    for p in sorted(glob.glob(os.path.join(BENCH, "*.log"))):
        fn = os.path.basename(p); date = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        if fn.startswith(("cycle_", "peer_", "priorart_", "retro")) or (since and date < since): continue
        txt = open(p, encoding="utf-8", errors="replace").read(); st = list(CR.BGRUN_START_RE.finditer(txt))
        if not st or SKIP_CMD.search(st[-1].group(1)) or not CR.BGRUN_FAIL_RE.search(txt[st[-1].end():]): continue
        seg = txt[st[-1].end():]; g = CR.GATE_FAIL_RE.search(seg); d = DUR_RE.search(seg)
        line = (g.group(1) or g.group(2)) if g else next((l for l in reversed(seg.splitlines()) if not l.startswith(
            "BGRUN") and re.search(r"\w(Error|Exception)\b|FAIL|refus", l)), "(no failing line)")
        add("log", "script: %s\nfirst failing line: %s" % (os.path.basename(st[-1].group(1).split()[-1])[:120], line[:300]),
            "?", date, round(int(d.group(1)) / 60.0, 1) if d else None, None, fn)
    return items


def classify(device, items, n=None, workers=4, ask=None):
    ask = ask or jev.ask_n
    def one(it):
        mean, spread, err = ask({"device": device, "item": it["text"], "kind": it["kind"], "cycle": it.get("cycle"),
                                 "loss_min": it.get("loss_min")}, {"effect": Q}, n=n, purpose="device-value")
        if not isinstance(mean, dict) or not mean: return dict(it, answer="unknown", p=None, err=err)
        w = max(mean, key=mean.get); return dict(it, answer=w, p=round(mean[w], 3), spread=(spread or {}).get("spread"))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, items))


def totals(rows):
    t = {c: sum(r["answer"] == c for r in rows) for c in CLASSES + ("unknown",)}
    for k in ("loss_min", "loss_usd"):
        t[k + "_prevented"] = round(sum(r.get(k) or 0 for r in rows if r["answer"] == "prevented"), 2)
        t[k + "_reduced_half"] = round(0.5 * sum(r.get(k) or 0 for r in rows if r["answer"] == "reduced"), 2)
        t[k + "_expected"] = round(t[k + "_prevented"] + t[k + "_reduced_half"], 2)
    ds = sorted(r["date"] for r in rows if r.get("date"))
    t["days"] = (datetime.date.fromisoformat(ds[-1]) - datetime.date.fromisoformat(ds[0])).days + 1 if ds else 0
    t["loss_min_expected_per_day"] = round(t["loss_min_expected"] / t["days"], 2) if t["days"] else None
    return t


def main(argv=None):
    a = argparse.ArgumentParser()
    for f in ("--device", "--since", "--after", "--slug"): a.add_argument(f)
    for f in ("--dry", "--reprint"): a.add_argument(f, action="store_true")
    a = a.parse_args(argv)
    slug = a.slug or re.sub(r"\W+", "_", a.device.lower())[:40].strip("_")
    out = os.path.join(BENCH, "device_value_%s%s.json" % (slug, "_after_" + a.after if a.after else ""))
    items = [] if a.reprint else corpus(since=a.after or a.since)   # --reprint: table from the saved json, no Jev call
    print("CORPUS %d items %s" % (len(items), {k: sum(i["kind"] == k for i in items) for k in ("violation", "finding", "log")}))
    if a.dry: return 0
    rows = json.load(open(out, encoding="utf-8"))["rows"] if a.reprint else classify(a.device, items); t = totals(rows)
    for r in rows:   # item text is printed VERBATIM: bgrun exempts a Jev COMMAND from its inner-failure scan
        # (docs/violation-decisions.md `## device-failed - 2026-09-24 03:53`), so no mangling is needed or allowed
        print("%-9s p=%-5s %-9s c%-4s lm=%-5s %s" % (r["answer"], r["p"], r["kind"], r["cycle"], r["loss_min"],
                                                   r["text"].replace("\n", " | ")[:110]))
    if not a.reprint: json.dump({"device": a.device, "since": a.since, "after": a.after, "totals": t, "rows": rows,
                                 "created": datetime.datetime.now().isoformat(timespec="seconds")}, open(out, "w", encoding="utf-8"), indent=1)
    print("TOTALS %s -> %s" % (json.dumps(t), os.path.relpath(out, ROOT)))
    prior = os.path.join(BENCH, "device_value_%s.json" % slug)
    if a.after and os.path.exists(prior):
        pt = json.load(open(prior, encoding="utf-8"))["totals"]
        print("PRIOR %s\nREALISED loss_min/day saved = pre %s - post %s" % (json.dumps(pt), pt.get(
            "loss_min_expected_per_day"), t["loss_min_expected_per_day"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
