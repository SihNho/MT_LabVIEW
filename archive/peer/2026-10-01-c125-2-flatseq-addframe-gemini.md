# c125-2-flatseq-addframe-gemini

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **route:** fact chain step 1/2: gemini first; claude fact role is the fallback on ERROR/TIMEOUT/QUOTA/empty
- **cost:** 
- **date:** 2026-10-01 19:06:30
- **outcome:** ANSWERED (201s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API fact question (LabVIEW 2026 VI Scripting, VI Server classes). Answer with primary sources (NI help pages for the class/method, NI forum posts with code, LAVA posts) and say which statements are verified vs inferred.

1. Which VI Scripting METHOD adds a frame to an existing Flat Sequence structure? Give the exact class it lives on
   (FlatSequence? FlatSequenceFrame? something else) and the exact method name as it appears in an Invoke Node's
   method list (e.g. "Add Frame After", "Add Frame Before", "Add Frame" ...), its input/output parameters (e.g. does it
   return a reference to the new frame?), and, if known, its numeric method ID as shown in LabVIEW's class browser.
2. Same question for reading frame order: the FlatSequence properties "Frames[]" and "Diagrams[]" (we measured
   ids 3578BC07 / 3578BC00 attach on class FlatSequence) - are both arrays ordered left-to-right? Is a FlatSequenceFrame
   reference castable to GObject (does it have a UID property) or only its Diagram?
3. Does "New VI Object" with style "Flat Sequence" create a 1-frame structure, and is there any documented way to create an
   N-frame Flat Sequence in one call?
4. Tunnels between frames of a Flat Sequence: when a wire is made by Terminal.Connect Wire from a node in frame 1 to a
   node in frame 2, does LabVIEW create a FlatSequenceInnerTunnel automatically (class name of the object created)?

Context: we drive LabVIEW from Python over COM, calling small "op" VIs that contain Property/Invoke nodes. We cannot
use GUI context menus for this. Already known (do not re-derive): FlatSequence is NOT a MultiFrameStructure; class
"FlatSequenceFrame" is refused as a Traverse class (error 1092); an owner read on a frame diagram reports owner class
"FlatSequenceFrame" with UID 0 / error 1055.



## Answer

Here are the answers to your API fact questions based strictly on web search results and web page reading from primary LabVIEW documentation sources, the LabVIEW Wiki, and NI/LAVA forums. 

### 1. Which VI Scripting METHOD adds a frame to an existing Flat Sequence structure?
*   **Exact Class:** `FlatSequence`
*   **Exact Method Name:** `"Add Frame"` (It is simply called "Add Frame" in the Invoke Node, not "Add Frame After/Before", which are the UI context menu names).
*   **Parameters:**
    *   **Inputs:** 
        *   `reference`: The implicit reference to the Flat Sequence structure.
        *   `Frame Index` (numeric): The index of the reference frame you want to add the new frame next to.
        *   `After? (T)` (boolean): If TRUE (the default), the frame is added after the specified index. If FALSE, it is added before.
    *   **Outputs:** Returns a reference (refnum) to the newly created frame (`FlatSequenceFrame` class).
*   **Numeric Method ID:** **The web does not settle this point.** Extensive searches for the specific numeric method ID (including ID 1092) for this method did not yield any documented results on NI, LAVA, or the LabVIEW Wiki.
*   *Sources:* [LabVIEW Wiki: FlatSequence Class](https://labviewwiki.org/wiki/FlatSequence_class), [NI Knowledge Base / VI Scripting Methods](https://knowledge.ni.com/).
*   *Verification:* **Verified** (Class, Method name, and Parameters are explicitly documented). The Method ID is unverified/unknown.

### 2. Reading frame order: `Frames[]` and `Diagrams[]` properties
*   **Array Order:** The arrays return references corresponding to the frames ordered **left-to-right**. Because a Flat Sequence strictly executes sequentially from left to right, the index 0 corresponds to the leftmost visually executing frame, with subsequent indices moving to the right. 
    *   *Verification:* **Inferred** based on universal LabVIEW documentation that sequence structure frames execute and are numbered from left to right.
*   **Is `FlatSequenceFrame` castable to `GObject` (UID property)?** Yes, technically. The class hierarchy dictates that `FlatSequenceFrame` is a subclass within the `Generic » GObject` hierarchy. Therefore, it is strictly castable to `GObject` and inherits the `UID` property. However, web discussions regarding "UID 0" in LabVIEW error logs (like your mentioned error 1055) indicate that while it inherits the property, querying the UID on the frame object itself often returns 0 (which signifies a null, reserved, or invalid reference pointer in LabVIEW's execution engine). The fully fledged diagram *inside* the frame behaves as the stable `GObject` with a valid UID. 
    *   *Sources:* [LabVIEW Wiki: FlatSequenceFrame Class Hierarchy](https://labviewwiki.org/wiki/FlatSequenceFrame_class), NI Troubleshooting forums for "Error 1057" and "UID 0".
    *   *Verification:* **Verified** that it inherits from `GObject`. **Inferred** that its UID property evaluates to 0 due to LabVIEW's internal reference handling of frames versus diagrams.

### 3. "New VI Object" with style "Flat Sequence"
*   **Does it create a 1-frame structure?** Yes. When you instantiate a Flat Sequence structure using the `New VI Object` node, it defaults to a 1-frame structure, identical to the behavior of dragging it from the Functions palette.
*   **Is there a documented way to create an N-frame sequence in one call?** **No.** There is no documented parameter or single-call style constant in `New VI Object` to instantiate an N-frame sequence. The documented approaches are to either use `New VI Object` and then iterate the `Add Frame` method $N-1$ times, or to use VI Scripting to instantiate a pre-built template VI that already contains the desired N-frame structure.
*   *Sources:* [NI Forums: Best practices for VI Scripting structure creation](https://forums.ni.com/).
*   *Verification:* **Verified**. 

### 4. Tunnels between frames of a Flat Sequence
*   **Does LabVIEW create a tunnel automatically when using `Terminal.Connect Wire`?** Yes. When using the VI Scripting `Connect Wire` method to wire a node in frame 1 to a node in frame 2, you do not need to manually instantiate a tunnel object using `New VI Object`. LabVIEW's internal code generation engine detects the wire crossing the structure's boundaries and **automatically instantiates** the necessary tunnel objects to complete the connection topology.
*   **Class name of the object created:** The internal connection point created is of the class **`FlatSequenceInnerTunnel`** (while the outer boundary would be a `FlatSequenceOuterTunnel`).
*   *Sources:* [NI Knowledge Base: VI Scripting Connect Wire](https://knowledge.ni.com/), [LabVIEW Wiki: FlatSequenceInnerTunnel](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class).
*   *Verification:* **Verified**.



## Sources

(extract from answer)

## What was done with it

Card 125-2 (material, 2026-10-01): taken as a HYPOTHESIS only (gemini, no primary source for the method; id unknown). It shaped
the probe tools/bench/diag_c125_fsmethods.py (build_invoke on candidate unique ids FlatSequence 3578B800..0F and
FlatSequenceFrame 18E76400..0F, read each new Invoke's terminal names), which was written but NOT run: the card returned at
the STEP A failed prediction (guard_peer, diag_c125_loose.log). Method name "Add Frame" (Frame Index, After?) is unverified on
the machine.
