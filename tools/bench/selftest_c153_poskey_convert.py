# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-a2-3.md
# ---
r"""selftest_c153_poskey_convert - card 153-a2-3 (docs/d1/ring-p4d.md:172-183 PD371(b), gate-fp fp-70): CONVERTER from stored NAME-keyed
computation_diff rows (a pred's cdiff_rows: 'node|class|name|ordinal' sink strings) to the POSITION rule: one row per changed input slot
(owner, index, class); a slot whose source is unchanged gives no row even if renamed. A lost + new pair at the same slot -> ONE changed row
(sink = A's name, both names/sources carried); a pair with equal (name-free) sources -> nothing; a real removal / new / any other row stays.
PRIOR ART: the candidate's pos_keys/_pos_src (tools/bench/diag_c153_b2_1_vigraph_poskey.txt:847-875) define the slot = index in the node's
READ order (G["by_node"]); pos_table/name_free below restate that key from the PD371(b) text so the converter does not call the candidate.
A slot's value = vigraph.effective_sources mapped name-free (source position + frame tag). No LabVIEW, no COM, no file written.
PREDICTION (self-test, run as a script): S1 pair -> 1 changed row; S2 equal-source pair -> 0; S3 real removal stays; S4 real new stays;
S5 a row with no slot info passes through, a same-name same-slot change maps to itself; S6 idempotent; S7 the s06 #2626 replica
(S1 element x3 + array, s06 array x4, slot 4 rename-only) -> element|0..2 only. card 153-a2-5: O1-O3 convert_open_rows (10/0 in all)."""
import os, sys                                                                     # noqa: E401
# card chat-T7 (PD373(d), docs/script-writing.md rule 1): the converter now lives ONCE in tools/stagekit.py (pos_slot_table, pos_name_free,
# pos_slots, pos_convert, pos_convert_open_rows); this file keeps its old names as thin aliases (diag_c153_a2_[345]_run.py call them) and
# tests the LIBRARY functions. The definitions that stood here are git 18c241ec:tools/bench/selftest_c153_poskey_convert.py:19-76.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                              # noqa: E402  pure functions only (no LabVIEW call)


def pos_table(G):
    """Alias of stagekit.pos_slot_table."""
    return K.pos_slot_table(G)


def name_free(P, s):
    """Alias of stagekit.pos_name_free."""
    return K.pos_name_free(P, s)


def slots(G, V, nodes):
    """Alias of stagekit.pos_slots (argument order of the old copy)."""
    return K.pos_slots(G, nodes, V)


def convert(rows, SA, SB):
    """Alias of stagekit.pos_convert."""
    return K.pos_convert(rows, SA, SB)


def sinks(conv):
    """Sorted distinct sinks of converted rows."""
    return sorted(set(r["sink"] for r in conv))


def convert_open_rows(plan_open_rows, old_rows, new_rows):
    """Alias of stagekit.pos_convert_open_rows."""
    return K.pos_convert_open_rows(plan_open_rows, old_rows, new_rows)


def _selftest():
    G = []

    def gate(label, ok, d=""):
        G.append(bool(ok))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:300]), flush=True)
    n, x, y = 7, frozenset([("s1", "")]), frozenset([("s2", "")])
    A = {"7|T|element|0": ((n, 1, "T"), x)}
    c = convert(["7|T|element|0", "7|T|array|0"], A, {"7|T|array|0": ((n, 1, "T"), y)})
    gate("S1 lost+new pair at one slot -> 1 changed row carrying both names", sinks(c) == ["7|T|element|0"] and c[0]["name_b"] == "7|T|array|0", c)
    gate("S2 equal-source pair -> 0 rows", convert(["7|T|element|0", "7|T|array|0"], A, {"7|T|array|0": ((n, 1, "T"), x)}) == [])
    c = convert(["7|T|a|0"], {"7|T|a|0": ((n, 2, "T"), x)}, {})
    gate("S3 real removal stays (after None)", sinks(c) == ["7|T|a|0"] and c[0]["after"] is None, c)
    c = convert(["7|T|b|0"], {}, {"7|T|b|0": ((n, 3, "T"), y)})
    gate("S4 real new stays (before None)", sinks(c) == ["7|T|b|0"] and c[0]["before"] is None, c)
    c = convert(["9|T|q|0", "7|T|e|0"], {"7|T|e|0": ((n, 1, "T"), x)}, {"7|T|e|0": ((n, 1, "T"), y)})
    gate("S5 unrelated row passes through; same name same slot changed -> itself", sinks(c) == ["7|T|e|0", "9|T|q|0"], c)
    SA = {"7|T|element|0": ((n, 1, "T"), x), "7|T|a|0": ((n, 2, "T"), x)}
    SB = {"7|T|array|0": ((n, 1, "T"), y), "7|T|b|0": ((n, 3, "T"), y)}
    c1 = convert(["7|T|element|0", "7|T|array|0", "7|T|a|0", "7|T|b|0", "9|T|q|0"], SA, SB)
    gate("S6 idempotent on already-converted rows", sinks(convert(sinks(c1), SA, SB)) == sinks(c1), sinks(c1))
    v = [frozenset([("v%d" % i, "")]) for i in range(5)]
    SA = dict(("2626|Terminal|element|%d" % i, ((2626, i + 1, "Terminal"), v[i])) for i in range(3))
    SA["2626|Terminal|array|0"] = ((2626, 4, "Terminal"), v[4])
    SB = dict(("2626|Terminal|array|%d" % i, ((2626, i + 1, "Terminal"), frozenset([("w%d" % i, "")]) if i < 3 else v[4])) for i in range(4))
    rows = ["2626|Terminal|array|%d" % i for i in range(4)] + ["2626|Terminal|element|%d" % i for i in range(3)]
    gate("S7 s06 #2626 replica -> element|0..2 (slot 4 rename-only gives no row)", sinks(convert(rows, SA, SB)) == rows[4:], sinks(convert(rows, SA, SB)))
    op, o = [{"node": 2626, "term": "array"}, {"node": 2626, "term": "element"}, {"node": 9, "term": "q"}], convert_open_rows
    gate("O1 open pair removed entirely by the conversion is dropped (#2626 array)", o(op, rows, rows[4:]) == op[1:], o(op, rows, rows[4:]))
    gate("O2 unrelated / still-present pairs kept, order kept", o(op, ["7|T|x|0"], []) == op and o(op[1:], rows, rows[4:]) == op[1:], o(op, ["7|T|x|0"], []))
    gate("O3 idempotent", o(o(op, rows, rows[4:]), rows, rows[4:]) == o(op, rows, rows[4:]) and o(op, rows[4:], rows[4:]) == op)
    return G


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import protocol
    g = _selftest()
    f = g.count(False)
    print(protocol.result_line({"status": "PASS" if not f else "FAIL", "gates": {"pass": len(g) - f, "fail": f}, "first_fail": None if not f else "see log",
                                "artefacts": []}), flush=True)
    sys.exit(1 if f else 0)
