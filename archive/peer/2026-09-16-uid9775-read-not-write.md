# uid9775-read-not-write

- **agent:** gemini
- **model:** (agy default, not readable) (agy built-in default)
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** TIMEOUT (180s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting semantics. Attack this reading before it goes into a plan.

CLAIM: an IMAQdx Property Node (uid 9775) on a LabVIEW 2026 startup diagram READS the camera Height/Width; it does NOT write them.

MEASUREMENT. A scripting VI takes a WIRE UID, gets the Wire reference, walks Wire.Terms[] and per terminal reads Terminal 'Is Source?' (634A003), 'Connected Wire' (634A000) and Generic.Owner -> class name + UID. Observed:
  wire 32937 Terms[0] IsSource=True  owner class 'Property' uid 9775  reciprocal wire 32937
  wire 32937 Terms[1] IsSource=False owner class 'Diagram'  uid 13236 reciprocal wire 32937
  wire 32937 Terms[2] -> error 1055 (past end of Terms[])
  wire 32938 identical (source Property 9775, sink Diagram 13236)
An earlier dump established node uid 9775 has terminals ['IMAQdx Session','IMAQdx Session','error in','error out','Height','Width'], Height wired to 32937 and Width to 32938.

MY INFERENCE: IsSource=True on the node's own terminal means it DRIVES the wire, so that terminal is an OUTPUT, so the node is in READ mode for both properties. The far end owned by a 'Diagram' rather than a node suggests a front-panel indicator terminal.

WHY IT MATTERS: the instrument's owner said from memory that a CONSTANT is fed INTO this property node, i.e. a WRITE that sets the camera ROI. My measurement says the opposite, and I am about to write 'the VI does not set the frame size' into a build plan.

ANSWER THESE:
1. Is Terminal 'Is Source?' TRUE unambiguous evidence the terminal is an OUTPUT? Any case where a Property Node in WRITE mode reports IsSource TRUE on the written terminal?
2. Can one Property Node mix read and write terminals, and does that change Terms[] ordering or Is Source? behaviour?
3. Is Generic.Owner returning class 'Diagram' a reliable signature of a front-panel control/indicator terminal, or could it be a constant, tunnel or shift register?
4. Cheapest INDEPENDENT discriminating test, given I can read arbitrary VI Server properties by UID and must not open the editor?
5. Strongest reason my inference is wrong.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

(no answer within 180s — job stopped)

## Sources

(extract from answer)

## What was done with it

**NON-RESULT — this exchange told us nothing.** The gemini dispatch hit `OUTCOME: TIMEOUT (180 s)`
(`tools/bench/peer_uid9775.log`), which CLAUDE.md classifies as a call that told you nothing rather than as a
review. Recorded so the file is not mistaken for a completed review, and so the ladder step is visible.

The same question was re-dispatched one rung down, to codex with `-TimeoutSec 480`, and answered there:
`archive/peer/2026-09-16-uid9775-read-not-write-codex.md` (annotated). Its verdict confirmed the narrow claim —
uid 9775 READS the camera geometry — and refused the wide one, which is what stopped "the VI does not set the frame
size" from entering the master plan.

**Operational note worth keeping:** this question needed more than 180 s. When a peer question carries a block of
measured evidence to attack, dispatch it with `-TimeoutSec 480` from the start rather than paying for a timeout
first.
