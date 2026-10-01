# g5-g2-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:02:37
- **outcome:** ANSWERED (80s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

Based on my web research, here are the answers to your questions:

### 1. Can it be switched off programmatically for a specific VI?
**Yes**, the "Enable automatic error handling" option can be switched off programmatically for an individual VI using the VI Server via a Property Node.

### 2. Exact class and property name
*   **Class:** `VI`
*   **Property Name:** `Automatic Error Handling`
*(In a LabVIEW Property Node, this is typically selected by navigating to **VI » Execution » Automatic Error Handling**)*

### 3. Is there a global switch?
**No**, there is no programmatic global switch (i.e., no Application-class property) to dynamically turn off automatic error handling for all currently running VIs. It must be managed at the individual VI level.

However, there is a global configuration setting that dictates the default behavior for **new VIs** created in the environment:
*   **Manually in IDE:** You can toggle this globally for new VIs by navigating to **Tools » Options**, selecting the **Block Diagram** category, and unchecking **Enable automatic error handling in new VIs**.
*   **Via Configuration File:** You can also edit the LabVIEW `.ini` configuration file and add/modify the tokens `defaultErrorHandlingForNewVIs = False` and `EnableAutomaticErrorHandling = False`.

### Sources Cited
*   [ni.com - VI Property: Automatic Error Handling](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvM_w-ftr_hYedMhgcCJhSmvwjuR9ENeYcpSnDedQ3wKKsl6uASh4EKcPpiM4pm0UTh-xj3h9tomahgcdD679UW-96yn3t0PfS3dsKX9LUjIMw7laMTO2VJbiPZ94jp2Vm0oyUz4QyYdBHkSFqvApz9sW4i0-n4pQ0empbGOZ2cWdp3nbOSV72FHd1NVVNReBP282z34KvknCpElYoJVTtvSPDNuzvitlJxXO-vgk=)
*   [ni.com - LabVIEW Application Class lacks a global switch for Automatic Error Handling](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB_FUXgha80zcHAJban7HWbljcv0iuKq-qakVGBFBDwjuYULStsRes2Cxrjcaep-ZP-7bdzPPnI8cOoAxXEzP0Wy7Hl4mufdoSHcAKGKdBie4Q7Rw2x49fEPNxL9EIug10leo5JxPcbfrAzf0yKjwt0UpL3QRi_-bxfSRb)
*   [ni.com - Modifying default error handling in LabVIEW configuration (.ini)](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEekctsv8H8x0CHCl_0KEu6HM1C4JtzTX-Z1kav0C0TeNNGV5vF9qp0tq8ctpEd00uKHOE-JzycFUCwSljpqvc-C5FVMwLN0UGe3QWg7b6UxXUf73-xWbMCJJEzMsgpgFx4BKsd0ur_dXzXy_hj3lteeBqxoYe2rqeRDpL8bzJmxEkwVU=)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
