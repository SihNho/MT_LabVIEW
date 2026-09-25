r"""l2a1_unflip_81 - card 81-5 M1/M1b (docs/d1-loop12-17-split-plan.md 182(d)): does wiring a FLIPPED input SelectorTunnel's
outer from a source make it an input again? One LabVIEW launch, NOTHING saved, no VI run, no motor/camera/GUI.
On a dated work copy D1_k_scratch_l2a1_unflip_81_<stamp>.vi of the bed D1_k (md5 6cf5b077, never opened for write):
  [A] pre-move: the Terminals[] index of #5702's outer 6038 / #5725's outer 5741 on Case #5540 (match_term_uid, wired now)
  [B] the joint L2-A1 move = sim_l2a1_81.py TOPS (80-5's 10 tops + #23541) into 1.2 body #23166, one move_in per top
  [C] read_live -> directions of #5702 / #5725 / #5967 outer + inners (the flipped state, 80-5 measured it)
  [D] M1: add_shift_reg on #10170, LeftIn: SR L.inner -> #5540 Terminals[i6038] (= plan row sr2_L0, the RULE-CHAIN-S1
      replacement of 6038's K source #5805 L.inner 5817, which sits on loop #637 and cannot be wired into #10170 directly);
      M1b: a second register -> #5725's outer 5741 (plan: a rule-166 tunnel inner; here a register - both are sources)
  [E] read_live -> the same directions; the READ is the fact, no un-flip outcome is predicted.
RUN 2 (same file, WATCH widened): run 1 (l2a1_unflip_81.log, PASS 17/0) read #5702/#5725 inners back to sources and #5967
unchanged; run 2 also reads the OUTPUT tunnels #5680 (inner 5999 fed by 5705, inner 6003 by 5973) and #6016 (6022 by 5733,
6018 by #5825's 5828) so a cascade un-flip is read, not assumed.
WHAT EXISTED FIRST: l2a1_facts_80.py tunflip (same bed, same move loop, read_live, drop), stagekit.add_sr_row / wire_sr
LeftIn (gscript.wire_sr:748), stagekit.match_term_uid. Nothing new is built.
PREDICTIONS (gates): P1 11 move_in ops err ''; P2 after [B] 5705 & 6033 & 5729 & 5733 read is_source False (80-5); P3 after
[D] 6038's wire == the new left register's inner wire, 5741's wire == the second register's; P4 bed md5 unchanged, refs
opened==closed, scratch deleted, LabVIEW gone. The un-flip directions are REPORTED (ROW), never gated.
  MATERIAL=1 py tools/bgrun.py --material --max-min 30 --log tools/bench/l2a1_unflip_81.log -- py -u tools/bench/l2a1_unflip_81.py"""
import json, os, subprocess, sys, time                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                              # noqa: E402
g = K.g
B = K.BENCH
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
TOPS, BODY, LOOP, D639, CASE = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541], 23166, 10170, 639, 5540
WATCH = {5702: (6038, 5705, 6033), 5725: (5741, 5729, 5733), 5967: (5976, 5969, 5973),
         5680: (6007, 5999, 6003), 6016: (6026, 6022, 6018)}   # run 2: + the OUTPUT tunnels the inputs feed (cascade read)
GP = os.path.join(B, "l2a1_graph_k_80.json")


def node_idx(s, didx, uid):
    uids = [r["uid"] for r in g.node_labels(s.work, didx)]
    ni = uids.index(uid)
    echo, rows = g.node_terms_uid(s.work, didx, ni)
    if echo != uid:
        raise K.Stop("uid echo {0!r} != #{1}".format(echo, uid))
    return ni, rows


def read(s, tag, fs):
    rows = K.mod("wiki_build").read_live(s.work, fs_pairs=fs)["terminals"]
    by = dict((int(r["term_uid"]), r) for r in rows)
    out = {}
    for tun, ts in WATCH.items():
        for t in ts:
            r = by.get(t)
            out[t] = None if r is None else {"is_source": bool(r["is_source"]), "wire": int(r["wire_uid"]), "cls": r.get("term_class")}
            s.fact("{0} #{1} t{2} {3}".format(tag, tun, t, out[t]))
    return out, rows


