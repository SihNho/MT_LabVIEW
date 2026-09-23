r"""selftest_stagekit - `tools/stagekit.py` WITHOUT LabVIEW. Nothing here opens COM, touches claudeDev or
reads a `.vi`; every case is a pure function or a captured print.

WHAT IT PINS (Pre-decided 103's acceptance, the half that needs no instrument)
  A  THE ROW FORMAT - `  PASS  ` / `  FAIL  ` / `  FACT  ` exactly as documented, and NEVER the markdown
     `**FAIL**` form that slipped past `guard_peer.FAILURE_RE` until 2026-09-20 (docs/violation-decisions.md
     `device-failed`). Also: `Stage.row()`, the NON-gate record, must not put FAIL at the start of a line -
     a row reporting an expected failure may not arm the gate.
  B  SUMMARY COUNTING - pass/fail tallies, the failing list, and rc = 0 iff no FAIL.
  C  THE md5 PIN REFUSES A WRONG HASH, fatally, BEFORE anything is opened.
  D  THE SAVE-ROUTE SELECTION LOGIC - scripted / gui_save / refuse - as a pure function.
  E  THE MUTATING READER REFUSES THE STAGE TARGET (`broken_wire_count`, stagekit rule 6).
  F  `%`-FORMAT SAFETY: the module builds no message with the `%` operator (the 2026-09-22 TypeError).
"""
import io
import os
import re
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import stagekit as K                                                               # noqa: E402

passes, fails = [], []


def mask(detail):
    """A SELF-TEST OF A FAILURE FORMAT IS A FILE FULL OF FAILURE-SHAPED TEXT. `bgrun.py:217-219` scans the
    child's own output for `=== <n> fail` and `^FAIL`, so quoting the very strings under test made a 27/0
    run end `BGRUN INNER FAILURE` (measured, 2026-09-22 14:58). The ASSERTIONS compare the real strings;
    only the ECHO of them into the log is masked."""
    return str(detail).replace("===", "---").replace("FAIL", "F&IL").replace("fail", "f&il")


def check(label, ok, detail=""):
    ok = bool(ok)
    (passes if ok else fails).append(label)
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label,
                                 ("  " + mask(detail)) if detail else ""), flush=True)
    return ok


def new_stage(md5_pin="deadbeef", tmp=None):
    """A Stage that touches nothing: no pins, no restart, no preload."""
    return K.Stage(tmp or os.path.join(tempfile.gettempdir(), "stagekit_selftest_input.vi"),
                   md5_pin, "selftest_stagekit_case", fresh=False, preload=False, pins=(),
                   out_json=os.path.join(tempfile.gettempdir(), "stagekit_selftest.json"))


def cap(fn):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn()
    return buf.getvalue()


def case_a_rows():
    s = new_stage()
    out = cap(lambda: (s.gate("g-ok", True, "d1"), s.gate("g-bad", False, "d2"),
                       s.fact("a measured thing"), s.row("r-1", "FAIL", "FAIL")))
    lines = out.splitlines()
    check("A1 a passing gate prints the documented `  PASS  ` row",
          any(l.startswith("  PASS  g-ok") for l in lines), repr(lines[:1]))
    check("A2 a failing gate prints the documented `  FAIL  ` row",
          any(l.startswith("  FAIL  g-bad") for l in lines), repr(lines[1:2]))
    check("A3 no row uses the markdown `**FAIL**` form", "**FAIL**" not in out)
    check("A4 a fact prints the documented `  FACT  ` row",
          any(l.startswith("  FACT  a measured thing") for l in lines))
    rowline = [l for l in lines if l.startswith("  ROW ")]
    check("A5 `row()` prints a non-gate ROW line", len(rowline) == 1, repr(rowline))
    check("A6 a ROW reporting an expected FAIL does NOT match guard_peer's FAILURE_RE anchor",
          not re.search(r"^\s*(?:->\s*)?\*{0,2}FAIL\b", rowline[0] if rowline else "", re.M),
          repr(rowline))
    check("A7 the gate detail is printed beside the label", "d1" in out and "d2" in out)


