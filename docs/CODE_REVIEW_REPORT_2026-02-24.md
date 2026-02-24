# Code Review Report (2026-02-24)

## 1. Findings (Ordered by Severity)

### Critical

1. **Path permission checks are prefix-based and can be bypassed**
   - Evidence:
     - `nanobot/agent/tools/filesystem.py:12`
     - `nanobot/agent/tools/filesystem.py:44`
     - `nanobot/agent/tools/filesystem.py:46`
   - Impact:
     - `allowed_dir` and `allowed_paths` rely on `startswith(...)`.
     - A path like `.../workspace/reports2/...` can pass checks intended for `.../workspace/reports/...`.
     - This breaks the core isolation/least-privilege security model in `POSTS.md`.

2. **Multi-company role identity can silently fall back to generic identity**
   - Evidence:
     - `nanobot/agent/context.py:28`
     - `nanobot/agent/context.py:43`
     - `nanobot/agent/context.py:45`
     - `nanobot/agent/subagent.py:217`
   - Impact:
     - `SubagentManager` creates `ContextBuilder` without `company_name/company_path`.
     - For non-default companies, `get_agent_identity(post_id)` may not find the post and returns default `nanobot` identity.
     - This violates role isolation and can invalidate company-specific prompt/tool constraints.

### High

3. **`DocumentFlowTool` ignores company selection**
   - Evidence:
     - `nanobot/agent/tools/document_flow.py:65`
     - `nanobot/agent/subagent.py:384`
   - Impact:
     - Tool always loads schema with `CompanyConfigLoader(workspace)` default resolution.
     - Running non-default companies may still use default schemas, causing wrong document types/templates.

4. **Tool policy is fail-open when post tools are missing**
   - Evidence:
     - `nanobot/agent/subagent.py:391`
     - `nanobot/agent/subagent.py:402`
   - Impact:
     - If a post has empty/omitted tools, code grants all tools (including sensitive ones like `exec`).
     - This conflicts with least-privilege expectations in role-based design.

### Medium

5. **Workflow requirement is documented, but runtime workflow parsing/execution is still placeholder**
   - Evidence:
     - `nanobot/company/loader.py:65`
     - `nanobot/company/loader.py:93`
     - `nanobot/company/loader.py:98`
   - Impact:
     - `WORKFLOWS.md` is not parsed into executable routing/PDCA logic by loader.
     - Current dispatch is mainly `default_post` + task scanning.

6. **Task scan rule mismatches README examples**
   - Evidence:
     - `README.md:80` (example says any filename)
     - `nanobot/company/manager.py:111` (actual glob is `TASK_*.md`)
     - `nanobot/cli/company.py:78` (also says default scans `TASK_*.md`)
   - Impact:
     - User expectations differ from runtime behavior.

7. **Worker history is removed after run (may conflict with "performance/audit history" expectations)**
   - Evidence:
     - `nanobot/company/manager.py:167`
     - `nanobot/company/manager.py:169`
   - Impact:
     - `workers.json` entries and worker memory are deleted after completion.
     - Limits post-run traceability/performance retrospective unless external logs are collected.

## 2. Requirement-to-Implementation Traceability (Docs vs Code)

| Requirement Theme | Source Doc | Current Status | Notes |
| --- | --- | --- | --- |
| Multi-company loading (`--name`, `--path`) | `URD.md`, `MDD.md` | Implemented | Resolution order exists in `CompanyConfigLoader._resolve_base_path`. |
| Flexible task input (`--task` string/file) | `URD.md`, `MDD.md` | Implemented | `nanobot/cli/company.py:95-99` supports file-or-string task input. |
| Default post dispatch | `URD.md`, `MDD.md`, `README.md` | Implemented (with caveat) | Works when `default_post` exists; otherwise task is skipped. |
| Workflow/PDCA runtime orchestration from `WORKFLOWS.md` | `URD.md`, `MDD.md` | Partially implemented / Missing core parsing | Loader has placeholder; no full workflow engine execution from workflows file. |
| Doc schema-based document flow | `URD.md`, `MDD.md` | Partially implemented | `DocumentFlowTool` exists; validation is basic, and company context is not propagated. |
| Per-agent memory isolation | `URD.md`, `MDD.md` | Implemented | Worker memory path isolation exists (`workspace/workspace/memory/workers/{id}`). |
| Strict role-based tool/file permissions | `URD.md`, `MDD.md`, `POSTS.md` | Partially implemented with critical gaps | Prefix path bypass + fail-open tool grant. |
| Cron integration with workflow governance | `URD.md`, `MDD.md` | Partially implemented | Cron service exists, but not fully bound to parsed `WORKFLOWS.md` semantics. |
| Company-level sub-skills (`skills_dir`) | `URD.md` | Missing | `CompanyConfigLoader` does not load/propagate `skills_dir` for runtime skill scoping. |

