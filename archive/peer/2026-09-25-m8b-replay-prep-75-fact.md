# m8b-replay-prep-75-fact

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $3.4414  in 322 / out 16740 / cache-create 68126 / cache-read 578684  (277s, 78 turn(s))
- **date:** 2026-09-25 03:00:01
- **outcome:** ANSWERED (278s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API FACT QUESTIONS (LabVIEW 2026 VI Scripting / NI Vision Acquisition). Answer each with source URLs; say "not found" where you cannot find a source.

Q1. LabVIEW VI Server class "SubVI" has a scripting method "Replace" (labviewwiki.org/wiki/SubVI_class/Replace_method, method id 635E001?). What are its exact inputs (VI Path? VI Reference? other options), is it public or private (needs SuperSecretPrivateSpecialStuff?), and does it keep the node's existing wires connected when the new VI has the same connector pane pattern and terminal assignments? What happens to wires on terminals whose position differs?

Q2. Is there another scripting route to swap the VI a subVI node calls while keeping wires: e.g. GObject/Node "Replace" method (with a class name / VI path), "Replace With" style option, or "Relink To SubVI"? Give method names and ids if documented.

Q3. NI-IMAQdx "IMAQdx Get Image.vi" (vi.lib\vision\driver\IMAQdx.llb): is it a POLYMORPHIC VI? If yes, list its instances and each instance's VI file name; which instance has terminals Session In, Image In, Buffer Number Mode, Buffer Number In, error in -> Session Out, Image Out, Buffer Number Out, error out? Give each terminal's data type (IMAQdx session refnum, IMAQ Image refnum, enum type/values, U32, error cluster).

Q4. For a subVI node whose callee is a polymorphic VI's instance, what VI path does VI Scripting's SubVI node report (the polymorphic VI or the instance), and does SubVI.Replace on such a node work with a non-polymorphic replacement VI?


## Answer

**Q1. SubVI class "Replace" (ID 635E001)**

- **Inputs:** one required input, `VI Path` (Path). No return value. Source: https://labviewwiki.org/wiki/SubVI_class/Replace_method
- **Scope:** listed as **Private** on the wiki, so it is not exposed in the normal VI Scripting palette and needs the private-methods INI switch (SuperSecretPrivateSpecialStuff). The wiki does not spell out the INI key on this page. Same source.
- **Wire behavior:** **not found.** The wiki page has no description of how wires are handled, and the forum thread that used it (https://forums.ni.com/t5/LabVIEW/How-to-use-SubVI-replace-invoke-node-in-VI-scripting/td-p/3716153) only reports that the replacement worked and that the caller must be saved afterward. Nothing documented states what happens to wires on terminals whose position differs.
- Closest documented rule is for the interactive Replace command: "If the number of terminals or data types in the objects are different, you might have broken wires." https://www.ni.com/docs/en-US/bundle/labview/page/replacing-block-diagram-objects.html. Whether the private scripting method follows the same rule is not documented.

**Q2. Other scripting routes**

- **GObject.Replace (ID 632A402), public VI Scripting.** Inputs: `Style` (U32, built-in object), `Path` (Path, "Replaces the current object with a control or a subVI"), `Palette String` (String). Use exactly one. Returns a GObject refnum to the new object. Sources: https://labviewwiki.org/wiki/GObject_class/Replace_method and https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/replace.html. Wire preservation is not stated in either.
- **GObject.Replace No Attributes (ID 632A403)**, same inputs, does not keep size/color attributes. **Replace Preferring Stub DDO OnFP (ID 632A406)**, undocumented. Source: https://labviewwiki.org/wiki/GObject_class
- **SubVI.Relink To VI (ID 635E000), public VI Scripting.** No inputs beyond the refnum. "LabVIEW uses the new connector pane pattern and attempts to reconnect any existing wires to the new pattern." It relinks to the same VI, it does not swap to a different VI. Sources: https://labviewwiki.org/wiki/SubVI_class/Relink_To_VI_method and https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/subvi/relinktovi.html
- **SubVI.Swap Instance VI (ID 635E004), private**, input `Name` (String). No description. Source: https://labviewwiki.org/wiki/SubVI_class/Swap_Instance_VI_method
- A "Replace With" scripting method: **not found.** Only the interactive Find/Replace UI offers "Replace with" (https://forums.ni.com/t5/LabVIEW/Is-there-a-way-to-search-and-replace-a-subvi-in-multiple-VIs/td-p/1599046).

**Q3. IMAQdx Get Image.vi**

- **Not polymorphic** as far as the documentation shows. The NI reference pages for both IMAQdx Get Image and IMAQdx Get Image2 describe a single VI with a fixed terminal list and never mention polymorphism or instances. Sources: https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_get_image.html and https://www.ni.com/docs/en-US/bundle/ni-imaqdx-vi-ref/page/ni-imaqdx_vi_reference/imaqdx_get_image2.html. I could not find a file listing of IMAQdx.llb online, so "no polymorphic instances" is inferred from the docs, not confirmed against the LLB.
- **The terminal set you list matches IMAQdx Get Image.vi** (the legacy VI). IMAQdx Get Image2.vi has the same terminals plus `Timeout (ms)` (I32, default 5000, -1 infinite, -2 use Timeout attribute). Get Image2 was added in Feb 2015 and the old VI is kept for compatibility, both in `vi.lib\vision\driver\IMAQdx.llb`: https://forums.ni.com/t5/Machine-Vision/IMAQdx-Get-Image2-vi-Issues/td-p/3329711
- **Terminals:**

| Terminal | Type |
|---|---|
| Session In / Session Out | IMAQdx session refnum (from IMAQdx Open Camera) |
| Image In / Image Out | IMAQ Image refnum |
| Buffer Number Mode | Enum: Next (default), Last, Buffer Number, Every, Last New |
| Buffer Number In / Buffer Number Out | U32 |
| error in / error out | Error cluster (status, code, source) |

Enum values are quoted from the NI page above. The public C header only lists Next, Last, BufferNumber (plus a guard), so Every and Last New are newer than that header: https://github.com/wpilibsuite/nivision/blob/master/cpp/include/Vision/NIIMAQdx.h. Last vs Last New semantics: https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US

**Q4. SubVI node calling a polymorphic instance**

- A node that calls a polymorphic VI is a **PolymorphicSubVI** (class 16443, child of SubVI). It has `Polymorphic VI` (7DBC6404, returns a reference to the polymorphic VI), `Selected Type` (7DBC6400, "Specifies the polymorphic VI instance to select. Writing to this property removes automatic selection"), `Selector`, `Selector Visible`, `Automatic`. Sources: https://labviewwiki.org/wiki/PolymorphicSubVI_class and https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/subvi/polymorphicsubvi/polyvi.html
- **What VI Path returns (polymorphic VI or instance): not found.** The VI Path property page says only "Path to the subVI file" (https://labviewwiki.org/wiki/SubVI_class/VI_Path_property). The existence of a separate `Polymorphic VI` property suggests the base properties point at the instance, but no source states this. For malleable VIs, one forum states VI Path returns "an internal '.vi' path made by LabVIEW, containing the name of the host VI and a GUID": https://forums.ni.com/t5/LabVIEW/Scripting-Help-with-Automated-VIM-Replacement/td-p/4362243. That is a VIM, not a polymorphic VI.
- **SubVI.Replace on a polymorphic node with a non-polymorphic VI: not found.** No documentation or forum report covers this. Since Q3 indicates IMAQdx Get Image.vi is not polymorphic, this case may not arise for that VI.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
