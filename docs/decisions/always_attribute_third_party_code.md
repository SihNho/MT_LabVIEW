---
name: always-attribute-third-party-code
description: "Every piece of borrowed or derived code must carry a traceable citation — author, source URL, version, licence — so anyone can find the original"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 72babae7-a0eb-4591-80eb-3f88511dbec4
  modified: 2026-08-26T03:52:33.007Z
type: decision
status: in-force
date: 2026-08-26
source: memory/always_attribute_third_party_code.md
---

# Cite every borrowed or derived piece of code

The user's standing requirement (2026-08-26), given when authorising work that builds on third-party
libraries: *"이 사용한 reference 코드들은 표시해둬야 해. 논문에서 인용하는 타입이든 아니면 그냥 웹
주소든 어쨌든 다른 사람이 보고 원본 레퍼런스 찾을 수 있도록."* — every reference used must be marked,
whether in academic citation form or simply as a URL, **so that another person can locate the
original**.

This is an academic-lab norm, not a formality: work here may end up in a thesis or a paper, and code
whose provenance cannot be traced is a liability. So whenever code is copied, adapted, cloned, or
merely learned from:

- Record **author, project name, version, licence, and a resolvable URL**, plus the date accessed.
- State **what was derived from what** — if a file began life as a copy of someone's example, say so
  explicitly, naming both files. A future reader must be able to diff against the original.
- Keep a single project-level references file (`REFERENCES.md` in this project) as the canonical list,
  and additionally put the citation *inside* the artefact where the format allows — a comment header
  in a script, or the VI Description field (`File > VI Properties > Documentation`) for a `.vi`, since
  a LabVIEW binary has nowhere else to carry text.
- Note the **licence** explicitly, because it governs reuse. Anything with no declared licence is
  "all rights reserved" and must be read for technique only, never vendored.

Apply this to LabVIEW libraries, example VIs shipped with LabVIEW itself, code from forums, and any
snippet adapted from documentation — not only to formally packaged dependencies.