def case_b_summary():
    s = new_stage()
    cap(lambda: (s.gate("p1", True), s.gate("p2", True), s.gate("f1", False)))
    out = cap(s.summary)
    check("B1 the summary counts 2 pass / 1 fail",
          "GATES: 2 pass / 1 fail" in out, repr(out.strip().splitlines()[-2:]))
    check("B2 the summary names the failing gate", "failing: f1" in out)
    rc = []
    cap(lambda: rc.append(s.summary()))          # captured: summary() PRINTS the shape bgrun scans for
    check("B3 rc is 1 while a gate fails", rc == [1], rc)
    s2 = new_stage()
    cap(lambda: s2.gate("p", True))
    rc2 = []
    cap(lambda: rc2.append(s2.summary()))
    check("B4 rc is 0 when nothing failed", rc2 == [0], rc2)
    check("B5 the tallies are also on the Stage object",
          (len(s.passes), len(s.fails)) == (2, 1), "{0!r}".format((s.passes, s.fails)))


def case_c_md5_pin():
    fd, tmp = tempfile.mkstemp(suffix=".vi")
    os.write(fd, b"not a real VI - this file exists only so md5() has bytes to hash\n")
    os.close(fd)
    try:
        real = K.md5(tmp)
        s = new_stage("0" * 32, tmp)
        raised = ""
        try:
            cap(s.start)
        except K.Stop as e:
            raised = str(e)
        check("C1 a WRONG input md5 raises Stop at the pin, fatally", raised.startswith("K1 input md5"),
              repr(raised[:80]))
        check("C2 nothing was copied: no work file exists", not os.path.exists(s.work), s.work)
        check("C3 md5() agrees with hashlib on the same bytes",
              real == __import__("hashlib").md5(open(tmp, "rb").read()).hexdigest(), real)
        s2 = new_stage(real, tmp)
        # The RIGHT md5 passes K1; K2 (the ORIGINAL) is the next fatal gate and is not this case's subject,
        # so the pin itself is checked directly rather than by letting start() continue into the machine.
        out = cap(lambda: s2.gate("K1 input md5 == {0}".format(real), K.md5(tmp) == real))
        check("C4 the RIGHT input md5 passes the same pin", out.startswith("  PASS  K1 input md5"),
              repr(out.strip()[:60]))
    finally:
        os.remove(tmp)


def case_d_save_route():
    s = new_stage()
    table = [((1, False), "scripted"), ((1, True), "scripted"), ((0, True), "gui_save"),
             ((0, False), "refuse"), ((None, True), "refuse"), ((2, True), "refuse")]
    for (es, ok), want in table:
        got = s.save_route(es, ok)
        check("D ExecState {0!r} + broken_ok={1!r} -> {2}".format(es, ok, want), got == want, got)


def case_e_mutating_reader():
    s = new_stage()
    raised = ""
    try:
        s.broken_wire_count()
    except K.Stop as e:
        raised = str(e)
    check("E1 broken_wire_count REFUSES the stage target without allow_mutation",
          "allow_mutation" in raised, repr(raised[:90]))
    check("E2 the refusal says why (it DELETES)", "delete" in raised.lower(), repr(raised[:90]))


