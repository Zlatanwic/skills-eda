# SkVM Alignment

This project is inspired by the SkVM paper, but it is not a full SkVM compiler/runtime implementation.

## Paper Concepts Used

- Skills are treated as natural-language programs rather than raw context.
- LLMs and harnesses are treated as heterogeneous execution targets.
- Skill requirements are decomposed into primitive capabilities.
- Target model/harness capability profiles are used to reason about portability.
- Environment assumptions are treated as a source of fragility.

## Implemented In SkillScope

- Local and SkVM skill collection.
- Markdown/frontmatter/code-block parsing.
- Structural feature extraction.
- Derived SCR extraction with primitive names, levels, evidence, and confidence.
- SkVM TCP profile import from SkVM-data.
- SCR/TCP gap calculation by target profile.
- Primitive bottleneck aggregation.
- Model x harness portability heatmap.
- Dependency and environment risk detection.
- Findings cards and rewrite/compilation priority ranking.
- Generated SCR validation sample.

## Partial Approximation

- The project primitive catalog is not a verbatim copy of the paper's primitive catalog.
- Project primitives are mapped to closest SkVM primitive ids for TCP comparison.
- Environment binding is represented as dependency risk detection, not generated setup scripts.
- Concurrency extraction is represented as `agent.parallel` and workflow complexity signals, not executable DAG extraction.
- Validation sample is generated, but manual adjudication remains to be completed.

## Not Implemented

- AOT skill compilation.
- Target-specific rewritten skill variants.
- Environment-binding setup script generation.
- Concurrency DAG extraction and runtime scheduling.
- JIT code solidification.
- Adaptive recompilation based on failure logs.
- Task-level completion-rate evaluation.
- Token consumption and latency/speedup measurement.

## Suggested Wording For The Report

Use this wording:

> SkillScope is a SkVM-inspired exploratory data analysis dashboard. It adopts SkVM's view of skills as natural-language programs and uses SCR/TCP-style capability comparison to study portability risk. It does not reproduce SkVM's compiler or runtime.

Avoid this wording:

> SkillScope implements SkVM.

## Key Distinction

- Official imported data: SkVM TCP profiles.
- Project-derived data: SCR labels, taxonomy, environment risk, prioritization score, findings.
