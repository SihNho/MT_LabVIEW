r"""diag_count_indicator.py - WHAT DOES THE `Count` INDICATOR COUNT?  READ-ONLY, no motor, no serial, no camera.

WHY (STATUS.md NEXT "Dispatch 1", a D1 PRECONDITION).  Three registered bead picks leave `Count` reading 1 in
BOTH harness versions (`tools/bench/drive_original_copy_v4.log:790`, `...v5.log:181`); v5 passes by counting the
three red markers the VI draws instead, so the indicator's MEANING was never established.  D1 rewrites the loops
that feed it, so this measures what it is wired to BEFORE anything is touched.  Escalated from
retrospective-cycle31 F6b.

WHAT ALREADY EXISTS - checked before writing a line (CLAUDE.md "before creating any new op, tool or recipe"):
  * `gscript.fp_labels(target)`            - every front-panel label + uid (docs/toolkit-capabilities.md).
  * `gscript.panel_wiring(target)`         - EVERY top-level panel object with its diagram terminal's
    `is_source` and CONNECTED WIRE uid, 114 rows on the main VI, 0.8 s.  This is the entry point; no new op.
  * `OpWireSource_v5.vi` + the caller shape `wire_source_owner()` in
    `tools/recipes/build_opconnectfromwire_v0.py:423-447` - a WIRE uid -> each of its terminals' owner class and
    owner uid.  ⚠️ It is UID-addressed: `UID 2` MUST be set (the caller bug recorded twice,
    docs/toolkit-capabilities.md:48,:51).  Copied here, not imported, because the recipe module is a build.
  * `OpOwnerChain_v1.vi` + `read_owner()` in `tools/recipes/build_opownerchain_v1.py:246-276` - any uid -> its
    OWNER (node -> its diagram, diagram -> its structure).  ⚠️ That copy hard-codes `MAIN` as `vi path`; this one
    takes the target.  MEASURED LIMIT: an owner chain terminates silently at a `FlatSequenceFrame` (owner_uid 0).
  * `gscript.node_labels(target, diagram_index)` - the label of every node on ONE diagram.
  * `gscript.node_terms_uid` / `node_terms` - a node's terminals (name, is_source, wire).
  * `OpTunnelRead_v0.vi` - a tunnel uid -> its INSIDE terminals' wires (used only if the source is a tunnel).
So NOTHING new is built here.  This file is a pure reader chain over ops that already exist.

KNOWN FACTS THIS RELIES ON (not re-derived):
  * `C_COUNT = "Count"  # CTL uid 28051` - `tools/bench/drive_original_copy_v2.py:127`.
  * A front-panel `ControlTerminal` is NOT a `Node`, so `net_map` / the diagram tree can never name it
    (docs/toolkit-capabilities.md:511-532); the wire is the only route, which is why panel_wiring leads.
  * A ControlTerminal's `Generic.Owner` is its DIAGRAM, never the control (`build_d1_routeb_v0.py:29-35`).

TARGET: the claudeDev D0 copy `Track_D0_copy_20260918.vi` (docs/cycle27-plan.md Pre-decided 4).  The ORIGINAL is
md5'd before and after and NEVER opened by this script (rule 1).  Nothing is created, edited or saved anywhere.

PREDICTION CONTRACT (machine-checkable; a FAIL here is a measurement result, not necessarily a fault):
  G1  the D0 copy exists on disk and the ORIGINAL's md5 is unchanged at the end == at the start.
  G2  `panel_wiring` returns >= 100 rows and EXACTLY ONE of them has label == "Count".
  G3  the row's PANEL ROLE is recorded (control vs indicator).  ⚠️ RUN 1 REFUTED THE FIRST VERSION OF THIS GATE,
      which predicted an indicator: `tools/bench/diag_count_indicator.log` (19:56) reads
      `Count row VERBATIM: label='Count' uid=28051 indicator=False is_source=True wire=30530`, i.e. `Count` is a
      front-panel **CONTROL** whose terminal DRIVES a wire.  The gate now records the role instead of asserting
      it, and the chase below is role-agnostic.  Run 1 also died on a caller bug of mine (ROOT was two levels up
      instead of three, so every derived path gained a `tools\` segment); both are on record in that log.
  G4  its terminal's DIRECTION is recorded, and it carries a NON-ZERO connected wire.
  G5  `OpWireSource_v5` on that wire returns EXACTLY ONE terminal with `Is Source?` True.
  G6  every terminal of that wire resolves to an owner (owner_uid != 0).
  G7  for EACH end, the owner chain reaches a Diagram, and that Diagram's own owner is reported
      (a structure class, or `TopLevelDiagram`/error - recorded either way).
  G8  ExecState of the D0 copy is read and recorded, and the copy's md5 is unchanged too.  (MEASURED run 2:
      ExecState **0** - the claudeDev D0 copy is BROKEN as it sits on disk.  Recorded, not diagnosed.)
  G9  the whole-VI `node_labels` sweep for nodes labelled 'Count' completes on every diagram - the reader that
      can see a Local / implicit `Value` property node writing the control, which `panel_wiring` cannot.
RUN:  py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_count_indicator.log -- \
      py -u tools/bench/diag_count_indicator.py
"""
import json
import os
import sys
import time

