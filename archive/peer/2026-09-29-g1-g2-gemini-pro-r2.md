# g1-g2-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-29 20:21:13
- **outcome:** ANSWERED (122s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

**Yes**, the 'Enable automatic error handling' option can be switched off programmatically for a specific VI via VI Server.

- **Class:** `VI`
- **Property Name:** `Automatic Error Handling` (Short Name: `Auto Err Handling`)

Setting this Boolean property to `FALSE` will disable automatic error handling for the referenced VI.

### Global Switch
There is no programmatic global switch or property to disable this for all *existing* VIs retroactively. However, there is a global environment setting to disable it for all **new** VIs:
*   Navigate to **Tools » Options » Block Diagram**
*   Uncheck **Enable automatic error handling in new VIs**

### Sources
*   [NI Documentation: Automatic Error Handling Property](https://www.ni.com/docs/en-US/bundle/labview/page/lvprop/vi_auto_err_handling.html)
*   [NI Documentation: Disabling Automatic Error Handling in LabVIEW](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019O27SAE)
*   [LAVA Forums / NI Forums Consensus on Error Handling Practices](https://forums.ni.com/)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
