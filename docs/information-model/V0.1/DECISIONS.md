# Information Model V0.1 — Decision Record

## Final status

**VALIDÉ SOUS RÉSERVES → LOCKED**

The remaining reservations were converted into explicit normative requirements before lock.

## Applied corrections

1. **Experiment baseline/intervention**
   - Controlled experiments must carry structured, queryable references for `baseline_ref` and `intervention_refs`.
   - Baseline and Intervention remain properties/references, not new first-class objects.

2. **Experiment ↔ Performance traceability**
   - Experiment results must be traceable to the experiment through Performance, directly or through the Publications belonging to its experimental arms.

3. **Path-dependent traceability**
   - The model does not force a universal chain. It records the actual provenance path and must not fabricate missing causal or creative ancestry.

4. **Learning lifecycle**
   - Learning must support at least `active`, `saturated`, `deprecated`, `contested`, and `rehabilitated` states.

## Deliberate minimality decisions

No new first-class objects were added for Baseline, Intervention, Knowledge Claim, Metric, Score, Analysis, Inference, generic Context or Saturation.

Evidence replaces the former Signal/Observation split.

## Lock rule

The next work product is the Logical Data Schema. If schema design reveals a semantic problem, it must be raised explicitly as a proposed Information Model change rather than silently changing V0.1.
