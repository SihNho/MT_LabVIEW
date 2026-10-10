---
card: 164-a1-2
date: 2026-10-10
status: current
---
# 164-a1-2 facts (read-only; no LabVIEW)
1. Adopted frame-True pass wires (w_gpass r_in:431-445, w_hpass r_in:510-524, w_c7_pass c:259-273) compile as op kind `case_frame_wire` (stagexec.py:936-937, or :931-933 for '#uid' on a BASE case; c.json:842-847 k8 route case_frame_wire). Precondition: any end carries `frame` (stagexec.py:928); it is a standalone wire op, not part of a tunnel group.
2. In those groups each tunnel is followed by TWO frameless wires: TG1 t_gi (r_in:367-376) -> w_gl in (:377-387) + w_g376 out (:388-398); TG2 t_go (:399-408) -> w_gout in + w_gr out (:409-430); TC7 t_ci7 (c:196-205) -> w_ci7_in + w_ci7_inc (c:206-219); TD7 t_co7 (c:236-244) -> w_inc7_co + w_co7_r (c:245-258). The pass wire comes AFTER both groups.
3. K3: OK3 t_k3o (r_in:789-798) -> w_k3out in + w_k3r out (:799-816) = complete. IK3 t_k3i dir in, body new:CQ7.f1 (:817-826) -> w_k3l in (:827-833) + w_k3pass (:834-848, src AND dst frame 'True'). IK3 has no frameless out-wire inside its 2-row window.
4. Differences IK3 vs TG1/TC7: (a) no frameless out-wire from the in-tunnel's inner face; (b) the pass wire is inside the tunnel's 2-row window and is its only candidate out-wire; (c) pass wire src carries `frame`; (d) TC7/TD7 loop = base uid 31308 with '#31506/#31517' frames (adopted c.json) vs new:CQ7 / 'True' in r_in.
5. stagexec.py:893-903 requires, within the 2 actions after `tunnel`, exactly one group wire with dst = tunnel (ins) and exactly one with src = tunnel (outs); group wire = op wire with NO `frame` on either end (:896-897); outs also accepts case_pass_wire(...) True (:899).
6. case_pass_wire (stagexec.py:6283-6288) returns False when src carries `frame` (:6287) or dst lacks `frame`; accepted shape = frameless src = this tunnel's inner, dst `frame` = in-tunnel's own body frame name (:6290-6304), dir must be 'in' (:6291).
7. Where adopted groups get the second wire: from the frameless inner-face wire (w_g376 / w_ci7_inc / w_gr / w_co7_r) inside the window; compiled as kind `tunnel` acts [i,i+1,i+2] (stagexec.py:922) or connect_term_uid register variant (:913-919).
OPEN: K3/K4 shape - frameless src per stagexec.py:6286-6288, or a frameless out-wire before the pass wire as in TG1/TC7 - judgement's call.
