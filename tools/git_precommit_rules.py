# ---
# labview: none
# hardware: none
# ---
"""git_precommit_rules - CANDIDATE pre-commit check (card chat-X6, discussion structure-equal-02 experiment 2): refuse a
commit whose STAGED protected files (tools/rules_protected.json) do not match the md5 the ledger
(tools/bench/rules_ledger.jsonl) last recorded for them, i.e. a protected change that did not come through
`tools/rules_apply.py apply`. WRITTEN AND TESTED, NOT INSTALLED - installing it into .git/hooks is a joint decision.

    py tools/git_precommit_rules.py [--root R]      exit 0 = pass, 1 = refused; ends with a RESULT line

Line endings: with core.autocrlf the index blob is LF while the ledger hashed the working tree, so a staged file matches
when the ledger md5 equals the blob's md5, the blob's LF->CRLF md5, or (when the working tree equals the index) the
working-tree md5. A staged DELETION of a protected file is refused. Logic shared with rules_apply (load_protected,
is_protected, read_ledger, last_md5s, md5_file) - called, not copied. Self-test: tools/bench/selftest_rules_apply.py.
"""
import argparse
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import protocol as P                                                                    # noqa: E402
import rules_apply as RA                                                                # noqa: E402


def _git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True)


def staged_paths(root):
    """[(status_letter, repo path)] of the staged changes (git diff --cached --name-status)."""
    out = _git(root, "diff", "--cached", "--name-status", "-z", "--no-renames").stdout.decode("utf-8", "replace")
    parts = [p for p in out.split("\0") if p]
    return [(parts[i][0], parts[i + 1]) for i in range(0, len(parts) - 1, 2)]


def staged_md5s(root, rel):
    """Set of md5s the staged version of `rel` may legitimately carry (blob, blob LF->CRLF, worktree if == index)."""
    blob = _git(root, "cat-file", "blob", ":" + rel).stdout
    lf = blob.replace(b"\r\n", b"\n")
    s = {hashlib.md5(blob).hexdigest(), hashlib.md5(lf.replace(b"\n", b"\r\n")).hexdigest()}
    if _git(root, "diff", "--quiet", "--", rel).returncode == 0:
        w = RA.md5_file(os.path.join(root, rel))
        if w:
            s.add(w)
    return s


def check_staged(root):
    """[(label, ok, detail)] one per staged protected path; non-protected staged paths are not judged."""
    prot = RA.load_protected(root)
    last = RA.last_md5s(RA.read_ledger(root))
    g = []
    for st, rel in staged_paths(root):
        if not RA.is_protected(rel, prot):
            continue
        if st == "D":
            g.append(("staged:" + rel, False, "deletion of a protected file"))
            continue
        want = last.get(rel)
        if want is None:
            g.append(("staged:" + rel, False, "never applied (not in ledger)"))
            continue
        ok = want[0] in staged_md5s(root, rel)
        g.append(("staged:" + rel, ok, "ledger %s (%s %s)%s" % (want[0], want[1], want[2],
                                                                 "" if ok else " - staged content differs")))
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)
    root = a.root or _git(RA.ROOT, "rev-parse", "--show-toplevel").stdout.decode().strip() or RA.ROOT
    g = check_staged(os.path.abspath(root))
    for name, ok, det in g:
        print("%s  %s  %s" % ("PASS" if ok else "REFUSED", name, det))
    fails = [n for n, ok, _ in g if not ok]
    if fails:
        print("pre-commit refused: protected files changed outside tools/rules_apply.py apply")
    print(P.result_line(P.make_result(len(g) - len(fails), len(fails),
                                      ("precommit: " + fails[0]) if fails else None)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
