# SkillScope Demo Script

Goal: present the project motivation, data, method, findings, and limitations in about 5 to 7 minutes.

## 1. Opening

This project is called SkillScope. It performs exploratory data analysis and visualization over LLM agent skills.

The motivation comes from the SkVM paper: skills are not just reusable prompts. They are natural-language programs with steps, tools, dependencies, capability assumptions, and runtime environment assumptions.

The dashboard asks:

- What primitive capabilities do skills require?
- Which skills are less portable across model/harness targets?
- Do environment dependencies and external tools create major risk?

## 2. Data And Pipeline

The current dashboard uses 1,739 skills, including local skills, 96 public GitHub skills, SkVM benchmark skills, and TCP profiles from SkVM-data.

Pipeline:

1. Collect local skills, public GitHub skills, and SkVM benchmark skills.
2. Parse markdown, frontmatter, headings, code blocks, and steps.
3. Extract structural features, tool evidence, dependency evidence, and taxonomy.
4. Extract derived SCR labels: primitive capability requirements for each skill.
5. Merge optional LLM-assisted SCR labels for selected skills; the current snapshot has 20 `rule+llm` SkVM benchmark annotations.
6. Compare SCR with SkVM TCP profiles to compute portability gaps.
7. Generate static dashboard JSON for the Vue/Vite frontend.

Key distinction: SkVM TCP is imported official data. SCR is derived by this project.

## 3. Findings Page

Open the `Findings` page.

This page turns research questions into finding cards:

- `follow.procedure` is the most common primitive.
- `doc.generate` is the largest portability bottleneck.
- `deepseek-v4-pro / openclaw` is the most compatible target in the current profile set.
- A large share of skills mention dependencies, credentials, packages, or environment setup.
- The dashboard now also reports whether model mismatch or harness mismatch contributes more to risk.

## 4. Primitives Page

Switch to `Primitives`.

This page explains capability demand:

- `Primitive level heatmap`: required capability level distribution.
- `Primitive demand ranking`: most common derived SCR primitives.
- `Workflow complexity map`: step count vs primitive diversity.
- `Bottleneck primitives`: primitives that create the largest SCR/TCP gaps.

Main point: many skills are multi-step, tool-heavy, verification-heavy workflows.

## 5. Risks Page

Switch to `Risks`.

This page explains portability:

- `Model x Harness portability heatmap`: average gap by model/harness target.
- `Target compatibility`: best and worst target profiles.
- `Model vs harness contribution`: whether model or harness mismatch contributes more.
- `Dependency / Environment Risk`: CLI, Git/GitHub, browser, runtime, credentials, and package-manager signals.
- `Rewrite / compilation priority`: skills that should be inspected or rewritten first.

Main point: portability risk is not only a model problem. It also depends on harness capabilities, dependency setup, and skill complexity.

## 6. Alignment Page

Switch to `Alignment`.

This page explains what the project implements relative to the SkVM paper.

Implemented:

- Skills as analyzable natural-language programs.
- Derived SCR extraction.
- Imported TCP profile comparison.
- SCR/TCP portability gaps.
- Environment risk detection.

Not implemented:

- AOT skill compilation.
- Generated environment-binding setup scripts.
- Concurrency DAG extraction.
- JIT code solidification.
- Adaptive recompilation.
- Task-level completion, token, and speedup evaluation.

This makes the scope precise: SkillScope is a SkVM-inspired EDA dashboard, not a SkVM compiler/runtime reproduction.

## 7. Skill Detail

Click a high-risk skill in the ranking table.

The detail panel shows taxonomy, length, steps, code blocks, risk profile, top primitives, and evidence. This makes the dashboard less black-box: scores can be traced back to extracted skill signals.

## 8. Limitations

- SCR is derived, not official SkVM annotation. The current snapshot includes 20 LLM-assisted SCR labels, but most labels remain rule-derived.
- Primitive mapping is approximate.
- Public skill sampling is implemented and currently includes 96 public GitHub skills, but this is still a small exploratory sample.
- Environment risk is keyword-based.
- The project does not execute tasks or measure speedup/token reduction.

## 9. Closing

SkillScope turns skills from reusable prompt-like files into analyzable natural-language programs. It shows common capability requirements, portability bottlenecks, target compatibility, environment risks, and which skills should be prioritized for rewriting or future compilation.
