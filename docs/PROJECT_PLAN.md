# SkillScope Project Plan

## 1. Project Title

**SkillScope: Exploratory Analysis and Visualization of LLM Agent Skills**

## 2. Background and Motivation

LLM agent skills are reusable natural-language programs that describe workflows, tool usage, coding conventions, environment requirements, and domain-specific procedures. Inspired by the SkVM paper, this project treats skills as analyzable program artifacts rather than ordinary text.

The project will build a dashboard website for exploratory data analysis and visualization of skills. It will analyze skill corpora from local installed skills, SkVM benchmark data, and public skill sources. The dashboard will focus on skill taxonomy, workflow structure, code/tool fragments, dependency risks, primitive capability requirements, and portability gaps across model and harness profiles.

## 3. Core Research Questions

This project should answer concrete questions, not only display charts:

1. **What capability requirements are most common in skill ecosystems?**
   Identify frequently required primitive capabilities such as tool execution, file read/write, multi-step following, shell generation, Python generation, web access, and document generation.

2. **Do skills from different sources have different structures and risks?**
   Compare local skills, SkVM benchmark skills, and public skills by length, workflow complexity, code fragments, dependencies, taxonomy, and primitive requirements.

3. **Which skills are least portable across model and harness combinations?**
   Compare derived skill capability requirements (SCR) with official SkVM target capability profiles (TCP) to compute capability gaps.

4. **Is model mismatch or harness mismatch the stronger source of skill fragility?**
   Use SkVM TCP profiles to compare the same model across harnesses and the same harness across models.

5. **Which primitive capabilities become bottlenecks most often?**
   Aggregate gap scores by primitive capability to identify the most common reasons a skill may fail on weaker targets.

6. **How do skill taxonomy and primitive requirements relate?**
   Test whether tool-reference skills require more tool primitives, procedural skills require more instruction-following primitives, and generative skills require more code/content generation primitives.

7. **Are environment dependencies a major portability risk?**
   Analyze npm, pip, CLI tools, API keys, browsers, OS assumptions, and external service dependencies.

8. **Which skills should be prioritized for rewriting or compilation?**
   Rank skills by combined complexity, dependency risk, capability gap, and low-confidence extraction signals.

## 4. Data Sources

### 4.1 Local Skills Corpus

Local installed skills are used as the primary demo corpus because they are immediately available and large enough for exploratory analysis.

Initial observed counts:

- `C:/Users/27651/.codex/skills`: 14 `SKILL.md` files
- `C:/Users/27651/.agents/skills`: 68 `SKILL.md` files
- `C:/Users/27651/.cc-switch/skills`: 1459 `SKILL.md` files

Expected use:

- Main corpus for dashboard exploration
- Personal environment skill map
- Fast local reproducibility

### 4.2 SkVM-data Corpus

SkVM publicly provides a data repository with benchmark skills, tasks, and target capability profiles.

Expected contents:

- `skills/`: benchmark skill directories, each containing `SKILL.md`
- `tasks/`: task definitions
- `profiles/`: pre-built target capability profiles for model + harness combinations

Expected use:

- Align project with the SkVM paper
- Use official TCP profiles for model/harness capability visualization
- Use benchmark skills as a clean reference subset

Important distinction:

- **Official data**: SkVM TCP profiles for target model/harness capabilities
- **Derived project data**: SCR labels extracted from skills by this project

### 4.3 Public Skills Sample

Public skills will be collected with scripts from open sources such as skills marketplaces, public GitHub repositories, and skill indexes where accessible.

Scope:

- Start with a reproducible sample of 500 to 3000 public skills
- Do not promise full ecosystem crawling in the first version
- Store source URL, crawl time, license/availability signals, and extraction status

Expected use:

- Broader ecosystem comparison
- Long-tail and source-level analysis
- Public vs local vs benchmark contrast

## 5. Data Model

Each skill record should be normalized into a JSON object:

```json
{
  "skill_id": "local_cc_switch__api_security_best_practices",
  "name": "api-security-best-practices",
  "source": "local.cc-switch",
  "path_or_url": "...",
  "raw_text": "...",
  "metadata": {
    "description": "...",
    "frontmatter": {},
    "created_or_crawled_at": "..."
  },
  "features": {
    "char_count": 0,
    "word_count": 0,
    "section_count": 0,
    "code_block_count": 0,
    "step_count": 0,
    "dependency_count": 0,
    "tool_count": 0,
    "has_branching": false,
    "has_loop": false,
    "has_verification": false
  },
  "taxonomy": {
    "primary_type": "tool-reference",
    "domains": ["data", "code"],
    "confidence": 0.85
  },
  "scr": {
    "method": "rule",
    "confidence": 0.72,
    "requirements": [
      {
        "primitive": "tool.exec",
        "level": 2,
        "evidence": ["mentions shell command execution"]
      }
    ]
  },
  "risks": {
    "model_mismatch": 0.0,
    "harness_mismatch": 0.0,
    "environment_mismatch": 0.0,
    "overall": 0.0
  }
}
```

## 6. Primitive Capability Framework

The project will adapt the SkVM idea of primitive capabilities. SkVM uses 26 primitives across broad domains such as code generation, tool use, reasoning, and instruction following. The exact primitive catalog should be loaded from SkVM documentation or data if available; otherwise the project will define a compatible simplified catalog.

Initial project primitive groups:

### Code Generation

- `gen.code.shell`
- `gen.code.python`
- `gen.code.javascript`
- `gen.code.typescript`
- `gen.code.sql`
- `gen.code.edit`
- `gen.code.test`

### Tool Use

- `tool.exec`
- `tool.file.read`
- `tool.file.write`
- `tool.web.search`
- `tool.web.fetch`
- `tool.browser`
- `tool.git`
- `tool.github`
- `tool.package_manager`

### Data and Documents

- `data.parse`
- `data.transform`
- `data.visualize`
- `doc.generate`
- `doc.convert`
- `spreadsheet.process`
- `presentation.generate`

### Reasoning and Instruction Following

- `reason.plan`
- `reason.decompose`
- `reason.diagnose`
- `reason.analyze`
- `follow.procedure`
- `follow.constraints`
- `follow.format`
- `follow.verify`

### Parallelism and Runtime

- `agent.parallel`
- `workflow.dag`
- `runtime.env_bind`
- `runtime.template_solidify`

Levels:

- `L0`: no requirement or unsupported
- `L1`: basic/simple usage
- `L2`: standard multi-step usage
- `L3`: complex usage with branching, verification, composition, or tool coordination

## 7. SCR Extraction Strategy

SCR means Skill Capability Requirement: what primitive capabilities a skill requires and at what level.

The project will use a mixed extraction strategy:

1. **Rule-based extraction**
   Parse markdown structure, code blocks, commands, dependencies, explicit steps, branching words, verification instructions, package managers, APIs, and external service mentions.

2. **Optional LLM-assisted extraction**
   Use LLM classification for a selected subset if API access is available. This is an enhancement, not a hard dependency.

3. **Manual validation**
   Manually inspect 50 to 100 sampled skills to estimate label quality and refine rules.

4. **Confidence scoring**
   Every SCR label stores extraction method, evidence snippets, and confidence.

Dashboard wording should clearly distinguish derived SCR labels from official SkVM TCP profiles.

## 8. Analysis Metrics

### 8.1 Structural Metrics

- Character and word count
- Markdown section count
- Code block count
- Numbered step count
- Average step length
- Branching/loop/verification indicators
- Template-like command count

### 8.2 Taxonomy Metrics

- Primary skill type: `tool-reference`, `procedural`, `generative`, or `mixed`
- Domain tags: code, data, document, office, web, security, research, agent, automation, design, cloud, database
- Taxonomy confidence

### 8.3 Code and Tool Metrics

- Code language distribution
- CLI/tool mentions
- File operation signals
- Git/GitHub/GitLab signals
- Browser and web-search signals
- API/service signals

### 8.4 Dependency Metrics

- pip dependencies
- npm dependencies
- system binaries
- environment variables and API keys
- OS-specific assumptions
- external service requirements

### 8.5 Capability Metrics

- Primitive requirement frequency
- Required level distribution
- Co-occurrence matrix between primitives
- Primitive diversity per skill
- Average required capability level per taxonomy

### 8.6 Portability Metrics

Given a skill SCR and a target TCP:

```text
gap(skill, target, primitive) = max(0, required_level - provided_level)
```

Derived metrics:

- Total gap score
- Max primitive gap
- Number of missing primitives
- Hard gap count: required L2/L3 but target L0
- Weak gap count: target has lower but nonzero proficiency
- Domain-level gap: generation/tool/reasoning/following
- Best target recommendation: lowest gap model+harness pair
- Worst target warning: highest gap model+harness pair

