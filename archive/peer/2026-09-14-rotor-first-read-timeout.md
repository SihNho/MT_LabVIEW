---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, rotor]
---

# rotor-first-read-timeout

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (72s)
- **why asked:** failed prediction in hw_rotor_read.log run 1 (the first read after Configure timed out; the next call got the reply)
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/hw_rotor_read.log (tools/bench/hw_rotor_read.py): first hardware contact with the Autonics PMC-2HS rotor controller (RS-232, NI-VISA alias Rotor). Sequence: Configure copy (VISA Open + one init write) -> SetCommand_signed.vi Ring 2 (POS query + VISA Read) -> a copy of the ORIGINAL SetCommand.vi Ring 2. OBSERVED: the signed copy's VISA Read timed out (-1073807339) after 2.0 s with an empty buffer; the original copy, run immediately after, returned 'POS 000186A0,00000000\r' in 0.0 s (two-axis reply: X = 0x186A0 = 100000 pulses = 72000 deg at 0.72 deg/pulse, Y = 0; the +200-turn baseline the lab uses). PREDICTED: both read the same reply. MY EXPLANATION: the first query after the port was (re)opened was answered later than the 2-s VISA timeout (controller/USB-serial wake-up, or the init write's own response still pending), and that late reply sat in the serial buffer until the NEXT VISA Read consumed it - so the original 'read' actually returned the signed copy's reply; nothing about the signed edit (which touches only the parse after VISA Read) can affect a VISA timeout. DISCRIMINATOR I am running now: same script with the order swapped and a third read (original, signed, signed) - expect the first call to time out or be slow regardless of which VI, and the later ones to agree. ATTACK: (a) plausible? (b) does the PMC serial protocol echo or reply to the Configure init write in a way that leaves an unread line ('OK'?) in the buffer, so that reads are offset by one until flushed - and would a VISA buffer flush before the query fix it; (c) anything in the two-axis reply format ('POS x,y') that the driver's 8-digit substring [4,8] handles differently from a one-axis reply (it took the first 8 digits = X: fine?).

## Answer

The swapped-order run breaks the failed prediction cleanly: whichever VI reads first times out; every later read returns `000186A0`. The signed edit is exonerated.

- **(a) Plausible:** Yes. Error `-1073807339` is VISA timeout `0xBFFF0015`, consistent with a delayed first response. However, the test does **not** distinguish ?쐁ontroller wakes up once??from ?쏿ll reads remain one reply behind.??[NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L3mSAE&l=es-ES)

- **(b) Configure residue:** The PMC manual documents command-specific responses and ?쏯o-response?? it does not document generic echo or `OK`. So an init reply cannot be asserted without knowing Configure.vi?셲 exact write string. Request reporter output for that string, then look up that command?셲 response. An input-buffer flush discards already received bytes and is appropriate after Configure, but cannot discard a response that arrives afterward. The stronger sequence is: Configure ??wait >2 s ??flush RX ??`POS\r` ??read with a longer timeout. [PMC manual](https://s3.iautomatica.ru/uf/3cb/fujhb1pl558c4ozmuf7n1uuim22u67km/PMC-1_2HS_EN_User_DRW170814AF_20190424_W.pdf), [NI flush semantics](https://documentation.help/ni-visa/ControllingSerialIOBuffers.html)

- **Best discriminator:** Make successive replies distinguishable?봰uery `POS`, change position only if safely authorized, then query again?봮r inspect ?쐀ytes at port??immediately before each write. Repeating identical `POS` replies cannot prove whether reads are current or one-behind.

- **(c) Parsing:** `[4,8]` correctly selects the X field in both documented formats: one-axis `POS XXXXXXXX\r` and two-axis `POS XXXXXXXX,YYYYYYYY\r`. It ignores Y intentionally. The two-axis comma does not affect that substring. [PMC POS specification](https://s3.iautomatica.ru/uf/3cb/fujhb1pl558c4ozmuf7n1uuim22u67km/PMC-1_2HS_EN_User_DRW170814AF_20190424_W.pdf)

Bottom line: your explanation is strongly supported as a **first-transaction/session issue**, but ?쐋ate reply consumed by the next call??remains one of two live mechanisms until a flush-and-delay or distinguishable-response test separates it from simple wake-up latency.

## Sources

(extract from answer)

## What was done with it

Discriminator run (order swapped, hw_rotor_read.log run 2): the first read times out whichever VI asks, later reads agree - first-transaction artefact confirmed; the acceptance run then used distinguishable values (0 -> FFFFFFF6 -> 0), which rules out the one-behind mechanism the reviewer kept live. Verdict: correct.
