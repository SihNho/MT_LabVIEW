"""build_opaddshiftreg_v0.py - OpAddShiftReg_v0.vi: CREATE a shift register on a While loop by script.

WHY. Stage 2's tracking loop feeds the kernel's `x,y,z array out` / `Bead is good? array out` / `pos in cal image
out` back to the next iteration. No op in the fleet writes a shift register; `while_loop` / `loop_in` make input
tunnels, `exit_while` makes output tunnels, `OpShiftRegs_v0/v1` only READ. The first plan proposed to abuse
erdosmiller `Exit While Loop.vi`'s never-exercised `Shift Registers` input; the peer review
(archive/peer/2026-09-14-stage2-shiftreg-primitive.md) refused that and pointed at the documented method this
project had ALREADY catalogued and never verified: NAMES.md:234, `Loop` class 16405, method
**`Add Shift Register` 6361000**, input `Y Position` (U32), returns a `RightShiftRegister` reference.

DONOR. `OpWhileCast_v0.vi` - it already holds a WhileLoop-TYPED reference (the cast-free typed-control seed,
toolkit-capabilities.md) coming out of a To More Specific Class, which is exactly the `Loop`-derived reference the
method must be invoked on. Added:
  A  Invoke `VI Server:Loop` . `Add Shift Register` (6361000); `reference` <- TMSC 'specific class reference' (branch)
  B  control on the invoke's `Y Position`; PN GObject[UID] 632A813 <- the invoke's return; indicator on that UID
  C  indicator on the invoke's `error out`; auto error handling OFF; ExecState 1 -> save; labels json

PREDICTION CONTRACT (a miss prints OBSERVED and stops - nothing is saved):
  A1  build_invoke yields ONE new Invoke whose terminals include `reference`, `Y Position`, a RETURN terminal and the
      error pair. If it carries ONLY `reference` / `error out`, that is the documented private-member signature
      (toolkit-capabilities.md, 'PRIVATE members need the Allow Private setters') - STOP; `Invoke.Set Method
      (Allow Private)` 6370003 is a NEXT reviewed batch, never a continuation of this one.
  A2  FUNCTIONAL, on a scratch copy of HARNESS_copyloop with one scripted While loop:
      loop_cast(...,'WhileLoop')['shift_reg_uids'] 0 -> 1; the single element == the UID the op reported;
      shift_reg_left reports ONE LeftShiftRegister whose outside wire is 0 and whose inside wire is 0.
  Scratch is deleted on every exit path; the donor's md5 is checked unchanged.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opaddshiftreg_v0.log -- py -u tools/recipes/build_opaddshiftreg_v0.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

# SR_SEED=For (2026-09-14 23:5x, step B revised route): the same op on the ForLoop-typed seed (OpLoopCast_v1 donor)
# -> OpAddShiftRegF_v0; the test then uses HARNESS_copyloop's EXISTING For loop instead of creating a While loop.
SEED = os.environ.get("SR_SEED", "While")
FOR = SEED == "For"
CLS = "ForLoop" if FOR else "WhileLoop"
SRC = os.path.join(g.CLAUDEDEV, "OpLoopCast_v1.vi" if FOR else "OpWhileCast_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpAddShiftRegF_v0.vi" if FOR else "OpAddShiftReg_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opaddshiftregF_labels.json" if FOR else "opaddshiftreg_labels.json")
SCRATCH_SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_addsr_{os.getpid()}.vi")
STOP = "Shift Registers?"          # Boolean control borrowed from OpForLoop_v0; the label is irrelevant
M_ADDSR, P_UID = "6361000", "632A813"
g._run.__defaults__ = (6.0, 120.0)
STEPS, PASS = [], []


def com_preflight(tries=15, gap=4.0):
    """Refuse to start until LabVIEW answers the SAME cheap round-trip twice in a row.

    Run 2 (22:35:43) died with 'RPC server is unavailable' three calls in: the batch had been started seconds after a
    forced Stop-Process, and 'Dispatch succeeded' plus two working calls was NOT evidence that the instance would
    still be there for the third. A successful call is not a readiness signal; two successful calls spaced apart,
    against a process whose pid has not changed between them, is the weakest signal worth trusting.
    """
    import subprocess
    def pid():
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return out or None
    last = None
    for k in range(tries):
        try:
            p0 = pid()
            n = g.count(os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi"), "Wire")
            time.sleep(gap)
            n2 = g.count(os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi"), "Wire")
            p1 = pid()
            if n == n2 and p0 and p0 == p1:
                print(f"   COM preflight OK (pid {p0}, two round-trips agree: {n} wires)", flush=True)
                return True
            last = f"pid {p0}->{p1}, wires {n}->{n2}"
        except Exception as e:
            last = str(e)[:160]
        print(f"   COM preflight attempt {k + 1}/{tries}: {last}", flush=True)
        time.sleep(gap)
    print(f"   COM preflight FAILED after {tries} attempts: {last}", flush=True)
    return False


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def walk(target, diagram=0, limit=80):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(limit):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows])
    return out


def snap(tag=""):
    return (f"{tag} Property={len(g.report_all(OP, 'Property'))} Invoke={len(g.report_all(OP, 'Invoke'))} "
            f"Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def ctls():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if not is_ind and lab]


def a0():
    """Diagnostic only, no gate: what IS OpExitWhile_v0's unexercised 'Shift Registers' input wired to?"""
    print("\n== A0 (diagnostic, read-only) OpExitWhile_v0's 'Shift Registers' feeder", flush=True)
    try:
        w = walk(os.path.join(g.CLAUDEDEV, "OpExitWhile_v0.vi"), 0)
        gos = [(u, v) for u, v in w.items() if (v[1] or "").startswith("Get Outputs")]
        for u, (n, lab, rows) in gos:
            nin = next((wi for _i, nm, s, wi in rows if nm == "Node in" and not s), 0)
            outp = next((wi for _i, nm, s, wi in rows if nm == "Outputs" and s), 0)
            sink = next(((uu, nm) for uu, (nn, ll, rr) in w.items() for _i, nm, s, wi in rr
                         if not s and wi and wi == outp and uu != u), None)
            print(f"   Get Outputs {u}: 'Node in' wire {nin}; 'Outputs' -> {sink}", flush=True)
    except Exception as e:
        print(f"   (diagnostic failed, not a gate) {str(e)[:200]}", flush=True)