## 9. Dashboard Modules

### 9.1 Corpus Overview

Purpose:

- Show what data was collected and from where.

Visualizations:

- Source count cards
- Skill length histogram
- Skill source treemap
- Crawl/import status table
- Missing/invalid record diagnostics

Questions answered:

- How large is the corpus?
- Which sources dominate?
- Are there data quality problems?

### 9.2 Skill Taxonomy

Purpose:

- Classify skills by role and domain.

Visualizations:

- Type distribution bar chart
- Domain treemap
- Source-by-type stacked bar
- Type-by-domain heatmap

Questions answered:

- Are most skills tool references, procedures, or generators?
- Does local skill usage differ from public skill ecosystems?

### 9.3 Workflow Structure

Purpose:

- Analyze skills as natural-language workflows.

Visualizations:

- Step count histogram
- Branching/verification indicator matrix
- Complexity scatter plot
- Workflow complexity ranking

Questions answered:

- How procedural are skills?
- Which skills have complex control flow?

### 9.4 Code and Tool Fragments

Purpose:

- Analyze embedded code-like content.

Visualizations:

- Code language bar chart
- Tool mention ranking
- Source-by-language heatmap
- Skill detail panel with extracted code blocks

Questions answered:

- Which tools and languages dominate?
- Are skills more like documentation, scripts, or workflows?

### 9.5 Dependency and Environment Risk

Purpose:

- Identify environment mismatch risks.

Visualizations:

- Dependency category stacked bars
- API key/env-var risk badges
- OS-specific assumption table
- High-risk dependency ranking

Questions answered:

- Which skills are hard to run on a clean machine?
- Which dependency types create the most risk?

### 9.6 Primitive Capabilities

Purpose:

- Show skill capability requirements.

Visualizations:

- Primitive frequency bar chart
- Primitive level heatmap
- Skill-by-primitive matrix
- Primitive co-occurrence network
- Taxonomy vs primitive Sankey diagram

Questions answered:

- Which primitive capabilities are most demanded?
- How do capability requirements vary by skill type?

### 9.7 Portability Risk

Purpose:

- Compare derived SCR with official or imported TCP profiles.

Visualizations:

- Skill-target gap heatmap
- Model/harness ranking by average gap
- Primitive bottleneck chart
- Same-model different-harness comparison
- Risk radar chart for selected skill

Questions answered:

- Which skills are least portable?
- Which model/harness pairs are most compatible with the corpus?
- Is fragility caused more by model capability or harness capability?

### 9.8 Skill Similarity Map

Purpose:

- Support open-ended exploration and outlier discovery.

Visualizations:

- 2D embedding map using TF-IDF/embeddings plus UMAP or t-SNE
- Cluster labels by dominant domain or taxonomy
- Clickable skill detail drawer
- Outlier list

Questions answered:

- What clusters exist in the skill ecosystem?
- Which skills are unusual or hard to classify?

## 10. Website Design

Technology:

- Vue 3
- Vite
- TypeScript
- ECharts for heatmaps, Sankey, radar, treemap, graph, and matrix views
- Plotly if needed for high-density scatter/embedding interactions
- Static JSON generated by Python scripts

Architecture:

```text
data/
|-- raw/
|-- interim/
|-- processed/
|-- dashboard/

scripts/
|-- collect_local_skills.py
|-- collect_skvm_data.py
|-- collect_public_skills.py       # optional extension
|-- extract_features.py
|-- extract_scr.py
|-- compute_risks.py
|-- build_dashboard_data.py

src/
|-- components/
|-- composables/
|-- types.ts
|-- App.vue
```

Design principles:

- First screen should be the actual dashboard, not a marketing landing page.
- Layout should prioritize dense but readable analytical views.
- Use filters for source, taxonomy, domain, primitive, risk level, and search.
- Every chart should connect to a research question.
- Selected skill detail panel should show evidence, not only scores.

## 11. Implementation Roadmap

### Phase 0: Project Scaffolding

Deliverables:

- Vite React TypeScript app
- Python script structure
- Basic README
- Data directory convention
- `docs/PROJECT_PLAN.md`

Acceptance criteria:

- App runs locally
- Scripts can be executed independently
- Project structure is clear

