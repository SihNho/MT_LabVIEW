LabVIEW VI Scripting (LabVIEW 2020+), API facts only, with primary-source citations (ni.com docs, labviewwiki class pages,
NI forum posts by NI staff):

1. A Case Structure data tunnel (classes Tunnel / ConditionalTunnel / SelectorTunnel): which property returns its INNER terminal(s),
   one per frame? Is it `Tunnel.Inside Terminals[]` (id 6356000)? Is the array order documented as the order of
   `MultiFrameStructure.Frames[]`? Does `Terminal.Diagram` (634A002) return the frame's Diagram?
2. Is a Tunnel object listed in a frame Diagram's `Nodes[]`, or in the structure's `Terminals[]`? (Is `Tunnel` a subclass of
   `Node`? What is the class hierarchy of Tunnel?)
3. To wire two terminals on one frame diagram (e.g. the input tunnel's inner terminal in frame 1 to the output tunnel's inner
   terminal in frame 1): is `Terminal.Connect Wire` (method 6349C03) with input `Wire Source` = the other Terminal the documented
   route? Any restriction when both terminals belong to tunnels of the same structure?
4. Does vi.lib `VIServer\UID to GObject Reference.vi` resolve a Terminal's UID (a Terminal is a GObject), and does it return an
   error or a stale object for an unallocated UID?
5. Is there a documented way to set a case tunnel to "Use Default if Unwired" / to read the selector tunnel's inner terminal?
Answer each numbered item separately; say "no primary source found" where that is the case.