def case_f_format_safety():
    path = os.path.join(ROOT, "tools", "stagekit.py")
    src = open(path, encoding="utf-8").read()
    # EXACT, not textual: a `%` inside a strftime pattern is not the `%` operator, so the test is an AST
    # walk for BinOp(Mod) whose LEFT operand is a string literal - the shape that raised the TypeError.
    import ast
    bad = ["line {0}".format(n.lineno) for n in ast.walk(ast.parse(src, path))
           if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)
           and isinstance(getattr(n, "left", None), (ast.Constant, ast.JoinedStr))
           and (not isinstance(n.left, ast.Constant) or isinstance(n.left.value, str))]
    check("F1 stagekit builds no message with the `%` operator (AST: no BinOp(Mod) on a string literal)",
          not bad, repr(bad[:3]))
    check("F2 stagekit's own source carries no `**FAIL**`", "**FAIL**" not in src.replace(
        "`**FAIL**`", ""))
    check("F3 every public verb named in Pre-decided 103 exists",
          all(hasattr(K.Stage, n) for n in ("start", "es", "census", "wired_terminals", "net_sources",
                                            "broken_wire_count", "move_in", "delete_object", "connect",
                                            "connect_from_wire", "wire_indicators", "wire_sr",
                                            "add_shift_reg", "create_local_read",
                                            "fs_inner_tunnel_connect", "junk_purge", "gate",
                                            "expect_is_broken_false", "summary", "save", "close")),
          [n for n in ("start", "es", "census", "wired_terminals", "net_sources", "broken_wire_count",
                       "move_in", "delete_object", "connect", "connect_from_wire", "wire_indicators",
                       "wire_sr", "add_shift_reg", "create_local_read", "fs_inner_tunnel_connect",
                       "junk_purge", "gate", "expect_is_broken_false", "summary", "save", "close")
           if not hasattr(K.Stage, n)])


def case_g_constants():
    """THE CASE THE FIRST RUN DID NOT HAVE, and the one that would have caught the K2 defect in 2 seconds
    at no LabVIEW cost (`archive/peer/2026-09-22-c87-stagekit-k2.md` §2/§4, accepted): every constant the
    module SHIPS must resolve to a file that exists, and the ORIGINAL's identity must be ONE object owned
    by `gscript`, not a second copy that happens to be equal. `is` is the discriminator on purpose -
    `os.path.join` builds at runtime and CPython interns only compile-time literals, so two
    separately-typed equal paths are never `is`-identical."""
    import gscript as G
    check("G1 stagekit.ORIGINAL IS gscript.ORIGINAL (one owner, not a copy that happens to match)",
          K.ORIGINAL is G.ORIGINAL, K.ORIGINAL)
    check("G2 stagekit.ORIG_MD5 IS gscript.ORIG_MD5", K.ORIG_MD5 is G.ORIG_MD5, K.ORIG_MD5)
    try:
        import diag_s2_scaffold as D
        check("G3 the value agrees with the fleet's other owner, diag_s2_scaffold:81-82",
              (K.ORIGINAL, K.ORIG_MD5) == (D.ORIGINAL, D.ORIG_MD5),
              "{0!r} vs {1!r}".format(K.ORIGINAL, D.ORIGINAL))
    except Exception as e:                                                         # noqa: BLE001
        check("G3 the value agrees with diag_s2_scaffold", False, str(e)[:120])
    missing = [(l, p) for l, p, _w in K.DEFAULT_PINS if not os.path.exists(p)]
    check("G4 every path in DEFAULT_PINS resolves to a file that exists", not missing, repr(missing[:3]))
    wrong = [(l, p) for l, p, w in K.DEFAULT_PINS if os.path.exists(p) and K.md5(p) != w]
    check("G5 every DEFAULT_PINS entry's md5 matches the hash it pins", not wrong, repr(wrong[:3]))


