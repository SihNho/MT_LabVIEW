# g1-g3-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:21:37
- **outcome:** ANSWERED (184s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In NI-IMAQdx (C function IMAQdxGetImageData, or the LabVIEW IMAQdx Get Image2 VI), what numeric value does each buffer-number mode (Next, Last, BufferNumber, Every, LastNew) have, and which of these modes returns immediately without waiting for a new frame from the camera?

Search the web and cite the URL of every source you used.

## Answer

**Last (1)** is the only mode that returns immediately without waiting for a new frame.

### Numeric Values
The `IMAQdxBufferNumberMode` enumeration maps as follows:
- **Next**: `0`
- **Last**: `1`
- **BufferNumber** (or Buffer Number): `2`
- **Every**: `3`
- **LastNew** (or Last New): `4`

### Reasoning
- **Last (1)** does not wait. It immediately returns the most recently acquired image currently available in the driver's memory. If your loop runs faster than the camera's frame rate, it will return duplicate frames without blocking. 
- **LastNew (4)** acts like Last, but guarantees a unique image. If the most recent frame in the buffer was already returned by a previous call, it blocks and waits for the camera to acquire a *new* frame.
- **Next (0)**, **BufferNumber (2)**, and **Every (3)** all inherently block until their requested future frames arrive in the circular buffer.

*(Sources: NI Vision Acquisition Software documentation for [IMAQdx Get Image2](https://www.ni.com/docs/en-US/bundle/ni-vision-acquisition-software/page/imaqdx/imaqdx_get_image2.html) and [IMAQdxGetImageData](https://www.ni.com/docs/en-US/bundle/ni-vision-acquisition-software/page/imaqdx/imaqdxgetimagedata.html))*



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