## 3. Documentation Quality Review (Full `docs/` Set)

### Accurate or Mostly Accurate
- `docs/URD.md`
- `docs/MDD.md`
- `docs/ADD.md`
- `docs/COMPONENTS.md`

### Partially Outdated (Needs Update)
- `docs/introduction.md`
  - `docs/introduction.md:79` mentions `routes.json`, but current dispatch code no longer uses it.
- `docs/MANUAL_VERIFICATION.md`
  - `docs/MANUAL_VERIFICATION.md:14` uses old local path `c:\Users\golde\code\nanobot-company`.
  - `docs/MANUAL_VERIFICATION.md:78` event log path description is outdated.
- `docs/components/CLI.md`
  - `docs/components/CLI.md:59` says `workspace/company`; actual init path is `workspace/companies/<name>` (`nanobot/cli/company.py:20`).
- `docs/components/CHANNELS.md`
  - `docs/components/CHANNELS.md:43` references `config.yaml`; runtime config is JSON (`nanobot/config/loader.py:10`, `nanobot/config/loader.py:16`).
- `docs/components/PROVIDERS.md`
  - `docs/components/PROVIDERS.md:53`, `docs/components/PROVIDERS.md:57`, `docs/components/PROVIDERS.md:60` still describe `config.yaml` + `llm:` layout.
- `docs/components/SESSION.md`
  - `docs/components/SESSION.md:12` claims `workspace/memory/sessions`; actual path is `~/.nanobot/sessions` (`nanobot/session/manager.py:64`).
- `docs/components/HEARTBEAT.md`
  - Mentions hook-based flow and legacy prompt wording not matching current `HEARTBEAT_PROMPT` behavior.

### Significantly Outdated / Historical (Should Be Marked Archived)
- `docs/TRANSFORMATION_PLAN.md`
  - Contains plan-phase interfaces not matching current implementation (e.g., `create_task/submit_report/audit_report` style APIs).
- `docs/MANAGER_HIERARCHY_ANALYSIS.md`
  - Has stale assumptions (e.g., "15 iterations" at `docs/MANAGER_HIERARCHY_ANALYSIS.md:36`; code is 30 at `nanobot/agent/subagent.py:250`).
  - Includes local `file:///...` links that are environment-specific.
- `docs/components/UTILS.md`
  - Documents functions not present in `nanobot/utils/helpers.py` (e.g., `clean_json_markdown`, `truncate_text`, `calculate_cost`, `format_token_usage`).

## 4. Test & Verification Notes

- Ran tests in current directory only:
  - `python -m pytest -q`
  - Result: **119 passed, 1 warning**.
- Initial direct `pytest -q` failed due interpreter/environment path mismatch; package-local run via `python -m pytest` succeeds.

## 5. Recommended Priority Actions

1. Fix filesystem permission checks using canonical path boundary comparison (`Path.resolve()` + parent containment), not string prefix.
2. Propagate `company_name/company_path` into subagent `ContextBuilder` and `DocumentFlowTool`.
3. Change tool policy to fail-closed (empty post tools => no sensitive defaults).
4. Implement/finish `WORKFLOWS.md` parsing and execution linkage or clearly scope it as unsupported.
5. Refresh component docs (`CLI/CHANNELS/PROVIDERS/SESSION/HEARTBEAT/UTILS`) and mark historical docs as archived.