def body(s):
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); BD = K.mod("build_d1_v0"); A = K.mod("allterms")   # noqa: E702
    s.fact("HANDLES start {0!r}".format(bp.labview_handles()))
    fs = json.load(open(GP, encoding="utf-8"))["fs_tunnel_pairs"]
    s.head("[A] pre-move Terminals[] indices on Case #5540 (diagram #639)")
    d639 = BD.diag_index(s.work, D639); ni, rows = node_idx(s, d639, CASE); allr = A.read_terms(s.work)[0]   # noqa: E702
    idx = {}
    for t in (6038, 5741):
        i, a = K.match_term_uid(t, allr, rows, False)
        idx[t] = (i, rows[i]["name"])
        s.fact("PRE t{0} -> #5540 Terminals[{1}] name {2!r} wire {3}".format(t, i, rows[i]["name"], a["wire_uid"]))
    s.head("[B] joint L2-A1 move into body #23166")
    dB = BD.diag_index(s.work, BODY); errs = []                                   # noqa: E702
    for i, u in enumerate(TOPS):
        rec = s.move_in(u, dB, (4700 + 160 * i, 6300)); s.junk_purge("mv{0}".format(u)); errs.append(rec["err"])   # noqa: E702
    s.gate("P1 11 move_in ops returned err ''", errs == [""] * len(TOPS), errs)
    s.head("[C] read after the move")
    r1, _ = read(s, "AFTER-MOVE", fs)
    s.gate("P2 inners 5705 6033 5729 5733 read is_source False after the move (80-5 flip)",
           all(r1.get(t) and not r1[t]["is_source"] for t in (5705, 6033, 5729, 5733)), dict((t, r1.get(t)) for t in (5705, 6033, 5729, 5733)))
    s.head("[D] M1 / M1b: a register L.inner -> the flipped outer")
    lefts = {}
    for t in (6038, 5741):
        sr = s.add_sr_row({"loop_uid": LOOP}, tag="sr{0}".format(t))
        dB = BD.diag_index(s.work, BODY); nc, crow = node_idx(s, dB, CASE); i, nm = idx[t]   # noqa: E702
        s.fact("SINK t{0}: #5540 now Nodes[{1}] of D[{2}], Terminals[{3}] = {4!r} (pre-move name {5!r})".format(t, nc, dB, i, crow[i], nm))
        s.gate("D0 t{0}'s index still names the same unwired sink".format(t), crow[i]["name"] == nm and not crow[i]["wire"] and not crow[i]["is_source"], crow[i])
        rec = s.wire_sr("LeftIn", sr["loop_index"], sr["k"], node_index=nc, term_index=i); s.junk_purge("wsr{0}".format(t))   # noqa: E702
        s.gate("D1 wire_sr LeftIn -> t{0} returned err ''".format(t), rec["err"] == "", rec["err"])
        lefts[t] = sr["left"]
    s.head("[E] read after the re-wire")
    r2, rows2 = read(s, "AFTER-WIRE", fs)
    for t, L in lefts.items():
        li = [r for r in rows2 if int(r["owner_uid"]) == L and r.get("term_class") == "InnerTerminal"]
        w = int(li[0]["wire_uid"]) if li else None
        s.gate("P3 t{0}'s wire == register #{1} L.inner's wire".format(t, L), w and r2.get(t) and r2[t]["wire"] == w, (w, r2.get(t)))
    for tun, ts in WATCH.items():
        s.row("UNFLIP #{0} (outer, inner, inner) is_source before->after".format(tun),
              [(t, (r1.get(t) or {}).get("is_source"), (r2.get(t) or {}).get("is_source")) for t in ts])
    s.R["reads"] = {"after_move": r1, "after_wire": r2, "lefts": lefts, "idx": idx}
    s.fact("HANDLES end {0!r}".format(bp.labview_handles()))


if __name__ == "__main__":
    st_ = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "l2a1_unflip_81", work_name="D1_k_scratch_l2a1_unflip_81_{0}.vi".format(st_), preload=False,
                pins=tuple(K.DEFAULT_PINS) + (("K bed", BED, BED_MD5),), deadline_min=25,
                out_json=os.path.join(B, "l2a1_unflip_81.json"), task="card 81-5 M1/M1b")
    K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
    s.gate("F7 LabVIEW process gone at the end", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    sys.exit(s.summary())
