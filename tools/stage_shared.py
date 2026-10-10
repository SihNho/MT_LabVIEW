# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_162-a2-3.md
# ---
r"""stage_shared - bench helpers that several tools/bench prep / self-test scripts need (card 162-a2-3, docs/d1/ring-p5b.md PD392(e) / PD393(e)).
Pure json-in / json-out, no LabVIEW, no module state. Kept OUT of stagekit / stagexec / stagesim / stage_prerun on purpose: their md5s are pinned by
launch gates and self-tests. Self-test: tools/bench/selftest_c162_stage_shared.py (replays the recorded old-block outputs).
Copies replaced (prep_c162_a2_3_copies.log): base_sink_renames <- 8 licence writers; checkpoint_step_table <- 5 pred writers;
insert_stub_deletes <- selftest_c160_regface.py and prep_c160_b3_1_mk.py."""
import collections


def base_sink_renames(actions, base_terms, why_fmt):
    """Licence rename table (PD365(d)): returns (ren, own, wr) - ren = [{"node", "term_uids", "why"}] per BASE owner whose SINK terminal a plan
    `wire` action wires by dst term uid (sorted by owner), own = {owner: set(term uids)}, wr = {owner: [action ids]}; `why_fmt`.format(owner, rows).
    base_terms = {term_uid: graph terminal row}. Self-test: tools/bench/selftest_c162_stage_shared.py."""
    own, wr = collections.defaultdict(set), collections.defaultdict(list)
    for a in actions:
        if str(a.get("op")).lower() != "wire" or not isinstance(a.get("dst"), dict) or a["dst"].get("term_uid") is None:
            continue
        r = base_terms.get(int(a["dst"]["term_uid"]))
        if r is None or r.get("is_source"):
            continue
        own[int(r["owner_uid"])].add(int(r["term_uid"]))
        wr[int(r["owner_uid"])].append(a["id"])
    ren = [{"node": o, "term_uids": sorted(own[o]), "why": why_fmt.format(o, wr[o])} for o in sorted(own)]
    return ren, own, wr


def checkpoint_step_table(ops, cps, sfn, actions=None):
    """E1 checkpoint table: returns [{"op", "kind", "action", ["ids",] "step_file", "md5"}] for each checkpoint op number k in `cps` (0 = base),
    action = the last action number of op k, step file / md5 from sfn = {action number: step_files entry}; `ids` (the op's action ids, [] for k 0)
    only when `actions` (the plan's action list) is given. Self-test: tools/bench/selftest_c162_stage_shared.py."""
    cpe = []
    for k in cps:
        an = max(ops[k - 1]["acts"]) if k else 0
        x = sfn.get(an)
        e = {"op": k, "kind": ops[k - 1]["kind"] if k else "base", "action": an}
        if actions is not None:
            e["ids"] = [actions[n - 1]["id"] for n in ops[k - 1]["acts"]] if k else []
        e["step_file"], e["md5"] = x and x["path"], x and x.get("md5")
        cpe.append(e)
    return cpe


def insert_stub_deletes(actions, wire_by_id, why):
    """Returns a new action list = `actions` with a row {"op": "delete_wire", "id": "dw_" + id[2:], "wire_uid": wire_by_id[id], "why": why} inserted
    just before every action whose id is a key of wire_by_id (PD391(a) stub delete before the group's connect); the action dicts are not copied.
    Self-test: tools/bench/selftest_c162_stage_shared.py."""
    acts = []
    for a in actions:
        if a.get("id") in wire_by_id:
            acts.append({"op": "delete_wire", "id": "dw_" + a["id"][2:], "wire_uid": wire_by_id[a["id"]], "why": why})
        acts.append(a)
    return acts
