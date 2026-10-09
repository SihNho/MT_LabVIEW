# ---
# labview: none
# hardware: none
# ---
"""Live Google Doc for a Claude-GPT discussion, written by this program (no LLM on the way, so it costs nothing).

User 2026-10-09: "두 에이전트 사이에서 디스커션 … 내가 실시간으로 확인하며 필요시 대화에 참여" · one Google Doc per topic in
the Drive folder the user made · "OAuth로 가자". The program drives tools/debate_relay.py one turn at a time:

  before each turn  read NEW comments on the doc:  '/stop' -> stop now (also kills a turn in progress through the relay's
                    STOP file) · '/end' -> finish after this point · '/continue' -> go on after a pause · anything else
                    -> the user's intervention, passed to both speakers (relay --user) and noted in the doc
  each turn         append "[n] Speaker (time)" as a heading + the message + its STATE line to the end of the doc
  converged / repeating  the doc gets a pause note; the program waits for '/continue' or '/end' (no fixed turn cap)

Auth (OAuth, desktop app): client file from the user env var GOOGLE_OAUTH_CLIENT_FILE; token cached at
~/.config/debate/token.json (delete it, or remove the app at myaccount.google.com/connections, to disconnect).
Scopes: documents + drive.file (only files this program creates or opens).

Usage:
  py tools/debate_gdoc.py login                                        # first time: opens a browser to consent
  py tools/debate_gdoc.py run --topic <file> --title "<doc title>" [--folder <id>] [--dir <local dir>] [relay opts]
  py tools/debate_gdoc.py selftest                                     # fake doc + fake comments + stub speakers
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = "1bcU3muvll71F2GGvF1HqqH4or8nIHkRE"          # the user's Drive folder for discussion docs (2026-10-09)
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"]
TOKEN = os.path.join(os.path.expanduser("~"), ".config", "debate", "token.json")


def creds():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES) if os.path.exists(TOKEN) else None
    if c and c.valid:
        return c
    if c and c.expired and c.refresh_token:
        try:
            c.refresh(Request())
            _save(c)
            return c
        except Exception:                          # noqa - expired consent (7 days in Testing): log in again
            pass
    client = os.environ.get("GOOGLE_OAUTH_CLIENT_FILE")
    if not client or not os.path.exists(client):
        raise SystemExit("GOOGLE_OAUTH_CLIENT_FILE is not set or the file is missing - set the user env var first")
    from google_auth_oauthlib.flow import InstalledAppFlow
    c = InstalledAppFlow.from_client_secrets_file(client, SCOPES).run_local_server(port=0)
    _save(c)
    return c


def _save(c):
    os.makedirs(os.path.dirname(TOKEN), exist_ok=True)
    with open(TOKEN, "w", encoding="utf-8") as f:
        f.write(c.to_json())


class GoogleDoc:
    """The real doc, through the Docs and Drive APIs."""

    def __init__(self):
        from googleapiclient.discovery import build
        c = creds()
        self.docs = build("docs", "v1", credentials=c, cache_discovery=False)
        self.drive = build("drive", "v3", credentials=c, cache_discovery=False)
        self.id = None

    def create(self, title, folder):
        meta = {"name": title, "mimeType": "application/vnd.google-apps.document"}
        if folder:
            meta["parents"] = [folder]
        try:
            f = self.drive.files().create(body=meta, fields="id,webViewLink").execute()
        except Exception as e:                      # noqa - drive.file may not reach a folder it did not create
            if not folder:
                raise
            print("FOLDER NOT REACHABLE (%s) - creating the doc in My Drive instead" % str(e)[:160], flush=True)
            meta.pop("parents")
            f = self.drive.files().create(body=meta, fields="id,webViewLink").execute()
        self.id = f["id"]
        return f["webViewLink"]

    def append(self, heading, body):
        """Heading (HEADING_3) + body at the end of the doc, guarded by the revision read just before it."""
        d = self.docs.documents().get(documentId=self.id, fields="revisionId,body.content(endIndex)").execute()
        end = d["body"]["content"][-1]["endIndex"] - 1
        text = heading + "\n" + body.rstrip() + "\n\n"
        reqs = [{"insertText": {"location": {"index": end}, "text": text}},
                {"updateParagraphStyle": {"range": {"startIndex": end, "endIndex": end + len(_u16(heading)) + 1},
                                          "paragraphStyle": {"namedStyleType": "HEADING_3"}, "fields": "namedStyleType"}},
                {"updateParagraphStyle": {"range": {"startIndex": end + len(_u16(heading)) + 1,
                                                    "endIndex": end + len(_u16(text))},
                                          "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}, "fields": "namedStyleType"}}]
        self.docs.documents().batchUpdate(documentId=self.id, body={
            "requests": reqs, "writeControl": {"requiredRevisionId": d["revisionId"]}}).execute()

    def comments(self):
        r = self.drive.comments().list(fileId=self.id, fields="comments(id,content,resolved)", pageSize=100).execute()
        return [(c["id"], c.get("content", "")) for c in r.get("comments", []) if not c.get("resolved")]

    def reply(self, comment_id, text):
        self.drive.replies().create(fileId=self.id, commentId=comment_id, body={"content": text},
                                    fields="id").execute()


def _u16(s):
    """Docs indexes count UTF-16 code units; len(_u16(s)) is that count."""
    return s.encode("utf-16-le")[1::2]


class FakeDoc:
    """Self-test stand-in: a local markdown file + a local comments.json the test writes into."""

    def __init__(self, d):
        self.d, self.id = d, "fake"

    def create(self, title, folder):
        open(os.path.join(self.d, "doc.md"), "w", encoding="utf-8").write("# %s\n\n" % title)
        return "file://" + os.path.join(self.d, "doc.md")

    def append(self, heading, body):
        with open(os.path.join(self.d, "doc.md"), "a", encoding="utf-8") as f:
            f.write("### %s\n%s\n\n" % (heading, body.rstrip()))

    def comments(self):
        p = os.path.join(self.d, "comments.json")
        return [tuple(x) for x in json.load(open(p, encoding="utf-8"))] if os.path.exists(p) else []

    def reply(self, comment_id, text):
        with open(os.path.join(self.d, "replies.log"), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (comment_id, text))


GEMINI_BRIEF = (
    "You are an external fact-checker for a discussion between two other AI models about a LabVIEW project. You cannot "
    "see the project; you check only facts that live OUTSIDE it (LabVIEW, NI or library behaviour, published specs) using "
    "the web. For each factual claim or question below: verdict 맞음 / 틀림 / 확인 불가, one or two sentences why, and the "
    "source URL. A verdict without a source URL counts as 확인 불가. Write in Korean, short. Do not judge who wins the "
    "discussion and do not give project advice.")


def gemini_check(a, question, recent):
    """One web fact-check by Gemini (agy --mode plan, prompt on stdin, run from an empty temp dir as tools/peer.ps1
    does). The relay's STOP file kills it like a speaker. -> text (never raises)."""
    if a.stub:
        return "가짜 외부 검토: '%s' -> 확인 불가 (가짜)" % question[:60]
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import debate_relay
    prompt = "%s\n\n## 확인할 질문\n%s\n\n## 최근 발언 (주장 출처)\n%s" % (GEMINI_BRIEF, question, recent[-6000:])
    exe = os.path.join(os.environ.get("LOCALAPPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Local")),
                       "agy", "bin", "agy.exe")
    cmd = [exe, "--mode", "plan", "--print-timeout", "%ds" % a.gemini_timeout, "--model", a.gemini_model]
    rc, out, err, stopped = debate_relay.run_killable(cmd, tempfile.mkdtemp(prefix="gemini_"), prompt, dict(os.environ),
                                                      os.path.join(a.dir, "STOP"), timeout=a.gemini_timeout + 60)
    if stopped:
        return "(외부 검토 중단됨: 멈춤 요청)"
    return (out or "").strip() or "(외부 검토 실패 rc=%s: %s)" % (rc, (err or "")[-300:])


