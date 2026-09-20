"""Offline call-graph extractor for LabVIEW VIs.

Byte-scans each .vi for referenced "<name>.vi" strings and resolves them against an
index of every .vi on disk. No LabVIEW involved, so it is safe to run against
originals: it only reads bytes.

Caveats (state them wherever the output is used):
  - String presence proves a REFERENCE, not a call site count, and cannot see
    which loop/case frame a call sits in.
  - Names that resolve nowhere are almost always NI library VIs (vi.lib) or
    typedefs; they are reported separately rather than dropped.
"""
import os
import re
import sys
from collections import OrderedDict

ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
MAIN = os.path.join(ROOT, r"AAA_UNIST\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")

NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9 _\-\.,%()+&'!?]{2,60}\.vi")

# Folders that are archives/duplicates - prefer canonical locations when a name is ambiguous.
PREFER = ["background VIs", "AAA_UNIST\\2. Tracking", "Shared VIs", "SiHyeong Modified"]
DEPRIORITISE = ["\\old\\", "InstCache", "LVAutoSave", "archive", "V6_ParallelLoop"]


def build_index():
    idx = {}
    for dirpath, _dirs, files in os.walk(ROOT):
        for f in files:
            if not f.lower().endswith(".vi"):
                continue
            full = os.path.join(dirpath, f)
            key = f.lower()
            idx.setdefault(key, []).append(full)
    # rank candidates
    def rank(p):
        s = 0
        for i, pref in enumerate(PREFER):
            if pref.lower() in p.lower():
                s -= (len(PREFER) - i) * 10
        for d in DEPRIORITISE:
            if d.lower() in p.lower():
                s += 50
        return (s, len(p))
    return {k: sorted(v, key=rank) for k, v in idx.items()}


def refs_of(path, index):
    try:
        data = open(path, "rb").read()
    except OSError:
        return [], []
    text = data.decode("latin-1")
    own = os.path.basename(path).lower()
    seen, local, external = set(), [], []
    for m in NAME_RE.finditer(text):
        name = m.group(0).strip()
        key = name.lower()
        if key == own or key in seen:
            continue
        seen.add(key)
        if key in index:
            local.append(name)
        else:
            external.append(name)
    return sorted(local), sorted(external)


def main():
    index = build_index()
    print("indexed %d distinct .vi filenames under %s\n" % (len(index), ROOT))

    tree = OrderedDict()
    externals = {}
    order = []

    def walk(path, depth, chain):
        name = os.path.basename(path)
        key = name.lower()
        if key in chain:                       # cycle guard
            return
        if key in tree:
            return
        local, ext = refs_of(path, index)
        tree[key] = (name, path, local, depth)
        externals[key] = ext
        order.append(key)
        if depth >= 4:
            return
        for child in local:
            ck = child.lower()
            cands = index.get(ck)
            if not cands:
                continue
            walk(cands[0], depth + 1, chain | {key})

    walk(MAIN, 0, frozenset())

    print("=" * 78)
    print("CALL GRAPH (project-local VIs only, depth-first, first-seen)")
    print("=" * 78)
    for key in order:
        name, path, local, depth = tree[key]
        where = os.path.dirname(path).replace(ROOT, "…")
        print("%s%s" % ("  " * depth, name))
        print("%s    [%s]  ->%d local refs" % ("  " * depth, where, len(local)))

    print()
    print("=" * 78)
    print("DIRECT REFERENCES OF THE MAIN VI")
    print("=" * 78)
    mk = os.path.basename(MAIN).lower()
    for n in tree[mk][2]:
        print("   L  %s" % n)
    print()
    print("   unresolved (NI library / typedef / false positive):")
    for n in externals[mk]:
        print("   X  %s" % n)


if __name__ == "__main__":
    sys.exit(main())
