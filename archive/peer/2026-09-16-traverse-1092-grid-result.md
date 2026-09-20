# traverse-1092-grid-result

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (139s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this conclusion. Failure record: tools/bench/diag_autofocus_panel.log, produced by tools/bench/diag_autofocus_panel.py (LabVIEW 2026, VI Scripting through ActiveX/COM).

THE FAILED PREDICTION. I predicted a traverse-based reporter would return a large VI's property nodes; it raised error 1092 inside 'VI Scripting - Traverse.lvlib:Traverse for GObjects.vi'.

THE DISCRIMINATING TEST I THEN RAN, 2x2, both class names on both a large VI and a small one:
  count(MAIN,       'PropertyNode') -> FAIL error 1092
  report_all(MAIN,  'PropertyNode') -> FAIL error 1092
  count(MAIN,       'Property')     -> OK, 106
  report_all(MAIN,  'Property')     -> OK, 106
  count(small VI,   'PropertyNode') -> FAIL error 1092
  report_all(small, 'PropertyNode') -> FAIL error 1092
  count(small VI,   'Property')     -> OK, 12
  report_all(small, 'Property')     -> OK, 12

MY CONCLUSION, which I want refuted: the failure follows the CLASS-NAME STRING and not the VI; 'Property' is the legal traverse class name for a property node in LabVIEW 2026 and 'PropertyNode' is not; therefore every place our tooling passes 'PropertyNode' to a traverse is a latent bug that will raise 1092 the moment it runs, including a build recipe we are about to execute that counts and deletes objects of that class.

WHAT WOULD MAKE ME WRONG, and please look for it: (1) is 'PropertyNode' legal in some OTHER scripting context - Traverse for GObjects' own class ring, a 'Traverse Target' setting, a different traverse VI, or the New VI Object class list - so that our usage is merely in the wrong place rather than a wrong name? (2) is 'Property' actually a SUPERCLASS that also matches other node kinds, so that a count of 106 is not 106 property nodes and my replacement would silently over-select? (3) what does error 1092 actually mean, cited to NI's own documentation rather than inferred? (4) is there a way to enumerate the legal class strings from LabVIEW itself, so this is never guessed again?

Also still open from the same run: for an IMPLICIT property node (its 'reference' terminal unwired), is there a scripting property that names the front-panel object it is linked to, and on which class does it live? If there is none in LabVIEW 2026, say so plainly.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest attempted refutation is that your conclusion overreaches across scripting APIs: a New VI Object *style*, a node?셲 `Style` value, and Traverse?셲 `Class Name` are different namespaces. Thus an occurrence of `PropertyNode` is not automatically defective merely because Traverse rejects it. NI defines Traverse?셲 input specifically as a **VI Server class name**, while New VI Object separately accepts a class and a style. [NI: Traverse for GObjects](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html), [NI: New VI Object style usage](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000CWCD0A4&l=en-US)

That refutes only the universal wording, however?봭ot your narrow claim about calls that actually pass `PropertyNode` to Traverse.

1. Strongest reason the claim could be wrong

`PropertyNode` might be a legal token in a different API namespace?봯articularly a style ring or display name?봢ven though it is not a Traverse class name. NI documents a node?셲 `Style` separately as ?쐔he type of node,??and New VI Object?셲 style is distinct from its object-class input. [NI: Node Style](https://www.ni.com/docs/en-NF/csh?context=lvcore_lvscript_node_style)

I found no evidence that `PropertyNode`?봶ithout a space?봧s actually a legal New VI Object style in LabVIEW 2026. Therefore this possibility prevents a repository-wide textual replacement, but does not rescue any confirmed Traverse call.

2. Alternative explanation of the evidence

Error 1092 is a traversal-initialization failure caused by some precondition rejected during initialization; an invalid class string is one such explanation, but the number alone does not prove which precondition failed. An NI Community case reports 1092 as ?쏷raverse Initialization Failed??when traversal was attempted in an unsupported runtime context, demonstrating that 1092 is not uniquely ?쐕nknown class name.??[NI Community: error 1092 during traversal initialization](https://forums.ni.com/t5/LabVIEW/Error-1092-happened-while-running-the-executalbe-file-from-an/td-p/415352)

Your 2횞2 result nevertheless makes that alternative very weak here: the failure follows the string across two VIs and two callers. A recent NI Community answer also explicitly gives the Traverse names as `Invoke`, `Property`, and `SubVI`, not `InvokeNode`, `PropertyNode`, and `SubVINode`. [NI Community: proper Traverse class names](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Open-VI-reference-without-refees/idi-p/2329706/page/3)

NI?셲 public Traverse documentation does **not** define error 1092 numerically; it only documents the generic `error out`. Consequently, I cannot supply the requested official NI definition beyond saying that the observed source description is traversal initialization failure. Claiming that NI officially defines 1092 as ?쐇nvalid class name??would be unsupported. [NI: Traverse for GObjects inputs and outputs](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)

3. Observation that would falsify the claim

Any one of these would falsify it:

- LabVIEW 2026?셲 VI Server class enumeration contains an unlocalized class named `PropertyNode`.
- `Traverse for GObjects("PropertyNode")` succeeds on any valid BD target in the same LabVIEW instance.
- References returned by `Traverse("Property")` report concrete classes other than `Property` or its subclasses.
- `Property` has subclasses representing non-property-node objects.

The published VI Server hierarchy instead identifies `Property`, class ID 16419, under `ObjectFunction`, alongside `Invoke`; it lists **no children**. Therefore `Property` is not a broad superclass that silently includes other node kinds. [LabVIEW Wiki: Property class](https://labviewwiki.org/wiki/Property_class), [LabVIEW Wiki: VI Server hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

So 106 results should be 106 Property-class nodes, subject only to verifying LabVIEW 2026?셲 live hierarchy rather than trusting an older external table.

4. Verdict after attempting the refutation

The broad wording ?쐃very place our tooling uses `PropertyNode` is a bug??is too broad unless each occurrence is known to feed Traverse.

The narrower conclusion survives: **every confirmed `Traverse for GObjects` call whose Class Name is `PropertyNode` is defective in this LabVIEW 2026 environment; `Property` is the supported class name.** On the supplied evidence, a recipe that traverses `PropertyNode` to count or delete objects should be treated as guaranteed to fail before deletion, not merely latent.

For the implicit-node question: there is a scripting property. It is **`Linked Control` on the `Property` class**. It returns a reference to the front-panel control linked to the property node; from that reference, read the control?셲 label/name as needed. The same class also exposes `Link To Control` and `Disconnect From Control`. [LabVIEW Wiki: Property.Linked Control](https://labviewwiki.org/wiki/Property_class) NI independently describes an implicit property node as being linked to the front-panel object from which it was created. [NI: implicit versus explicit Property Nodes](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000wwBXCAY&l=en-US)

The cheapest discriminating test is read-only: have the manager query `ClassSpecifierConstant.AllTypes[]` in LabVIEW 2026 and print only entries whose unlocalized name contains `Property`; then traverse the small VI with `Property` and print `ClassName` plus `Linked Control` validity for all 12 references. `AllTypes[]` is specifically described as LabVIEW?셲 programmatic enumeration of VI Server class IDs, parents, and localized/unlocalized names. [LabVIEW Wiki: programmatic class enumeration](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy#Programmatic_Access_to_the_Classes)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED, and it changed three things.** (Annotated 2026-09-16 by the session that asked.)

1. **The narrowing is right and I adopted it.** My claim "every place our tooling uses `PropertyNode` is a bug"
   was too broad; only strings that reach `Traverse for GObjects` are defective. Checked every occurrence:
   `tools/recipes/build_opownerchain_v0.py` (3 sites, all feeding `count`/`report_all` → fixed to `Property`) and
   `tools/bench/census_opwiresource_v5.py` (1 site, also `InvokeNode` → fixed to `Property`/`Invoke`). The rest
   are prose in docstrings.
2. **`Property` does not over-select** — the class has no children (class ID 16419 under `ObjectFunction`), so the
   106 hits are 106 property nodes. That was the one way my replacement could have been silently wrong.
3. **`Linked Control` exists, and it answers the question I could not** — the implicit property node's linked
   front-panel object is readable from the `Property` class (with `Link To Control` / `Disconnect From Control`
   alongside). This is the route to name the autofocus interval N behind Property Node `#30146`
   (STATUS OPEN 6). Recorded in `docs/NAMES.md`; the op to read it is queued behind the build gate.
4. **`ClassSpecifierConstant.AllTypes[]`** was the answer to "how do we stop guessing class names" — a
   programmatic enumeration of class IDs with unlocalized names. Also recorded in `docs/NAMES.md`.

Not verified against the machine yet: `Linked Control` and `AllTypes[]` are peer-sourced (LabVIEW Wiki), which
this project treats as a hypothesis until a run confirms it. Both are cheap to confirm and are named as such.