def chat_inbox(d):
    """The user's chat messages, written by the chat with `debate_gdoc.py say` (user 2026-10-09: "채팅으로 넣어줘 …
    폰으로는 보기만"). Same commands as Doc comments. -> [(id, text)]"""
    p = os.path.join(d, "chat_inbox.jsonl")
    out = []
    if os.path.exists(p):
        for i, line in enumerate(open(p, encoding="utf-8")):
            try:
                out.append(("chat-%d" % i, json.loads(line)["text"]))
            except (ValueError, KeyError):
                continue
    return out


def say(d, text):
    """Queue one chat message for the running discussion; '/stop' also writes the relay STOP file at once."""
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "chat_inbox.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "text": text}, ensure_ascii=False) + "\n")
    if text.strip().lower() == "/stop":
        open(os.path.join(d, "STOP"), "w").close()


def relay_step(a, user, first_topic, note=""):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "debate_relay.py"), "round" if a.mode == "rounds" else "step",
           "--dir", a.dir, "--first", a.first]
    if first_topic:
        cmd += ["--topic", a.topic]
    if user:
        cmd += ["--user", user]
    if note:
        cmd += ["--note", note]
    if a.stub:
        cmd += ["--stub", "--stub-secs", str(a.stub_secs)]
    for k in ("claude_effort", "gpt_effort", "gpt_model", "gpt_sandbox"):
        if getattr(a, k, None):
            cmd += ["--" + k.replace("_", "-"), str(getattr(a, k))]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [x for x in r.stdout.splitlines() if x.startswith("{")]
    if not lines:
        return {"error": (r.stderr or r.stdout)[-400:]}
    return json.loads(lines[-1])