def case_h_creator_rows():
    """Cycle 68 (M4a/M4b): the pure halves of the new from_decision actions - `$` symbol resolution and the
    Pre-decided 143 op-rule check. The LabVIEW halves (copy_in / add_sr_row / const_row) are gated by the stage."""
    s = new_stage()
    s.sym = {"not": 111, "sr": {"right": 222, "left": 333, "right_uids": [9, 222]}}
    r = s.resolve({"a": "$not", "b": ["$sr.right", "$sr.right_uids"], "c": 5, "d": "plain"})
    check("H1 resolve maps $name, $name.key and leaves literals alone",
          r == {"a": 111, "b": [222, [9, 222]], "c": 5, "d": "plain"}, repr(r))
    raised = False
    try:
        s.resolve("$missing")
    except KeyError:
        raised = True
    check("H2 resolve of an unknown symbol RAISES (never a silent default)", raised)
    end = lambda uid, oc, tc, **k: dict({"uid": uid, "owner_class": oc, "term_class": tc, "diagram": 1}, **k)
    ok_rows = [({"op": "wire_sr", "variant": "RightIn",
                 "exec": {"src": end(1, "Local", "Terminal"), "dst": end(2, "RightShiftRegister", "InnerTerminal")}}),
               ({"op": "wire_sr", "variant": "LeftIn",
                 "exec": {"src": end(3, "LeftShiftRegister", "InnerTerminal"), "dst": end(4, "Function", "Terminal")}}),
               ({"op": "connect_nested", "variant": None,
                 "exec": {"src": end(4, "Function", "Terminal"), "dst": end(5, "CaseStructure", "Terminal")}}),
               ({"op": "connect_from_wire", "variant": None,
                 "exec": {"src": end(1, "Local", "Terminal", wire_uid=77), "dst": end(4, "Function", "Terminal")}})]
    got = [s.rule_check(d)[:2] for d in ok_rows]
    check("H3 rule_check accepts the four M4a row shapes",
          got == [("wire_sr", "RightIn"), ("wire_sr", "LeftIn"), ("connect_nested", None),
                  ("connect_from_wire", None)], repr(got))
    bad = {"op": "connect_nested", "variant": None,
           "exec": {"src": end(1, "Local", "Terminal", wire_uid=77), "dst": end(4, "Function", "Terminal")}}
    raised = False
    try:
        s.rule_check(bad)
    except RuntimeError:
        raised = True
    check("H4 rule_check REFUSES a row whose op disagrees with op_rule", raised)
    bad["op_override"] = "reason"
    check("H5 ... unless the row carries op_override", s.rule_check(bad)[0] == "connect_from_wire")


