# g5-g2-gemini-pro-r1

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:00:18
- **outcome:** ANSWERED (77s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

In LabVIEW, can the 'Enable automatic error handling' option (VI Properties > Execution) of one specific VI be switched off programmatically through VI Server? If so, give the exact class and property name. Is there also a global switch?

Search the web and cite the URL of every source you used.

## Answer

Based on web research, here are the answers to your questions regarding LabVIEW's "Enable automatic error handling":

### 1. Can it be switched off programmatically?
Yes. You can programmatically enable or disable the "Automatic Error Handling" setting for a specific VI during runtime by using a Property Node.

### 2. Exact Class and Property Name
*   **Class:** `VI` 
*   **Property Name:** `Automatic Error Handling` (its short name in VI Server is `Auto Err Handling`).

*(Note: You must wire a boolean `False` to this property to switch it off programmatically. This VI Server property is not supported in the LabVIEW Run-Time Engine.)*

### 3. Is there a global switch?
**No**, there is no global Application-level VI Server property or programmatic switch that can turn off automatic error handling for all VIs at runtime. The property only applies to the specific VI referenced by the Property Node. 

However, there is a global *development environment* setting:
*   You can navigate to **Tools » Options » Block Diagram** and uncheck **"Enable automatic error handling in new VIs"** (or set `defaultErrorHandlingForNewVIs=False` in the `LabVIEW.ini` file). 
*   This will only change the default behavior for any *newly created* VIs moving forward. It does not act as a runtime switch and will not affect existing VIs. 

### Sources Used
*   [NI - Programmatically Disable Automatic Error Handling in LabVIEW](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGumPJQvJ0HwUel0_8Cb9G2CWBK5GsN30GcWi7HMbCsUkbbB4VDULHZHAZMjiDhYMEzf3VkZoqm0ER_rs3itUXso7OvCD45mUClCtpYKQentAT9azuIJLtHuY2X3m1o3djJTls_XbRq6uE5IqV4BGPJEw_tDQXfEtw4EdF5th68M8HOyGu5)
*   [NI - Automatic Error Handling property details](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvAlTIy6DD3hT59k7lUbsnabIfDWgjXsArK4TdIVV5DTc2oUglWPHmG7UEV-DGLnlCAi05qRjmmJYVWWubS-JJqR-rj5VExRQLk9I0LeG_v512IQytdzMs1s5ec-l6rHSAqjroebACeH4utBaX_rNGBa0NoDH8ueLWuwk=)
*   [NI - Property scope and application](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF66JJxHY0Sxd9IBTmEEfrJn2uGybb7L0fsvPWUWkwke_lOgD8DHqNZduc6X-AqNuIjL9WIqa9ZHpgMAsgERiNOIxf8jXNqciAV_aereGaD94e2hsU5klnJPZUBBBJtcwTKS_8rdpVoom5DTryHHN2kdh3tYyJNBUZQHp8yk44CzqNchDO12foGwagPoe4FnxV5LosNQcKBZlnxIncjX7r15e_AfWxQCJkRuQ9Dee8=)
*   [DQMH - Best Practices for New VIs](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPbQ8ZzNiU9eDC64qbt3EhRdC4Z8LlS4kxP-HYb8ipfWlht36wyRaY3z5TJbjLvskBdIJ4PCgw-PlltPO3VGf4uigesUf8eVHyxpbg28XiD6CJjPYuuYIq2A==)



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
