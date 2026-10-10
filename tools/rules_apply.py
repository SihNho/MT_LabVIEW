# ---
# labview: none
# hardware: none
# ---
"""rules_apply - the ONE apply path for protected files (rules, CLAUDE.md, AGENTS.md, both harnesses' hooks and settings,
the protected list, this device). CANDIDATE device, card chat-X6 = experiment 2 of discussion structure-equal-02 (agreed
round 6, relay/round_06_claude.md:43 and relay/round_06_gpt.md:24). Not active: nothing refuses direct edits yet.

    py tools/rules_apply.py [--root R] stage <id> --debate <dir> --round N
    py tools/rules_apply.py [--root R] add-test <id> --command "<cmd>" --log <log> [--md5 path=md5 ...]
    py tools/rules_apply.py [--root R] check <id>
    py tools/rules_apply.py [--root R] apply <id>
    py tools/rules_apply.py [--root R] audit [--baseline [--dry]]

Layout and manifest: tools/bench/candidates/README.md. Protected globs: tools/rules_protected.json (the one place).
Ledger: tools/bench/rules_ledger.jsonl (one JSON line per apply / baseline). Every command ends with a RESULT line.
PRIOR ART: debate_relay.state_of (STATE parser, reused), protocol.result_line / parse_result_line (reused); no earlier
apply/ledger device in tools/ (grep "ledger" tools/*.py: only usage ledgers). Self-test: tools/bench/selftest_rules_apply.py.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import protocol as P                                                                    # noqa: E402
from debate_relay import state_of                                                       # noqa: E402

ROOT = os.path.dirname(HERE)
PROTECTED_REL = "tools/rules_protected.json"
LEDGER_REL = "tools/bench/rules_ledger.jsonl"
CAND_REL = "tools/bench/candidates"


def md5_file(path):
    """md5 hex of a file's bytes, or None when it does not exist."""
    if not os.path.isfile(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def norm(rel):
    """Repo-relative path with forward slashes; raises on an absolute or escaping path."""
    r = rel.replace("\\", "/").strip()
    while r.startswith("./"):
        r = r[2:]
    if not r or r.startswith("/") or re.match(r"^[A-Za-z]:", r) or ".." in r.split("/"):
        raise ValueError("not a clean repo-relative path: %r" % rel)
    return r


def _glob_re(g):
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif g.startswith("**", i):
            out, i = out + ".*", i + 2
        elif g[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif g[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(g[i]), i + 1
    return re.compile("^" + out + "$", re.I)


def load_protected(root=ROOT):
    """The protected-list dict from <root>/tools/rules_protected.json (globs, exclude, open)."""
    with open(os.path.join(root, PROTECTED_REL), encoding="utf-8") as f:
        return json.load(f)


def is_protected(rel, prot):
    """True when repo-relative `rel` matches a protected glob and no exclude glob."""
    r = norm(rel)
    return any(_glob_re(g).match(r) for g in prot["globs"]) and \
        not any(_glob_re(g).match(r) for g in prot.get("exclude", []))


def protected_files(root, prot):
    """Sorted repo-relative paths of every existing file under root that is protected (walks only each glob's fixed prefix)."""
    found = set()
    for g in prot["globs"]:
        parts = g.split("/")
        k = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[")), len(parts))
        base = os.path.join(root, *parts[:k]) if k else root
        if k == len(parts):
            if os.path.isfile(base):
                found.add("/".join(parts))
            continue
        for dp, dns, fns in os.walk(base):
            dns[:] = [d for d in dns if d not in (".git",)]
            for fn in fns:
                rel = os.path.relpath(os.path.join(dp, fn), root).replace("\\", "/")
                if is_protected(rel, prot):
                    found.add(rel)
    return sorted(found)


def read_ledger(root=ROOT):
    """List of ledger entries (dicts) in file order; [] when there is no ledger."""
    p = os.path.join(root, LEDGER_REL)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def last_md5s(ledger):
    """{path: (md5, kind, id)} from the LAST ledger entry naming each path."""
    out = {}
    for e in ledger:
        for pm in e.get("paths", []):
            out[pm["path"]] = (pm["md5"], e.get("kind"), e.get("id"))
    return out


def _append_ledger(root, entry):
    p = os.path.join(root, LEDGER_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")


def cand_dir(root, cid):
    return os.path.join(root, CAND_REL, cid)


def agreement_check(root, ag):
    """[(label, ok, detail)] - both relay/round_NN_<side>.md carry ag['token'] in their last STATE 'agreed' list, exactly."""
    out = []
    for side in ("claude", "gpt"):
        f = os.path.join(root, norm(ag["debate"]), "relay", "round_%02d_%s.md" % (int(ag["round"]), side))
        if not os.path.isfile(f):
            out.append(("agreement:" + side, False, "missing " + f))
            continue
        with open(f, encoding="utf-8") as fh:
            st = state_of(fh.read())
        agreed = st.get("agreed") or []
        ok = isinstance(agreed, list) and ag["token"] in agreed
        why = "token in agreed" if ok else ("token only in STATE.open" if ag["token"] in (st.get("open") or [])
                                            else "token not in STATE.agreed")
        out.append(("agreement:" + side, ok, "%s (%s)" % (why, os.path.basename(f))))
    return out


def check(root, cid):
    """[(label, ok, detail)] for candidate `cid`: manifest, agreement, protected, no drift, candidate md5, extras, tests."""
    g = []
    mp = os.path.join(cand_dir(root, cid), "manifest.json")
    try:
        with open(mp, encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError) as e:
        return [("manifest", False, "%s: %s" % (mp, e))]
    g.append(("manifest", m.get("schema") == "rules-candidate/1" and m.get("change_id") == cid and
              bool(m.get("protected_paths")), "schema/change_id/paths"))
    try:
        g += agreement_check(root, m["agreement"])
    except (KeyError, ValueError, TypeError) as e:
        g.append(("agreement", False, "bad agreement block: %s" % e))
    prot = load_protected(root)
    listed = set()
    for pp in m.get("protected_paths", []):
        try:
            rel = norm(pp["path"])
        except ValueError as e:
            g.append(("path", False, str(e)))
            continue
        listed.add(rel)
        g.append(("protected:" + rel, is_protected(rel, prot), "in tools/rules_protected.json"))
        live = md5_file(os.path.join(root, rel))
        g.append(("no-drift:" + rel, live == pp.get("base_md5"), "live %s base %s" % (live, pp.get("base_md5"))))
        cand = md5_file(os.path.join(cand_dir(root, cid), "files", rel))
        g.append(("cand-md5:" + rel, cand is not None and cand == pp.get("cand_md5"),
                  "file %s manifest %s" % (cand, pp.get("cand_md5"))))
    extra = []
    fdir = os.path.join(cand_dir(root, cid), "files")
    for dp, _, fns in os.walk(fdir):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), fdir).replace("\\", "/")
            if rel not in listed:
                extra.append(rel)
    g.append(("no-unlisted-files", not extra, ",".join(extra)[:150]))
    tests = m.get("tests") or []
    g.append(("tests-present", bool(tests), "%d test(s)" % len(tests)))
    for i, t in enumerate(tests):
        r = P.parse_result_line(t.get("result_line", ""))
        g.append(("test%d:pass" % i, r is not None and not P.result_failed(r) and r.get("status") == "PASS",
                  (r or {}).get("status")))
        md5s = t.get("md5s") or {}
        bad = [pp["path"] for pp in m.get("protected_paths", []) if md5s.get(pp["path"]) != pp.get("cand_md5")]
        g.append(("test%d:md5s" % i, not bad, "differs from cand_md5: " + ",".join(bad) if bad else "all cand md5s"))
    return g


def _finish(gates, label, artefacts=()):
    for name, ok, det in gates:
        print("%s  %s  %s" % ("PASS" if ok else "FAIL", name, str(det)[:200]))
    fails = [n for n, ok, _ in gates if not ok]
    print(P.result_line(P.make_result(len(gates) - len(fails), len(fails),
                                      (label + ": " + fails[0]) if fails else None, artefacts)))
    return 1 if fails else 0


def cmd_stage(root, cid, debate, rnd):
    """(Re)write manifest.json from files/: base_md5 = live, cand_md5 = candidate; keeps recorded tests."""
    d = cand_dir(root, cid)
    mp = os.path.join(d, "manifest.json")
    old = {}
    if os.path.isfile(mp):
        with open(mp, encoding="utf-8") as f:
            old = json.load(f)
    paths = []
    for dp, _, fns in os.walk(os.path.join(d, "files")):
        for fn in fns:
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, os.path.join(d, "files")).replace("\\", "/")
            paths.append({"path": rel, "base_md5": md5_file(os.path.join(root, rel)), "cand_md5": md5_file(full)})
    m = {"schema": "rules-candidate/1", "change_id": cid, "protected_paths": sorted(paths, key=lambda x: x["path"]),
         "agreement": {"debate": norm(debate), "round": int(rnd), "token": cid + " 동의"},
         "tests": old.get("tests", [])}
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    return _finish([("staged", bool(paths), "%d path(s)" % len(paths))], "stage",
                   [{"path": os.path.relpath(mp, root).replace("\\", "/"), "md5": md5_file(mp)}])


def cmd_add_test(root, cid, command, log, md5_args):
    """Append a test entry: the log's last RESULT line; md5s from its artefacts plus path=md5 args."""
    mp = os.path.join(cand_dir(root, cid), "manifest.json")
    with open(mp, encoding="utf-8") as f:
        m = json.load(f)
    with open(log, encoding="utf-8", errors="replace") as f:
        txt = f.read()
    r = P.parse_result_line(txt)
    md5s = {norm(a["path"]): a.get("md5") for a in ((r or {}).get("artefacts") or []) if a.get("path")}
    for kv in md5_args or []:
        k, v = kv.split("=", 1)
        md5s[norm(k)] = v.strip()
    m.setdefault("tests", []).append({"command": command, "result_line": P.result_line(r) if r else "",
                                      "md5s": md5s})
    with open(mp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    return _finish([("result-line", r is not None, (r or {}).get("status"))], "add-test")


def cmd_check(root, cid):
    return _finish(check(root, cid), "check " + cid)


def cmd_apply(root, cid):
    """check, then copy the candidates over the live paths, re-hash, append one ledger line. Refuses on any failed gate."""
    gates = check(root, cid)
    if not all(ok for _, ok, _ in gates):
        print("REFUSED apply %s: check failed, nothing written" % cid)
        return _finish(gates, "apply " + cid)
    with open(os.path.join(cand_dir(root, cid), "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    done = []
    for pp in m["protected_paths"]:
        rel = norm(pp["path"])
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".rules_apply.tmp"
        shutil.copyfile(os.path.join(cand_dir(root, cid), "files", rel), tmp)
        os.replace(tmp, dst)
        got = md5_file(dst)
        gates.append(("rehash:" + rel, got == pp["cand_md5"], got))
        done.append({"path": rel, "md5": got})
    ok = all(o for _, o, _ in gates)
    if ok:
        _append_ledger(root, {"schema": "rules-ledger/1", "kind": "apply", "id": cid,
                              "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "paths": done,
                              "agreement": m["agreement"],
                              "tests": [{"command": t.get("command"), "md5s": t.get("md5s")} for t in m["tests"]]})
    gates.append(("ledger", ok, LEDGER_REL if ok else "not written: re-hash mismatch"))
    return _finish(gates, "apply " + cid, done)


def audit(root):
    """[(label, ok, detail)] per protected file: VIA-APPLY / BASELINE when it equals the ledger, else OUT-OF-BAND."""
    prot = load_protected(root)
    last = last_md5s(read_ledger(root))
    g = []
    files = protected_files(root, prot)
    for rel in files:
        live = md5_file(os.path.join(root, rel))
        if rel not in last:
            g.append(("OUT-OF-BAND " + rel, False, "never applied (not in ledger)"))
        elif last[rel][0] == live:
            g.append(("%s %s" % ("VIA-APPLY" if last[rel][1] == "apply" else "BASELINE", rel), True, last[rel][2]))
        else:
            g.append(("OUT-OF-BAND " + rel, False, "live %s ledger %s (last %s %s)" % (live, last[rel][0],
                                                                                  last[rel][1], last[rel][2])))
    for rel in sorted(set(last) - set(files)):
        if is_protected(rel, prot):
            g.append(("OUT-OF-BAND " + rel, False, "in ledger but missing on disk"))
    return g


def cmd_audit(root, baseline=False, dry=False):
    if not baseline:
        return _finish(audit(root), "audit")
    prot = load_protected(root)
    files = protected_files(root, prot)
    entry = {"schema": "rules-ledger/1", "kind": "baseline", "id": "baseline-" + time.strftime("%Y%m%d-%H%M%S"),
             "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "paths": [{"path": r, "md5": md5_file(os.path.join(root, r))} for r in files]}
    existing = read_ledger(root)
    for pm in entry["paths"]:
        print("BASELINE-FILE  %s  %s" % (pm["path"], pm["md5"]))
    print("BASELINE %s: %d protected file(s) found" % ("DRY (no ledger write)" if dry else "WRITE", len(files)))
    gates = [("baseline-files", bool(files), "%d file(s)" % len(files)),
             ("ledger-empty", not existing, "%d existing entr(ies)" % len(existing))]
    if dry or not all(ok for _, ok, _ in gates):
        if existing:
            print("REFUSED baseline: a ledger already exists (a second baseline would launder out-of-band edits)")
        return _finish(gates, "audit --baseline")
    _append_ledger(root, entry)
    return _finish(gates + [("ledger-written", True, LEDGER_REL)], "audit --baseline")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("stage"); s.add_argument("id"); s.add_argument("--debate", required=True)
    s.add_argument("--round", type=int, required=True)
    s = sp.add_parser("add-test"); s.add_argument("id"); s.add_argument("--command", required=True)
    s.add_argument("--log", required=True); s.add_argument("--md5", action="append")
    sp.add_parser("check").add_argument("id")
    sp.add_parser("apply").add_argument("id")
    s = sp.add_parser("audit"); s.add_argument("--baseline", action="store_true"); s.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if a.cmd == "stage":
        return cmd_stage(root, a.id, a.debate, a.round)
    if a.cmd == "add-test":
        return cmd_add_test(root, a.id, a.command, a.log, a.md5)
    if a.cmd == "check":
        return cmd_check(root, a.id)
    if a.cmd == "apply":
        return cmd_apply(root, a.id)
    return cmd_audit(root, a.baseline, a.dry)


if __name__ == "__main__":
    sys.exit(main())
