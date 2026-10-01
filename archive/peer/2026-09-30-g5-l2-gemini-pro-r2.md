# g5-l2-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:09:15
- **outcome:** ANSWERED (158s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

With NI-IMAQdx and a USB3 Vision camera, a program opens a camera session, writes new values to attributes such as Width/Height (ROI), ExposureAuto/ExposureTime or the acquisition frame rate, confirms them by reading back, and then closes the session. When the next IMAQdxOpenCamera (or IMAQdx Open Camera VI) call opens the same camera, what values do those attributes have, and why?

Search the web and cite the URL of every source you used.

## Answer

Based on web search results regarding NI-IMAQdx and USB3 Vision camera behavior, here is what happens to the attribute values and why.

### What values do the attributes have?
When the next `IMAQdxOpenCamera` (or IMAQdx Open Camera VI) call opens the same camera, the attributes (Width/Height, ExposureTime, etc.) will **revert to the previous values stored in the camera's associated `.icd` (Interface Control Document) configuration file** on the host PC. 

*(Note: If a specific obscure attribute was modified but is not tracked/present in the `.icd` file, it would retain its newly written value. However, standard attributes like Width, Height, and ExposureTime are virtually always present in the default `.icd` file and will therefore be overwritten).*

### Why does this happen?
This behavior is the result of how NI-IMAQdx handles programmatic attribute changes versus session initialization:

1. **Programmatic Changes are Volatile by Default:**
   When your program writes new values to attributes during an open session, it successfully updates the camera's internal volatile memory and the current software session. However, these programmatic changes are **not automatically saved** to the `.icd` file on your hard drive (typically located in `C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data`). Unless you explicitly call the `IMAQdx Write Attributes` function before closing the session to persist them, the `.icd` file retains its older, previous values.
   
2. **The Camera Retains State Without a Power Cycle (But it gets overwritten):**
   Because you only closed the session and did not physically power cycle the USB3 Vision camera, the hardware actually retains your new attribute values in its internal volatile memory. 
   
3. **IMAQdxOpenCamera Automatically Loads the `.icd` File:**
   The critical step happens when `IMAQdxOpenCamera` is called. By design, this function automatically locates the `.icd` configuration file associated with that camera's serial number and model. It reads the settings from this file and **writes them down to the camera**, effectively overwriting the camera's current volatile memory state with the older values stored in the file. 

To make your programmatic changes persist across sessions, you would need to explicitly call `IMAQdx Write Attributes` before closing the session to update the `.icd` file, or save the settings to the camera's non-volatile memory (e.g., using GenICam `UserSetSave` features).

### Sources Used:
* **NI-IMAQdx Opening Camera and .icd Configuration File Loading Behavior:** 
  [ni.com - Loading Settings Programmatically](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPsII_by41u_Z3lHivsPuKOwwp-AALpChwQ8Xaku3VnfBuZZpajdcsD5Wsktnbi8W1UCsYl9NcsezyG1L3DG7RKGDMolmJKMl3ZYHLvlWoo7O1Wt8q884R7GOf2mMhwpvWqkEKzLI9BJu4yOGLbT7BHxsnlOljK9lfUTZl)
* **IMAQdx Write Attributes and Programmatic Saving Constraints:**
  [ni.com - Programmatic Attributes](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeP5a1aWe3LeQlE4xrSdFb00lGeyVp6F05lMYHeGrOeDGerVXLZTeWXozzwrCVCemJhaPzarsEMJ3ZLCCqFplKow53pb2S6SxKTO6sM6mDxKYMgu8zD-QrLbAqRLryoBcTcCezFM68Ul2SZxdjtucrKq47ixSAyU3okA0vXJJrIJ9YGD1GXC54vPKEpZl3rSJaBZZ0Lfr9)
* **NI-IMAQdx Session and Device Reset Behavior:**
  [ni.com - Reverting Camera Settings](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1Hm2L36zivVW3LcOWYirscBIYfYCdfp8Dumu7t2sU71V40aTkxSXnvNFTioOGU3ea8s_pNphfyrE-TlPfsuC-tah_wUitn0iwVMHBNrmWtCLdLx3Cs0ewrfqJ11ZzRaI7rqAf0uybkWF6teWnz3ZS4CjIrBWKVolZv0_a6oIR8wpuy5TAFiUNlfAug_4ypeRaXr1reL0bJ0TYqzA=)
* **USB3 Vision / GenICam Camera Volatile Memory Characteristics:**
  [Teledyne Vision Solutions - Persistent Settings](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcMOMmgSB-N9_NfJsoj-jdnUeYpdHJSZJj0gPL0a8RwI02z9FT4YIjn5ruLob0KYA-PXMtGao1e7eJdhbY5O2Yo6QnatWLZyQqz11v-_hXtsNX7ZESV5OGz0D7V_gL8h_c7NzK2812Fn-wNBOVOlToq69NyBiHRnNsAo2YTpXCA3CIat-Obw6EIVelybBPEI4bd5nzf4OwHKsITrGFsrd2ImpFlo85iTGvJ1sjJoZ1pf4EmvLLJaCxZMCb5gvlfXNOVH3wIetO7qG_LiV2JqLi-A==)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