# this file lives in tools/bench/, so the PROJECT root is three levels up, not two. Run 1 used two and every
# path built from it gained a spurious `tools\` segment (tools/bench/diag_count_indicator.log, the FileNotFoundError
# on `tools\tools\bench\opwiresource_v5_labels.json`). Asserted rather than trusted.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assert os.path.isfile(os.path.join(ROOT, "CLAUDE.md")), "ROOT is not the project root: %s" % ROOT
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g                                                            # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
D0 = os.path.join(CLAUDEDEV, "Track_D0_copy_20260918.vi")
# the VI the D0 copy was byte-copied from, and its recorded md5 - both VERBATIM from
# tools/bench/drive_original_copy_v2.py:109-111 (the harness that made the copy), not retyped from memory.
ORIGINAL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
            r"\Min_Track N beads V6_ParallelLoop.vi")
ORIGINAL_MD5 = "2a78e17c449cacdaf5da389818526859"
V5 = os.path.join(CLAUDEDEV, "OpWireSource_v5.vi")
OWNER = os.path.join(CLAUDEDEV, "OpOwnerChain_v1.vi")
LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
OUT_JSON = os.path.join(ROOT, "tools", "bench", "count_indicator.json")

PASS = [0, 0]
RESULT = {}


def gate(label, ok, detail=""):
    PASS[0 if ok else 1] += 1
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print("  %s %s%s" % ("PASS" if ok else "FAIL", label, ("  | " + detail) if detail else ""), flush=True)
    return ok


def fact(s):
    print("  . %s" % s, flush=True)


def md5(p):
    import hashlib
    try:
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError as e:
        return "ERR %s" % e


