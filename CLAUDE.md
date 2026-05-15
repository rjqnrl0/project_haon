# AI-DLC Workflow Rules for Claude Code

This project uses the AI-DLC (AI-Driven Development Life Cycle) methodology.

## Rule Files Location

Rule files are stored in `.claude/rules/`:
- `.claude/rules/aws-aidlc-rules/core-workflow.md` — Main workflow entry point
- `.claude/rules/aws-aidlc-rule-details/` — Detailed stage rules

## Loading Rules

At the start of any development task, load rules in this order:
1. `aws-aidlc-rules/core-workflow.md`
2. `aws-aidlc-rule-details/common/process-overview.md`
3. `aws-aidlc-rule-details/common/terminology.md`
4. `aws-aidlc-rule-details/common/depth-levels.md`
5. Stage-specific rules as needed

Load opt-in extensions from `aws-aidlc-rule-details/extensions/` — check for `*.opt-in.md` files.

## Key Principles

- **Display the welcome message** (`common/welcome-message.md`) once at the start of a new workflow
- **Always execute**: Workspace Detection, Requirements Analysis, Workflow Planning, Code Generation, Build and Test
- **Conditional stages**: All others based on project complexity
- **User approval required** before proceeding past each major stage
- **Audit everything**: Log all interactions to `aidlc-docs/audit.md` with ISO timestamps
- **Never overwrite** `audit.md` — always append
- **Application code**: workspace root only (never `aidlc-docs/`)
- **Documentation**: `aidlc-docs/` only

## Documentation Structure

All AI-DLC workflow artifacts go in `aidlc-docs/`:
```
aidlc-docs/
  aidlc-state.md          # Workflow state tracking
  audit.md                # Complete audit trail
  inception/
    requirements/
    reverse-engineering/
    user-stories/
    application-design/
    units-generation/
    execution-plan.md
  construction/
    plans/
    {unit-name}/
      functional-design/
      nfr-requirements/
      nfr-design/
      infrastructure-design/
      code/
    build-and-test/
```
