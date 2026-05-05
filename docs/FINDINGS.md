# SkillScope Findings

This document records the current exploratory findings supported by the dashboard data.

Important distinction: SkVM TCP profiles are imported official data from SkVM-data. Skill Capability Requirements (SCR) are derived by this project through rule-based extraction and optional LLM-assisted extraction. Therefore, all capability requirement claims should be phrased as derived SCR findings.

## Data Snapshot

- Corpus size: 1,643 skills.
- Data sources: local `.cc-switch`, local `.agents`, local `.codex`, and SkVM benchmark skills.
- TCP profiles: 25 model/harness profiles.
- Harnesses: `bare-agent`, `hermes`, `openclaw`.
- Models: 12 unique models.

## Main Findings

### 1. Procedure-following dominates the skill corpus

The most common derived primitive is `follow.procedure`, appearing in 1,427 skills, or 86.9% of the corpus. This supports the project framing that skills are closer to natural-language workflows than ordinary documentation snippets.

Related dashboard view: `Findings`, `Primitives -> Primitive demand ranking`.

### 2. Verification is a major workflow pattern

1,368 skills, or 83.3% of the corpus, include verification signals such as test, check, confirm, inspect, or validate. This suggests many skills encode not only how to act, but how to decide whether the action succeeded.

Related dashboard view: `Findings`, `Primitives -> Workflow complexity map`, selected skill detail.

### 3. `doc.generate` is the largest portability bottleneck

Across the SCR/TCP comparison, `doc.generate` has the largest aggregate gap score at 17,059. Other high bottlenecks include `reason.plan`, `data.parse`, `data.transform`, and `tool.github`.

Interpretation: writing structured or long-form outputs, planning, data handling, and GitHub/web-mediated work are recurring weak points when skill requirements are compared against available target profiles.

Related dashboard view: `Risks -> Portability Risk`, `Primitives -> Bottleneck primitives`.

### 4. Target compatibility varies strongly by model/harness pair

The best observed target profile is `deepseek-v4-pro / openclaw`, with an average gap of 0.341. The weakest target in the current profiles is `qwen3.5-9b / openclaw`, with an average gap of 19.358.

This makes the model/harness pair a useful unit of analysis: the same skill corpus can look much more or less portable depending on runtime and model pairing.

Related dashboard view: `Risks -> Model x Harness portability heatmap`, `Risks -> Target compatibility`.

### 5. Tool-reference skills are the highest-risk taxonomy

Among derived skill taxonomies, `tool-reference` has the highest average risk at 0.214. This is plausible because tool-reference skills often depend on CLIs, APIs, credentials, package managers, Git/GitHub flows, or external services.

Related dashboard view: `Risks -> Risk by taxonomy`, `Dependency / Environment Risk`.

### 6. Environment dependencies are common

1,038 of 1,643 skills, or 63.2%, mention dependencies, credentials, packages, environment variables, or setup hints. The largest environment categories are:

- `system cli`: 1,018 skills
- `version control`: 978 skills
- `web/browser`: 942 skills
- `runtime`: 811 skills
- `credentials`: 707 skills
- `package managers`: 389 skills

This supports the idea that environment mismatch is not a marginal issue for skills; it is a visible part of the ecosystem.

Related dashboard view: `Risks -> Dependency / Environment Risk`.

### 7. Model/harness mismatch is now measured as a separate contribution

The dashboard computes average model mismatch and average harness mismatch across the filtered corpus. This directly supports the research question: "Is model mismatch or harness mismatch the stronger source of skill fragility?"

Related dashboard view: `Risks -> Model vs harness contribution`.

### 8. Some skills can be prioritized for rewriting or compilation

The dashboard ranks skills by a composite priority score that combines overall risk, environment mismatch, primitive diversity, workflow complexity, and SCR confidence. This provides a concrete list of skills that should be inspected, rewritten, or compiled first.

Related dashboard view: `Risks -> Rewrite / compilation priority`.

## Limitations

- SCR labels are derived by project rules, not official SkVM labels.
- The primitive mapping from project primitives to SkVM TCP primitives is approximate for extra project-specific primitives such as `tool.github`, `data.visualize`, and `runtime.env_bind`.
- Public skills sampling is not yet implemented, so current findings compare local skills and SkVM benchmark data.
- The current environment risk detector is keyword-based. It is useful for EDA, but should be validated manually before making strong claims.
- The dashboard does not implement SkVM AOT compilation, JIT code solidification, adaptive recompilation, runtime scheduling, or task-level performance evaluation.

## Takeaway

The strongest current story is:

Skills behave like natural-language programs: they encode procedures, verification, tool use, runtime assumptions, and capability demands. By extracting SCR primitives and comparing them to SkVM TCP profiles, SkillScope can identify which capabilities are common, which target profiles are compatible, and which skills are likely to be fragile because of model, harness, or environment mismatch.
