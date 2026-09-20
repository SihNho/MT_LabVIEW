---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# agy-permissions-schema

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ERROR (64s)
- **why asked:** agy headless auto-denies all tools; need the real permissions.allow schema and file location.
- **verdict:** adopted

## Question

The Antigravity CLI (command 'agy', Google's successor to gemini-cli for individual accounts, config directory ~/.gemini) auto-denies tool use in headless print mode with messages like: 'a tool required the read_file permission that headless mode cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. read_file(<target>)). Alternatively, re-run with --dangerously-skip-permissions'. Questions: (1) What is the exact settings.json schema for permissions.allow in the Antigravity CLI - file location (user-level ~/.gemini/settings.json vs project .gemini/settings.json), rule syntax (bare tool name? name(target-glob)?), and the canonical tool names for file reading, directory listing, file search, web search, and web fetch? (2) Does an interactive session's 'always allow' choice persist rules to settings.json, and where? (3) Any official docs page for Antigravity CLI settings/permissions? Search the web including Google's docs, GitHub (google-gemini or google antigravity repos), and community posts; cite URLs.

## Answer

## Findings

### 1. Exact `permissions.allow` schema

For Antigravity CLI (`agy`), the documented user-level file is:

```text
~/.gemini/antigravity-cli/settings.json
```

?봭ot Gemini CLI?셲 `~/.gemini/settings.json`. Google?셲 AGY CLI settings and headless-mode pages both specify the Antigravity-specific path. [AGY CLI settings](https://www.agy.dev/docs/cli/using/), [headless permissions](https://www.agy.dev/docs/cli/headless/)

The schema is:

```json
{
  "permissions": {
    "allow": [
      "read_file(path-or-directory)",
      "read_url(domain)"
    ]
  }
}
```

Rules are strings in `action(target)` form. A bare tool/action name such as `"read_file"` is not the documented syntax. The global wildcard goes inside the parentheses, such as `read_file(*)` or `read_url(*)`. [Official permissions reference](https://www.agy.dev/docs/permissions/)

Examples:

```json
{
  "permissions": {
    "allow": [
      "read_file(G:/Codes/MyProject)",
      "read_url(ni.com)",
      "read_url(github.com)"
    ]
  }
}
```

`read_file(directory)` recursively authorizes files and directories underneath that target. Targets may be absolute or relative to a workspace root. On Windows, Antigravity documents normalization that removes drive letters and converts backslashes to forward slashes before matching, although using normalized forward-slash paths is the least ambiguous choice. [Official matching rules](https://www.agy.dev/docs/permissions/)

#### Canonical permission actions

The important distinction is between an internal tool name and the permission action which governs it:

| Operation | Internal tool names observed | `permissions.allow` action |
|---|---|---|
| Read a file | `view_file` / UI ?쏳ead??| `read_file(path)` |
| List a directory | `list_directory` / `list_dir` | `read_file(directory)` |
| Search file contents | `search_directory` / `grep_search` | `read_file(directory)` |
| Find files by name | `find_file` / `find_by_name` | `read_file(directory)` |
| Web search | `search_web` | `read_url(domain)` |
| Fetch webpage contents | `read_url_content` | `read_url(domain)` |

The official permissions schema does **not** define separate `list_directory`, `find_file`, `search_web`, or `web_fetch` permission actions. Its complete supported-action table lists `read_file`, `write_file`, `read_url`, `execute_url`, `command`, `unsandboxed`, and `mcp`. [Official supported actions](https://www.agy.dev/docs/permissions/)

Google?셲 Antigravity SDK enumerates internal tools including `list_directory`, `search_directory`, `find_file`, `view_file`, `search_web`, and `read_url_content`; these are tool identifiers, not valid `permissions.allow` action names. [Antigravity SDK tool enum](https://github.com/google-antigravity/antigravity-sdk-python/blob/main/google/antigravity/types.py)

For web access, the official documentation explicitly says that the internal `read_url_content` tool is authorized through `read_url(domain)`. The same permission also governs loading domains for browser research; browser interaction such as clicking or typing instead requires `execute_url(domain)`. [Official `read_url` explanation](https://www.agy.dev/docs/permissions/)

For unrestricted read-only research, the broad configuration would therefore be:

```json
{
  "permissions": {
    "allow": [
      "read_file(*)",
      "read_url(*)"
    ]
  }
}
```

That grants reading across the system and outbound access to every domain, so narrower directory/domain rules are safer.

#### User versus project settings

The official AGY headless documentation only promises the global file:

```text
~/.gemini/antigravity-cli/settings.json
```

I found no official AGY documentation saying that `agy -p` reads `project/.gemini/settings.json`. That path belongs to the separate Gemini CLI configuration system. [Gemini CLI settings documentation](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md)

A recent Antigravity issue reports testing project-local permission scopes and finding that headless mode only used the fixed global Antigravity settings file. Treat that as user-reported behavior, not a contractual guarantee. [Antigravity CLI issue #627](https://github.com/google-antigravity/antigravity-cli/issues/627)

### 2. Does interactive ?쏿lways allow??persist?

Intended behavior: yes, when the prompt explicitly says something equivalent to:

```text
Yes, and always allow ??(Persist to settings.json)
```

That option is intended to add a persistent rule to the global Antigravity settings file. A Windows report confirms rules being written to:

```text
C:\Users\<user>\.gemini\antigravity-cli\settings.json
```

and displayed under `/permissions` as global rules. [Antigravity CLI issue #619](https://github.com/google-antigravity/antigravity-cli/issues/619)

Actual behavior appears version/platform-dependent and buggy:

- Issue #619 reports that the rules were written and loaded, but specific `command(...)` rules still did not prevent later prompts on Windows; only `command(*)` worked. [Issue #619](https://github.com/google-antigravity/antigravity-cli/issues/619)
- Issue #548 reports that the interactive ?쏱ersist to settings.json??selection wrote nothing?봳he file remained byte-identical?봞nd that headless mode ignored manually added rules. That report concerns Windows and remains an open issue, so it is evidence of a defect rather than documentation of intended behavior. [Issue #548](https://github.com/google-antigravity/antigravity-cli/issues/548)

Therefore: **it is supposed to persist globally, but do not assume it succeeded. Verify the global file immediately afterward and test a harmless matching operation in a fresh session.**

### 3. Official documentation

Yes:

- [Antigravity permissions and rule syntax](https://www.agy.dev/docs/permissions/)
- [Antigravity headless mode and `permissions.allow`](https://www.agy.dev/docs/cli/headless/)
- [AGY CLI settings and configuration-file location](https://www.agy.dev/docs/cli/using/)
- [Official Antigravity CLI GitHub repository](https://github.com/google-antigravity/antigravity-cli)

The clearest answer is: use `~/.gemini/antigravity-cli/settings.json`, use `action(target)` rules, and authorize filesystem inspection with `read_file(...)` and web research/fetching with `read_url(...)`. Do not copy Gemini CLI?셲 separate `~/.gemini/settings.json`, `toolPermissions`, or policy-file schema into AGY.

## Sources

(extract from answer)

## What was done with it

Answer verified against agy.dev by direct WebFetch: path, action(target) syntax, and Windows drive-letter normalization all confirmed accurate (the wrapper's ERROR classification was a false positive from the answer quoting agy's error text - regex narrowed). Applying the schema still did not unblock agy in practice; see the perm-allowlist-test series for the closure.