def run(a, doc=None):
    os.makedirs(a.dir, exist_ok=True)
    doc = doc or GoogleDoc()
    resuming = bool(getattr(a, "doc_id", None))
    if resuming:                               # same doc, same relay state: continue where the last run stopped
        doc.id = a.doc_id
        note_text = a.resume_note
        if note_text.startswith("@") and os.path.exists(note_text[1:]):      # @file: keeps launch scripts ASCII
            note_text = open(note_text[1:], encoding="utf-8-sig").read().strip()
        doc.append("중계 재개 (%s)" % time.strftime("%H:%M"), note_text or "이어서 진행합니다.")
        print("DOC resumed %s" % a.doc_id, flush=True)
    else:
        url = doc.create(a.title, a.folder)
        print("DOC %s" % url, flush=True)
        doc.append("주제", open(a.topic, encoding="utf-8-sig").read())
    seen, stop_file, first, paused = set(), os.path.join(a.dir, "STOP"), not resuming, False
    if resuming:                               # comments and chat lines handled by the earlier run stay handled
        seen.update(cid for cid, _ in doc.comments() + chat_inbox(a.dir))
    recent, checks, note = [], [], ""          # recent turn texts; pending Gemini questions; Gemini result for next turn
    while True:
        user, cmds = [], set()
        for cid, text in doc.comments() + chat_inbox(a.dir):
            if cid in seen:
                continue
            seen.add(cid)
            t = text.strip()
            reply = doc.reply if not cid.startswith("chat-") else (lambda _c, _t: None)   # chat lines get no doc reply
            if t.lower() in ("/stop", "/end", "/continue"):
                cmds.add(t.lower())
                reply(cid, "받았습니다: %s" % t)
            elif t.lower().startswith("/gemini"):
                checks.append(t[len("/gemini"):].strip() or "직전 두 발언에서 외부 사실에 기대는 주장을 모두 확인")
                reply(cid, "Gemini 외부 검토를 요청했습니다.")
            else:
                user.append(t)
                reply(cid, "다음 발언부터 양쪽에 전달합니다.")
        if "/stop" in cmds or "/end" in cmds:
            open(stop_file, "w").close()
            doc.append("중계 종료 (%s)" % time.strftime("%H:%M"), "사용자 요청 %s" % " ".join(sorted(cmds)))
            print("END by user %s" % sorted(cmds), flush=True)
            return 0
        if checks and not os.path.exists(stop_file):
            q = "\n".join("- " + c for c in checks)
            checks = []
            print("GEMINI %s" % q[:120].replace("\n", " "), flush=True)
            res = gemini_check(a, q, "\n\n".join(recent[-2:]))
            doc.append("[외부 검토] Gemini (%s)" % time.strftime("%H:%M"), "질문:\n%s\n\n%s" % (q, res))
            note = (note + "\n" + res).strip()
        if paused and not user and not note and "/continue" not in cmds:
            time.sleep(a.poll)
            continue
        paused = False
        if user:
            doc.append("사용자 개입 반영 (%s)" % time.strftime("%H:%M"), "\n".join(user))
        r = relay_step(a, "\n".join(user), first, note)
        first, note = False, ""
        if r.get("error"):
            doc.append("중계 오류 (%s)" % time.strftime("%H:%M"), r["error"])
            print("ERROR %s" % r["error"][:200], flush=True)
            return 1
        if r.get("stopped"):
            doc.append("중단됨 (%s)" % time.strftime("%H:%M"), "발언 도중 멈춤 요청으로 끊었습니다.")
            print("STOPPED", flush=True)
            return 0
        turns = ([(n, r["files"][n], r["states"].get(n) or {}) for n in ("Claude", "GPT")] if "files" in r
                 else [(r["speaker"], r["file"], r.get("state") or {})])
        for who, path, s in turns:
            text = open(path, encoding="utf-8").read()
            head, _, body = text.partition("\n")
            doc.append(head.strip(), body.strip())
            recent.append(body.strip())
            if s.get("check"):
                checks.append("%s의 요청: %s" % (who, s["check"]))
        print("ROUND %s" % r["round"] if "round" in r else "TURN %s %s" % (r["turn"], r["speaker"]), flush=True)
        if r.get("converged") or r.get("repeating"):
            why = ("두 토론자가 모두 끝났다고 했고 서로에게 남은 질문이 없습니다" if r.get("converged")
                   else "같은 쟁점이 세 번 되풀이됐습니다")
            doc.append("일시 정지 (%s)" % time.strftime("%H:%M"),
                       "%s. 계속하려면 댓글에 /continue 또는 지시를, 끝내려면 /end 를 남겨 주세요." % why)
            paused = True
            print("PAUSED %s" % why, flush=True)