def build():
    # NB: `g._lv = None` is NOT done here. Run 2 (22:35) died with 'RPC server is unavailable' on a call against a
    # CACHED op-VI proxy, because a0() had already cached reporter VI references and build() then re-Dispatched the
    # Application underneath them (peer: archive/peer/2026-09-14-addshiftreg-run2-rpc-unavailable.md, H3 - a
    # disconnected proxy, not a dead process). The reset happens ONCE, at the top of main(), before anything caches.
    try:
        g.close_panel(OP); time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)
    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy is not runnable.", flush=True)
        return None, donor_md5
    w = walk(OP, 0)
    for u, (n, lab, rows) in w.items():
        print(f"   node {u} (n={n}) {lab!r}: {[nm for _i, nm, _s, _wi in rows if nm]}", flush=True)
    tmsc = next((u for u, (n, lab, rows) in w.items()
                 if any(nm == "specific class reference" for _i, nm, _s, _wi in rows)), None)
    print(f"   TMSC node: {tmsc}", flush=True)
    if tmsc is None:
        print("STOP: no To More Specific Class in the donor - the typed WhileLoop reference is not where expected.", flush=True)
        return None, donor_md5
    fidx = lambda u: [o["uid"] for o in g.report_all(OP, "Function")].index(u)

    inv = step("A1 Invoke Loop.Add Shift Register (6361000)", "Invoke +1",
               lambda: g.build_invoke(OP, "VI Server:Loop", M_ADDSR, (900, 900))[-1]["uid"])
    if not inv:
        return None, donor_md5
    w2 = walk(OP, 0)
    inv_terms = [nm for _i, nm, _s, _wi in w2.get(inv, (0, None, []))[2] if nm]
    print(f"   Invoke terminals: {inv_terms}", flush=True)
    generic = {"reference", "reference out", "error in (no error)", "error in", "error out"}
    specific = [t for t in inv_terms if t not in generic]
    check("A1 the method attached (non-generic terminals present)", bool(specific), str(specific))
    if not specific:
        print("   OBSERVED: only generic terminals = the documented PRIVATE-member signature "
              "(toolkit-capabilities.md). STOP - 'Invoke.Set Method (Allow Private)' 6370003 is a NEXT batch.", flush=True)
        return None, donor_md5
    has_y = any(t.lower().startswith("y pos") for t in specific)
    check("A1 'Y Position' input present", has_y, str(specific))

    inv_i = lambda: [o["uid"] for o in g.report_all(OP, "Invoke")].index(inv)
    # Run 1 (22:30) gated on ExecState here and read 0, and the recipe called that "the Loop-class invoke rejects a
    # WhileLoop reference". BOTH halves were unsound (peer: archive/peer/2026-09-14-addshiftreg-fail1-branch-or-decline.md):
    #   * `Y Position` is a REQUIRED input, so ExecState 0 before it is wired is expected and NON-discriminating -
    #     it is equally consistent with a landed branch, a declined branch and a class conflict;
    #   * branch=True only SKIPS gscript.wire's wire-count check, so an unchanged count is not evidence of success.
    # The discriminator is the wire UID reported on BOTH ends (a branch shares the existing Wire object):
    # measured 22:33 (tools/bench/diag_addsr_fail1.log) - TMSC 'specific class reference' = 366 and
    # Invoke 'reference' = 366, so the branch LANDS and a WhileLoop reference IS accepted by a Loop-class invoke.
    step("A1b TMSC 'specific class reference' -> Invoke.reference (branch)", "same wire uid on both ends",
         lambda: (g.wire(OP, "Function", fidx(tmsc), "specific class reference", "Invoke", inv_i(), "reference",
                         branch=True), snap("after"))[1])
    w3 = walk(OP, 0)
    w_src = next((wi for _i, nm, s, wi in w3[tmsc][2] if nm == "specific class reference" and s), 0)
    w_ref = next((wi for _i, nm, s, wi in w3[inv][2] if nm == "reference" and not s), 0)
    check("A1b the branch landed (Invoke.reference wire == TMSC output wire)",
          bool(w_src) and w_ref == w_src, f"src={w_src} ref={w_ref}")
    if not w_ref or w_ref != w_src:
        print("   OBSERVED: the by-name branch did not land. Repair route (peer): the index-based native "
              "Terminal.Connect Wire (gscript.connect_terminals), which documents branching from a wired source. "
              "STOP - that is a NEXT batch.", flush=True)
        return None, donor_md5

    # Every terminal from here on is addressed by INDEX + DIRECTION, never by name: this node carries `Y Position`
    # and `Add Shift Register` TWICE each (measured: 6 = Y sink / 7 = Y source, 4 = return sink / 5 = return source),
    # the same duplicate-name trap that cost two recipes today (opqueue `error out`, opexitwhile `Outputs`).
    labels = {}
    rows, ni = w3[inv][2], w3[inv][0]
    ty = next((i for i, nm, s, _wi in rows if nm and nm.lower().startswith("y pos") and not s), None)
    print(f"   'Y Position' sink terminal index: {ty}", flush=True)
    if ty is not None:
        before = set(ctls()); g.create_control(OP, ni, ty)
        new = [l for l in ctls() if l not in before]
        print(f"   control on 'Y Position' -> {new}", flush=True)
        if new:
            labels["y_position"] = new[-1]
    ret = next((i for i, nm, s, _wi in rows if nm and s and nm not in generic), None)
    print(f"   return SOURCE terminal index: {ret} "
          f"({[(i, nm, s) for i, nm, s, _w in rows if nm not in generic]})", flush=True)
    pn = None
    if ret is not None:
        pn = step("B1 PN GObject[UID] on the returned reference", "Property +1",
                  lambda: g.build_property(OP, "VI Server:GObject", [(P_UID, False)], (1250, 900))[-1]["uid"])
        if pn:
            w4 = walk(OP, 0)
            npn = w4[pn][0]
            t_ref = next((i for i, nm, s, _wi in w4[pn][2] if nm == "reference" and not s), None)
            step("B2 Invoke return -> PN.reference BY INDEX (never by the duplicated name)",
                 "wire on both ends",
                 lambda: g.connect_terminals(OP, npn, t_ref, w4[inv][0], ret))
            w4 = walk(OP, 0)
            npn = w4[pn][0]
            tu = next((i for i, nm, s, _wi in w4[pn][2] if nm and s and nm not in generic), None)
            if tu is not None:
                before = set(inds()); g.create_indicator(OP, npn, tu)
                new = [l for l in inds() if l not in before]
                print(f"   indicator on UID -> {new}", flush=True)
                if new:
                    labels["uid"] = new[-1]
    w5 = walk(OP, 0)
    te = next((i for i, nm, s, _wi in w5[inv][2] if nm == "error out" and s), None)
    if te is not None:
        before = set(inds()); g.create_indicator(OP, w5[inv][0], te)
        new = [l for l in inds() if l not in before]
        print(f"   indicator on Invoke.error out -> {new}", flush=True)
        if new:
            labels["error"] = new[-1]
    step("C auto error handling OFF", "silent", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:") + f" labels {labels}", flush=True)
    if es != 1 or any(k == "exc" for _n, k in STEPS) or "y_position" not in labels or "uid" not in labels:
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}, labels {labels}) - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)          # run 1 left this VI open and unsaved, which forced a LabVIEW restart
        except Exception:
            pass
        return None, donor_md5
    g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("   saved; labels ->", MAP_OUT, flush=True)
    return labels, donor_md5


