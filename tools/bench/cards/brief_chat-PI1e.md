# Brief chat-PI1e — addendum to brief_chat-PI1.md (judgement 2026-10-16, after result_chat-PI1d)

OpGetImage_v0.vi is built and hygiene-PASS (b7c5667b) - do not rebuild it. Only the shots remain.

Judgement decision on the open question of chat-PI1d:
- uid 22700 came from docs/frame-loop-anatomy.md, which was read on the WORKING COPY (2026-09-12), not on the original;
  its absence from the original's Traverse('Node') is not a defect. **Drop 22700 from crop A's required set.**
- Crop A required set = #6810 (camera buffer, get buff image-lost frames) and #5058 (tracking kernel). Find the While
  loop that owns BOTH (owner chain). If they are not in the same While loop, RETURN with both owner chains.
- Inside that loop, add to the crop the nearby subVI calls that save / plot the result (by subVI name, e.g. save trace,
  N bead plot, Draw Flattened Pixmap), as far as the crop stays readable (<= ~1800 x 1100 px, else split A1/A2).
  Optional members: a missing optional member is a note, not a failure.
- B, C, D unchanged from brief_chat-PI1.md. For B / C / D the same rule: the named UIDs are required; if one is
  absent, RETURN with what Traverse found nearby (names + uids), no guessing.
