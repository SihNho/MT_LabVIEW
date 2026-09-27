"""c108c helper - offline graph walker over a wiki-style graph JSON (terminals/objs). No LabVIEW.

Prior art checked: tools/vigraph.py (build4: wire + node pass-through + SR machine pairs + fs pairs + locals; no
first-sink walker), tools/bench/diag_c96_cons_trace.py (96-3: forward trace of #1359's two out tunnels on S1, no
tagging, no upstream walk). This file adds: diagram->loop location, first-non-carrier walks down AND up, and tags.
Carriers walked THROUGH: LoopTunnel/Tunnel/SelectorTunnel (one object, both faces), shift registers (machine pairs
`left_of`, else none), flat-sequence tunnels (fs_tunnel_pairs), an indicator read back by same-label Locals.
"""
import json, re, collections

TUN = {"LoopTunnel", "Tunnel", "SelectorTunnel"}
FS = {"FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel"}
SR = {"LeftShiftRegister", "RightShiftRegister"}
MOTOR = ("MOV.vi", "VEL.vi", "GOH.vi", "SetCommand", "Move Axis", "Motor control", "Configure.vi")
LOOPNAME = {637: "1.1", 10170: "1.2", 23032: "1.5", 23041: "1.7"}


class Graph:
    def __init__(self, path, owners=None, loops=None):
        raw = open(path, encoding="utf-8").read()
        g = json.loads(raw)
        self.name, self.md5 = path.replace("\\", "/").split("/tools/bench/")[-1], g.get("md5")
        self.terms = g["terminals"]
        self.cls = {o["uid"]: o["class"] for o in g["objs"]}
        self.term = {t["term_uid"]: t for t in self.terms}
        self.by_owner, self.by_wire = collections.defaultdict(list), collections.defaultdict(list)
        for t in self.terms:
            self.by_owner[t["owner_uid"]].append(t)
            if t["wire_uid"]:
                self.by_wire[t["wire_uid"]].append(t)
        self.subvi = {c["node_uid"]: c["subvi_name"] for c in g["graph_summary"].get("subvi_calls", [])}
        self.owners = {int(k): v for k, v in (owners or g.get("owners") or {}).items()}
        self.lines = {}
        if "\n" in raw:                                   # indented file: term_uid -> line number
            for i, ln in enumerate(raw.split("\n"), 1):
                m = re.match(r'\s*"term_uid": (\d+),', ln)
                if m and int(m.group(1)) not in self.lines:
                    self.lines[int(m.group(1))] = i
        self.pair = collections.defaultdict(list)          # SR right <-> left (machine)
        for L in (loops if loops is not None else g.get("loops", [])):
            for r, ls in (L.get("left_of") or {}).items():
                for l in (ls if isinstance(ls, list) else [ls]):
                    self.pair[int(r)].append(int(l)); self.pair[int(l)].append(int(r))
        self.fs = {}
        for p in g.get("fs_tunnel_pairs", []):
            if p.get("term_a") and p.get("term_b") and not p.get("errs"):
                self.fs[p["term_a"]] = p["term_b"]; self.fs[p["term_b"]] = p["term_a"]
        self.struct_outer = {}
        for u, ts in self.by_owner.items():
            if self.cls.get(u) in TUN:
                s = self.struct_of_tunnel(u)
                out = [t["frame_diagram"] for t in ts if t["term_class"] == "OuterTerminal"]
                if s and out:
                    self.struct_outer.setdefault(s, out[0])
        self.locals = collections.defaultdict(list)
        for t in self.terms:
            if t["owner_class"] == "Local":
                self.locals[t["term_name"]].append(t)

    def cite(self, term_uid):
        if term_uid in self.lines:
            return "tools/bench/%s:%d" % (self.name, self.lines[term_uid])
        return "tools/bench/%s:1 term_uid=%s" % (self.name, term_uid)

    def node(self, t):
        return t["term_uid"] if t["term_class"] == "ControlTerminal" else t["owner_uid"]

    def ncls(self, n):
        return self.cls.get(n, "?")

    def struct_of_tunnel(self, u):
        for t in self.by_owner.get(u, []):
            if t["term_class"] == "InnerTerminal":
                o = self.owners.get(t["frame_diagram"])
                if o:
                    return o[1]
        return None

    def diag(self, n):
        ts = self.by_owner.get(n) or ([self.term[n]] if n in self.term else [])
        out = [t["frame_diagram"] for t in ts if t["term_class"] == "OuterTerminal"]
        return out[0] if out else (ts[0]["frame_diagram"] if ts else None)

    def chain(self, n):
        """structures enclosing node n, inner -> outer."""
        out, D, guard = [], self.diag(n), 0
        while D is not None and guard < 40:
            o = self.owners.get(D)
            if not o or not o[1]:
                break
            out.append(o[1]); D = self.struct_outer.get(o[1]); guard += 1
        return out

    def loop(self, n):
        for s in self.chain(n):
            if self.cls.get(s) == "WhileLoop":
                return LOOPNAME.get(s, "while#%d" % s)
        return "outside-while"

    def label(self, n):
        if n in self.subvi:
            return self.subvi[n]
        if self.ncls(n) == "ControlTerminal" or (n in self.term and self.term[n]["term_class"] == "ControlTerminal"):
            return self.term[n]["term_name"]
        return self.ncls(n)

    def is_motor(self, n):
        return any(k in self.subvi.get(n, "") for k in MOTOR)

    def through_down(self, t):
        """sink terminal t of a carrier -> source terminals to continue from ([] = not a carrier)."""
        n, c = self.node(t), self.ncls(self.node(t))
        if c in TUN:
            return [x for x in self.by_owner[n] if x["is_source"]]
        if c in SR:
            nxt = [x for x in self.by_owner[n] if x["is_source"]]
            for p in self.pair.get(n, []):
                nxt += [x for x in self.by_owner[p] if x["is_source"]]
            return nxt
        if t["owner_class"] in FS and t["term_uid"] in self.fs:
            o = self.term.get(self.fs[t["term_uid"]])
            return [o] if o and o["is_source"] else []
        if t["term_class"] == "ControlTerminal" and not t["is_source"]:
            return [x for x in self.locals.get(t["term_name"], []) if x["is_source"]]
        return []

    def through_up(self, t):
        """source terminal t of a carrier -> sink terminals to continue from."""
        n, c = self.node(t), self.ncls(self.node(t))
        if c in TUN:
            return [x for x in self.by_owner[n] if not x["is_source"]]
        if c in SR:
            nxt = [x for x in self.by_owner[n] if not x["is_source"]]
            for p in self.pair.get(n, []):
                nxt += [x for x in self.by_owner[p] if not x["is_source"]]
            return nxt
        if t["owner_class"] in FS and t["term_uid"] in self.fs:
            o = self.term.get(self.fs[t["term_uid"]])
            return [o] if o and not o["is_source"] else []
        if c == "Local":
            fp = [x for x in self.terms if x["term_class"] == "ControlTerminal" and x["term_name"] == t["term_name"]]
            return [x for x in fp if not x["is_source"]] or []
        return []

    def walk(self, start, down, stop):
        """first non-carrier ends from terminal `start`; `stop(node)` True = end there (e.g. group-B member).
        Returns [(end terminal, [carrier node uids])]; an unwired start yields [(None, [])]."""
        out, seen, q = [], set(), collections.deque([(start, [])])
        while q:
            t, path = q.popleft()
            w = t["wire_uid"]
            ends = [x for x in self.by_wire.get(w, []) if x["is_source"] != down] if w else []
            if not ends and not path:
                out.append((None, [])); continue
            for e in ends:
                if e["term_uid"] in seen:
                    continue
                seen.add(e["term_uid"])
                n = self.node(e)
                nxt = [] if stop(n) else (self.through_down(e) if down else self.through_up(e))
                if nxt:
                    for x in nxt:
                        q.append((x, path + [n]))
                else:
                    out.append((e, path))
        return out
