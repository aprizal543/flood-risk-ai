# FRI v2 Boundary Document

## Objective

Define what FRI v2 documentation and future implementation may and may not touch.

## Current Sprint Boundary

This sprint is documentation only. The only allowed changes are Markdown documents under `docs/research/fri_v2/`.

## Allowed In This Sprint

- Create `docs/research/fri_v2/`.
- Create FRI v2 design-freeze documents.
- Create future sprint planning documents.
- Summarize frozen decisions and constraints.

## Forbidden In This Sprint

- Source code changes.
- Backend changes.
- Frontend changes.
- Dataset changes.
- Model retraining.
- Model artifact generation.
- Data cleaning or merge changes.
- Authentication changes.
- Security changes.
- Supabase changes.
- Infrastructure changes.

## Future Implementation Boundary

Future implementation sprints may modify only the files explicitly allowed in their sprint document. If a required file is not listed as allowed, it is forbidden until the sprint document is updated and approved.

## Globally Forbidden Areas Unless Separately Approved

- Dataset files.
- Merge scripts.
- Cleaning scripts.
- Frontend.
- Authentication.
- Security.
- Supabase.
- Infrastructure.

## Boundary Enforcement

Every future sprint must include a final diff review that classifies changed files as allowed or forbidden. Any forbidden file change fails the sprint acceptance criteria.
