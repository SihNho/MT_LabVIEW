API-fact question (LabVIEW 2026 VI Scripting, Windows). Answer from NI documentation, NI forums, LAVA, or GitHub code; give URLs. Say plainly where no source was found.

Q1. Can `New VI Object` (VI Scripting function, or the `AbstractDiagram.New VI Object`-equivalent) create these built-in primitives directly on a given nested subdiagram (a While Loop's body): `Not Equal?`, `And`, `Select`, `Wait (ms)`? For each: which `vi object class` (e.g. `Function`, `Comparison`) and which `style` value / style name must be passed, and is the numeric style ID stable across LabVIEW versions? Is there a published list of `New VI Object` style IDs for comparison/boolean/timing primitives (e.g. the LAVA "New VI Object style list" thread)?

Q2. For a Comparison node created as `Equal?`, can its comparison function be switched to `Not Equal?` afterwards through a scripting property (e.g. `Comparison.Comparison Mode` / `Operation`), and what is the property's exact name?

Q3. A While Loop's iteration terminal `i`: in VI Scripting, which class and which property of the loop returns a reference to it (e.g. `Loop.Iteration Terminal`, `WhileLoop.Loop Count Terminal`)? Given such a Terminal reference, does the `Terminal.Create Indicator` invoke method (6349C02) create a front-panel indicator wired to it even though the terminal sits on a nested diagram (not the top-level block diagram)?

Q4. Given a GObject UID (e.g. from `GObject.UID`), `vi.lib\VIServer\UID to GObject Reference.vi` returns a generic reference; is casting it with `To More Specific Class` to `Terminal` and calling `Create Indicator` a documented or forum-reported working route?