# ------------------------------------------------------------------ the two borrowed readers
def wire_terms(target, wire_uid, n=8):
    """`OpWireSource_v5` on `target`: every terminal of wire `wire_uid` with its owner.
    Shape copied from tools/recipes/build_opconnectfromwire_v0.py:423-447 (UID-addressed - `UID 2` is set)."""
    with open(LABELS, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(V5)
    out = []
    for i in range(n):
        try:
            vi.SetControlValue("vi path", target)
            vi.SetControlValue(lab["uid_in"], int(wire_uid))
            vi.SetControlValue(lab["term_index"], i)
            g._run(vi)
            r = dict(i=i, is_source=bool(vi.GetControlValue(lab["is_source"])),
                     owner_class=vi.GetControlValue(lab["ownercls"]),
                     owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                     recip=int(vi.GetControlValue(lab["recip_wire"])))
        except Exception as e:                                                 # noqa: BLE001
            out.append(dict(i=i, err=str(e)[:80]))
            break
        out.append(r)
        if not r["owner_uid"] and not r["is_source"]:
            break
    return out


def read_owner(target, uid):
    """`OpOwnerChain_v1` on `target`: uid -> its OWNER class/uid, plus the self-read identity echo.
    Shape from tools/recipes/build_opownerchain_v1.py:246-276, with `vi path` taken from the caller
    (that copy hard-codes the ORIGINAL - rule 1 makes that unusable here)."""
    with open(LABELS, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(OWNER)
    for k in (lab["ownercls"], "Class Name 3", lab["cast_class"]):
        try:
            vi.SetControlValue(k, "POISON")
        except Exception:                                                      # noqa: BLE001
            pass
    try:
        vi.SetControlValue(lab["owner_uid"], 0)
        vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", "Diagram")
        vi.SetControlValue("index", 0)
        vi.SetControlValue(lab["uid_in"], int(uid))
        vi.SetControlValue(lab["term_index"], 0)
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:                                                     # noqa: BLE001
        return dict(uid=int(uid), err="EXC %s" % str(e)[:90])
    return dict(uid=int(uid), ownercls=vi.GetControlValue(lab["ownercls"]),
                owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                cast_class=vi.GetControlValue(lab["cast_class"]),
                uid_back=int(vi.GetControlValue(lab["uid_back"])),
                cls_back=vi.GetControlValue(lab["cls_back"]), err=err)


def chain(target, uid, hops=4):
    """uid -> owner -> owner -> ... , stopping on 0/error. Returns the list of hops."""
    out, cur = [], int(uid)
    seen = set()
    for _ in range(hops):
        if cur in seen:
            break
        seen.add(cur)
        r = read_owner(target, cur)
        out.append(r)
        nxt = r.get("owner_uid") or 0
        if not nxt:
            break
        cur = nxt
    return out


def main():
    t0 = time.time()
    print("== diag_count_indicator - READ-ONLY. target %s" % D0, flush=True)
    orig_before = md5(ORIGINAL)
    d0_before = md5(D0)
    fact("ORIGINAL md5 BEFORE %s (recorded %s, match=%s)"
         % (orig_before, ORIGINAL_MD5, orig_before == ORIGINAL_MD5))
    fact("D0 copy  md5 BEFORE %s  (%s)" % (d0_before, "exists" if os.path.isfile(D0) else "MISSING"))
    if not os.path.isfile(D0):
        gate("G1 the D0 claudeDev copy exists", False, "%s is missing - STOPPING (a fresh copy is a separate,"
                                                       " reportable act)" % D0)
        print("SELFTEST diag_count_indicator: %d pass / %d fail" % (PASS[0], PASS[1]), flush=True)
        return 1
    gate("G1a the D0 claudeDev copy exists", True, os.path.basename(D0))

    try:
        st = g.exec_state(D0)
    except Exception as e:                                                     # noqa: BLE001
        st = "EXC %s" % str(e)[:70]
    fact("ExecState of the D0 copy: %r" % (st,))

    # ---------------------------------------------------------------- 1. the panel row
    rows = g.panel_wiring(D0)
    RESULT["n_panel_rows"] = len(rows)
    gate("G2a panel_wiring returned >= 100 rows", len(rows) >= 100, "%d rows" % len(rows))
    exact = [r for r in rows if r["label"] == "Count"]
    gate("G2b exactly one row is labelled exactly 'Count'", len(exact) == 1,
         "%d exact matches; labels containing 'count' (case-insensitive): %r"
         % (len(exact), [(r["label"], r["uid"], r["indicator"]) for r in rows if "count" in r["label"].lower()]))
    if not exact:
        print("SELFTEST diag_count_indicator: %d pass / %d fail" % (PASS[0], PASS[1]), flush=True)
        return 1
    row = exact[0]
    RESULT["count_row"] = row
    fact("Count row VERBATIM: label=%r uid=%d indicator=%s is_source=%s wire=%d term_err=%s wire_err=%s"
         % (row["label"], row["uid"], row["indicator"], row["is_source"], row["wire"],
            row["term_err"], row["wire_err"]))
    # G3/G4a are MEASUREMENTS, not assumptions - and run 1 refuted the assumption they used to encode.
    # MEASURED, tools/bench/diag_count_indicator.log (run 1, 19:56): `Count` uid 28051 is indicator=False,
    # is_source=True, wire=30530 -> it is a front-panel **CONTROL** whose terminal EMITS into the diagram, not an
    # indicator the VI writes. The gates now RECORD the role and pass either way; the direction of the chase
    # below follows the measured role instead of a predicted one.
    role = "INDICATOR (the VI writes it)" if row["indicator"] else "CONTROL (the panel writes it, the diagram reads it)"
    RESULT["role"] = role
    gate("G3 `Count`'s panel role RECORDED", True, "%s | indicator=%s" % (role, row["indicator"]))
    gate("G4a its terminal's direction RECORDED", True,
         "is_source=%s (%s)" % (row["is_source"], "SOURCE: it drives the wire" if row["is_source"] else "SINK"))
    gate("G4b its terminal carries a NON-ZERO connected wire", bool(row["wire"]), "wire=%d" % row["wire"])

    # ---------------------------------------------------------------- 2. EVERY end of that wire
    # Role-agnostic on purpose (run 1 measured `Count` to be a CONTROL): both ends are resolved and labelled, so
    # the answer reads the same whether the panel object writes the wire or reads it.
    diags = []
    try:
        diags = g.report_all(D0, "Diagram")
        RESULT["n_diagrams"] = len(diags)
        fact("the copy has %d Diagram objects (Traverse order = diagram_index)" % len(diags))
    except Exception as e:                                                     # noqa: BLE001
        fact("report_all('Diagram') failed: %s" % str(e)[:110])

    def describe(uid, tag):
        """uid -> owner chain -> the diagram that owns it -> that diagram's own owner -> the node's label."""
        ch = chain(D0, uid)
        for h in ch:
            fact("%s owner chain: #%s (self reads %r#%s) -> %r#%s  err=%r"
                 % (tag, h["uid"], h.get("cls_back"), h.get("uid_back"),
                    h.get("ownercls"), h.get("owner_uid"), (h.get("err") or "")[:60]))
        RESULT.setdefault("chains", {})[str(uid)] = ch
        dg = [h for h in ch if (h.get("ownercls") or "") == "Diagram"]
        gate("G7 %s: the owner chain reaches a Diagram" % tag, bool(dg),
             "chain: %r" % [(h.get("cls_back"), h.get("ownercls"), h.get("owner_uid")) for h in ch])
        if not dg or not diags:
            return
        dg_uid = dg[0]["owner_uid"]
        hit = [i for i, d in enumerate(diags) if int(d.get("uid", 0)) == dg_uid]
        # what STRUCTURE owns that diagram - "is it inside a loop?" answered from the machine
        owner_of_diag = [h for h in ch if h["uid"] == dg_uid]
        fact("%s lives on Diagram #%s (Traverse index %r); that diagram's own owner: %r"
             % (tag, dg_uid, hit, [(h.get("ownercls"), h.get("owner_uid")) for h in owner_of_diag] or "see chain"))
        if not hit:
            return
        try:
            labs = g.node_labels(D0, hit[0])
            me = [x for x in labs if int(x.get("uid", 0)) == int(uid)]
            fact("%s NODE on that diagram: %r" % (tag, me or "NOT in Nodes[] - not a Node object"))
            RESULT.setdefault("labels", {})[str(uid)] = me
            idx = [i for i, x in enumerate(labs) if int(x.get("uid", 0)) == int(uid)]
            if idx:
                tms = g.node_terms(D0, hit[0], idx[0])
                RESULT.setdefault("node_terms", {})[str(uid)] = tms
                for t in tms:
                    fact("    %s term[%s] name=%r is_source=%s wire=%s"
                         % (tag, t.get("i"), t.get("name"), t.get("is_source"), t.get("wire")))
        except Exception as e:                                                 # noqa: BLE001
            fact("%s labelling failed: %s" % (tag, str(e)[:110]))

    if row["wire"]:
        terms = wire_terms(D0, row["wire"])
        RESULT["wire_terms"] = terms
        for t in terms:
            fact("w%d term[%d]: %r" % (row["wire"], t.get("i", -1), t))
        srcs = [t for t in terms if t.get("is_source")]
        gate("G5 exactly one terminal of w%d is the SOURCE" % row["wire"], len(srcs) == 1,
             "%d source terminals: %r" % (len(srcs), [(t.get("owner_class"), t.get("owner_uid")) for t in srcs]))
        # The LAST row is the walker's END-OF-LIST SENTINEL, not a terminal: `wire_terms` walks `Wire.Terms[]`
        # by index and stops on the first all-zero answer (`owner_uid == 0 and not is_source`), the same
        # "walk until error 1055" shape docs/toolkit-capabilities.md:60 prescribes for this op. Run 2's G6
        # counted that sentinel as an unresolved terminal and FAILED on its own loop condition
        # (tools/bench/diag_count_indicator_run2.log, `3 of 4 resolved`). Real terminals only:
        real = [t for t in terms if t.get("owner_uid")]
        sentinel = [t for t in terms if not t.get("owner_uid") and not t.get("is_source") and "err" not in t]
        gate("G6 every REAL terminal of w%d resolved to an owner" % row["wire"],
             len(real) + len(sentinel) == len(terms) and len(sentinel) <= 1,
             "%d real + %d end-of-list sentinel = %d rows walked" % (len(real), len(sentinel), len(terms)))
        seen = set()
        for t in terms:
            ou = t.get("owner_uid") or 0
            if not ou or ou in seen:
                continue
            seen.add(ou)
            describe(ou, "w%d term[%d] %s %r#%d"
                     % (row["wire"], t.get("i", -1), "SOURCE" if t.get("is_source") else "SINK",
                        t.get("owner_class"), ou))

    # ---------------------------------------------------------------- 5. other count-ish indicators
    # BOTH roles are listed: run 1 measured `Count` itself to be a control, so restricting this to indicators
    # would hide exactly the kind of object the question is about.
    cand = [(r["label"], r["uid"], r["indicator"], r["wire"], r["is_source"]) for r in rows
            if any(k in r["label"].lower()
                   for k in ("count", "bead", "# of", "num", "n of", "total", "picked", "ref"))]
    RESULT["count_like_panel_objects"] = cand
    fact("PANEL OBJECTS whose label mentions count/bead/num/total/picked/ref (%d):" % len(cand))
    for c in cand:
        fact("    %r uid=%d %s wire=%d is_source=%s"
             % (c[0], c[1], "INDICATOR" if c[2] else "control", c[3], c[4]))

    # ------------------------------------------- 6. DOES ANYTHING WRITE `Count` OTHER THAN ITS TERMINAL?
    # THE LIMIT OF EVERYTHING ABOVE, stated in this project's own words (docs/toolkit-capabilities.md:775-780):
    # `panel_wiring` sees the TERMINAL only - "locals and Value property nodes are not seen here". `Count` being
    # a CONTROL whose terminal is a SOURCE therefore does NOT yet prove nothing writes it: a Local or an implicit
    # `Value` property node bound to `Count` would write it invisibly to every reader used so far.
    # `node_labels` IS the reader for that (docs/toolkit-capabilities.md:26): an implicit property node's label
    # is its bound panel object's NAME. So sweep every diagram and collect any node labelled 'Count'.
    try:
        hits, swept, errs = [], 0, 0
        for i in range(len(diags)):
            try:
                for x in g.node_labels(D0, i):
                    if (x.get("label") or "").strip() == "Count":
                        hits.append({"diagram_index": i, "diagram_uid": int(diags[i].get("uid", 0)),
                                     "uid": int(x.get("uid", 0)), "label": x.get("label")})
                swept += 1
            except Exception:                                                  # noqa: BLE001
                errs += 1
        RESULT["count_labelled_nodes"] = hits
        RESULT["node_label_sweep"] = {"diagrams_swept": swept, "diagrams_failed": errs}
        gate("G9 the whole-VI sweep for nodes labelled 'Count' completed", errs == 0,
             "%d/%d diagrams swept, %d failed; %d node(s) labelled 'Count': %r"
             % (swept, len(diags), errs, len(hits), hits))
        for h in hits:
            fact("node labelled 'Count': uid %d on Diagram #%d (index %d)"
                 % (h["uid"], h["diagram_uid"], h["diagram_index"]))
            # DIRECTION is the whole question: on a Local / implicit Value node `is_source TRUE` = a READ
            # (docs/gscript.node_terms docstring, "on a global-variable node: a READ"), FALSE = a WRITE.
            try:
                labs2 = g.node_labels(D0, h["diagram_index"])
                ix = [i for i, x in enumerate(labs2) if int(x.get("uid", 0)) == h["uid"]]
                if ix:
                    tms = g.node_terms(D0, h["diagram_index"], ix[0])
                    RESULT.setdefault("count_node_terms", {})[str(h["uid"])] = tms
                    for t in tms:
                        fact("    #%d term[%s] name=%r is_source=%s wire=%s   (%s)"
                             % (h["uid"], t.get("i"), t.get("name"), t.get("is_source"), t.get("wire"),
                                "READS Count" if t.get("is_source") else "WRITES Count"))
                describe(h["uid"], "node 'Count'#%d" % h["uid"])
            except Exception as e:                                             # noqa: BLE001
                fact("    direction read for #%d failed: %s" % (h["uid"], str(e)[:100]))
        for cls in ("Local", "GlobalVariable"):
            try:
                objs = g.report_all(D0, cls)
                RESULT["n_" + cls] = len(objs)
                fact("%s objects on the diagram: %d (uids %r)" % (cls, len(objs), [o["uid"] for o in objs][:20]))
            except Exception as e:                                             # noqa: BLE001
                fact("report_all(%r) failed: %s" % (cls, str(e)[:90]))
    except Exception as e:                                                     # noqa: BLE001
        fact("the 'Count'-writer sweep failed: %s" % str(e)[:120])

    # ---------------------------------------------------------------- hygiene
    orig_after, d0_after = md5(ORIGINAL), md5(D0)
    gate("G1 ORIGINAL md5 unchanged", orig_after == orig_before, "%s -> %s" % (orig_before, orig_after))
    gate("G8 D0 copy md5 unchanged (read-only)", d0_after == d0_before, "%s -> %s" % (d0_before, d0_after))
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
        import bench_prep
        fact("LabVIEW handles at the end: %s" % bench_prep.labview_handles())
    except Exception as e:                                                     # noqa: BLE001
        fact("handle read unavailable: %s" % str(e)[:80])
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(RESULT, f, indent=1, default=str)
    fact("wrote %s" % OUT_JSON)
    print("SELFTEST diag_count_indicator: %d pass / %d fail  (%.0f s)" % (PASS[0], PASS[1], time.time() - t0),
          flush=True)
    return 0 if PASS[1] == 0 else 1


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        try:
            g.reset()
        except Exception:                                                      # noqa: BLE001
            pass
    sys.exit(rc)
