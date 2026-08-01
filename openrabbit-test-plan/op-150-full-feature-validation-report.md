# OP-150 Full OpenRabbit Feature Validation Report

Date: 2026-08-01

OpenRabbit version: `1.9.0`

Testing issue: `https://github.com/Sohail-Shaikh-07/testing-openrabbit/issues/11`

Testing PR: `https://github.com/Sohail-Shaikh-07/testing-openrabbit/pull/12`

Final tested head: `fc0b6f3fa9cdbad54239b6cecfdde0452b4409c7`

## Summary

- Passed areas: 14
- Failed product behaviors: 2
- Environment-blocked areas: 2
- Testing app: 8 tests passed
- GitHub CI: no checks configured in `testing-openrabbit`

The installed OpenRabbit CLI completed the main review, interactive, publishing,
memory, connector, eval, maintenance, and slash-command workflows against a live
pull request. Two production issues were found and filed. Raw command logs remain
untracked under `openrabbit-test-plan/logs/op-150/`.

## Command Results

| Area | Command or flow | Result | Evidence |
| --- | --- | --- | --- |
| App quality | Ruff, Black, mypy, pytest, build | Pass | Tracked `app` and `tests` clean; 8 tests passed; sdist and wheel built |
| CLI | Version and command help | Pass | Installed version is `1.9.0`; expected command surface is present |
| Model | `model-health` | Pass | OpenAI `gpt-4.1-mini` returned reachable |
| Connectors | `connector-health` | Pass | MCP, web search, multi-repo, Jira, and Linear safely reported disabled |
| Index | `index` | Blocked | Local Qdrant connection unavailable; command failed clearly |
| Review | Incremental and full dry-run | Pass | Both modes completed with zero findings and diff-only RAG fallback |
| Re-review | Review after second commit | Pass | New head and previous review SHA were detected correctly |
| Interactive | `describe`, `ask`, `improve`, `labels` | Pass | Structured JSON included schema, PR metadata, evidence, and controls |
| Publishing | Managed `describe` and `ask` | Pass | Second runs updated comment IDs `5150416459` and `5150416483` |
| PR commands | Slash command matrix | Pass with retry | Summary, review, full review, ask, improve, learn, pause, resume, and ignore were exercised |
| Memory | PR memory and learnings | Pass | PR head stored; new repository learning persisted as learning ID 4 |
| Eval | Single-PR evaluation | Pass | One PR evaluated, zero failures, JSON and Markdown generated locally |
| Maintenance | Changelog, docs, similar issues | Pass | Commands stayed read-only and returned workflow controls |
| Labels | Dry-run and apply | Pass | Existing `bug` label applied; missing `tests` label skipped; temporary label removed |
| Daemon | Foreground start and cross-terminal stop | Fail | Live PID was treated as stale and daemon kept running |

## Findings

### Windows daemon stop

`openrabbit start` wrote live Python PID `11008` to `.openrabbit/daemon.json`.
`openrabbit stop --workspace .` reported that PID as stale, removed the metadata,
and left the process running. The foreground process was cleaned up with Ctrl+C.

Tracked in `https://github.com/Sohail-Shaikh-07/openrabbit/issues/281`.

### Failed command cursor

GitHub returned `401 Bad credentials` while `/openrabbit ask` was being handled.
The command cursor still advanced to comment `5150419485`, so credential recovery
continued with later comments and did not retry the failed ask command. A fresh ask
comment was required to complete validation.

Tracked in `https://github.com/Sohail-Shaikh-07/openrabbit/issues/282`.

### Improvement quality

After the first useful `improve` suggestion was applied, a second run returned a
no-op suggestion asking for a type hint that was already present. The command was
operational, but suggestion filtering should eventually reject already-satisfied
advice.

## Environment Notes

- RAG indexing was unavailable because the local Qdrant endpoint could not be reached.
- Review, describe, ask, improve, and eval degraded to diff-only context successfully.
- Repository-wide Ruff and Black include old untracked test fixtures with known format
  errors. Checks scoped to the tracked application and tests passed.
- The active `GITHUB_TOKEN` became invalid during polling. The authenticated GitHub CLI
  keyring credential was used to complete the test without exposing token values.
- The testing repository has no GitHub status checks configured for PR #12.

## Plan Corrections

The execution pass corrected three stale command examples in the OP-149 plan:

- Full review uses `--mode full`, not `--full`.
- `ask` accepts the question as a positional argument, not `--question`.
- `eval` selects pull requests with `--prs`, not `--pr`.

## Final Assessment

OpenRabbit v1.9.0 passes the broad functional validation surface, including slash
commands and managed publishing. The Windows daemon stop bug and failed-command cursor
bug should be fixed before treating daemon polling as fully production-ready on Windows.
