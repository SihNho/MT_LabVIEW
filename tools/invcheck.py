# ---
# labview: none
# hardware: none
# offline-args: (library; run through a thin caller, e.g. tools/bench/diag_c156_b2_2_inv_c156a21.py before|after)
# evidence: tools/bench/cards/brief_156-b2-2.md
# ---
"""invcheck - the per-card INVARIANT check ("inv" script) as ONE shared module (card 156-b2-2, PD380(e), docs/script-writing.md rules 1/4/7).

Before this module every card copied the inv script (22 files tools/bench/*_inv.py, newest diag_c156_a2_1_inv.py) and changed only pins and
names. What every copy did, now here once: md5 helper; GATE counting; the pin loop (`startswith` on a short md5); card-input pins read from the
card JSON (minus the exempt files); the `before` snapshot write / `after` snapshot compare; the md5 FACT of the exempt files; the main/scratch
recipe FACT; the claudeDev listing FACT; the leftover-scratch gate; the RESULT line (protocol.result_line) and the exit code.
Everything a copy changed is an ARGUMENT of run_inv(). A caller holds inputs and one call (see diag_c156_b2_2_inv_c156a21.py).
Self-test: tools/bench/selftest_c156_b2_2_invcheck.py (replays diag_c156_a2_1_inv_before.log / _after.log gate by gate + one FAIL case).
Output lines are byte-compatible with diag_c156_a2_1_inv.py's GATE / FACT lines; the RESULT line is protocol.result_line's form."""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "tools", "bench")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SNAP_EXCLUDE = ("material_marker.log",)          # written by a hook on every call; never part of a snapshot (diag_c156_a2_1_inv.py:76)


