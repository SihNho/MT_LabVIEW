# Failed prediction: a ControlTerminal's connected wire could not be read by uid

LabVIEW 2026, VI Scripting over ActiveX/COM from Python. Read-only research question. No VI is attached.

## The prediction that failed

`tools/bench/diag_c62_branch.py` gate **A_4**: *"a wire uid was obtained for BOTH ControlTerminals
#23541 and #23576"*. Observed: **None for both**, by both routes it tried
(`tools/bench/diag_c62_branch.log:81-90`).

## What was measured, verbatim

- `owner_of(#23541)` -> `owner 'Diagram' uid 639 | self 'ControlTerminal'#23541`. Same for `#23576`.
  So both uids EXIST and both are owned by block diagram `#639`.
- `report_all(target,'ControlTerminal')` lists them: `{'i': 70, 'class': 'ControlTerminal', 'uid': 23541,
  'pos': (2759, 4933), 'owner': 'Diagram'}` and `{'i': 71, ..., 'uid': 23576, 'pos': (2759, 5133)}`.
  Census 116 (114 before the two indicators this VI's stage S3a created).
- `node_labels(target, diagram_index=46)` (= `Diagram.Nodes[]` -> `Node.Label` -> `Text.Text`) lists **73
  nodes on `Diagram #639` and NONE of them echoes uid 23541 or 23576.** `#10407` (a CaseStructure),
  `#10686` (a Function, 'And') and `#10757` (an IndexArray) on the same diagram ARE in that list, at
  Nodes[] 24, 25 and 27, and `node_terms` read their full terminal tables with connected-wire uids.
- `panel_wiring(target)` (= `Panel.Controls[]` -> `Control.Terminal` -> `Terminal.Connected Wire`) returns
  116 rows. Its last two rows are
  `{'label': 'index', 'indicator': True, 'uid': 23525, 'is_source': False, 'wire': 10990}` and
  `{'label': 'Automatic Error Handling', 'indicator': True, 'uid': 23555, 'is_source': False,
  'wire': 10799}` — note the uids **23525 / 23555**, which are NOT 23541 / 23576.

## The explanation formed after the fact (attack this)

*A `ControlTerminal` is a GObject owned by the diagram but is NOT a member of `Diagram.Nodes[]`, so no
verb that addresses objects through `Diagram.Nodes[]` (`node_labels`, `node_terms`) can reach one.
`panel_wiring` reaches the same wiring from the PANEL side, but it reports the CONTROL's uid (23525 /
23555), not the ControlTerminal's (23541 / 23576), and this toolkit has no verb that maps one to the
other — `ControlTerminal.Control` (property id 6353000) is recorded as UNVERIFIED in our own notes
(`docs/d1-build-plan.md:866` and `:909`). Therefore "the wire on ControlTerminal #23541" is not readable
by that uid with the verbs that exist here, and the prediction was written in terms of an addressing
route that does not exist.*

## Already ruled out (do not propose these)

- Not a stale uid: `owner_of` resolved both uids on the same open VI seconds earlier and echoed the class
  `ControlTerminal`.
- Not a loading/silent-decline problem: every other read on the same open VI in the same run succeeded
  (`#10407`, `#10686`, `#10757` full terminal tables; 116 panel rows; a wire delete that returned the exact
  uid it targeted).
- Not a bounded-scan truncation: the scan cap was not reached — the diagram has 73 nodes and all 73 were
  enumerated (`diag_c62_branch.log:100,:104`).

## What I am asking you for

1. The strongest reason the explanation above is WRONG.
2. An alternative explanation for the same observations.
3. What observation would falsify the explanation.
4. The CHEAPEST discriminating test, expressed as a LabVIEW VI Server call sequence (class / property or
   method id / short name), that would either (a) read a `ControlTerminal`'s connected wire addressed by
   the ControlTerminal's own uid, or (b) map a `ControlTerminal` uid to the `Control` uid `panel_wiring`
   reports, or (c) show that neither is possible over this interface.

State explicitly where LabVIEW's own documentation says which container a block-diagram terminal of a
front-panel control belongs to (`Diagram.Nodes[]`, `Diagram.GObjects[]`, or something else), with the
source.
