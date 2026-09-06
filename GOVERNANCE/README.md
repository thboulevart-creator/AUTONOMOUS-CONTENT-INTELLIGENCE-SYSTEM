# GOVERNANCE

This directory is the authoritative home for validated governance rules that constrain the operation, modification, qualification, and evolution of this repository.

## Mandatory rule

Before any GitHub action, the acting agent MUST independently verify:

1. `repository_full_name` — exact repository identity.
2. Target branch.
3. Reference/base commit.
4. Exact target file/path.

If any of these four elements is not confirmed, the agent MUST NOT write, commit, merge, or otherwise modify repository state.

Conversation context is never sufficient evidence of repository identity.

## Rule lifecycle

Only rules that have been explicitly validated/adjudicated for this system may be treated as normative. A proposal, hypothesis, discussion, or unverified recommendation MUST NOT be represented as a validated rule.

Material validated rules MUST be persisted in this directory at the narrowest applicable scope. Existing system-specific contracts remain authoritative for their stated scope; this directory does not silently override them.

## Status discipline

A governance rule MUST preserve uncertainty. `BLOCKED`, `TO-PROVE`, `UNKNOWN`, or equivalent states MUST NOT be promoted to `PASS` without the evidence required by the applicable contract.

## Repository isolation

Rules and work from another repository MUST NOT be imported merely because the projects are related. Cross-repository reuse requires explicit verification of applicability and provenance.
