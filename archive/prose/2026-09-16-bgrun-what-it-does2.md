# bgrun-what-it-does2

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** prose
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (8s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

`tools/bgrun.py`는 백그라운드로 도는 명령에 마감시한을 강제로 걸어주는 실행기다.
`py tools/bgrun.py --max-min 5 --log tools/bench/x.log -- py -u <script>` 형태로 부르면, 자식 프로세스 트리 전체를 5분 뒤에 죽인다.
끝날 때는 어떤 경우든 로그 마지막 줄에 `BGRUN END rc=<n> after <초>s` 또는 `BGRUN TIMEOUT killed after <초>s`를 쓴다.
이 마지막 줄이 있기 때문에, 로그가 조용한 것과 프로세스가 죽어서 아무것도 못 쓴 것을 구분할 수 있다.
2026-09-05에 백그라운드 작업 하나가 3시간 48분 동안 멈춰 있었던 게 이 도구를 만든 이유이고, `tools/hooks/guard_bash.py`가 이 경로를 거치지 않는 백그라운드 실행을 거부한다.


## Answer

`tools/bgrun.py`는 백그라운드에서 실행되는 명령에 마감 시간을 강제로 적용하는 실행기다.
`py tools/bgrun.py --max-min 5 --log tools/bench/x.log -- py -u <script>` 형식으로 실행하면, 5분 뒤에 자식 프로세스 트리 전체를 종료한다.
종료될 때는 어떤 경우든 로그의 마지막 줄에 `BGRUN END rc=<n> after <초>s` 또는 `BGRUN TIMEOUT killed after <초>s`를 기록한다.
이 마지막 줄 덕분에 로그가 조용한 경우와 프로세스가 종료되어 아무것도 기록하지 못한 경우를 구분할 수 있다.
2026-09-05에 백그라운드 작업 하나가 3시간 48분 동안 멈춰 있었던 일이 이 도구를 만든 계기이며, `tools/hooks/guard_bash.py`는 이 경로를 거치지 않는 백그라운드 실행을 거부한다.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
