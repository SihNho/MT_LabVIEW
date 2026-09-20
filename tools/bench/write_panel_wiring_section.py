"""write_panel_wiring_section.py - append/replace the measured WIRING section of docs/main-vi-panel-map.md from
tools/bench/main_vi_panel_wiring.json (written by test_oppanelwiring.py T3; no LabVIEW here).

The section is delimited by marker comments so it can be regenerated. Column semantics are stated in the section
itself: "terminal wired" is a read of Control.Terminal -> Terminal.Connected Wire; NO means the object's diagram
terminal has no wire - the object may still be read/written through a local variable or a Value property node,
which this measurement does not see (the main VI has 106 property nodes). So NO = "not used via its terminal",
never "unused" - that stronger claim needs the property-node / local census.
  py tools/bench/write_panel_wiring_section.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, "main_vi_panel_wiring.json")
DOC = os.path.join(ROOT, "docs", "main-vi-panel-map.md")
BEGIN, END = "<!-- wiring-section:begin -->", "<!-- wiring-section:end -->"


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    rows = d["rows"]
    orphans = [r for r in rows if not r["wire"]]
    lines = [BEGIN, "",
             "## Wiring column — measured 2026-09-14 with `OpPanelWiring_v0` (`Control.Terminal` → `Terminal.Connected Wire`)",
             "",
             f"Source `tools/bench/main_vi_panel_wiring.json` ({len(rows)} rows, one op run, `test_oppanelwiring.py` T3). "
             "**Semantics:** *terminal wired = YES* means the object's block-diagram terminal carries a wire; *NO* means the "
             "terminal is bare. A bare terminal does **not** prove the object is unused — the main VI reads and writes "
             "objects through local variables and `Value` property nodes (106 property nodes), which this read does not "
             "see. So NO = \"not used via its terminal\"; \"unused\" needs the property-node/local census (next pass). "
             "`Is Source?` agreed with CTL/IND on every row (controls' terminals are sources, indicators' are sinks).",
             "",
             f"**{len(orphans)} objects have a bare terminal:**", ""]
    for r in orphans:
        lines.append(f"- {'IND' if r['indicator'] else 'CTL'} `{r['label']!r}` (uid {r['uid']})")
    lines += ["", "| # | label | type | terminal wired | wire uid | control uid |", "|---:|---|---|---|---:|---:|"]
    for i, r in enumerate(rows):
        lab = r["label"].replace("\n", "\\n").replace("|", "\\|")
        lines.append(f"| {i} | `{lab}` | {'IND' if r['indicator'] else 'CTL'} | {'YES' if r['wire'] else '**NO**'} | "
                     f"{r['wire'] or ''} | {r['uid']} |")
    lines += ["", f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/bench/write_panel_wiring_section.py._", "", END]
    block = "\n".join(lines)
    text = open(DOC, encoding="utf-8").read()
    if BEGIN in text and END in text:
        pre, rest = text.split(BEGIN, 1)
        _old, post = rest.split(END, 1)
        text = pre + block + post
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    open(DOC, "w", encoding="utf-8").write(text)
    print(f"wrote wiring section: {len(rows)} rows, {len(orphans)} bare terminals -> {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
