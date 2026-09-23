r"""jev_device_value_labels.py - measure the device-value menu (tools/jev_device_value.py Q) on the hand-labelled set
tools/bench/jev_device_value_labels.json (38 items x 2 device sentences, labelled before any Jev call; the question text was
fixed before the run, so the set is held-out for it). 5-sample consensus (jev.ask_n default). Writes
tools/bench/jev_device_value_labels_result.json. Scored twice: all items, and real (non-synthetic) items only.
Dangerous direction = unrelated -> prevented (a device credited with a loss it would not have removed).
Usage: py tools/bench/jev_device_value_labels.py [labels.json]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import jev_device_value as D  # noqa: E402


def score(rows, dk):
    pairs = [(r["labels"][dk], r["answer"]) for r in rows]
    per = {c: [sum(1 for t, a in pairs if t == c == a), sum(1 for t, _ in pairs if t == c)] for c in D.CLASSES}
    return {"n": len(pairs), "accuracy": round(sum(t == a for t, a in pairs) / float(len(pairs) or 1), 3),
            "per_class_hit_of": per,
            "fp_unrelated_to_prevented": sum(t == "unrelated" and a == "prevented" for t, a in pairs)}


def measure(path, n=None, ask=None, out_path=None):
    L = json.load(open(path, encoding="utf-8")); out = {}
    for dk, sentence in L["devices"].items():
        rows = D.classify(sentence, L["items"], n=n, ask=ask)
        out[dk] = {"device": sentence, "all": score(rows, dk),
                   "real_only": score([r for r in rows if not r.get("synthetic")], dk),
                   "misses": [[r["key"], r["labels"][dk], r["answer"], r.get("p")] for r in rows
                              if r["labels"][dk] != r["answer"]]}
        for part in ("all", "real_only"):
            s = out[dk][part]
            print("LABELS %s %-9s n=%d acc=%.3f per_class(hit/of)=%s fp(unrelated->prevented)=%d" % (
                dk, part, s["n"], s["accuracy"], s["per_class_hit_of"], s["fp_unrelated_to_prevented"]))
        for m in out[dk]["misses"]:
            print("  MISS %s %s" % (dk, m))
    if out_path:
        json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1)
    return out


if __name__ == "__main__":
    lab = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "jev_device_value_labels.json")
    measure(lab, out_path=os.path.join(HERE, "jev_device_value_labels_result.json"))