def selftest():
    import tempfile
    import threading
    d = tempfile.mkdtemp(prefix="gdoc_selftest_")
    topic = os.path.join(d, "topic.md")
    open(topic, "w", encoding="utf-8").write("시험 주제")
    ap = parser()
    a = ap.parse_args(["run", "--topic", topic, "--title", "selftest", "--dir", os.path.join(d, "relay"), "--stub",
                       "--stub-secs", "1", "--poll", "0.5"])
    fd = FakeDoc(d)
    cpath = os.path.join(d, "comments.json")

    def later(sec, comments):
        threading.Timer(sec, lambda: json.dump(comments, open(cpath, "w", encoding="utf-8"), ensure_ascii=False)).start()
    later(1.5, [["c1", "하드웨어는 빼고 이야기해"]])
    threading.Timer(4.0, lambda: say(os.path.join(d, "relay"), "채팅에서 온 지시")).start()
    later(7.0, [["c1", "하드웨어는 빼고 이야기해"], ["c3", "/gemini 로컬 변수 읽기 순서"]])
    later(11.0, [["c1", "하드웨어는 빼고 이야기해"], ["c3", "/gemini 로컬 변수 읽기 순서"], ["c2", "/end"]])
    rc = run(a, fd)
    doc = open(os.path.join(d, "doc.md"), encoding="utf-8").read()
    reps = open(os.path.join(d, "replies.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "replies.log")) else ""
    ok = [("G1 doc has the topic and at least two turns", doc.count("] Claude") >= 1 and doc.count("] GPT") >= 1),
          ("G2 the comment became an intervention note in the doc", "사용자 개입 반영" in doc),
          ("G3 a speaker heard it", "사용자 지시 반영" in doc),
          ("G4 the comment got a reply", "c1" in reps),
          ("G5 convergence paused the run", "일시 정지" in doc),
          ("G6 /end finished it", "중계 종료" in doc and rc == 0),
          ("G7 a speaker's STATE check started a Gemini review", "Claude의 요청" in doc or "GPT의 요청" in doc),
          ("G8 the next speaker got the review as evidence", "외부 검토 반영" in doc),
          ("G9 a /gemini comment started a review", "로컬 변수 읽기 순서" in doc and "[외부 검토] Gemini" in doc),
          ("G10 a chat message reached the discussion", "채팅에서 온 지시" in doc)]
    for n, g in ok:
        print("%s  %s" % ("PASS" if g else "FAIL", n))
    print("RESULT %s" % json.dumps({"schema": "result-line/1", "status": "PASS" if all(g for _, g in ok) else "FAIL",
                                     "gates": {"pass": sum(g for _, g in ok), "fail": sum(not g for _, g in ok)}}))
    return 0 if all(g for _, g in ok) else 1


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("login", "run", "say", "selftest"))
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--topic")
    ap.add_argument("--title", default="Claude–GPT 토론 " + time.strftime("%Y-%m-%d %H:%M"))
    ap.add_argument("--folder", default=FOLDER)
    ap.add_argument("--dir")
    ap.add_argument("--first", choices=("claude", "gpt"), default="claude")
    # user 2026-10-09: "클로드와 GPT가 같은 단계에서 서로에게 질문하고 피드백하며 수렴" -> both write each round at once
    ap.add_argument("--mode", choices=("rounds", "turns"), default="rounds")
    ap.add_argument("--poll", type=float, default=15)
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--stub-secs", type=float, default=3)
    ap.add_argument("--claude-effort")
    ap.add_argument("--gpt-effort")
    ap.add_argument("--gpt-model")
    # user 2026-10-09: "전체접근으로 키고 (어차피 코드베이스 읽어야 하니)" - GPT runs in the V6_debate worktree, read-only by instruction
    ap.add_argument("--gpt-sandbox", default="danger-full-access")
    ap.add_argument("--doc-id", help="resume: keep writing into this existing doc (relay state in --dir)")
    ap.add_argument("--resume-note", default="")
    ap.add_argument("--gemini-model", default="gemini-3.1-pro-high")   # the fact-chain model of tools/peer.ps1
    ap.add_argument("--gemini-timeout", type=int, default=600)
    return ap


def main(argv=None):
    a = parser().parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "say":
        if not a.dir or not a.text:
            raise SystemExit('say needs --dir and the text')
        say(a.dir, a.text)
        print("QUEUED %s" % a.text[:80])
        return 0
    if a.cmd == "login":
        creds()
        print("LOGIN OK - token at %s" % TOKEN)
        return 0
    if not a.topic or not a.dir:
        raise SystemExit("run needs --topic and --dir")
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
