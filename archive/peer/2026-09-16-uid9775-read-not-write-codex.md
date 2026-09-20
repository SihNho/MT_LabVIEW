# uid9775-read-not-write-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (103s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting. Answer compactly; a gemini attempt timed out at 180s.

CLAIM TO ATTACK: an IMAQdx Property Node (uid 9775) on a LabVIEW startup diagram READS camera Height/Width; it does NOT write them.

MEASURED (tools/bench/diag_9775_direction.log, this project): a scripting VI takes a WIRE UID, walks Wire.Terms[] and per terminal reads Terminal 'Is Source?' (634A003), 'Connected Wire' (634A000), Generic.Owner -> class + UID:
  wire 32937 Terms[0] IsSource=True  owner 'Property' uid 9775   reciprocal 32937
  wire 32937 Terms[1] IsSource=False owner 'Diagram'  uid 13236  reciprocal 32937
  wire 32937 Terms[2] -> error 1055 (past end)
  wire 32938 identical.
Node uid 9775 terminals: ['IMAQdx Session','IMAQdx Session','error in','error out','Height','Width']; Height->32937, Width->32938.

MY INFERENCE: IsSource TRUE on the node's own terminal = that terminal DRIVES the wire = an OUTPUT = the property is being READ. Far end owned by a 'Diagram' = a front-panel terminal.

WHY IT MATTERS: the rig's owner said from memory that a CONSTANT is fed INTO this node (a WRITE setting the camera ROI). My measurement says the opposite and is about to go into a build plan as 'the VI does not set the frame size'.

ALREADY RULED OUT: position-proximity around uid 9775 (invalid - this diagram was Clean Up'd, positions carry no meaning); the Nodes[] net walk (front-panel terminals and constants are not Nodes, so it saw only one terminal per net).

ANSWER:
1. Is Terminal 'Is Source?' TRUE unambiguous evidence of an OUTPUT terminal? Any case where a Property Node in WRITE mode reports IsSource TRUE on the written terminal?
2. Can one Property Node mix read and write terminals; does that change Terms[] order or Is Source?
3. Is Generic.Owner = 'Diagram' a reliable signature of a front-panel control/indicator terminal, or could it be a constant, tunnel or shift register?
4. Cheapest INDEPENDENT discriminating test by VI Server property read (I can read any property by UID, must not open the editor)?
5. Strongest reason my inference is wrong.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The attack succeeds only against the build-plan conclusion, not against the direction of node 9775.

1. `Is Source? = TRUE` means that terminal is an output/source. NI explicitly recommends this property to distinguish node inputs from outputs. A write-property?셲 value terminal is necessarily an input, so it should report `FALSE`; I found no documented exception where the written-value terminal reports `TRUE`. [NI employee guidance](https://forums.ni.com/t5/LabVIEW/How-to-create-fixed-point-number-using-LabVIEW-VI-scripting/m-p/2838374/highlight/true)

2. One Property Node can mix reads and writes. Direction is per property item; mixing does not reverse `Is Source?`. The conventional terminal sequence remains ref-in, ref-out, error-in, error-out, then property-item terminals, but use `Property Items[].Terminal` rather than depending on array order. [NI documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kF58SAE&l=en-US), [terminal-order example](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

3. `Owner = Diagram` is characteristic of a `ControlTerminal`: unlike ordinary node terminals, ControlTerminals are directly owned by their diagram. Owner alone is not formal type proof; also read the terminal?셲 runtime class. If it is `ControlTerminal`, it is a front-panel control/indicator terminal?봭ot a constant, tunnel, or shift register. [NI discussion and explanation](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)

4. The observation that falsifies your claim is: the `Height` or `Width` `PropertyItem.Is Write` value is `TRUE`, or its `PropertyItem.Terminal` is not the terminal attached to wire 32937/32938. `Is Write = TRUE` specifically means a write item; `FALSE` means read.

5. Strongest alternative explanation: node 9775 reads Height/Width exactly as measured, but some other node?봯ossibly elsewhere in startup or a called VI?봶rites ROI dimensions. Therefore, ?쐕id 9775 does not set frame size??is supported; ?쐔he VI does not set frame size??is not established by this evidence.

I still believe the narrow claim holds. What would change my mind is `PropertyItem.Is Write = TRUE`.

Cheapest discriminating test: resolve uid 9775 ??read `Property Items[]` ??for the Height and Width items read only `Property`, `Is Write`, and `Terminal` UID. No editor opening, wire traversal, or position inference. [NI scripting solution showing individual property-item references](https://forums.ni.com/t5/LabVIEW/LabVIEW-VI-scripting-property-change-to-Write/m-p/3943545/highlight/true)

## Sources

(extract from answer)

## What was done with it

**Accepted, and it changed what got written — this review stopped a wrong sentence from entering the master plan.**

The reviewer's split is the whole value of the exchange: points 1–3 **confirm** the narrow reading (`Is Source? =
TRUE` is NI's own recommended way to tell an output terminal from an input; mixing read and write items on one
Property Node does not reverse it; `Owner = Diagram` is characteristic of a `ControlTerminal`), while point 5
**refutes the conclusion I was about to draw from it**: *"'uid 9775 does not set frame size' is supported; 'the VI
does not set frame size' is not established by this evidence."* The plan sentence was going to be the second one.

Confirmed within the hour, and the reviewer was right in a stronger way than it knew — **the VI does write a size.**
The rig's owner then said from memory: *"프로퍼티 노드로 아마 카메라 프레임 읽어오기 → 이후 프로퍼티 노드로
IMAQ 화면 사이즈 셋팅하는 걸로 기억함."* Both halves check out, from dumps already on disk and with no LabVIEW run:
diagram 97 reads the panel `Height`/`Width` back (uids 30445 / 30471), bundles them, **divides by the constant 2**
(uid 27664) and writes the result into **`Image Area Size`** (uid 30118) and **`Draw Area Size`** (uid 30422). So
the size the VI sets is the **front-panel image display's**, not the camera's ROI — which is exactly why it never
appeared in any ROI test. Written up in `docs/camera-acquisition-facts.md`, "MEASURED 2026-09-16 — uid 9775 READS
the geometry…".

Point 4's cheaper test (`PropertyItem.Is Write` per item, no wire walking) is **adopted as the route for the
VI-wide question** that remains open — is there any node that writes the camera ROI? — instead of the wire walk
used here. Recorded in the plan's Phase A9 rather than run now.

Process note for the ladder: a gemini dispatch of the same question **timed out at 180 s** and told us nothing
(`tools/bench/peer_uid9775.log`), so this was the next rung down, with `-TimeoutSec 480`. Worth remembering that
this question needed the longer budget.
