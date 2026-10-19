# ---
# labview: none
# hardware: none
# ---
"""Copy discussions that were only written to a local doc.md (Google login expired -> DEBATE-NO-DOC) into Google Docs.

User 2026-10-19: "구글 닥스에 기록되지 않은 것들도 옮겨두도록". One Google Doc per local doc.md, in the discussion folder
(debate_gdoc.FOLDER), title = the doc.md first line. The link is written next to the local doc as gdoc_url.txt, and a
directory that already has gdoc_url.txt is skipped, so a re-run only uploads what is new. The local doc.md is not changed.

Usage:
  py tools/debate_backfill.py [--root <dir with debate subdirs>] [--dry-run]
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debate_gdoc import FOLDER, GoogleDoc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ROOT = os.path.join(os.path.dirname(ROOT), "V6_lean", "tools", "bench", "debate")
CHUNK = 200000          # characters per append; a 74 KB doc.md goes in one call


def pending(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, "*", "doc.md"))):
        if not os.path.exists(os.path.join(os.path.dirname(p), "gdoc_url.txt")):
            out.append(p)
    return out


def upload(doc, path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    first = text.splitlines()[0].lstrip("# ").strip() if text.strip() else os.path.basename(os.path.dirname(path))
    url = doc.create(first + " [local record]", FOLDER)
    head = "Local record copied on 2026-10-19 from %s (Google login had expired when it ran)" % path
    for i in range(0, len(text), CHUNK):
        doc.append(head if i == 0 else "(continued)", text[i:i + CHUNK])
    with open(os.path.join(os.path.dirname(path), "gdoc_url.txt"), "w", encoding="utf-8") as f:
        f.write(url + "\n")
    return url


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    todo = pending(a.root)
    print("PENDING %d local docs under %s" % (len(todo), a.root), flush=True)
    done, failed = 0, []
    if not a.dry_run and todo:
        doc = GoogleDoc(interactive=False)
        for p in todo:
            try:
                print("UPLOADED %s -> %s" % (os.path.basename(os.path.dirname(p)), upload(doc, p)), flush=True)
                done += 1
            except Exception as e:                  # noqa - report and go on with the next doc
                failed.append(os.path.basename(os.path.dirname(p)))
                print("FAILED %s: %s" % (p, str(e)[:200]), flush=True)
    status = "PASS" if not failed else "FAIL"
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": status, "pending": len(todo), "uploaded": done,
                                  "failed": failed, "dry_run": a.dry_run}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
