# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1 census part 3 (F7, F8, F1 per-slot carriers): (1) protocol.check_requires on an IN-MEMORY requires list
for the queue tooling (no card file written); (2) the s09 1.1 writers of the per-slot arrays FrameIdx / BufDiff (which
value each slot carries); (3) save trace.vi in subvi_requiredness.json; (4) memory_model fields for s09 (quoted).
Reads files only. Prediction: the 4 OpQueue*_v0 ops are FOUND; FrameIdx's slot value traces to #637 i (t644)."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # offline: file system + JSON only (protocol.py:1046-1052)
REQ = [{"kind": "op", "name": n} for n in ("OpQueueObtain_v0", "OpQueueEnqueue_v0", "OpQueueDequeue_v0", "OpQueueRelease_v0")]
REQ += [{"kind": "verb", "name": n} for n in ("queue_node", "delete_object", "delete_wire")]
REQ += [{"kind": "file", "name": n} for n in ("tools/bench/opqueue_obtain_labels.json", "tools/bench/opqueue_enqueue_labels.json",
                                              "tools/bench/opqueue_dequeue_labels.json", "tools/bench/opqueue_release_labels.json")]
r = protocol.check_requires({"requires": REQ})
print("== F7 requires ok=%s" % r["ok"])
for it in r["found"]:
    print("  FOUND  ", it["kind"], it["name"], "->", it["cite"])
for it in r["missing"]:
    print("  MISSING", it["kind"], it["name"])
G = json.load(open("tools/bench/graph_ring_p4s09_20261009_062044.json", encoding="utf-8"))
BO, BW = collections.defaultdict(list), collections.defaultdict(list)
for t in G["terminals"]:
    BO[t["owner_uid"]].append(t)
    if t["wire_uid"]:
        BW[t["wire_uid"]].append(t)

def src_of(t):
    return [(x["owner_uid"], x["owner_class"], x["term_name"], x["term_uid"], x["frame_diagram"]) for x in BW.get(t["wire_uid"], [])
            if x["is_source"] and x["term_uid"] != t["term_uid"]]
print("== per-slot writers (Local sinks) in s09")
for name in ("FrameIdx", "BufDiff", "TransPos", "RotPos", "Num", "Latest", "StopAll"):
    for t in G["terminals"]:
        if t["owner_class"] == "Local" and t["term_name"] == name and not t["is_source"]:
            s = src_of(t)
            print("  write %-8s local #%s d%s <- %s" % (name, t["owner_uid"], t["frame_diagram"], s))
            for (u, c, tn, tu, d) in s:
                for x in BO.get(u, []):
                    if not x["is_source"]:
                        print("       #%s %s in %r w%s <- %s" % (u, c, x["term_name"], x["wire_uid"], src_of(x)))
                        for (u2, c2, tn2, tu2, d2) in src_of(x):
                            if c2 in ("IndexArray", "Function", "LoopTunnel", "FlatSequenceInnerTunnel", "SelectorTunnel", "Tunnel"):
                                for y in BO.get(u2, []):
                                    if not y["is_source"]:
                                        print("            #%s %s in %r <- %s" % (u2, c2, y["term_name"], src_of(y)))
q = json.load(open("tools/bench/subvi_requiredness.json", encoding="utf-8"))
hit = {k: v for k, v in (q.items() if isinstance(q, dict) else []) if "save trace" in str(k).lower() or "save trace" in json.dumps(v)[:300].lower()}
print("== subvi_requiredness save trace:", json.dumps(hit)[:600] if hit else "NOT LISTED", "| top keys", list(q)[:8] if isinstance(q, dict) else type(q))
M = json.load(open("tools/bench/memory_model.json", encoding="utf-8"))
print("== F8 memory_model")
print("  load_by_vi[eb1d0f31..] =", json.dumps(M["load_by_vi"].get("eb1d0f3107bbba49c9ae67a47c0ee50f")))
for k in ("formula", "start_rule", "op0_read_mb", "read_mb", "edit_mb", "other_mb", "final_read_mb", "fail_above_mb", "memstop_mb", "load_growth_mb_per_op"):
    print("  %s = %s" % (k, json.dumps(M.get(k))[:400]))
print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d},"first_fail":null,"artefacts":[]}'
      % ("PASS" if r["ok"] else "FAIL", len(r["found"]), len(r["missing"])))