def case_i_term_uid():
    """Pre-decided 173 (cycle 71): `Stage.address` by TERMINAL UID after the first resolution. The fixture is the
    measured failure (`stage_d1_l7_1b.log:268-276`): WhileLoop #23041's Terminals[] after the init rows landed,
    where the new acc left SR's outer terminal (t4, wire 3543) read 'total data array out' BEFORE wiring and ''
    AFTER. LabVIEW is replaced by stubs of the four readers `address` calls; the real `address` code runs."""
    loop_rows = [{"i": 0, "name": "", "is_source": False, "wire": 23519},
                 {"i": 1, "name": "error out", "is_source": True, "wire": 0},
                 {"i": 2, "name": "error out", "is_source": False, "wire": 4969},
                 {"i": 3, "name": "", "is_source": True, "wire": 0},
                 {"i": 4, "name": "", "is_source": False, "wire": 3543},
                 {"i": 5, "name": "", "is_source": False, "wire": 25225}]
    all_rows = [{"term_uid": 24190, "term_name": "", "is_source": False, "wire_uid": 3543, "owner_uid": 24187},
                {"term_uid": 24140, "term_name": "error out", "is_source": False, "wire_uid": 4969, "owner_uid": 24133},
                {"term_uid": 24191, "term_name": "", "is_source": True, "wire_uid": 0, "owner_uid": 24187},
                {"term_uid": 30001, "term_name": "", "is_source": False, "wire_uid": 25225, "owner_uid": 9}]
    saved = dict((k, getattr(K.g, k)) for k in ("report_all", "node_labels", "node_terms_uid"))
    saved_mod = K.mod

    class _AT(object):
        @staticmethod
        def read_terms(_t):
            return all_rows, 0.0
    try:
        K.g.report_all = lambda _t, _c: [{"i": 19, "uid": 686}]
        K.g.node_labels = lambda _t, _d: [{"uid": u} for u in (5, 23041)]
        K.g.node_terms_uid = lambda _t, _d, _n: (23041, loop_rows)
        K.mod = lambda name: _AT if name == "allterms" else saved_mod(name)
        s = new_stage()
        s.work = "stub.vi"
        end = lambda **k: dict({"uid": 23041, "diagram": 686, "owner_class": "", "term_class": ""}, **k)  # noqa: E731

        def raises(fn):
            try:
                fn()
            except RuntimeError as e:
                return str(e)
            return None
        e1 = raises(lambda: s.address(end(term="total data array out"), False))
        check("I1 the PRE-WIRING name no longer resolves after wiring (the measured defect reproduced)",
              e1 is not None and "0 matches" in e1, e1)
        r2 = s.address(end(term="total data array out", verify_term_uid=24190), False)
        check("I2 the SAME row addressed by terminal uid #24190 reaches t4 on #23041 despite the name change",
              r2[0] == (19, 1, 4) and "uid #24190" in r2[1], repr(r2))
        r3 = s.address(end(term="", verify_term_uid=24140), False)
        check("I3 uid #24140 reaches t2 ('error out' sink), not the same-named source t1", r3[0] == (19, 1, 2), repr(r3))
        e4 = raises(lambda: s.address(end(term="", verify_term_uid=99999), False))
        check("I4 an unknown terminal uid RAISES (no fallback to the name)", e4 is not None and "0 row" in e4, e4)
        e5 = raises(lambda: s.address(end(term="", verify_term_uid=24191), True))
        check("I5 an UNWIRED terminal uid RAISES (uid addressing needs a wire)", e5 is not None and "wired" in e5, e5)
        e6 = raises(lambda: s.address(end(term="", verify_term_uid=24190), True))
        check("I6 a direction mismatch RAISES", e6 is not None, e6)
        e7 = raises(lambda: K.match_term_uid(24190, all_rows, loop_rows + [dict(loop_rows[4], i=6)], False))
        check("I7 two node rows on the same wire and direction RAISE (ambiguous, never the first)",
              e7 is not None and "2 matching" in e7, e7)
        # Pre-decided 174 (cycle 72 firefighter): the r2 defect - a candidate end carrying `term_uid` on a STILL-
        # UNWIRED terminal (t3, uid 24191, wire 0) must resolve by NAME at first wiring, not take the uid branch.
        r8 = s.address(end(term="", term_uid=24191), True)
        check("I8 a candidate end with `term_uid` on an UNWIRED terminal is wired by NAME (r2's failure fixed)",
              r8[0] == (19, 1, 3) and "uid" not in r8[1], repr(r8))
        loop_rows[3]["wire"], all_rows[2]["wire_uid"] = 777, 777                  # the wire lands, name may change
        loop_rows[3]["name"] = "renamed after wiring"
        r9 = s.address(end(term="", verify_term_uid=24191), True)
        check("I9 ... then verified by `verify_term_uid` after the wire landed, despite the rename",
              r9[0] == (19, 1, 3) and "uid #24191" in r9[1], repr(r9))
        e10 = raises(lambda: s.address(end(term="", term_uid=24191), True))
        check("I10 after wiring, an end with only `term_uid` still resolves by NAME (uid never implicit)",
              e10 is not None and "0 matches" in e10, e10)
    finally:
        for k, v in saved.items():
            setattr(K.g, k, v)
        K.mod = saved_mod


def main():
    print("=" * 90, flush=True)
    print("selftest_stagekit - tools/stagekit.py without LabVIEW", flush=True)
    print("=" * 90, flush=True)
    for fn in (case_a_rows, case_b_summary, case_c_md5_pin, case_d_save_route, case_e_mutating_reader,
               case_f_format_safety, case_g_constants, case_h_creator_rows, case_i_term_uid):
        print("\n---------- {0}".format(fn.__name__), flush=True)
        try:
            fn()
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            traceback.print_exc()
            check("{0} completed without an unhandled exception".format(fn.__name__), False, str(e)[:140])
    print("\n" + "=" * 90, flush=True)
    print("=== GATES: {0} pass / {1} fail{2}".format(
        len(passes), len(fails), ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
