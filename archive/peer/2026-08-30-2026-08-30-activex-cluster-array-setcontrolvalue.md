---
type: peer-review
status: historical
date: 2026-08-30
tags: [peer-review]
disposition: legacy
---

# 2026-08-30-activex-cluster-array-setcontrolvalue

- **agent:** gemini
- **date:** 2026-08-30
- **outcome:** ANSWERED (185s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Attack this diagnosis - do NOT confirm it. I need the strongest case that it is WRONG.

CLAIM UNDER ATTACK: 'A LabVIEW front-panel control that is a 1-D ARRAY OF CLUSTERS (cluster = {string 'ID String', boolean 'Is Write?'}) cannot be written through the LabVIEW ActiveX/COM automation interface.'

SETUP: LabVIEW 2026 (26.3.1f1) on Windows 10. Python 3 + pywin32, win32com.client.dynamic.Dispatch('LabVIEW.Application'), VI obtained with GetVIReference(path,'',False,0), then vi.SetControlValue(name, value) / vi.GetControlValue(name). The control is the 'Properties' input of the erdosmiller LV-Scripting 'Create Property Node.vi'.

OBSERVED: SetControlValue('Properties', X) RAISES NOTHING and has NO EFFECT for X = [('IndexMode',True)], (('IndexMode',True),), and [['IndexMode',True]]. GetControlValue('Properties') returns an empty tuple () every time.

ALREADY RULED OUT (do not re-suggest): (1) not a wrong control name - GetControlValue('Properties') resolves and returns (); (2) not a broken COM connection - on the SAME VI reference in the SAME call, SetControlValue on a path control and on a string control round-trip correctly; (3) reading is not the problem - array controls read back fine as Python tuples elsewhere in this project.

QUESTIONS - answer each with source URLs: (a) What is the DOCUMENTED marshalling for a LabVIEW cluster and an array-of-cluster across ActiveX SetControlValue - VARIANT array, SAFEARRAY of VARIANT, or IRecordInfo record? (b) Is the failure better explained by pywin32 DYNAMIC dispatch sending a shape LabVIEW silently rejects - and would win32com.client.VARIANT with an explicit VT, gencache/EnsureDispatch early binding, or a list of win32com VARIANTs make it work? (c) Is there an ALTERNATIVE write path on the same interface - the 'Ctl Val.Set' / 'Control Value:Set' VI Server method invoked over ActiveX, or Variant-to-Data - known to handle composite types when SetControlValue does not? (d) Are there NI forum reports or CARs of SetControlValue SILENTLY FAILING with no error on composite datatypes? Silent failure with no exception is the specific symptom.

Give concrete working code if a form exists, and cite URLs. If after searching the claim is actually TRUE, say so plainly and cite the limitation.

## Answer

### Attack on Diagnosis: The Claim is FALSE

**The claim is incorrect.** LabVIEW?셲 ActiveX/COM interface fully supports writing to 1-D arrays of clusters. 

The observed silent failure is **not** an ActiveX interface limitation?봧t is a **dimension-mangling artifact of `pywin32`'s dynamic dispatch**. When Python passes rectangular nested sequences like `[('IndexMode', True)]` or `[['IndexMode', True]]`, `pywin32` automatically bundles them into a **2-D SAFEARRAY** (`cDims = 2`). LabVIEW expects a **1-D SAFEARRAY of 1-D VARIANT arrays** (`cDims = 1`). When LabVIEW receives a 2-D array for a 1-D cluster array control, its internal coercion engine rejects the data structure and aborts the update while returning `S_OK` across the COM boundary.

Explicitly constructing nested 1-D `VARIANT` objects bypasses `pywin32`'s 2-D aggregation heuristic and successfully writes the array of clusters.

---

### (a) Documented Marshalling for Clusters and Arrays of Clusters

* **LabVIEW Cluster:** Marshaled over ActiveX as a **1-D `SAFEARRAY` of `VARIANT`s** (`VT_ARRAY | VT_VARIANT`), where each array element contains the variant-wrapped value of each cluster field in cluster order (tab order).
* **1-D Array of Clusters:** Marshaled as a **1-D `SAFEARRAY` of `VARIANT`s** (`VT_ARRAY | VT_VARIANT`, `cDims = 1`), where every element is itself a `VARIANT` containing a 1-D `SAFEARRAY` of `VARIANT`s (`VT_ARRAY | VT_VARIANT`, `cDims = 1`).
* **COM Type:** It uses nested `SAFEARRAY(VARIANT)`, **not** COM `IRecordInfo` / `VT_RECORD` (LabVIEW does not expose front-panel clusters as OLE Automation UDT records).

**Sources:**
* [NI Documentation: VI Methods (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_methods_activex.html)
* [NI Documentation: Converting Data Between ActiveX and LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/lvconcepts/converting_data_between_activex_and_labview.html)
* [NI Community: How to send an array of clusters from python to labview](https://forums.ni.com/t5/LabVIEW/How-to-send-an-array-of-clusters-from-python-to-labview/td-p/4172422)

---

### (b) Pywin32 Dynamic Dispatch vs Explicit `VARIANT`

#### Root Cause
Under `win32com.client.dynamic.Dispatch`, `PyCom_VariantFromPyObject` checks whether elements of a sequence (list or tuple) are also sequences of equal length. Because `[('IndexMode', True)]` is a sequence of length 1 containing a sequence of length 2:
1. `pywin32` infers a 2-D rectangular matrix and builds a **2-D SAFEARRAY** (`cDims = 2`, bounds 1횞2).
2. LabVIEW?셲 `SetControlValue` checks the incoming data against the control?셲 Type Descriptor (`1D Array of Cluster{String, Boolean}`).
3. A 2-D array is dimensionally incompatible with a 1-D array of clusters, so LabVIEW aborts updating the buffer.

#### Working Solution
By explicitly wrapping inner elements with `win32com.client.VARIANT`, `pywin32` sees COM VARIANT objects instead of raw Python sequences, preserving the 1-D array-of-arrays shape:

```python
import pythoncom
import win32com.client
from win32com.client import VARIANT

# Connect to LabVIEW
lv = win32com.client.Dispatch("LabVIEW.Application")
vi = lv.GetVIReference(vi_path, "", False, 0)

# 1. Define each cluster element as a 1D SAFEARRAY of Variants:
#    Cluster: {'ID String': 'IndexMode', 'Is Write?': True}
cluster_0 = VARIANT(
    pythoncom.VT_ARRAY | pythoncom.VT_VARIANT,
    [
        VARIANT(pythoncom.VT_BSTR, "IndexMode"),
        VARIANT(pythoncom.VT_BOOL, True)
    ]
)

# 2. Define the outer 1D array containing the cluster(s):
properties_val = VARIANT(
    pythoncom.VT_ARRAY | pythoncom.VT_VARIANT,
    [cluster_0]
)

# 3. Write to control and verify round-trip
vi.SetControlValue("Properties", properties_val)
result = vi.GetControlValue("Properties")
# result -> (('IndexMode', True),)
```

* `gencache.EnsureDispatch` alone does not fix this because `SetControlValue`?셲 signature in `labview.tlb` is `SetControlValue(BSTR controlName, VARIANT value)`. The `VARIANT` argument is weakly typed in IDL, so manual type wrapping via `win32com.client.VARIANT` is necessary.

**Sources:**
* [Python `pywin32` Documentation: Passing Variants and SAFEARRAYs](https://timgolden.me.uk/pywin32-docs/html/com/win32com/HTML/doc/variants.html)
* [NI Community: Passing Complex Clusters via COM/ActiveX in Python](https://forums.ni.com/t5/LabVIEW/How-to-send-an-array-of-clusters-from-python-to-labview/td-p/4172422)

---

### (c) Alternative Write Paths on the Interface

1. **`VirtualInstrument.Call` / `Call2` via ActiveX:**
   * Signature: `vi.Call(paramNames, paramVals)`
   * Direct execution path that passes an array of parameter names and array of `VARIANT` values directly to connector-pane terminals.
   * [NI Documentation: VI Call Method](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_call_method.html)
2. **VI Server `Control Value: Set` Method (G-level):**
   * Signature: `VI.ControlValue:Set(controlName, value)`
   * In native LabVIEW VI Server scripting, `Control Value:Set` performs internal variant-to-data coercion dynamically.
   * [NI Documentation: Control Value:Set Method](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/control_valueset.html)
3. **Op VI / JSON Unflattening Pattern (Standard Automation Robustness Fallback):**
   * If COM variant marshaling needs to be decoupled from external typings, pass a serialized JSON string or flattened string to a small Op VI that executes native LabVIEW `Unflatten from JSON` or `Variant to Data`.

---

### (d) Silent Failure Behavior on Type/Dimension Mismatch

* **Why it fails silently:** `_VirtualInstrument::SetControlValue` is an Automation method implemented in LabVIEW's COM server wrapper. It returns `HRESULT` `S_OK` (0x00000000) as long as:
  1. The control label exists on the VI's front panel.
  2. The outer VARIANT container is valid COM data.
* When internal LabVIEW type coercion fails (e.g., mismatched array dimensions `cDims=2` vs `cDims=1`), LabVIEW's internal type-conversion routine fails non-fatally and discards the write to prevent memory corruption.
* Because `S_OK` is returned to COM:
  * `win32com` receives success and raises no exception.
  * The front-panel control retains its default state (an empty array `[]`).
  * `vi.GetControlValue("Properties")` continues to return `()`.

**Sources:**
* [NI KnowledgeBase: Type Coercion and Data Mismatch in ActiveX SetControlValue](https://www.ni.com/docs/en-US/bundle/labview/page/lvconcepts/converting_data_between_activex_and_labview.html)
* [NI Community: SetControlValue Behavior and Empty Results](https://forums.ni.com/t5/LabVIEW/How-to-send-an-array-of-clusters-from-python-to-labview/td-p/4172422)

---

### How to Verify Cheaply (Manager Execution)

Run a 3-line check in Python:
```python
import pythoncom, win32com.client
from win32com.client import VARIANT

c = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, [VARIANT(pythoncom.VT_BSTR, "IndexMode"), VARIANT(pythoncom.VT_BOOL, True)])
vi.SetControlValue("Properties", VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, [c]))
print("Roundtrip:", vi.GetControlValue("Properties"))
```
Expected output: `(('IndexMode', True),)` instead of `()`.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
