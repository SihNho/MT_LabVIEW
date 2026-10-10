# ---
# labview: none
# hardware: none
# ---
"""rules_apply - the ONE apply path for protected files (rules, CLAUDE.md, AGENTS.md, both harnesses' hooks, settings and
agent definitions, the protected list, this device). CANDIDATE device, card chat-X6 = experiment 2 of discussion
structure-equal-02 (agreed round 6, relay/round_06_claude.md:43 and relay/round_06_gpt.md:24); bundle binding, token
reuse refusal and the hash-chained ledger: card chat-X9 (agreed round 10, relay/round_10_claude.md:38,
relay/round_10_gpt.md:27). Not active: nothing refuses direct edits yet and no real ledger exists.

    py tools/rules_apply.py [--root R] stage <change-id> --debate <dir> --round N
    py tools/rules_apply.py [--root R] add-test <change-id> --command "<cmd>" --log <log> [--md5 path=md5 ...]
    py tools/rules_apply.py [--root R] check <bundle-id>
    py tools/rules_apply.py [--root R] apply <bundle-id>
    py tools/rules_apply.py [--root R] audit [--baseline [--dry]]
    py tools/rules_apply.py [--root R] baseline-list --out <file>

BUNDLE ID = <change-id>@<first 8 hex of the md5 of the manifest's canonical core> (core = the manifest without its
`agreement` and `bundle` blocks: paths + base/cand md5s, rules_apply_md5, tests). Any change to the staged content gives a
new id. AGREEMENT TOKEN = "<bundle-id> 동의", required in the last STATE `agreed` list of BOTH relay round files.
`check` binds the id to the staged hash; `apply` re-hashes manifest, candidates and live files right before writing and
copies from the bytes it hashed. A token already in the ledger is refused. LEDGER: tools/bench/rules_ledger.jsonl, one
JSON line per apply / genesis baseline, each carrying `prev` = sha256 of the previous line (genesis: 64 zeros); `audit`
refuses a broken chain, a second baseline, a reused token, an apply line whose agreement no longer re-verifies against
the relay files (token in both STATE agreed lists AND the relay files' sha256 as recorded) or whose path md5s are not
its bundle's cand_md5s, and a live ledger of which the git-committed ledger is not a prefix.
Layout and manifest: tools/bench/candidates/README.md. Protected lists: tools/rules_protected.json (the one place).
PRIOR ART: debate_relay.state_of (STATE parser, reused), protocol.result_line / parse_result_line (reused); no earlier
apply/ledger device in tools/ (grep "ledger" tools/*.py: only usage ledgers). Self-tests: tools/bench/selftest_rules_apply.py,
tools/bench/selftest_shellguard_cand.py.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
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
SELF_REL = "tools/rules_apply.py"
GENESIS = "0" * 64
BID_RE = re.compile(r"^(?P<cid>[A-Za-z0-9._-]+)@(?P<h>[0-9a-f]{8})$")
SKIP_RE = re.compile(r"(?:^|/)__pycache__/|\.pyc$")


def md5_file(path):
    """md5 hex of a file's bytes, or None when it does not exist."""
    if not os.path.isfile(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def text_sha256(path):
    """sha256 hex of a text file with CRLF folded to LF (a git checkout under core.autocrlf must not look like an
    edit), or None when it does not exist."""
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


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
    """The protected-list dict from <root>/tools/rules_protected.json (globs, exclude, chain_checked, agent_write_denied)."""
    with open(os.path.join(root, PROTECTED_REL), encoding="utf-8") as f:
        return json.load(f)


def is_protected(rel, prot):
    """True when repo-relative `rel` matches a protected glob and no exclude glob (chain_checked / agent_write_denied
    paths are NOT md5-tracked protected files and return False)."""
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


# ------------------------------------------------------------------ ledger (hash-chained)
def line_hash(line):
    """sha256 hex of one ledger line (no line ending)."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def ledger_lines(root=ROOT):
    """Raw ledger lines (line endings stripped, blank lines dropped); [] when there is no ledger."""
    p = os.path.join(root, LEDGER_REL)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return [x.rstrip("\r\n") for x in f if x.strip()]


def read_ledger(root=ROOT):
    """List of ledger entries (dicts) in file order; [] when there is no ledger."""
    return [json.loads(x) for x in ledger_lines(root)]


def verify_chain(lines):
    """[(label, ok, detail)] - every line parses and carries prev = sha256 of the line before (genesis 64 zeros)."""
    g, prev = [], GENESIS
    for i, ln in enumerate(lines):
        try:
            e = json.loads(ln)
        except ValueError as ex:
            g.append(("chain:%d" % i, False, "unparseable line: %s" % ex))
            prev = line_hash(ln)
            continue
        g.append(("chain:%d" % i, e.get("prev") == prev, "prev %s want %s" % (str(e.get("prev"))[:12], prev[:12])))
        prev = line_hash(ln)
    return g


def last_md5s(ledger):
    """{path: (md5, kind, id)} from the LAST ledger entry naming each path."""
    out = {}
    for e in ledger:
        for pm in e.get("paths", []):
            out[pm["path"]] = (pm["md5"], e.get("kind"), e.get("id"))
    return out


def _append_ledger(root, entry):
    """Append one entry with prev = sha256 of the current last line. Returns the written line."""
    lines = ledger_lines(root)
    e = dict(entry)
    e["prev"] = line_hash(lines[-1]) if lines else GENESIS
    line = json.dumps(e, ensure_ascii=False, separators=(",", ":"))
    p = os.path.join(root, LEDGER_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    return line


# ------------------------------------------------------------------ bundle
def cand_dir(root, cid):
    return os.path.join(root, CAND_REL, cid)


def bundle_core_md5(m):
    """md5 of the manifest's canonical core (everything but `agreement` and `bundle`)."""
    core = {k: v for k, v in m.items() if k not in ("agreement", "bundle")}
    return hashlib.md5(json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                       .encode("utf-8")).hexdigest()


def bundle_id(m):
    """'<change-id>@<8 hex>' for manifest dict m."""
    return "%s@%s" % (m.get("change_id"), bundle_core_md5(m)[:8])


def split_bid(bid):
    """(change-id, hash8) or (None, None) for a malformed bundle id."""
    mm = BID_RE.match(bid or "")
    return (mm.group("cid"), mm.group("h")) if mm else (None, None)


def _write_manifest(path, m):
    """Recompute bundle id + token, then write. Returns the bundle id."""
    bid = bundle_id(m)
    m["bundle"] = {"id": bid, "core_md5": bundle_core_md5(m)}
    m.setdefault("agreement", {})["token"] = bid + " 동의"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    return bid


def _cand_files(d):
    out = []
    fdir = os.path.join(d, "files")
    for dp, _, fns in os.walk(fdir):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), fdir).replace("\\", "/")
            if not SKIP_RE.search(rel):
                out.append(rel)
    return sorted(out)


