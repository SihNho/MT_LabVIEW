# g5-l4-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.9028  in 24 / out 4258 / cache-create 29242 / cache-read 445694  (132s, 19 turn(s))
- **date:** 2026-09-30 20:06:56
- **outcome:** ANSWERED (134s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW VI Scripting, a program enumerates the objects on a block diagram and reads each object's class name (for example with Traverse for GObjects.vi or the ClassName property of a GObject reference). What class name does a VISA Write function node report, is there a VISA-specific scripting class for it, and how would a program pick out only the VISA Write nodes?

Search the web and cite the URL of every source you used.

## Answer

The sources I found don't directly settle this. No NI page or forum post I found states what `ClassName` a VISA Write node returns. The class hierarchy does narrow it down, though.

**1. Is there a VISA-specific scripting class for a VISA Write node? Probably not.**
- The VI Server class hierarchy on the LabVIEW Wiki lists only two classes with "VISA" in the name: `VISAResourceName` (ClassID 50) and `VISAResourceNameConstant` (ClassID 16448). Those are the resource-name control and the resource-name constant, not the Read or Write functions. https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy
- Under `Node`, the node classes are generic ones such as `Function`, `GrowableFunction`, `SubVI` and `Structure`. https://labviewwiki.org/wiki/Node_class
- `Function` (ClassID 16400) has only a few subclasses: `ArrayToCluster`, `Comparison`, `FileDialog`, `FlattenUnflattenString`, `GPIBReadWrite`, `ReadWriteFile` and `TypeCast`. `GrowableFunction` (ClassID 16410) has none with VISA in the name either. https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy and https://labviewwiki.org/wiki/Function_class
- Note that GPIB Read/Write has its own class (`GPIBReadWrite`), but VISA Read/Write does not. https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy

**2. What class name does it report?** Probably the plain `Function` class, the generic class for built-in functions. This is an inference from the hierarchy above; I found no source that says so directly. The wiki pages are also incomplete (the Function class page is marked as a stub), so I can't rule out an unlisted class.

**3. How would a program pick out only the VISA Write nodes? The sources don't document a way.**
- **Filtering by class name won't work alone.** Traverse for GObjects filters by a class-name string (people pass "GObject" to get every object). https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133 and http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html
  - If VISA Write reports `Function`, filtering on that returns every node of that generic class, not just VISA Write. So a second check is needed. (I couldn't load NI's own page for the VI to confirm how the class-name input matches: https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)
- **A "Resource Id" property exists but is unreliable.** The `Function` class has a U32 property called "Resource Id" (short name ResId), which looks like it identifies which built-in function a node is.
  - The wiki marks it **Private** and says nothing about what it does. It also contradicts itself on access: the class page says read-only, the property page says write-only. https://labviewwiki.org/wiki/Function_class and https://labviewwiki.org/wiki/Function_class/Resource_Id_property
  - I found no published Resource Id value for VISA Write.
  - A third-party tool that reads LabVIEW's XML does key built-in functions by a "primResID". That supports the idea that this ID is what tells them apart, but the page gives no VISA numbers. https://github.com/pragmatest-dev/lvkit/issues/105
- **Two other checks are possible but have no support in the sources I found:**
  - comparing the node's label text or terminal names
  - checking for a VISA resource-name input terminal

  Both are guesses on my part.

The quickest way to settle it is in LabVIEW itself: put one VISA Write on a diagram and read that node's `ClassName`, `Class ID` and (if you have private access) Resource Id. The class-name and filtering claims above are unconfirmed until then.

Sources:
- https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy
- https://labviewwiki.org/wiki/Node_class
- https://labviewwiki.org/wiki/Function_class
- https://labviewwiki.org/wiki/Function_class/Resource_Id_property
- https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133
- http://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html
- https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html (tried but couldn't load)
- https://github.com/pragmatest-dev/lvkit/issues/105

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
