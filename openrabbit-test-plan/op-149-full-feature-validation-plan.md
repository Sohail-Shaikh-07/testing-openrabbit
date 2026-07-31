# OP-149 Full OpenRabbit Feature Validation Plan

Date: 2026-08-01

Repository under test: `Sohail-Shaikh-07/openrabbit`

Testing repository: `Sohail-Shaikh-07/testing-openrabbit`

Local testing folder: `D:\My work\Professional\testing-openrabbit`

Tracker issue: `https://github.com/Sohail-Shaikh-07/testing-openrabbit/issues/9`

## Goal

Validate OpenRabbit end to end against the testing repository before continuing v1.10 implementation work. The pass should cover old features, v1.5 through v1.9 features, command safety defaults, GitHub publishing behavior, and the current installed package.

## Safety Rules

- Run all destructive or mutating tests only against `Sohail-Shaikh-07/testing-openrabbit`.
- Keep generated logs, JSON outputs, and screenshots under `openrabbit-test-plan/logs/`.
- Do not commit test logs unless a later task explicitly asks for evidence artifacts.
- Prefer dry-run commands first, then repeat with publish or apply flags only where the plan says to do so.
- Never use production repositories for publish, label apply, daemon, or managed comment checks.
- Use `/openrabbit ...` for PR comment commands. `@openrabbit ...` may be checked only as legacy compatibility.

## Test Objects

Use issue #9 as the planning tracker. For the actual feature execution pass, create a separate live validation issue and PR with a small intentional code change so review, describe, ask, improve, labels, changelog, docs, and similar issue flows all have realistic PR data.

Suggested live objects:

- Issue title: `[OpenRabbit Test] Full feature validation`
- Branch: `openrabbit-test/full-feature-validation`
- PR title: `[OpenRabbit Test] Full feature validation`
- Linked issue phrase in PR body: `Closes #<issue-number>`

## Step 1 - Prepare Local Baseline

Run from `D:\My work\Professional\testing-openrabbit`.

```powershell
git checkout main
git pull origin main
git status --short --branch
openrabbit --version
openrabbit --help
```

Expected result:

- Branch is `main`.
- Only known testing artifacts are untracked.
- `openrabbit --version` reports the installed OpenRabbit release under test.
- Help output lists the current command surface.

## Step 2 - Create The Live Validation Issue

```powershell
gh issue create `
  --repo Sohail-Shaikh-07/testing-openrabbit `
  --title "[OpenRabbit Test] Full feature validation" `
  --body "Tracks the end-to-end OpenRabbit validation pass across review, interactive PR commands, memory, connectors, eval, daemon, and maintenance automation."
```

Record:

- Issue number
- Issue URL
- Labels applied

## Step 3 - Create The Live Validation Branch And PR

Create a small but realistic code change in the testing app. The change should touch application code and tests so OpenRabbit has meaningful review context.

Suggested change:

- Add a small field validation rule in `app/`.
- Add or update one matching test in `tests/`.
- Keep the change intentionally reviewable and low risk.

```powershell
git checkout -b openrabbit-test/full-feature-validation
python -m pytest
git add app tests
git commit -m "test: prepare openrabbit full feature validation"
git push -u origin openrabbit-test/full-feature-validation
```

Open the PR:

```powershell
gh pr create `
  --repo Sohail-Shaikh-07/testing-openrabbit `
  --base main `
  --head openrabbit-test/full-feature-validation `
  --title "[OpenRabbit Test] Full feature validation" `
  --body "Closes #<issue-number>`n`nThis PR is used to validate OpenRabbit old and new features end to end."
```

Record:

- PR number
- PR URL
- Head SHA

## Step 4 - Verify Testing App Quality Gates

```powershell
ruff check .
black --check .
mypy app tests
python -m pytest
```

Expected result:

- All testing app checks pass, or any intentional failures are documented as part of a review-quality scenario.

## Step 5 - Verify Core OpenRabbit CLI Commands

```powershell
openrabbit --version
openrabbit --help
openrabbit init --help
openrabbit model-health --help
openrabbit install-model --help
openrabbit connector-health --workspace .
```

Expected result:

- Commands exit successfully.
- Help text is readable.
- `connector-health` reports disabled or configured connectors without leaking secrets.

## Step 6 - Verify Repository Index And Context Commands

```powershell
openrabbit index --workspace .
openrabbit review --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --dry-run
openrabbit review --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --full --dry-run
```

Expected result:

- Indexing completes or fails with a clear local dependency message.
- Review dry-run produces grounded findings or a clear no-findings summary.
- Full review works without requiring publish mode.

## Step 7 - Verify Interactive PR Workflows

Run read-only output first.

```powershell
openrabbit describe --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json
openrabbit ask --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --question "What is the most important risk in this PR?" --format json
openrabbit improve --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json
openrabbit labels --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json
```

Then test managed publishing where safe.

```powershell
openrabbit describe --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --publish
openrabbit ask --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --question "Summarize the validation risk." --publish
```

Expected result:

- JSON outputs include `schema_version`, `command`, PR metadata, and workflow controls where applicable.
- Managed comments update in place on repeated runs.
- Label command remains read-only unless `--apply` is used.

## Step 8 - Verify PR Comment Commands

Post comments on the live validation PR and run the daemon once.

Commands to test:

- `/openrabbit summary`
- `/openrabbit review`
- `/openrabbit full review`
- `/openrabbit ask What changed in this PR?`
- `/openrabbit improve`
- `/openrabbit learn Prefer explicit validation errors in API handlers.`
- `/openrabbit pause`
- `/openrabbit resume`
- `/openrabbit ignore`

Execution:

```powershell
openrabbit start --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --once
```

Expected result:

- Slash commands are parsed.
- Legacy mention syntax remains compatible only where intentionally supported.
- Pause, resume, and ignore update command state without breaking later commands.
- Learn command persists memory without leaking raw secrets or unrelated content.

## Step 9 - Verify Memory Features

```powershell
openrabbit memory --workspace . --help
openrabbit memory --workspace . --repo Sohail-Shaikh-07/testing-openrabbit --format json
```

Expected result:

- Memory commands show stored review history and learnings if present.
- Output is bounded and does not expose credentials.

## Step 10 - Verify Connector Intelligence

Run connector checks with the local test config.

```powershell
openrabbit connector-health --workspace .
```

If connector fixtures are configured, validate:

- MCP connector health
- MCP web search disabled or configured behavior
- Jira read/write boundary reporting
- Linear read/write boundary reporting
- Multi-repo context using only approved sibling paths

Expected result:

- Disabled connectors fail open.
- Missing credentials are reported clearly.
- No raw tokens appear in output.

## Step 11 - Verify Context Precision And Eval

```powershell
openrabbit review --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --dry-run
openrabbit eval --workspace . --repo Sohail-Shaikh-07/testing-openrabbit --pr <pr-number>
```

Expected result:

- Review output includes focused changed-file context.
- Eval output is generated locally.
- Context diagnostics are bounded and do not contain raw secrets.

## Step 12 - Verify Maintenance Automation From v1.9

Read-only checks:

```powershell
openrabbit labels --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json
openrabbit changelog --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json --limit 10
openrabbit docs --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json --limit 20
openrabbit similar-issues --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --format json --limit 5
```

Optional mutation check:

```powershell
openrabbit labels --pr <pr-number> --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --apply
```

Expected result:

- Read-only commands do not mutate files or GitHub.
- `workflow_controls` reports dry-run and permission behavior.
- `labels --apply` only applies labels that already exist in the repository.
- Changelog, docs, and similar issue commands remain read-only.

## Step 13 - Verify Daemon Lifecycle

One-shot polling:

```powershell
openrabbit start --repo Sohail-Shaikh-07/testing-openrabbit --workspace . --once
```

Foreground stop test:

1. Terminal A:

```powershell
openrabbit start --repo Sohail-Shaikh-07/testing-openrabbit --workspace .
```

2. Terminal B:

```powershell
openrabbit stop --workspace .
```

Expected result:

- `.openrabbit/daemon.json` is written while the daemon is active.
- `openrabbit stop --workspace .` stops the running daemon.
- Stale daemon metadata is cleaned up safely.

## Step 14 - Verify GitHub Actions Examples

If workflow files are enabled in the testing repository, manually dispatch relevant workflows:

- Review workflow
- Interactive workflow
- Maintenance workflow

Expected result:

- Workflows install OpenRabbit.
- Commands run against the testing PR only.
- Required permissions match the command being tested.

## Step 15 - Capture Evidence

For every command, save output under:

```text
openrabbit-test-plan/logs/op-149/
```

Suggested filenames:

- `01-version.txt`
- `02-review-dry-run.txt`
- `03-describe.json`
- `04-ask.json`
- `05-improve.json`
- `06-labels.json`
- `07-changelog.json`
- `08-docs.json`
- `09-similar-issues.json`
- `10-start-once.txt`
- `11-stop-foreground.txt`

Do not commit these logs unless a later task explicitly requests evidence artifacts.

## Step 16 - Pass Or Fail Criteria

Pass:

- Local package is installed and version is correct.
- Testing app checks pass.
- Core review commands work in dry-run mode.
- Publish commands update managed comments without duplicates.
- Slash PR commands are processed.
- Memory and learnings work.
- Connectors fail open or report configured health safely.
- Eval output is generated locally.
- Maintenance commands keep read-only defaults.
- Daemon start and stop behavior works.

Fail:

- Any command mutates GitHub or files without an explicit flag.
- Any output leaks credentials, raw tokens, or unbounded private content.
- Managed comments duplicate on repeated runs.
- Slash commands are ignored or parsed incorrectly.
- Daemon metadata becomes stale and is not cleaned up.
- Labels are created unexpectedly by OpenRabbit.

## Final Report Template

```markdown
# OP-149 Full Feature Validation Report

Date:
OpenRabbit version:
Testing issue:
Testing PR:

## Summary

- Passed:
- Failed:
- Blocked:

## Command Results

| Area | Command or flow | Result | Evidence |
| --- | --- | --- | --- |
| CLI | openrabbit --version |  |  |
| Review | review dry-run |  |  |
| Interactive | describe/ask/improve/labels |  |  |
| PR commands | /openrabbit commands |  |  |
| Memory | learnings/history |  |  |
| Connectors | connector-health |  |  |
| Eval | eval report |  |  |
| Maintenance | labels/changelog/docs/similar-issues |  |  |
| Daemon | start/stop |  |  |

## Follow-ups

- 
```