def md5(path):
    """Full md5 hex of a file, or 'MISSING' when it does not exist. Self-test: selftest_c156_b2_2_invcheck.py (pin gates)."""
    if not os.path.exists(path):
        return "MISSING"
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Gates(object):
    """GATE counter: g(label, ok, detail) prints 'GATE PASS|FAIL | label | detail' and records it; .rows, .passed, .failed, .first.
    Self-test: selftest_c156_b2_2_invcheck.py (compares .rows with the recorded logs)."""

    def __init__(self, out=None):
        self.out = out or (lambda s: print(s, flush=True))
        self.rows = []
        self.passed = self.failed = 0
        self.first = None

    def __call__(self, label, ok, detail=""):
        ok = bool(ok)
        self.rows.append((label, ok, detail))
        self.passed, self.failed = self.passed + ok, self.failed + (not ok)
        self.first = self.first or (None if ok else label)
        self.out("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, detail))
        return ok

    def result(self, artefacts=()):
        """The RESULT line text (protocol.result_line, schema result-line/1) for the gates so far. Self-test: selftest_c156_b2_2_invcheck.py."""
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import protocol                                                                  # noqa: E402 (no LabVIEW; stdlib only)
        return protocol.result_line({"schema": "result-line/1", "status": "PASS" if self.failed == 0 else "FAIL",
                                     "gates": {"pass": self.passed, "fail": self.failed}, "first_fail": self.first,
                                     "artefacts": list(artefacts)})


def card_pins(card_path, exempt=(), root=ROOT):
    """Card-input pins: list of (path, md5) from the card JSON's inputs, path = os.path.join(root, input path) as written, minus `exempt`
    (compared by abspath). Self-test: selftest_c156_b2_2_invcheck.py (the brief_/plan_ pin gates of the recorded logs)."""
    card = json.load(open(card_path, encoding="utf-8"))
    ex = set(os.path.abspath(p) for p in exempt)
    out = []
    for inp in card.get("inputs", []):
        p = os.path.join(root, inp["path"])
        if os.path.abspath(p) not in ex:
            out.append((p, inp["md5"]))
    return out


def snapshot_files(globs, exclude_names=SNAP_EXCLUDE, root=ROOT):
    """{relpath with '/': md5} of every FILE matched by the glob patterns (relative to root, '**' recursive), basenames in
    exclude_names skipped. Self-test: selftest_c156_b2_2_invcheck.py (file count 153 vs the recorded snapshot)."""
    files = set()
    for pat in globs:
        for p in glob.glob(os.path.join(root, pat), recursive=True):
            if os.path.isfile(p) and os.path.basename(p) not in exclude_names:
                files.add(p)
    return dict((os.path.relpath(p, root).replace("\\", "/"), md5(p)) for p in sorted(files))


def _rel(p, root):
    try:
        return os.path.relpath(p, root)
    except ValueError:                                  # another drive (a temp snapshot in a self-test)
        return p


def run_inv(mode, pins, snap_path, snap_globs, snap_label, card_path=None, exempt=None, main_recipe=None, listing_glob=None,
            scratch_globs=(), root=ROOT, cd=CD, out=None):
    """Run one inv check and return the Gates (caller exits with gates.failed and 1 or 0). mode 'before' writes the snapshot, 'after'
    compares it. pins = {path: short md5} in gate order; card inputs (minus `exempt`) follow; exempt = {path: before-pin} is pinned in
    'before' and reported as an md5 FACT in 'after'. Self-test: selftest_c156_b2_2_invcheck.py."""
    say = out or (lambda s: print(s, flush=True))
    g = Gates(say)
    exempt = exempt or {}
    allp = dict(pins)                                    # dict semantics as the copies: a repeated raw key keeps its slot, takes the new value
    if card_path:
        for p, m in card_pins(card_path, exempt=list(exempt), root=root):
            allp[p] = m
    if mode == "before":
        allp.update(exempt)
    for p, pin in allp.items():
        m = md5(p)
        g("md5 {0} == {1}".format(os.path.basename(p), pin), m.startswith(pin), m)
    cur = snapshot_files(snap_globs, root=root)
    if mode == "before":
        main_md5 = md5(main_recipe) if main_recipe else None
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump({"main_recipe": main_md5, "files": cur}, f, indent=1)
        say("FACT snapshot {0} files -> {1} md5 {2}".format(len(cur), _rel(snap_path, root), md5(snap_path)))
    else:
        sn = json.load(open(snap_path, encoding="utf-8"))
        ch = sorted(k for k in set(cur) | set(sn["files"]) if cur.get(k) != sn["files"].get(k))
        g("{0} unchanged vs snapshot ({1} files)".format(snap_label, len(sn["files"])), not ch, ch)
        if exempt:
            say("FACT " + "; ".join("{0} md5 {1}".format(os.path.basename(p), md5(p)) for p in exempt))
    if main_recipe:
        say("FACT MAIN recipe md5 {0}; scratch recipe md5 {1}".format(md5(main_recipe), md5(main_recipe.replace(".py", "_scratch.py"))))
    if listing_glob:
        say("FACT claudeDev {0} files {1}".format(listing_glob[:-3] if listing_glob.endswith(".vi") else listing_glob,
                                                    [(os.path.basename(p), md5(p)[:8]) for p in sorted(glob.glob(os.path.join(cd, listing_glob)))]))
    if scratch_globs:
        left = [p for pat in scratch_globs for p in glob.glob(os.path.join(cd, pat))]
        g("no {0} in claudeDev".format(" / ".join(scratch_globs)), not left, left)
    say(g.result())
    return g


def main_inv(argv=None, **config):
    """Thin-caller entry: mode from argv[1] (default 'before'), run_inv(mode, **config), returns the exit code (1 if any gate FAILED).
    Self-test: selftest_c156_b2_2_invcheck.py runs the thin caller's config through run_inv."""
    argv = sys.argv if argv is None else argv
    mode = argv[1] if len(argv) > 1 else "before"
    g = run_inv(mode, **config)
    return 1 if g.failed else 0