### Phase 1: Local Corpus Import

Deliverables:

- Local skill collector
- Markdown/frontmatter parser
- Raw and normalized local skill JSON
- Basic corpus overview JSON

Acceptance criteria:

- Imports local `SKILL.md` files from configured directories
- Deduplicates by path/content hash
- Produces normalized records

### Phase 2: SkVM Data Import

Deliverables:

- SkVM-data downloader/importer
- Parser for SkVM skills, tasks, and profiles
- TCP profile normalization

Acceptance criteria:

- Imports SkVM benchmark skills
- Imports model/harness TCP profiles when available
- Displays TCP matrix in dashboard data

### Phase 3: Public Skill Sampling

Current status: implemented as an optional GitHub sampler. The current checked-in/generated data snapshot contains 96 `public.github` skills collected through GitHub code search, so the dashboard now compares local skills, SkVM benchmark skills, and a small public GitHub sample. The public sample is intentionally modest and should be described as exploratory rather than representative of the full public skill ecosystem.

Deliverables:

- Public source crawler/sampler (`scripts/collect_public_skills.py`)
- Source metadata tracking
- Rate-limit and failure handling

Acceptance criteria:

- Collects a reproducible sample of public skills
- Stores source URLs and timestamps
- Failed records are logged without breaking pipeline

### Phase 4: Feature Extraction

Deliverables:

- Structural feature extractor
- Code block detector
- Tool/dependency detector
- Taxonomy classifier

Acceptance criteria:

- Every skill has structural metrics
- Every skill has preliminary taxonomy and domain tags
- Extracted evidence is inspectable

### Phase 5: SCR Extraction

Deliverables:

- Primitive catalog
- Rule-based SCR extractor
- Optional LLM-assisted extractor interface
- Manual validation sample export

Acceptance criteria:

- Every skill has zero or more primitive requirements
- Each requirement has level, method, evidence, and confidence
- Validation subset can be reviewed manually

LLM-assisted SCR configuration:

- Copy `.env.example` to `.env`
- Fill `SKILLSCOPE_LLM_API_KEY`
- Set `SKILLSCOPE_LLM_MODEL` to the model used for annotation
- Run `scripts/extract_scr_llm.py` after the normal pipeline

Recommended commands:

```powershell
& 'C:\Users\27651\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\extract_scr_llm.py --source skvm.benchmark --limit 20
& 'C:\Users\27651\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\extract_scr_llm.py --source skvm.benchmark --limit 108 --merge
& 'C:\Users\27651\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\compute_risks.py
& 'C:\Users\27651\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\build_dashboard_data.py
```

The project should report LLM SCR as derived labels, not official SkVM labels. Current status: the project has merged 20 `rule+llm` SCR annotations for SkVM benchmark skills through the configured OpenAI-compatible LLM API; the rest of the corpus remains rule-derived unless more annotations are requested.

### Phase 6: Risk and Gap Analysis

Deliverables:

- Environment risk score
- Model/harness gap score
- Primitive bottleneck aggregation
- Skill prioritization ranking

Acceptance criteria:

- SCR can be compared with TCP
- Dashboard data includes gap matrices
- Top risky skills have explanations

### Phase 7: Dashboard Implementation

Deliverables:

- Dashboard pages for Findings, Skills, Risks, Primitives, and SkVM Alignment
- Advanced EDA page with primitive co-occurrence, taxonomy-to-primitive Sankey, source-language heatmap, skill-primitive matrix, histograms, and PCA/k-means exploration
- Global filters
- Skill detail panel
- Responsive layout
- Chart interactions

Acceptance criteria:

- Users can filter by source, taxonomy, primitive, and risk
- Clicking a chart item updates the skill detail panel
- Main research questions are answerable from the interface

### Phase 8: Report and Presentation

Deliverables:

- Final report
- Slides
- Demo script
- Limitations and future work section
- SkVM alignment notes
- SCR validation sample

Acceptance criteria:

- Report explains data source distinction: official TCP vs derived SCR
- Report includes at least 5 concrete findings
- Demo can be completed within course presentation time

## 12. Expected Findings

The project should aim to derive findings such as:

1. Tool-reference and procedural skills dominate the corpus, while purely generative skills are less common.
2. Most skills require a small set of recurring primitives such as tool execution, file operations, procedure following, and code generation.
3. A small number of primitives may account for most portability gaps.
4. Harness differences may strongly affect tool-use primitives even when the model is unchanged.
5. Local skills may be more engineering-heavy and tool-dependent than public marketplace skills.
6. Skills with many environment dependencies tend to have higher portability risk.
7. Some short skills can still be high-risk if they depend on external APIs, credentials, or specialized tools.
8. Similarity clusters may reveal skill families such as web automation, document generation, security auditing, code review, and data analysis.

These are hypotheses, not guaranteed results. The final report should present them as data-driven findings only after analysis.

## 13. Evaluation Plan

### Data Quality Evaluation

- Count successfully parsed skills
- Count invalid or missing metadata records
- Compare duplicate rates across sources
- Track crawler failure reasons

### SCR Quality Evaluation

- Manually review 50 to 100 sampled skills
- Evaluate whether extracted primitives are reasonable
- Track precision-like agreement for primitive presence
- Track level agreement where possible
- Refine extraction rules based on errors

### Dashboard Evaluation

- Verify each research question maps to one or more dashboard views
- Test with local, SkVM, and public sources enabled separately
- Test selected skill detail panels for evidence traceability
- Check that large heatmaps and scatter plots remain usable

## 14. Risks and Mitigations

### Risk: Public skill crawling is unstable

Mitigation:

- Treat public crawling as sampling, not full replication
- Cache raw records
- Keep local and SkVM data sufficient for the core dashboard

### Risk: SCR labels are noisy

Mitigation:

- Store evidence and confidence
- Use manual validation
- Separate official TCP from derived SCR
- Avoid overclaiming exact skill requirements

### Risk: Primitive catalog diverges from SkVM

Mitigation:

- Import SkVM primitive names if available
- Maintain a mapping from project primitives to SkVM-style groups
- Document simplifications clearly

### Risk: Dashboard becomes chart-heavy but insight-light

Mitigation:

- Tie every module to research questions
- Include findings cards and ranked lists
- Add selected skill explanations and evidence

### Risk: Time runs out

Mitigation:

- Minimum viable version uses local skills + SkVM profiles + 4 core modules
- Public crawling, embeddings, and LLM-assisted SCR are optional enhancements

## 15. Minimum Viable Product

If time is limited, the MVP should include:

1. Local skills collector
2. SkVM-data importer for skills and profiles
3. Structural feature extraction
4. Rule-based taxonomy and SCR extraction
5. Corpus Overview module
6. Primitive Capabilities module
7. Portability Risk module
8. Skill detail panel with evidence

This MVP is enough to demonstrate the core idea: skills can be analyzed as natural-language programs, and their capability requirements can be compared against model/harness capability profiles.

## 16. Final Deliverables

- Dashboard website
- Data collection and preprocessing scripts
- Processed JSON datasets
- Project report
- Presentation slides
- Demo script
- Documentation explaining official data, derived labels, metrics, and limitations
- `docs/FINDINGS.md`
- `docs/DEMO_SCRIPT.md`
- `docs/SKVM_ALIGNMENT.md`
- `docs/VALIDATION.md`

## 18. Current Implementation Notes

The current project is a SkVM-inspired exploratory dashboard, not a reimplementation of the SkVM compiler/runtime. It implements local, public GitHub, and SkVM skill collection, feature extraction, derived SCR extraction with optional LLM assistance, imported TCP profile comparison, portability gap analysis, dependency/environment risk detection, findings cards, primitive visualizations, model/harness heatmaps, Advanced EDA views, and skill prioritization.

The current project includes a public skill sampler and an active 96-record public GitHub sample. It does not implement AOT skill rewriting, generated environment-binding scripts, concurrency DAG extraction, JIT code solidification, adaptive recompilation, or task-level completion/token/speedup evaluation. These should be presented as future work or SkVM paper features outside the scope of this course dashboard.

## 17. Suggested Project Narrative

The final presentation can follow this story:

1. Skills are becoming reusable units for LLM agents, but they are currently treated as raw context.
2. Inspired by SkVM, this project treats skills as natural-language programs.
3. We collect skills from local, SkVM, and public sources.
4. We extract structure, taxonomy, dependencies, and primitive capability requirements.
5. We compare skill requirements with model/harness capability profiles.
6. We visualize where portability risks come from.
7. We identify which skills, primitives, and environments are most fragile.
8. The result is an exploratory dashboard that helps understand and debug the skill ecosystem.
