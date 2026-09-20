---
type: peer-review
status: historical
date: 2026-09-04
tags: [peer-review]
disposition: legacy
---

# uitars-latest-version-vs-claude

- **agent:** codex
- **date:** 2026-09-04
- **outcome:** ANSWERED (129s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Factual question, needs current web sources (GitHub bytedance/UI-TARS, Hugging Face, ByteDance Seed blog, arXiv). (1) What is the LATEST released UI-TARS model as of today (2026-09): name, version, release date, parameter sizes, and whether the WEIGHTS are publicly downloadable (Hugging Face link) or API-only. Specifically: is UI-TARS-2 (or any post-1.5 version) open-weight, and is there a 7B-class variant that runs locally on a 6 GB GPU via Ollama/llama.cpp (GGUF with vision projector available)? Compare against UI-TARS-1.5-7B which we run now. (2) Published GUI-grounding benchmark numbers (ScreenSpot-Pro, ScreenSpot-v2, OSWorld) for the latest UI-TARS vs UI-TARS-1.5-7B vs Anthropic Claude computer-use models (Claude Sonnet/Opus 4.x or 5 with computer use) - cite the tables. (3) Any known issues running UI-TARS newer versions in Ollama (vision projector/mmproj support). Already ruled out: we know 1.5-7B works locally via Ollama 0.32 with the mradermacher GGUF + mmproj. Give URLs.

## Answer

As of 4 September 2026, the latest publicly announced UI-TARS generation is still UI-TARS-2. It is not open-weight. There is no public UI-TARS-2 7B checkpoint, GGUF, or matching vision projector; therefore it is not currently a replacement for your locally running UI-TARS-1.5-7B.

## 1. Latest release and local availability

| Model | Announcement/release | Published size | Official weights | Practical status |
|---|---:|---:|---|---|
| UI-TARS-2 | 4 Sep 2025 | Not disclosed | No public checkpoint found | Hosted/API/demo model |
| UI-TARS-1.5 | 16 Apr 2025 | Full model size not disclosed | No full-model weights | Hosted model |
| UI-TARS-1.5-7B | 16 Apr 2025 | 7B class | Yes | Best current local UI-TARS |
| Earlier UI-TARS | Jan 2025 | 2B and 7B/72B variants | Some checkpoints public | Superseded for this use |

ByteDance?셲 repository explicitly dates UI-TARS-2 to **2025-09-04**, calls it the successor to UI-TARS-1.5, but links only to the technical report and showcase. In contrast, the very next update explicitly says UI-TARS-1.5-7B was ?쐎pen-sourced??and links its Hugging Face repository. That distinction is strong evidence that UI-TARS-2 was a model release/announcement, not a weight release: [ByteDance UI-TARS README, Updates](https://github.com/bytedance/UI-TARS#updates).

The UI-TARS-2 report was submitted on 2 September 2025 and revised on 5 September 2025: [UI-TARS-2 technical report](https://arxiv.org/abs/2509.02544). Neither the report abstract nor the official repository publishes a parameter count for UI-TARS-2.

ByteDance?셲 official Hugging Face account still has no UI-TARS-2 checkpoint. Its public UI-TARS checkpoint is [ByteDance-Seed/UI-TARS-1.5-7B](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B); the organization?셲 complete public model inventory can be checked here: [ByteDance-Seed models](https://huggingface.co/ByteDance-Seed/models).

UI-TARS-2 appears related to ByteDance?셲 much larger Seed vision-language stack, but it is unsafe to infer its parameter count from that. For context, Seed1.5-VL itself has a 532M vision encoder and an MoE language model with **20B active parameters**, and was exposed through Volcengine rather than released as weights: [Seed1.5-VL technical report](https://arxiv.org/abs/2505.07062).

**Direct answer:** no UI-TARS post-1.5 version is currently open-weight, and there is no post-1.5 7B-class UI-TARS that can be downloaded with a matching GGUF/mmproj for local inference on a 6 GB GPU.

Your current UI-TARS-1.5-7B remains the newest viable local version. Its official weights are [here](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B). Community GGUF conversion is possible because it is Qwen2.5-VL based, an architecture supported by llama.cpp?셲 multimodal converter: [llama.cpp multimodal documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/README.md).

Do not confuse **UI-TARS-2** with **UI-TARS-2B-SFT**. The latter means ??-billion-parameter UI-TARS,??not ?쏹I-TARS version 2.??Its older checkpoint is [ByteDance-Seed/UI-TARS-2B-SFT](https://huggingface.co/ByteDance-Seed/UI-TARS-2B-SFT).

## 2. Published benchmark numbers

The comparisons require care:

- ScreenSpot-v2 and ScreenSpot-Pro are single-screen grounding tests.
- OSWorld is an interactive agent benchmark affected heavily by scaffold, step limit, action interface, and benchmark revision.
- OSWorld and OSWorld-Verified results should not be treated as the same evaluation.

### Officially reported UI-TARS results

| Model | ScreenSpot-v2 | ScreenSpot-Pro | OSWorld |
|---|---:|---:|---:|
| UI-TARS-2 | Not reported | Not reported | **47.5** |
| UI-TARS-1.5 full/hosted model | **94.2** | **61.6** | **42.5** |
| UI-TARS-1.5-7B downloadable model | Not separately reported in headline table | **49.6** in scale table | **27.5** |
| UI-TARS-72B-DPO | ??| 38.1 | 24.6 |

The UI-TARS-2 paper reports **47.5 OSWorld**, plus 88.2 Online-Mind2Web, 50.6 WindowsAgentArena, and 73.3 AndroidWorld: [UI-TARS-2 abstract and report](https://arxiv.org/abs/2509.02544).

The official UI-TARS-1.5 Hugging Face model card reports:

- ScreenSpot-v2: UI-TARS-1.5 94.2, OpenAI CUA 87.9, Claude 3.7 87.6.
- ScreenSpot-Pro: UI-TARS-1.5 61.6, OpenAI CUA 23.4, Claude 3.7 27.7.
- Scale comparison: UI-TARS-1.5-7B scores 27.5 OSWorld and 49.6 ScreenSpot-Pro, while the larger hosted UI-TARS-1.5 scores 42.5 and 61.6 respectively: [official model-card benchmark table](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B).

One later leaderboard import assigns **61.6** to the repository as a whole, but that is the hosted UI-TARS-1.5 result, not clearly the downloadable 7B checkpoint. The Hugging Face evaluation discussion shows that imported value and its provenance: [HF ScreenSpot-Pro evaluation entry](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B/discussions/18/files). For a fair local-model estimate, I would use the official scale-table figure of **49.6**.

### Claude computer-use results

| Claude model | ScreenSpot-Pro | OSWorld | Comparability |
|---|---:|---:|---|
| Claude Computer Use, early version | **17.1** | ??| Same ScreenSpot-Pro table generation as early UI-TARS comparisons |
| Claude 3.7 | **27.7** | ??| Listed in UI-TARS-1.5 table |
| Claude Sonnet 4 | ??| **42.2** | Original OSWorld |
| Claude Sonnet 4.5 | ??| **61.4** | OSWorld-Verified, 100 steps, four-run average |
| Claude Sonnet 4.6 | **65.0** no tools / **82.4** with Python tools | **72.5** | Later Anthropic evaluation |
| Claude Opus 4.6 | **57.7** no tools / **83.1** with tools | **72.7** | Later Anthropic evaluation |
| Claude Opus 4.7 | **79.5** no tools | **78.0** | Later Anthropic system-card table |
| Claude Sonnet/Opus 5 | No directly comparable UI-TARS table | Evaluated on newer OSWorld variants | Not directly comparable |

The original ScreenSpot-Pro table gives Claude Computer Use **17.1 overall**: [GUI-Spotlight Table 3 reproduction](https://openreview.net/pdf?id=ZNAY3ivd62).

Anthropic reports Sonnet 4 at **42.2 OSWorld** and Sonnet 4.5 at **61.4 OSWorld-Verified**: [Sonnet 4.5 announcement](https://www.anthropic.com/news/claude-sonnet-4-5). Anthropic specifies that the latter uses OSWorld-Verified, 100 steps, averaged over four runs, so it is not an apples-to-apples comparison with UI-TARS-2?셲 47.5 original-OSWorld figure.

Anthropic?셲 later system-card table reports Sonnet 4.6 at **72.5 OSWorld-Verified**, Opus 4.6 at **72.7**, Opus 4.5 at **66.3**, and Sonnet 4.5 at **61.4**: [Claude Sonnet 4.6 system card](https://www-cdn.anthropic.com/bbd8ef16d70b7a1665f14f306ee88b53f686aa75/Claude%20Sonnet%204.6%20System%20Card.pdf).

For ScreenSpot-Pro, Anthropic reports Sonnet 4.6 at **65.0 without tools / 82.4 with Python**, and Opus 4.6 at **57.7 / 83.1**. Its later table reports Opus 4.7 at **79.5 without tools** and **78.0 OSWorld**: [Anthropic system-card tables](https://www-cdn.anthropic.com/037f06850df7fbe871e206dad004c3db5fd50340/Claude%20Opus%204.7%20System%20Card.pdf).

Claude Sonnet 5 and Opus 5 exist as of the requested date, but Anthropic?셲 public material emphasizes OSWorld-Verified or OSWorld 2.0 cost/performance curves rather than publishing a clean number comparable to UI-TARS-2?셲 2025 original-OSWorld run: [Sonnet 5 announcement](https://www.anthropic.com/research/claude-sonnet-5), [Opus 5 announcement](https://www.anthropic.com/news/claude-opus-5).

The defensible conclusion is:

- On the same older UI-TARS tables, hosted UI-TARS-1.5 greatly out-grounded Claude 3.7.
- UI-TARS-2 improved original OSWorld from 42.5 to 47.5.
- Later Claude 4.x models report substantially higher OSWorld-Verified and ScreenSpot-Pro results, but under newer protocols/scaffolds.
- No current table establishes UI-TARS-2 versus Claude 5 on identical settings.

## 3. Ollama/GGUF and projector issues

There cannot yet be a UI-TARS-2-specific Ollama compatibility result because no UI-TARS-2 checkpoint exists to convert.

For future checkpoints, llama.cpp supports Qwen2-VL and Qwen2.5-VL conversion with `--mmproj`; runtime normally needs the language-model GGUF plus its exact corresponding projector: [llama.cpp multimodal README](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/README.md), [CLI `--mmproj` option](https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md).

Ollama is more problematic for arbitrary community multimodal GGUFs:

- An open Ollama issue reports that a Modelfile containing separate model and projector `FROM` lines hangs on Ollama 0.32.5; manually constructing the manifest works, implying runtime support but no supported import syntax: [Ollama issue #17491](https://github.com/ollama/ollama/issues/17491).
- Using `ADAPTER` for an mmproj does not solve it: Ollama treats adapters and vision projectors differently, and reports `500: unable to load model`: [Ollama issue #15346](https://github.com/ollama/ollama/issues/15346).
- Ollama?셲 source does contain a separate `application/vnd.ollama.image.projector` layer, but that does not mean arbitrary two-file community imports are supported through normal Modelfile syntax: [Ollama create implementation](https://github.com/ollama/ollama/blob/main/server/create.go).
- Current Ollama compatibility code includes explicit Qwen2.5-VL projector translation, so architecture support has improved, but packaging/import remains the fragile part: [Ollama llama.cpp compatibility table](https://github.com/ollama/ollama/blob/main/llama/compat/README.md).

Thus, your known-good UI-TARS-1.5-7B setup should be preserved. A hypothetical UI-TARS-2 GGUF would require all three:

1. actual released source weights;
2. a llama.cpp-supported architecture conversion;
3. a matching mmproj plus an Ollama packaging/import method that genuinely registers it as an image projector.

Today, condition 1 already fails. There is therefore no evidence-based UI-TARS-2 upgrade path for a 6 GB GPU.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