def add_shift_reg(target, loop_index, y_position, labels):
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", CLS)
    vi.SetControlValue("index", loop_index)
    vi.SetControlValue(labels["y_position"], int(y_position))
    g._run(vi)
    err = g._err(vi, labels["error"]) if "error" in labels else ""
    return int(vi.GetControlValue(labels["uid"])), err


def a2(labels):
    """FUNCTIONAL: create a register on a real scripted While loop and read it back with an independent reader."""
    print("\n== A2 (functional) add a shift register to a scratch While loop", flush=True)
    print("   predict: shift_reg_uids 0 -> 1, element == the op's reported UID, one LeftShiftRegister, both sides unwired",
          flush=True)
    shutil.copyfile(SCRATCH_SRC, S); time.sleep(0.3)
    try:
        g.copy_into(g.OP_FORLOOP, STOP, S)
        g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
        inv0 = g.uids(S, "Invoke")
        if FOR:
            # HARNESS_copyloop already carries exactly one For loop (N = 1024, IMAQ Copy inside): use it as-is
            if len(g.report_all(S, "ForLoop")) != 1:
                check("A2 scratch has exactly one For loop", False, str(len(g.report_all(S, "ForLoop"))))
                return
            print(f"   scratch (For loop): ExecState {g.exec_state(S)}", flush=True)
        else:
            wl0 = len(g.report_all(S, "WhileLoop"))
            dia0 = {d["uid"] for d in g.report_all(S, "Diagram")}
            g.while_loop(S, (200, 1400))
            new_d = [(i, d) for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] not in dia0]
            if wl0 != 0 or len(g.report_all(S, "WhileLoop")) != 1 or len(new_d) != 1:
                check("A2 one fresh While loop on the scratch", False, f"wl0={wl0} new_d={len(new_d)}")
                return
            body_uid = new_d[0][1]["uid"]
            body = next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid)
            g.exit_while(S, STOP, body)            # conditional terminal wired -> the loop is legal
            print(f"   scratch after exit_while: ExecState {g.exec_state(S)}", flush=True)
        before = g.loop_cast(S, 0, CLS)
        print(f"   before: {before}", flush=True)
        uid, err = add_shift_reg(S, 0, 120, labels)
        print(f"   add_shift_reg -> uid {uid}, error {err!r}", flush=True)
        after = g.loop_cast(S, 0, CLS)
        print(f"   after : {after}", flush=True)
        regs = after.get("shift_reg_uids", []) or []
        check("A2 no error from the invoke", not err, err)
        check("A2 shift_reg_uids 0 -> 1", len(before.get("shift_reg_uids", []) or []) == 0 and len(regs) == 1,
              f"{before.get('shift_reg_uids')} -> {regs}")
        check("A2 the created register is the one the op reported", bool(uid) and regs == [uid], f"{uid} vs {regs}")
        if len(regs) == 1 and FOR:
            # the register READERS (OpShiftRegs_v0/v1) are WhileLoop-seeded (1055 on a ForLoop ref): on the For
            # variant the left/right census is not available; loop_cast's uid identity + ExecState carry the check
            print("   (For seed: left/right terminal census skipped - readers are WhileLoop-seeded)", flush=True)
        if len(regs) == 1 and not FOR:
            r = g.shift_reg(S, 0, 0, "WhileLoop")
            lft = g.shift_reg_left(S, 0, 0, 0, "WhileLoop")
            print(f"   right: {r}", flush=True)
            print(f"   left : {lft}", flush=True)
            left = lft.get("left", {})
            check("A2 right register class", "RightShiftRegister" in str(r.get("class", "")), str(r.get("class")))
            check("A2 one LeftShiftRegister, both sides unwired",
                  "LeftShiftRegister" in str(left.get("class", "")) and len(lft.get("left_uids", [])) == 1
                  and left.get("out", {}).get("wire") == 0
                  and all(t.get("wire") == 0 for t in left.get("inside", [])),
                  f"class={left.get('class')!r} lefts={lft.get('left_uids')} out={left.get('out')} inside={left.get('inside')}")
        check("A2 no junk Invoke on the scratch", not [u for u in g.uids(S, "Invoke") if u not in inv0])
        print(f"   scratch ExecState after the register: {g.exec_state(S)} "
              "(0 is expected and correct: an unwired shift register breaks the VI until both sides are wired)", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        if os.path.exists(S):
            os.remove(S)


def main():
    g._lv = None                       # ONCE, before any op-VI proxy is cached (see build()'s note)
    if not com_preflight():
        print("STOP: LabVIEW is not reliably answering COM - nothing was built.", flush=True)
        return 1
    a0()
    labels, donor_md5 = build()
    if labels:
        a2(labels)
    else:
        try:
            g.close_panel(OP)          # never leave a dirty VI loaded: run 1 did, and it cost a restart
        except Exception:
            pass
    same = hashlib.md5(open(SRC, "rb").read()).hexdigest() == donor_md5
    print(f"\ndonor md5 unchanged: {same}", flush=True)
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS   steps {STEPS}", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if (labels and PASS and n_ok == len(PASS) and same) else 1


if __name__ == "__main__":
    sys.exit(main())
