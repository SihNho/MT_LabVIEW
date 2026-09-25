"""diag_c89_donor_census - card 89-2 offline read (no LabVIEW): which non-forbidden wiki subVI dumps hold the
primitives the t0_stamp.vi body needs, so a donor for copy_by_index can be named from files, not guessed."""
import json, glob, os, collections, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol
NEED = ['Replace Array Subset', 'Quotient & Remainder', 'Write to Binary File', 'Open/Create/Replace File',
        'Close File', 'Initialize Array', 'Equal To 0?', 'Increment', 'Build Path', 'Array Subset', 'Equal?',
        'Select', 'Array Size', 'Tick Count (ms)']
hits = collections.defaultdict(list)


def walk(o, f):
    if isinstance(o, dict):
        for v in o.values():
            if isinstance(v, str) and v in NEED:
                hits[v].append(f)
            walk(v, f)
    elif isinstance(o, list):
        for v in o:
            walk(v, f)


for f in glob.glob('docs/wiki/subvi/*.json'):
    if 'D1_' in f:
        continue
    walk(json.load(open(f, encoding='utf-8')), os.path.basename(f))
# the main-VI lineage (D1_* copies of Min_Track N beads V6_ParallelLoop.vi) - per-diagram labels with uids
mv = json.load(open('tools/bench/main_vi_node_labels.json', encoding='utf-8'))
for dg, nodes in mv['diagrams'].items():
    for n in nodes:
        if n.get('label') in NEED:
            hits[n['label']].append('MAINVI diag %s uid %s' % (dg, n['uid']))
missing = []
for k in NEED:
    fs = sorted(set(hits[k]))
    print(repr(k), len(hits[k]), fs[:3])
    if not fs:
        missing.append(k)
print(protocol.result_line({"status": "PASS" if not missing else "FAIL", "gates": {"pass": len(NEED) - len(missing),
                            "fail": len(missing)}, "first_fail": ("no donor for " + ", ".join(missing)) if missing else None}))
