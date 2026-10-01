# g5-l4-opus-medium-r1

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.7507  in 28 / out 4381 / cache-create 26774 / cache-read 514481  (116s, 25 turn(s))
- **date:** 2026-09-30 20:07:01
- **outcome:** ANSWERED (118s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, a program enumerates the objects on a block diagram and reads each object's class name (for example with Traverse for GObjects.vi or the ClassName property of a GObject reference). What class name does a VISA Write function node report, is there a VISA-specific scripting class for it, and how would a program pick out only the VISA Write nodes?

Search the web and cite the URL of every source you used.

## Answer

I couldn't find a source that answers any of your three questions, so I'm not going to guess.

**1. What class name does a VISA Write node report?** Not settled. No page I found names the ClassName that VISA Write returns. The closest was an lvkit GitHub issue about parsing LabVIEW's XML. It shows primitive nodes in general tagged `class="prim"` and identified by a numeric `primResID`, but it never mentions VISA Write ([lvkit #103](https://github.com/pragmatest-dev/lvkit/issues/103), [lvkit #105](https://github.com/pragmatest-dev/lvkit/issues/105)). That is a file format, not the VI Server ClassName property, so it doesn't answer the question.

**2. Is there a VISA-specific scripting class?** Not settled. A community list of class IDs 1–135 includes `VISAResourceName` (value 50). That is a front-panel control type, not a block-diagram function class. None of the pages I found name a VISA function class ([NI forum: class IDs and names](https://forums.ni.com/t5/LabVIEW/Complete-list-of-class-IDs-and-names/td-p/2504572)).

**3. How would a program pick out only the VISA Write nodes?** Not settled. The help says scripting can identify objects "by their class name, data type, label, tag, or array index" ([unofficial LabVIEW help mirror](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/scripting_property_method.html)). The traverse examples only show filtering by a whole class, such as `CaseStructure` ([LabVIEW Artisan, Traverse tip](http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html)). Nothing I found shows which property tells one function apart from another within a class.

The NI reference pages that would likely answer this were among my search results, but the fetch returned only site navigation, not their content:
- [VI Server Class Hierarchy](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/class-hierarchy.html)
- [Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)

**Quickest way to settle it:** if running something is allowed, drop one VISA Write on a diagram and read its ClassName property. Then open the Class Browser (View » Class Browser) on that class and check which property holds the function's identity. Compare it with a different function of the same class. That tells you the class name, whether there is a VISA-specific class, and the filter to use.

Other sources I checked had nothing relevant: [LabVIEW Wiki: VI Scripting](https://labviewwiki.org/wiki/VI_Scripting), [LAVA: Hidden Primitives](https://lavag.org/topic/16532-hidden-primitives/), [NI forum: VISA Script](https://forums.ni.com/t5/LabVIEW/VISA-Script/td-p/3813616).

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
