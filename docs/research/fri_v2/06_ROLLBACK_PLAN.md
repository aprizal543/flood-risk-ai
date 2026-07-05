# FRI v2 Rollback Plan

## Objective

Define how future FRI v2 implementation can be reverted to stable FRI v1 if validation, scientific review, or production monitoring fails.

## Current Sprint Rollback

Because this sprint creates documentation only, rollback means removing or revising documents under `docs/research/fri_v2/`. No application behavior, model artifact, dataset, backend, or frontend rollback is required.

## Future Implementation Rollback Principle

FRI v1 must remain available until FRI v2 is fully accepted in production. Future v2 work must not delete v1 documentation, model artifacts, or operational knowledge needed for recovery.

## Rollback Triggers

- FRI v2 fails scientific evaluation.
- FRI v2 produces unacceptable regression against v1 metrics.
- Backend responses become incompatible with existing clients.
- Model artifact validation fails.
- Production deployment introduces instability.
- Any forbidden area is modified without approval.

## Rollback Actions

| Area | Action |
|------|--------|
| Feature engineering | Restore v1 feature derivation behavior |
| Scoring | Restore v1 FRI scoring formula and weights |
| Model | Restore last accepted v1 Random Forest artifact |
| Backend | Repoint backend to v1 scoring/model path |
| Frontend | No rollback expected because frontend changes are forbidden |
| Dataset | No rollback expected because dataset changes are forbidden |

## Rollback Validation

After rollback, validate:

- API responses match v1 contract.
- Model artifact loads successfully.
- FRI output range remains 0-100.
- Risk classification works as before.
- Dataset checks confirm no mutation.
- No frontend, authentication, Supabase, or infrastructure files changed.

## Documentation Requirement

Every future implementation sprint must update its own rollback notes with exact files, artifacts, commands, and verification evidence.
