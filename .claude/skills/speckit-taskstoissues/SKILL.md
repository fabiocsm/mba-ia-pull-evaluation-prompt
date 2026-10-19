---
name: "speckit-taskstoissues"
description: "Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts."
argument-hint: "Optional filter or label for GitHub issues"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/taskstoissues.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before tasks-to-issues conversion)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_taskstoissues` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").
1. **IF EXISTS**: Load `.specify/memory/constitution.md` for project principles and governance constraints.
1. From the executed script, extract the path to **tasks**.
1. Get the Git remote by running:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

1. **Define feature-scoped task identities**: Normalize `FEATURE_DIR` to its repository-relative path, with `/` separators and no trailing slash (for example, `specs/001-preparar-experimentos`). Use `(feature_path, task_id)` as the identity everywhere; task IDs restart in each feature and are not repository-wide identifiers. Build the set of identities from this feature's `tasks.md`. Each task ID is a `T` followed by **at least** three digits, matched as the whole token `\bT\d{3,}\b`: `/speckit-converge` uses `T{M+1:03d}`, a floor rather than a cap. Thus `T1000` is valid, `T100` must not match inside it, and `ST001` must not match `T001`.
1. **Fetch existing issues for deduplication**: Use the GitHub MCP server's `list_issues` tool, omitting `state` to return both open and closed issues. Request `perPage: 100` and follow cursor-based pagination with `after` set to the preceding `endCursor`. Read titles and bodies to determine each issue's own identity, not task IDs mentioned as dependencies or examples. A canonical issue has title `[<feature_path>] T001: <description>` and body lines `Feature: <feature_path>` and `Task: T001`. Match the exact feature path and whole task ID; an issue for another feature never covers this feature's task. Conflicting identity fields require manual matching and must not be counted automatically.
   - For legacy titles such as `T001 ...`, `T001: ...` or `[T001] ...`, count the issue only when its body explicitly identifies the same feature path (for example, an unambiguous reference to `<feature_path>/tasks.md`) and its own task ID. Explicit evidence for another feature is not a match. A legacy issue with no unambiguous feature evidence is **unresolved**, not a duplicate: report its URL and candidate task identity for manual matching, and hold that affected task without creating or silently skipping it until the ambiguity is resolved. Continue processing unaffected tasks.
   - Stop paginating when every current feature identity has a confirmed match, or when no more pages exist. Matches belonging to other features and unresolved legacy candidates do not satisfy this early-stop condition. This preserves rerun deduplication without letting shared task IDs suppress a different feature.
1. For each task in the list, use the GitHub MCP server to create a new issue in the repository that is representative of the Git remote. Task lines in `tasks.md` start with a markdown checkbox, so first strip the leading `- [ ]` or `- [x]` (and any `[P]` / `[US#]` markers) to recover the task ID and its description. Use the canonical title `[<feature_path>] T001: <description>`, with the task ID written once in the title, and include the `Feature: <feature_path>` and `Task: T001` body lines. For example, `- [ ] T001 Create project structure` in `specs/001-preparar-experimentos/tasks.md` becomes `[specs/001-preparar-experimentos] T001: Create project structure`.
   - **Skip** only tasks whose full identity has a confirmed existing issue; report the feature path, task ID and issue URL.
   - Create issues only for identities with no confirmed match and no unresolved manual-match candidate. Report unresolved candidates separately from skipped and created issues.

### Offline regression scenarios

Validate identity decisions without creating remote issues:

- Convert feature A, then feature B with overlapping IDs: A's issues must not suppress B's tasks. In this repository, the 30 tasks in `specs/001-preparar-experimentos/tasks.md` and 25 in `specs/002-recuperar-prompt-v1/tasks.md` share 25 IDs; after A, all 25 B identities remain eligible.
- Re-run the same feature against its canonical issues, including closed issues: every matching identity is skipped and zero duplicates are eligible.
- A legacy `T001: ...` issue explicitly referencing A's `tasks.md` covers only A/T001. Without feature evidence, it is reported for manual matching, holds the candidate task, and does not enter the confirmed-match set.
- Whole-token boundaries: `T1000` matches itself, never `T100`; `ST001` does not match `T001`. Apply the same rules when parsing tasks and existing issue identities, including across pagination.

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL

## Post-Execution Checks

**Check for extension hooks (after tasks-to-issues conversion)**:
Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.after_taskstoissues` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently
