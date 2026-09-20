"""build_harness_copy.py - HARNESS_copy{0,1}.vi: the per-frame cost of a reference-safe image copy (IMAQ Copy).

    copy0  IMAQ Create(A) -> IMAQ ReadFile(File Path) ; IMAQ Create(B)                 (two allocations, no copy)
    copy1  + IMAQ Copy (A -> B)                                                        (the memcpy of 1280x1024 U8)
Timed like the display bench (tools/bench/run_copy_bench.py: one Run per frame, 200 frames, panels closed, files
pre-read); cost(Copy) = median(copy1) - median(copy0). Restructure gate G4 (image handoff between loops).
Same construction rules as build_harness_display.py: names read off each node with node_terms, save only when every
planned step succeeded and ExecState == 1, panels closed at the end.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_harness_copy.log -- py -u tools/recipes/build_harness_copy.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create")
R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
# IMAQ Copy is a Vision Development Module VI (nivision), not in the nivisioncommon runtime LLBs - run 1 hit error 7
# (file not found) in Basics.llb; found by string scan: Management.llb holds 'IMAQ Copy' and 'IMAQ ImageToImage 2'.
K_VI = os.path.join(r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision", "Management.llb", "IMAQ Copy")
SRC = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi")
OUT = {k: os.path.join(g.CLAUDEDEV, f"HARNESS_copy{k}.vi") for k in range(2)}
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "harness_copy_labels.json")
g._run.__defaults__ = (6.0, 90.0)
STEPS = []


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


def main():
    g._lv = None
    OP = OUT[1]
    for p in OUT.values():
        try:
            g.close_panel(p); time.sleep(0.2)
        except Exception:
            pass
        if os.path.exists(p):
            os.remove(p)
    for p in (C_VI, R_VI, K_VI):
        cont = p.split(".llb")[0] + ".llb"
        if not os.path.exists(cont):
            print(f"STOP: missing {cont}", flush=True); return 2
    shutil.copyfile(SRC, OP); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for idx in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", idx, verify=False)
            g.remove_bad_wires_scripted(OP)

    def sub_i(uid):
        return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)

    def snap(tag=""):
        return f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} Wire={len(g.report_all(OP, 'Wire'))} CtlTerm={len(g.report_all(OP, 'ControlTerminal'))} ExecState={g.exec_state(OP)}"

    for _ in range(len(g.report_all(OP, "Node")) + 2):
        if not g.report_all(OP, "Node"):
            break
        try:
            g.delete_object(OP, "Node", 0, verify=False)
        except Exception:
            break
    g.remove_bad_wires_scripted(OP)
    for _ in range(40):
        if not g.report_all(OP, "ControlTerminal"):
            break
        g.delete_object(OP, "ControlTerminal", 0, verify=False)
    g.remove_bad_wires_scripted(OP); purge()
    print("base cleared:", snap(), flush=True)
    NODE = {}

    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [u for u in g.uids(OP, "SubVI") if u not in before]
        assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)} new"
        u = new[0]; n = None
        for cand in range(len(g.report_all(OP, "Node")) + 2):
            nu, rows = g.node_terms_uid(OP, 0, cand)
            if not nu:
                break
            if nu == u:
                n = cand; NODE[u] = (n, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]}); break
        assert n is not None
        print(f"   dropped {os.path.basename(path)} uid {u} Nodes[] {n}: {list(NODE[u][1].keys())}", flush=True)
        return u

    def tname(u, *cands):
        names = NODE[u][1]
        for c in cands:
            if c in names:
                return c
        raise RuntimeError(f"no terminal among {cands} on uid {u}: {list(names)}")

    def ws(su, st, du, dt):
        return g.wire(OP, "SubVI", sub_i(su), st, "SubVI", sub_i(du), dt)

    uA = step("1 drop IMAQ Create (A)", "+1", lambda: drop(C_VI, (100, 300)))
    uR = step("2 drop IMAQ ReadFile", "+1", lambda: drop(R_VI, (330, 300)))
    uB = step("3 drop IMAQ Create (B)", "+1", lambda: drop(C_VI, (330, 520)))
    uK = step("4 drop IMAQ Copy", "+1", lambda: drop(K_VI, (600, 400)))
    if None in (uA, uR, uB, uK):
        print("STOP: a drop failed.", flush=True); return 3
    step("5 wires: A.New Image -> R.Image; R.Image Out -> Copy.Image Src; B.New Image -> Copy.Image Dst; error chain",
         "Wire +5..6",
         lambda: ([ws(uA, tname(uA, "New Image"), uR, tname(uR, "Image")),
                   ws(uR, tname(uR, "Image Out"), uK, tname(uK, "Image Src", "Image Src (source)", "Source Image", "Image")),
                   ws(uB, tname(uB, "New Image"), uK, tname(uK, "Image Dst", "Image Dst (destination)", "Destination Image", "Image Dst Out")),
                   ws(uA, "error out", uR, "error in (no error)"),
                   ws(uR, "error out", uB, "error in (no error)"),
                   ws(uB, "error out", uK, "error in (no error)")], snap("after"))[1])
    labels = {}

    def make(uid, term, kind):
        n = NODE[uid][0]; ti = NODE[uid][1][term][0]
        fp0 = {l for _i, l, _ in g.fp_labels(OP)}; w0 = len(g.report_all(OP, "Wire"))
        (g.create_control if kind == "control" else g.create_indicator)(OP, n, ti); purge()
        new = [l for _i, l, _ in g.fp_labels(OP) if l not in fp0]
        ok = bool(new) and len(g.report_all(OP, "Wire")) > w0
        print(f"   {kind} on {term!r} (node {n} t{ti}) -> {new} wired={ok} ExecState {g.exec_state(OP)}", flush=True)
        if not ok:
            raise RuntimeError(f"{kind} on {term} not wired")
        return new[-1]
    labels["Image Name"] = step("6 control Image Name (A)", "wired", lambda: make(uA, tname(uA, "Image Name"), "control"))
    labels["Image Name B"] = step("7 control Image Name (B)", "wired", lambda: make(uB, tname(uB, "Image Name"), "control"))
    labels["File Path"] = step("8 control File Path", "wired", lambda: make(uR, tname(uR, "File Path"), "control"))
    es = g.exec_state(OP)
    print("\n" + snap("copy1 assembled:"), "labels", labels, flush=True)
    if es != 1 or any(k == "exc" for _n, k in STEPS) or None in labels.values():
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}) - NOT SAVING.", flush=True); return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"labels": labels}, f, indent=2)
    dst = OUT[0]
    shutil.copyfile(OP, dst); g.report_all(dst, "SubVI"); g.open_panel(dst); time.sleep(0.8)
    ids = [o["uid"] for o in g.report_all(dst, "SubVI")]
    g.delete_object(dst, "SubVI", ids.index(uK), verify=False); g.remove_bad_wires_scripted(dst)
    es0 = g.exec_state(dst)
    print(f"   copy0: SubVI={len(g.report_all(dst, 'SubVI'))} Wire={len(g.report_all(dst, 'Wire'))} ExecState={es0}", flush=True)
    if es0 == 1:
        g.set_auto_error_handling(dst, False); g.save(dst)
    for p in OUT.values():
        try:
            g.close_panel(p)
        except Exception:
            pass
    print("steps:", STEPS, flush=True)
    print(f"\nVERDICT: HARNESS_copy1/copy0 {'built' if es0 == 1 else 'copy0 BROKEN'} (structural) - run tools/bench/run_copy_bench.py next", flush=True)
    return 0 if es0 == 1 else 4


if __name__ == "__main__":
    sys.exit(main())