def relay_paths(root, ag):
    """{side: repo-relative path} of the two relay round files an agreement cites."""
    return {side: "%s/relay/round_%02d_%s.md" % (norm(ag["debate"]), int(ag["round"]), side) for side in ("claude", "gpt")}


def agreement_check(root, ag):
    """[(label, ok, detail)] - both relay/round_NN_<side>.md carry ag['token'] in their last STATE 'agreed' list, exactly."""
    out = []
    for side, rel in relay_paths(root, ag).items():
        f = os.path.join(root, rel)
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


def _load_manifest(root, cid):
    with open(os.path.join(cand_dir(root, cid), "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def check(root, bid):
    """[(label, ok, detail)] for bundle `bid`: id format, manifest, bundle hash, token, agreement, apply-device version,
    token unused, ledger chain, per-path protected / no drift / candidate md5, no unlisted files, tests."""
    cid, h8 = split_bid(bid)
    if not cid:
        return [("bundle-id", False, "%r is not <change-id>@<8 hex>" % bid)]
    g = [("bundle-id", True, bid)]
    try:
        m = _load_manifest(root, cid)
    except (OSError, ValueError) as e:
        return g + [("manifest", False, "%s: %s" % (cand_dir(root, cid), e))]
    g.append(("manifest", m.get("schema") == "rules-candidate/1" and m.get("change_id") == cid and
              bool(m.get("protected_paths")), "schema/change_id/paths"))
    core = bundle_core_md5(m)
    g.append(("bundle-hash", core[:8] == h8 and (m.get("bundle") or {}).get("core_md5") == core,
              "staged core %s, id %s, recorded %s" % (core[:8], h8, ((m.get("bundle") or {}).get("core_md5") or "")[:8])))
    ag = m.get("agreement") or {}
    tok = bid + " 동의"
    g.append(("token", ag.get("token") == tok, "manifest token %r" % ag.get("token")))
    try:
        g += agreement_check(root, dict(ag, token=tok))
    except (KeyError, ValueError, TypeError) as e:
        g.append(("agreement", False, "bad agreement block: %s" % e))
    live_self = md5_file(os.path.join(root, SELF_REL))
    g.append(("rules-apply-version", bool(live_self) and live_self == m.get("rules_apply_md5"),
              "live %s bundle %s" % (live_self, m.get("rules_apply_md5"))))
    lines = ledger_lines(root)
    used = []
    for x in lines:
        try:
            used.append((json.loads(x).get("agreement") or {}).get("token"))
        except (ValueError, AttributeError):
            pass
    g.append(("token-unused", tok not in used, "token already in the ledger" if tok in used else "new token"))
    ch = verify_chain(lines)
    g.append(("ledger-chain", all(ok for _, ok, _ in ch), "%d line(s)" % len(lines)))
    prot = load_protected(root)
    listed = set()
    for pp in m.get("protected_paths", []):
        try:
            rel = norm(pp["path"])
        except ValueError as e:
            g.append(("path", False, str(e)))
            continue
        listed.add(rel)
        g.append(("protected:" + rel, is_protected(rel, prot), "in tools/rules_protected.json globs"))
        live = md5_file(os.path.join(root, rel))
        g.append(("no-drift:" + rel, live == pp.get("base_md5"), "live %s base %s" % (live, pp.get("base_md5"))))
        cand = md5_file(os.path.join(cand_dir(root, cid), "files", rel))
        g.append(("cand-md5:" + rel, cand is not None and cand == pp.get("cand_md5"),
                  "file %s manifest %s" % (cand, pp.get("cand_md5"))))
    extra = [r for r in _cand_files(cand_dir(root, cid)) if r not in listed]
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
    """(Re)write manifest.json from files/: base_md5 = live, cand_md5 = candidate, rules_apply_md5 = the live apply
    device; keeps recorded tests whose md5s still match. Prints the bundle id and the token to agree on."""
    d = cand_dir(root, cid)
    mp = os.path.join(d, "manifest.json")
    old = {}
    if os.path.isfile(mp):
        with open(mp, encoding="utf-8") as f:
            old = json.load(f)
    paths = [{"path": rel, "base_md5": md5_file(os.path.join(root, rel)),
              "cand_md5": md5_file(os.path.join(d, "files", rel))} for rel in _cand_files(d)]
    m = {"schema": "rules-candidate/1", "change_id": cid, "protected_paths": paths,
         "rules_apply_md5": md5_file(os.path.join(root, SELF_REL)),
         "agreement": {"debate": norm(debate), "round": int(rnd)},
         "tests": old.get("tests", [])}
    bid = _write_manifest(mp, m)
    print("BUNDLE %s  token %r" % (bid, bid + " 동의"))
    return _finish([("staged", bool(paths), "%d path(s)" % len(paths))], "stage",
                   [{"path": os.path.relpath(mp, root).replace("\\", "/"), "md5": md5_file(mp)}])


def cmd_add_test(root, cid, command, log, md5_args):
    """Append a test entry: the log's last RESULT line; md5s from its artefacts plus path=md5 args. Re-ids the bundle."""
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
    bid = _write_manifest(mp, m)
    print("BUNDLE %s  token %r" % (bid, bid + " 동의"))
    return _finish([("result-line", r is not None, (r or {}).get("status"))], "add-test")


def cmd_check(root, bid):
    return _finish(check(root, bid), "check " + bid)


def prehash(root, bid):
    """([(label, ok, detail)], {rel: bytes}) - re-hash RIGHT BEFORE writing: manifest -> bundle id, candidate bytes ->
    cand_md5, live -> base_md5, apply device -> rules_apply_md5. The returned bytes are what apply writes."""
    cid, h8 = split_bid(bid)
    g, data = [], {}
    m = _load_manifest(root, cid)
    g.append(("prehash:bundle", bundle_id(m) == bid, "now %s" % bundle_id(m)))
    g.append(("prehash:rules-apply", md5_file(os.path.join(root, SELF_REL)) == m.get("rules_apply_md5"), ""))
    for pp in m["protected_paths"]:
        rel = norm(pp["path"])
        with open(os.path.join(cand_dir(root, cid), "files", rel), "rb") as f:
            b = f.read()
        g.append(("prehash:cand:" + rel, hashlib.md5(b).hexdigest() == pp["cand_md5"], hashlib.md5(b).hexdigest()))
        g.append(("prehash:live:" + rel, md5_file(os.path.join(root, rel)) == pp["base_md5"], ""))
        data[rel] = b
    return g, data, m


def cmd_apply(root, bid, _after_check=None):
    """check, re-hash right before writing (prehash), write the hashed bytes over the live paths, re-hash, append one
    chained ledger line. Refuses on any failed gate. `_after_check` is a self-test seam (a change between check and write)."""
    gates = check(root, bid)
    if not all(ok for _, ok, _ in gates):
        print("REFUSED apply %s: check failed, nothing written" % bid)
        return _finish(gates, "apply " + bid)
    if _after_check:
        _after_check()
    pg, data, m = prehash(root, bid)
    gates += pg
    if not all(ok for _, ok, _ in pg):
        print("REFUSED apply %s: pre-apply re-hash differs from the checked bundle, nothing written" % bid)
        return _finish(gates, "apply " + bid)
    done = []
    for rel, b in data.items():
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".rules_apply.tmp"
        with open(tmp, "wb") as f:
            f.write(b)
        os.replace(tmp, dst)
        got = md5_file(dst)
        gates.append(("rehash:" + rel, got == hashlib.md5(b).hexdigest(), got))
        done.append({"path": rel, "md5": got})
    ok = all(o for _, o, _ in gates)
    if ok:
        ag = dict(m["agreement"])
        ag["files"] = {rel: text_sha256(os.path.join(root, rel)) for rel in relay_paths(root, ag).values()}
        _append_ledger(root, {"schema": "rules-ledger/2", "kind": "apply", "id": bid,
                              "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "paths": done,
                              "bundle_md5": bundle_core_md5(m), "rules_apply_md5": m.get("rules_apply_md5"),
                              "agreement": ag,
                              "tests": [{"command": t.get("command"), "md5s": t.get("md5s")} for t in m["tests"]]})
    gates.append(("ledger", ok, LEDGER_REL if ok else "not written: re-hash mismatch"))
    return _finish(gates, "apply " + bid, done)


def _git_head_ledger(root):
    """The ledger text committed at HEAD (LF), or None when root is not a git repo / the ledger is untracked."""
    try:
        q = subprocess.run(["git", "-C", root, "show", "HEAD:" + LEDGER_REL], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return q.stdout.decode("utf-8", "replace").replace("\r\n", "\n") if q.returncode == 0 else None


def audit_ledger(root):
    """[(label, ok, detail)] - chain, genesis, per-apply re-verification, committed-prefix."""
    lines = ledger_lines(root)
    g = verify_chain(lines)
    entries = []
    for ln in lines:
        try:
            entries.append(json.loads(ln))
        except ValueError:
            entries.append({})
    toks = [((e.get("agreement") or {}).get("token")) for e in entries]
    for i, e in enumerate(entries):
        k = e.get("kind")
        if k == "baseline":
            g.append(("entry:%d baseline" % i, i == 0, "genesis" if i == 0 else "a baseline after genesis launders"))
            continue
        if k != "apply":
            g.append(("entry:%d kind" % i, False, "unknown kind %r" % k))
            continue
        bid = e.get("id") or ""
        ag = e.get("agreement") or {}
        tok = bid + " 동의"
        g.append(("entry:%d token" % i, ag.get("token") == tok and toks.count(tok) == 1,
                  "token %r used %d time(s)" % (ag.get("token"), toks.count(ag.get("token")))))
        try:
            rp = relay_paths(root, ag)
            same = all(text_sha256(os.path.join(root, r)) == (ag.get("files") or {}).get(r) for r in rp.values())
            g.append(("entry:%d relay-files" % i, same and len(ag.get("files") or {}) == 2,
                      "relay sha256 as recorded" if same else "relay file changed or missing since apply"))
            ac = agreement_check(root, dict(ag, token=tok))
            g.append(("entry:%d agreement" % i, all(ok for _, ok, _ in ac), "; ".join(d for _, _, d in ac)[:160]))
        except (KeyError, ValueError, TypeError) as ex:
            g.append(("entry:%d agreement" % i, False, "bad agreement block: %s" % ex))
        cid, h8 = split_bid(bid)
        try:
            m = _load_manifest(root, cid)
            cm = {pp["path"]: pp["cand_md5"] for pp in m.get("protected_paths", [])}
            ok = bundle_id(m) == bid and {p["path"]: p["md5"] for p in e.get("paths", [])} == cm
            g.append(("entry:%d bundle" % i, ok, "paths md5 == bundle cand_md5" if ok else
                      "bundle %s vs line: paths/md5 differ or bundle changed" % bundle_id(m)))
        except (OSError, ValueError, TypeError, KeyError) as ex:
            g.append(("entry:%d bundle" % i, False, "bundle %s cannot be re-verified: %s" % (bid, ex)))
    head = _git_head_ledger(root)
    if head is not None:
        live = "".join(l + "\n" for l in lines)
        g.append(("ledger-committed-prefix", live.startswith(head.replace("\r", "")),
                  "HEAD ledger %d line(s) is a prefix of the live one" % head.count("\n")))
    return g


def audit(root):
    """[(label, ok, detail)] - audit_ledger, then per protected file: VIA-APPLY / BASELINE when it equals the ledger,
    else OUT-OF-BAND."""
    prot = load_protected(root)
    g = audit_ledger(root)
    last = last_md5s(read_ledger(root))
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
    entry = {"schema": "rules-ledger/2", "kind": "baseline", "id": "baseline-" + time.strftime("%Y%m%d-%H%M%S"),
             "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "paths": [{"path": r, "md5": md5_file(os.path.join(root, r))} for r in files]}
    existing = ledger_lines(root)
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


def baseline_list(root):
    """The status-record dict: every protected file + md5, the other lists' files, the repo version. NOT a ledger."""
    prot = load_protected(root)
    head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
    dirty = subprocess.run(["git", "-C", root, "status", "--porcelain"], capture_output=True, text=True, timeout=60)
    other = {}
    for key in ("chain_checked", "agent_write_denied"):
        other[key] = [{"path": p, "exists": os.path.isfile(os.path.join(root, p)),
                       "md5": md5_file(os.path.join(root, p))} for p in prot.get(key, [])]
    files = protected_files(root, prot)
    return {"schema": "rules-baseline-list/1",
            "header": "status record only - not an approval, not an auto-restore target (discussion structure-equal-02 "
                      "round 10, both sides). Restore = a verified approved bundle via tools/rules_apply.py apply, or the "
                      "pre-install state (tools/bench/candidates/README.md).",
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "repo_head": head.stdout.strip() or None,
            "repo_dirty_paths": len([x for x in dirty.stdout.splitlines() if x.strip()]),
            "protected_list_md5": md5_file(os.path.join(root, PROTECTED_REL)),
            "globs": prot["globs"], "exclude": prot.get("exclude", []),
            "files": [{"path": r, "md5": md5_file(os.path.join(root, r))} for r in files],
            "not_md5_tracked": other}


def cmd_baseline_list(root, out):
    d = baseline_list(root)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return _finish([("baseline-list", bool(d["files"]), "%d protected file(s), HEAD %s" % (len(d["files"]),
                                                                                         (d["repo_head"] or "")[:10]))],
                   "baseline-list", [{"path": os.path.relpath(out, root).replace("\\", "/"), "md5": md5_file(out)}])


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
    sp.add_parser("baseline-list").add_argument("--out", required=True)
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
    if a.cmd == "baseline-list":
        return cmd_baseline_list(root, os.path.abspath(a.out))
    return cmd_audit(root, a.baseline, a.dry)


if __name__ == "__main__":
    sys.exit(main())
