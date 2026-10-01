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
