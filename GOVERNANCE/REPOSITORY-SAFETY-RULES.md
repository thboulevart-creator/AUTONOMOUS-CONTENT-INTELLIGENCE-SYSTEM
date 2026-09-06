# Repository Safety Rules

**Status:** VALIDATED — mandatory operational rule
**Scope:** Entire repository and every GitHub operation affecting it.

## Rule RSR-01 — Verify repository identity before action

Before every GitHub action, the acting agent MUST independently verify:

- exact `repository_full_name`;
- target branch;
- reference/base commit;
- exact target file/path.

The agent MUST NOT infer repository identity from prior conversation, recent context, naming similarity, or previous task history.

If any required identity element is unconfirmed, the action is **BLOCKED** and no write operation is authorized.

## Rule RSR-02 — Repository isolation

An artifact, rule, patch, commit, branch, or workflow belonging to another repository MUST NOT be applied here without an explicit applicability check and provenance verification.

## Rule RSR-03 — Source-of-truth discipline

GitHub repository state and validated governance artifacts are the source of truth for repository work. Conversation text is not a substitute for repository verification.

## Rule RSR-04 — No false closure

`BLOCKED`, `TO-PROVE`, `UNKNOWN`, missing evidence, or failed prerequisites MUST remain unresolved until the applicable evidence and executable requirements are satisfied. No agent may relabel such a state as `PASS` for convenience.

## Rule RSR-05 — Provenance of governance rules

Only explicitly validated/adjudicated rules are normative. Ideas, hypotheses, draft recommendations, or agent suggestions MUST remain clearly non-normative until validated.

## Enforcement sequence

`IDENTIFY REPOSITORY → VERIFY BRANCH → VERIFY BASE/REFERENCE COMMIT → VERIFY TARGET PATH → CHECK APPLICABILITY/PROVENANCE → ACTION`

Any failed verification yields **BLOCKED — DO NOT WRITE**.
