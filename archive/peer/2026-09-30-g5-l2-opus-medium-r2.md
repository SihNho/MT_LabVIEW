# g5-l2-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.5751  in 18 / out 4694 / cache-create 19203 / cache-read 290893  (90s, 20 turn(s))
- **date:** 2026-09-30 20:02:41
- **outcome:** ANSWERED (92s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

With NI-IMAQdx and a USB3 Vision camera, a program opens a camera session, writes new values to attributes such as Width/Height (ROI), ExposureAuto/ExposureTime or the acquisition frame rate, confirms them by reading back, and then closes the session. When the next IMAQdxOpenCamera (or IMAQdx Open Camera VI) call opens the same camera, what values do those attributes have, and why?

Search the web and cite the URL of every source you used.

## Answer

**Short answer:** When the next Open Camera call runs, those attributes most likely hold the values stored in the camera's default NI-IMAQdx camera file (the `.icd` file NI MAX writes when you click Save). They do not keep the values your program wrote and read back in the earlier session. There is one exception: an attribute that is not saved in the `.icd` file isn't re-applied when the camera opens. In that case the sources don't settle what you'll see, and neither guess can be confirmed.

**Why:**

1. **Open Camera applies the camera file.** NI's help page for IMAQdx Open Camera says the VI "opens a camera, queries the camera for its capabilities, loads a camera configuration file, and creates a unique reference." I only saw that text in a search-result snippet, because the page returned HTTP 403 when I tried to fetch it. https://documentation.help/NI-IMAQdx-VI/IMAQdx_Open_Camera.html
   - NI MAX writes this default file every time you click Save, and the file "is then used whenever the camera is opened in either MAX or LabVIEW/C/VB/etc." https://forums.ni.com/t5/Machine-Vision/saving-camera-settings-with-NI-IMAQdx/td-p/658253
   - An NI employee said Open "will create a default ICD from the camera config if one does not exist." https://forums.ni.com/t5/Machine-Vision/IMAQdx-Read-Attributes-vi-WRITES-icd-file-if-none-exists-AWFUL/td-p/2867638

2. **Writing an attribute doesn't save it to that file.** The same thread says changes made at runtime aren't saved automatically. To keep them across sessions you have to save them yourself with IMAQdx Write Attributes and load them back with Read Attributes. https://forums.ni.com/t5/Machine-Vision/saving-camera-settings-with-NI-IMAQdx/td-p/658253
   - So reading a value back only proves the camera accepted it during that session. It says nothing about the next open.

3. **Only "Streamable" attributes go into the `.icd` file.** An NI employee explained that IMAQdx saves only the attributes the camera vendor marked `<Streamable>Yes</Streamable>` in the camera's GenICam XML. You can find that XML under `C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\XML`. https://forums.ni.com/t5/Machine-Vision/save-camera-attributes/td-p/3177343
   - Width, Height, ExposureAuto, ExposureTime and the frame rate are normally in the file, so they are reset to the file's values on open. I did not find a source that confirms this for your specific camera model.

**What I couldn't settle:**

- **Attributes that aren't in the `.icd` file:** I found no NI source saying what IMAQdx does with them on open. One forum thread gives an indirect clue: settings kept in the camera's volatile memory were lost when the camera was power-cycled, and the workaround was the camera's own UserSet feature. https://forums.ni.com/t5/LabVIEW/Camera-attributes-reset-to-invalid-values-on-power-cycle/td-p/3733922
  - That fits the idea that, without a power cycle, such an attribute might keep the value your program wrote. No source states this for IMAQdx.
- **Values in the file that don't get applied:** There is at least one report of Open Camera not applying some values that were correctly stored in the `.icd` file. Those attributes came up with default values instead. https://forums.ni.com/t5/LabVIEW/IMAQdx-incorrectly-loading-some-attributes-from-icd-file/td-p/4223918

**How to check on your setup:**

- Look in the camera's `.icd` file under `...\NI-IMAQdx\Data` to see which attributes it lists.
- To make your settings stick, pick one of these:
  - Click Save in NI MAX.
  - Call IMAQdx Write Attributes, then Read Attributes after you open the camera.
  - Write every setting again after each Open.

Sources:
- https://documentation.help/NI-IMAQdx-VI/IMAQdx_Open_Camera.html (search snippet only; fetch returned 403)
- https://forums.ni.com/t5/Machine-Vision/saving-camera-settings-with-NI-IMAQdx/td-p/658253
- https://forums.ni.com/t5/Machine-Vision/IMAQdx-Read-Attributes-vi-WRITES-icd-file-if-none-exists-AWFUL/td-p/2867638
- https://forums.ni.com/t5/Machine-Vision/save-camera-attributes/td-p/3177343
- https://forums.ni.com/t5/LabVIEW/Camera-attributes-reset-to-invalid-values-on-power-cycle/td-p/3733922
- https://forums.ni.com/t5/LabVIEW/IMAQdx-incorrectly-loading-some-attributes-from-icd-file/td-p/4223918

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
