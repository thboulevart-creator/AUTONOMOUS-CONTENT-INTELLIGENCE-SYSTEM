# AI OPERATING MEMORY — AUTONOMOUS CONTENT INTELLIGENCE SYSTEM

> Durable operating memory for AI-assisted work on this repository.
>
> This is a governance artifact. It must be consulted before substantive action. It does not replace source code, tests, evidence, experiments, or formal verdicts.

## 1. MANDATORY PRE-ACTION RULE

Before every substantive action, the AI MUST read this file and the latest applicable `GOVERNANCE/RECOVERY-CHECKPOINT.md`.

The AI MUST NOT rely solely on conversational memory for repository state, previous decisions, paths, files, experiments, branches, commits, or validated results.

If the state cannot be established from GitHub and available execution evidence, stop and classify the situation as **BLOCKED** rather than guessing.

## 2. SOURCE-OF-TRUTH HIERARCHY

1. Versioned repository code and governance artifacts on GitHub.
2. Versioned experiments, reports, verdicts, and Recovery Checkpoints.
3. Reproducible execution evidence from the current worktree/session.
4. Conversation history.
5. AI recollection or inference.

Lower-level memory never overrides higher-level evidence.

## 3. RECOVERY & TRACEABILITY INVARIANT

Every important workstream must maintain a versioned Recovery Checkpoint recording:

- repository/system and branch;
- reference commit;
- current work block;
- completed path and PASS/FAIL/BLOCKED states;
- evidence and artifact locations;
- code/tests/scripts/data/experiments state;
- failures, causes and corrections;
- lessons preventing recurrence;
- missing evidence;
- last verdict;
- exactly one next action.

The purpose is to resume work without repeating validated work and without depending on conversation history.

## 4. EVIDENCE DISCIPLINE

- Never issue a false PASS.
- Qualification verdicts are **PASS / FAIL / BLOCKED**.
- BLOCKED is not PASS.
- Distinguish current violation, architectural exposure, absence of proof, historical evidence, and reproducible current evidence.
- Never invent files, paths, experiments, data, hashes, branches, commits, or prior results.
- Verify the real repository state before writing or changing anything.

## 5. ADVERSARIAL WORK PROTOCOL

For important validation:

**formalisation → candidate → adversarial break → correction → re-break → verdict**

Normal-path success is insufficient. Attack bypasses, substituted inputs, incomplete inputs, stale assumptions, and misleading evidence where relevant.

## 6. CHANGE DISCIPLINE

- Do not modify `main` casually; governance changes are allowed when explicitly authorized.
- Do not merge, rebase, reset, force-push, or discard work without state/evidence review.
- Never use `git add .` for controlled qualification work.
- Avoid parasite artifacts created only to satisfy a check.
- Prefer clean rewrites or deliberate new files over fragile string replacement.
- Preserve validated baselines.

## 7. NO LOOPING / NO REPETITION

When something fails, diagnose the exact failure before retrying.

Never blindly repeat a command, assume a temporary probe still exists, assume a path from another worktree, or recreate already-proven work unless evidence has been lost or invalidated.

Record material failures and corrections in the Recovery Checkpoint.

## 8. EXPERIMENTAL MEMORY

Preserve hypotheses, experiments, tested explanations, results, failures, successful corrections, validated knowledge, and rejected approaches with their reasons.

The system must learn from explanations and experimental history, not only outcomes.

## 9. GOVERNANCE ARTIFACT CHAIN

For important work prefer:

**Script → Report → Verdict → Conclusion → Recovery Checkpoint**

Every artifact must identify the state it describes.

## 10. MINDSET

Do not try to prove another AI, hypothesis, or previous conclusion right or wrong. Determine what is true from evidence.

Before any conclusion, ask:

> **Where could I be wrong?**

Autonomy stops at the final evidence-based verdict.

## 11. CROSS-REPOSITORY RULE

These operating rules apply across the ALGO ECOSYSTEM repositories. When work crosses repositories, consult each affected repository's durable memory and Recovery Checkpoint.

Conflicting states must be surfaced, not silently reconciled.

## 12. CURRENT STATUS

This file establishes durable operating rules. It does not certify the technical state of the repository. The latest Recovery Checkpoint and evidence artifacts define the current state.
