"""subvi_harness.py - generic, script-only harness builder for ANY subVI (reentrant or not): a top-level VI that calls the
subVI once with a front-panel control on every input terminal and an indicator on every output terminal, so Python can
drive it over COM (SetControlValue / Run / GetControlValue).  Built from the FPTARGET_v0 base with drop_subvi +
create_control / create_indicator (toolkit ops, zero GUI); saved as claudeDev\HARNESS_<subvi name>.vi.

    h = build(subvi_path)               -> {"path", "controls": {terminal name: label}, "indicators": {...}}
    out = run(h, {"x center": 1.0, ...}, ["radial intensity profile"])
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import gscript as g  # noqa: E402

BASE = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi")
REG = os.path.join(HERE, "subvi_harnesses.json")


def _norm(s):
    return s.replace("\n", " ").strip()


def build(subvi_path, max_terms=32, force=False):
    reg = json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else {}
    name = os.path.splitext(os.path.basename(subvi_path))[0]
    if name in reg and not force and os.path.exists(reg[name]["path"]) and reg[name]["indicators"]:
        return reg[name]
    harness = os.path.join(g.CLAUDEDEV, f"HARNESS_{name}.vi")
    if os.path.exists(harness):
        # do NOT touch the old file through LabVIEW first (close_panel loads it; a VI in memory with the same path makes
        # the fresh copy unreadable: error 1012 in OpReport, 2026-09-07). If LabVIEW holds it, restart LabVIEW before build().
        os.remove(harness)
    shutil.copyfile(BASE, harness); g.report(harness, "SubVI"); g.open_panel(harness); time.sleep(1.0)
    while g.count(harness, "Node"):
        g.delete_object(harness, "Node", 0)
    g.remove_bad_wires_scripted(harness)
    g.drop_subvi(harness, subvi_path, 0, (300, 300))
    assert g.count(harness, "SubVI") == 1, "drop failed"
    fp0 = {l for _, l, _ in g.fp_labels(harness)}
    controls, indicators = {}, {}
    empties = 0
    for t in range(max_terms):
        w0 = g.count(harness, "Wire")
        new, label = g.create_control(harness, 0, t)
        if new and label:
            if g.count(harness, "Wire") > w0:
                controls[label] = t; fp0.add(label); empties = 0
                print(f"   t{t}: control {label!r}", flush=True); continue
            # Create Control on an OUTPUT terminal makes an UNWIRED control (2026-09-07): remove it, make an indicator
            ct = [o["uid"] for o in g.report(harness, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(harness, "ControlTerminal", ct.index(o["uid"])); ct = [o2["uid"] for o2 in g.report(harness, "ControlTerminal")]
            g.remove_bad_wires_scripted(harness)
            fp0 = {l for _, l, _ in g.fp_labels(harness)}
        new = g.create_indicator(harness, 0, t)
        labs = [l for _, l, _ in g.fp_labels(harness) if l not in fp0]
        if new and labs:
            indicators[labs[-1]] = t; fp0 |= set(labs); empties = 0
            print(f"   t{t}: indicator {labs[-1]!r}", flush=True); continue
        empties += 1
        if empties >= 3:
            break
    es = g.exec_state(harness)
    print(f"   harness {os.path.basename(harness)}: {len(controls)} controls, {len(indicators)} indicators, ExecState {es}", flush=True)
    if es != 1:
        raise RuntimeError(f"harness broken (ExecState {es})")
    g.save(harness)
    reg[name] = {"path": harness, "controls": {_norm(k): k for k in controls}, "indicators": {_norm(k): k for k in indicators}}
    json.dump(reg, open(REG, "w", encoding="utf-8"), indent=1)
    return reg[name]


def run(h, inputs, outputs):
    vi = g.op(h["path"])
    lab = lambda k: h["controls"].get(_norm(k)) or h["indicators"].get(_norm(k)) or k   # Create Control on an OUTPUT
    for k, v in inputs.items():                                                          # terminal yields an indicator
        vi.SetControlValue(lab(k), v)                                                     # that the builder may have filed
    g._run(vi)                                                                           # under "controls" - same label
    return {k: vi.GetControlValue(lab(k)) for k in outputs}
