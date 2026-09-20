r"""diag_fstunnel_wire_semantics.py - READ-ONLY DIAGNOSTIC (builds no op, saves no VI).

WHY: tools/recipes/build_opfstunnelterm_v0.py:392 -> tools/gscript.py:1330 died TWICE with
  `wire specific class reference->reference: wire count 40->40 with 0 new tunnel(s), expected 41`.
The previous log (tools/bench/build_opfstunnelterm_v0.log:51) measured only the SINKS and the cast's INPUT
(`TMSC target class wire 0`); nobody ever read the `wire` field on the TMSC's `specific class reference` OUTPUT
terminal. This file reads it, before and after the one connection, and reads the destination terminal too.

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "before creating any new op"):
  * `grep "^def " tools/gscript.py` - node_terms_uid, report_all, count, uids, delete_object, build_property,
    create_control, wire, wire_control, open_panel/close_panel, exec_state, fp_labels: ALL reused, none added.
  * `tools/recipes/build_opfstunnelterm_v0.py` module-level helpers (sweep/trow/twire/has/cidx/node_index_of/
    ctl_labels/SPEC/T_CAST_OUT/DONOR) are IMPORTED, not re-typed, so the reproduction is byte-identical to the
    failing path. Importing the module has no side effects (its work is under `if __name__ == "__main__"`).
  * `tools/bench/diag_tunnelsource_onehop.wire_terminals()` - the Wire.Terminals[] reader, for the residual-wire
    question (4). Not re-implemented.
  * `ls tools/recipes tools/bench` - no existing file reads a node terminal's `wire` around a wire() call.
NO new op is built. NO VI is saved. The scratch is a copy of the DONOR under a unique name, closed WITHOUT
saving and DELETED in the same run. No motor, no serial, no camera (cycle21 Pre-decided 2 / P1).

PREDICTION CONTRACT (every line printed PASS/FAIL; the run continues past a miss):
  P0  md5 of both originals + the donor unchanged before and after; the scratch is deleted.
  P1  the reproduction reaches the same state the failing run reached: B1/B2/B3 equivalents pass and
      `seed -> TMSC target class` is a NON-ZERO wire (log:51 measured 1457).
  P2  BEFORE the call, the three readings exist: w_out = wire on TMSC `specific class reference`,
      w_dst = wire on PN_A `reference`, n_before = Wire count. (A measurement, not a pass/fail.)
  P3  the single connection is performed through gscript.wire(..., branch=True) - the ONLY raw form the code
      offers (gscript.py:1325 `if not branch and not (lo <= after <= hi)`: branch=True asserts NOTHING extra,
      it merely SKIPS the count check; the `err` raise at :1320 still applies).
  P4  AFTER the call the same three readings are taken, and the outcome is classified against the three
      possibilities the review named:
        both w_out and w_dst the SAME NON-ZERO uid -> the connection SUCCEEDED, the helper's count test is a
            false negative for this shape;
        w_out non-zero, w_dst == 0           -> LabVIEW DECLINED the connection;
        both 0                               -> no branch happened and endpoint resolution is the problem.
  P5  if w_out is NON-ZERO BEFORE the call, that residual wire's uid and its full Wire.Terminals[] source/sink
      list are printed.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_wire_semantics.log -- py -u tools/bench/diag_fstunnel_wire_semantics.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                                   # noqa: E402
import build_opfstunnelterm_v0 as R                   # noqa: E402  - helpers reused verbatim
import diag_tunnelsource_onehop as onehop             # noqa: E402  - Wire.Terminals[] reader
from build_opconstvalue_v1 import fresh, lv_pid       # noqa: E402

SCR = os.path.join(g.CLAUDEDEV, f"SCRATCH_fswire_sem_{os.getpid()}.vi")
OUT = os.path.join(HERE, "diag_fstunnel_wire_semantics.json")
FILES = [R.ORIG_3STATE, R.V6, R.DONOR]
RES = {"gates": [], "before": {}, "after": {}, "md5": {}, "handles": {}, "residual": None, "verdict": None}
g._run.__defaults__ = (6.0, 120.0)


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return bool(ok)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def snapshot(tag):
    d = {os.path.basename(p): md5(p) for p in FILES}
    RES["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for k, v in d.items():
        print(f"   {v}  {k}", flush=True)
    return d


def handles(tag):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                              "Measure-Object -Property HandleCount -Sum).Sum"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out else 0
    except Exception as e:
        n = f"ERR {str(e)[:60]}"
    RES["handles"][tag] = n
    print(f"  HANDLES {tag}: {n}  (fresh baseline ~31,500)", flush=True)
    return n


def read3(tag, tmsc, pn_a):
    """The three readings: wire on the cast's OUTPUT terminal, wire on the PN's `reference` INPUT, Wire count."""
    by = R.sweep(SCR)
    w_out = R.twire(by, tmsc, R.T_CAST_OUT)
    w_dst = R.twire(by, pn_a, "reference")
    n = g.count(SCR, "Wire")
    row_out = R.trow(by, tmsc, R.T_CAST_OUT)
    row_dst = R.trow(by, pn_a, "reference")
    rec = {"w_out_specific_class_reference": w_out, "w_dst_reference": w_dst, "wire_count": n,
           "row_out": row_out, "row_dst": row_dst}
    RES[tag] = rec
    print(f"\n   === {tag.upper()} the call ===", flush=True)
    print(f"      TMSC #{tmsc} `{R.T_CAST_OUT}` .wire = {w_out}   (row: {json.dumps(row_out)[:200]})", flush=True)
    print(f"      PN_A #{pn_a} `reference`          .wire = {w_dst}   (row: {json.dumps(row_dst)[:200]})", flush=True)
    print(f"      diagram Wire count                      = {n}", flush=True)
    return rec


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("READ-ONLY DIAGNOSTIC - no op built, no VI saved. Contract P0..P5 in the docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    snapshot("before")
    rc = 0
    try:
        fresh()
        handles("after a fresh LabVIEW")
        op_path, cls, pid_a, short_a, pid_b, short_b, _lab = R.SPEC["OUT"]
        print(f"\n   reproducing build_one('OUT') on a SCRATCH copy of the donor:\n      {SCR}", flush=True)
        shutil.copy2(R.DONOR, SCR)
        time.sleep(0.4)
        g.open_panel(SCR)
        time.sleep(1.0)
        inv0 = g.uids(SCR, "Invoke")

        def purge():
            junk = [u for u in g.uids(SCR, "Invoke") if u not in inv0]
            if junk:
                order = [o["uid"] for o in g.report_all(SCR, "Invoke")]
                for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                    g.delete_object(SCR, "Invoke", i, verify=False)
                print(f"   purged {len(junk)} junk Invoke(s)", flush=True)

        st = g.exec_state(SCR)
        by = R.sweep(SCR)
        print(f"   copy of the donor: ExecState {st}, {len(by)} nodes on diagram 0", flush=True)
        pn_terms = next((u for u in by if R.has(by, u, "Terms[]", True)), None)
        w_terms = R.twire(by, pn_terms, "Terms[]") if pn_terms else None
        ia = next((u for u in by if R.has(by, u, "array", False) and R.twire(by, u, "array") == w_terms), None) \
            if w_terms else None
        el_w = R.twire(by, ia, "element") if ia else None
        tmsc = next((u for u in by if R.has(by, u, "target class") and R.has(by, u, R.T_CAST_OUT, True)
                     and R.twire(by, u, R.T_CAST_OUT) == R.twire(by, pn_terms, "reference")), None) \
            if pn_terms else None
        consumers = [u for u in by if R.trow(by, u, "reference") is not None
                     and R.twire(by, u, "reference") == el_w] if el_w else []
        w_targetclass = R.twire(by, tmsc, "target class") if tmsc else None
        print(f"   Terms[] PN {pn_terms} (wire {w_terms}) | Index Array {ia} (element wire {el_w}) | "
              f"front TMSC {tmsc} (target-class wire {w_targetclass}) | back-half sinks {consumers}", flush=True)
        if not must("P1a the donor copy is legal and the front section was found",
                    st == 1 and pn_terms and ia and tmsc and consumers,
                    f"ExecState {st}; terms {pn_terms} ia {ia} tmsc {tmsc} consumers {consumers}"):
            return 3

        for _cls, uid in (("Node", pn_terms), ("Node", ia)):
            order = [o["uid"] for o in g.report_all(SCR, _cls)]
            if uid in order:
                g.delete_object(SCR, _cls, order.index(uid), verify=False)
                print(f"   deleted {_cls} #{uid}", flush=True)
        for w in (w_terms, el_w, w_targetclass):
            if not w:
                continue
            order = [o["uid"] for o in g.report_all(SCR, "Wire")]
            if w in order:
                g.delete_object(SCR, "Wire", order.index(w), verify=False)
                print(f"   deleted Wire #{w}", flush=True)
        by = R.sweep(SCR)
        bare = {u: R.twire(by, u, "reference") for u in consumers}
        tc = R.twire(by, tmsc, "target class")
        print(f"   after the deletes: back-half sinks {bare}; TMSC target class wire {tc}", flush=True)
        must("P1b every sink is BARE and the cast's target class is unwired",
             all(v == 0 for v in bare.values()) and tc == 0, f"{bare}; target class {tc}")

        pn_a = g.build_property(SCR, cls, [(pid_a, False)], (900, 1250))[0]["uid"]
        purge()
        n_a = R.node_index_of(SCR, pn_a)
        c0 = set(R.ctl_labels(SCR))
        g.create_control(SCR, n_a, 0)
        purge()
        new_c = [l for l in R.ctl_labels(SCR) if l not in c0]
        print(f"   PN_A uid {pn_a} (Nodes[{n_a}], {short_a}); new control(s): {new_c}", flush=True)
        if not must("P1c create_control on the PN's `reference` made exactly one new CONTROL",
                    len(new_c) == 1, str(new_c)):
            return 3
        seed = new_c[0]
        by = R.sweep(SCR)
        w_seed = R.twire(by, pn_a, "reference")
        if w_seed:
            order = [o["uid"] for o in g.report_all(SCR, "Wire")]
            if w_seed in order:
                g.delete_object(SCR, "Wire", order.index(w_seed), verify=False)
                print(f"   deleted the seed->PN_A wire #{w_seed}", flush=True)
        g.wire_control(SCR, [seed], "Function", R.cidx(SCR, "Function", tmsc), ["target class"])
        by = R.sweep(SCR)
        w_tc = R.twire(by, tmsc, "target class")
        print(f"   seed {seed!r} -> TMSC `target class` wire {w_tc}", flush=True)
        must("P1d the seed really landed on `target class` (non-zero wire)", bool(w_tc), str(w_tc))

        # ------------------------------------------------------------------ P2  the three readings BEFORE
        before = read3("before", tmsc, pn_a)

        # ------------------------------------------------------------------ P5  residual wire on the cast output
        if before["w_out_specific_class_reference"]:
            wu = before["w_out_specific_class_reference"]
            print(f"\n   P5 a RESIDUAL wire #{wu} is already on the cast's output - reading its Terminals[]:",
                  flush=True)
            try:
                rows = onehop.wire_terminals(SCR, wu)
            except Exception as e:
                rows = f"EXC {str(e)[:200]}"
            RES["residual"] = {"wire_uid": wu, "terminals": rows}
            print(f"   P5 residual wire #{wu} terminals: {json.dumps(rows, default=str)[:900]}", flush=True)
        else:
            must("P5 no residual wire on the cast output before the call (nothing to report)", True, "w_out = 0")

        # ------------------------------------------------------------------ P3  the ONE connection, no count test
        print("\n   P3 performing the ONE connection through gscript.wire(..., branch=True) "
              "(gscript.py:1325 - branch=True SKIPS the count check and asserts nothing else)", flush=True)
        exc = None
        n_pre = g.count(SCR, "Wire")
        try:
            ret = g.wire(SCR, "Function", R.cidx(SCR, "Function", tmsc), R.T_CAST_OUT,
                         "Property", R.cidx(SCR, "Property", pn_a), "reference", branch=True)
            print(f"      wire(branch=True) returned {ret} (the post-call Wire count)", flush=True)
        except Exception as e:
            exc = str(e)[:300]
            print(f"      wire(branch=True) RAISED: {exc}", flush=True)
        RES["call"] = {"raised": exc, "wire_count_immediately_before": n_pre}
        must("P3 the raw connection call did not raise", exc is None, exc or "no exception")

        # ------------------------------------------------------------------ P4  the three readings AFTER
        after = read3("after", tmsc, pn_a)
        es = g.exec_state(SCR)
        RES["after"]["exec_state"] = es
        print(f"      ExecState after the call: {es} (0 is expected here - the back half is still bare)", flush=True)

        wo, wd = after["w_out_specific_class_reference"], after["w_dst_reference"]
        if wo and wd and wo == wd:
            verdict = ("CONNECTED: both terminals report the SAME non-zero wire "
                       f"#{wo} -> the connection succeeded and gscript.wire's count test is the false negative")
        elif wo and wd and wo != wd:
            verdict = (f"TWO DIFFERENT WIRES: cast output on #{wo}, destination on #{wd} - not one wire; "
                       "not any of the three predicted outcomes")
        elif wo and not wd:
            verdict = (f"DECLINED: cast output carries wire #{wo} but the destination `reference` is still 0 "
                       "-> LabVIEW declined the connection")
        elif not wo and not wd:
            verdict = ("NEITHER: both terminals report wire 0 -> no branch happened; endpoint resolution "
                       "(which terminal the op addressed) is the problem")
        else:
            verdict = f"UNEXPECTED: cast output {wo}, destination {wd}"
        RES["verdict"] = verdict
        print(f"\n   VERDICT: {verdict}", flush=True)
        must("P4 the three readings were taken after the call", True,
             f"w_out {wo} / w_dst {wd} / count {after['wire_count']}")
    finally:
        try:
            g.close_panel(SCR)      # NOT saved: closing an unsaved panel discards every edit (gscript.py:1202)
        except Exception as e:
            print(f"   close_panel: {str(e)[:120]}", flush=True)
        time.sleep(0.5)
        gone = None
        try:
            if os.path.exists(SCR):
                os.remove(SCR)
            gone = not os.path.exists(SCR)
        except Exception as e:
            gone = f"ERR {str(e)[:120]}"
        must("P0b the scratch VI was created and DELETED in the same run", gone is True, f"{SCR} -> {gone}")
        handles("at the end")
        after_md5 = snapshot("after")
        same = all(RES["md5"]["before"][k] == after_md5[k] for k in after_md5)
        must("P0a every original + the donor is byte-identical before and after", same,
             json.dumps(after_md5)[:300])
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, ensure_ascii=False, default=str)
        print(f"\n   -> {OUT}", flush=True)
        bad = [x["label"] for x in RES["gates"] if not x["ok"]]
        print(f"\nGATES {len(RES['gates']) - len(bad)}/{len(RES['gates'])} pass" +
              (f"; failing: {bad}" if bad else ""), flush=True)
        rc = 0 if not bad else 3
    return rc


if __name__ == "__main__":
    sys.exit(main())
