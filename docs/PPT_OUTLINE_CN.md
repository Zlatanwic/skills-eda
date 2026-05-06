# SkillScope 15 分钟 PPT 大纲与逐页讲稿

建议时长：15 分钟。  
建议页数：15 页，每页约 45-70 秒。  
展示方式：PPT 为主，Dashboard 只在第 8、10、12 页做短暂现场切换或放截图，避免演示占用过多时间。

每个模块代表性可视化图的详细讲法见：[VISUALIZATION_GUIDE_CN.md](VISUALIZATION_GUIDE_CN.md)。

## 总体时间分配

| 页码 | 标题 | 建议时长 |
|---|---|---:|
| 1 | 项目标题与一句话概括 | 40 秒 |
| 2 | 背景：为什么 skills 值得分析 | 60 秒 |
| 3 | 论文启发：SkVM 给了什么视角 | 60 秒 |
| 4 | 研究问题 | 60 秒 |
| 5 | 数据来源与当前数据快照 | 70 秒 |
| 6 | 数据处理与分析流程 | 70 秒 |
| 7 | SCR / TCP / Gap 指标解释 | 70 秒 |
| 8 | Findings：核心发现总览 | 75 秒 |
| 9 | Skills：语料画像与样本下钻 | 70 秒 |
| 10 | Primitives：能力需求结构 | 75 秒 |
| 11 | Risks：迁移风险与环境风险 | 90 秒 |
| 12 | Advanced EDA：共现、矩阵、PCA 与聚类 | 90 秒 |
| 13 | 与 SkVM 的对齐和边界 | 70 秒 |
| 14 | 结论、局限与未来工作 | 75 秒 |
| 15 | 总结与答辩收束 | 45 秒 |

合计约 16 分钟以内。实际答辩时第 8、10、12 页可以根据剩余时间略讲快一些。

## 第 1 页：项目标题与一句话概括

PPT 内容：

- 标题：SkillScope
- 副标题：LLM Agent Skills 的探索性分析与可视化
- 关键词：SkVM-inspired / EDA / Dashboard / SCR-TCP Gap / PCA & Clustering
- 一句话：把 skills 当作自然语言程序，分析其结构、能力需求与迁移风险。

对应文档：

- [CHINESE_PRESENTATION_SCRIPT.md](CHINESE_PRESENTATION_SCRIPT.md) 第 0 节

讲稿：

各位老师好，我这次课程项目的题目是 **SkillScope: LLM Agent Skills 的探索性分析与可视化**。这个项目受 SkVM 论文启发，但我的目标不是复现 SkVM 的编译器和运行时，而是从探索性数据分析的角度，把 LLM agent skills 当成一种新的数据对象进行分析。

一句话概括就是：我把 skills 看成自然语言程序，分析它们的结构、能力需求、工具依赖、环境风险，以及在不同 model 和 harness 上的可迁移性，并做成一个可交互的 dashboard。

## 第 2 页：背景：为什么 skills 值得分析

PPT 内容：

- 左侧：一个 skill 的组成示意
  - workflow steps
  - tools / CLI / APIs
  - code blocks
  - dependencies
  - verification
  - environment assumptions
- 右侧：问题
  - 直接塞进上下文
  - 缺少能力需求分析
  - 缺少运行环境风险分析

对应讲稿章节：

- 第 1 节：背景与研究问题

讲稿：

随着 LLM agent 系统的发展，skills 正在变成一种重要的复用单位。一个 skill 可以告诉 agent 如何做代码审查、如何生成文档、如何使用 GitHub、如何分析数据，或者如何调用某个工具链。

但问题是，skills 经常被当成普通 prompt 文件直接塞进上下文。实际上，很多 skills 里面包含步骤、工具、代码、依赖、验证和环境假设。比如它可能要求运行 shell、读写文件、安装 npm package、调用 API key，最后还要验证结果是否正确。

所以 skills 不只是文本说明，它们更像一类自然语言程序。如果我们不分析它们的结构和能力需求，就很难判断它们在不同模型或运行框架上是否可靠。

## 第 3 页：论文启发：SkVM 给了什么视角

PPT 内容：

- SkVM 关键词：
  - Skills as natural-language programs
  - Target Capability Profile, TCP
  - Primitive capabilities
  - Model/harness heterogeneity
  - Compilation / portability
- 本项目采用：
  - skill 分析视角
  - primitive requirement 思路
  - TCP profile 比较思路
- 本项目不做：
  - compiler/runtime 复现

对应讲稿章节：

- 第 0 节、第 10 节

讲稿：

SkVM 论文给我的主要启发是：skills 可以被看作自然语言程序，而不同模型和不同 harness 可以被看作不同的执行目标。既然是执行目标，就会有能力差异；既然 skill 有能力需求，就可以比较 skill 的需求和目标的能力是否匹配。

SkVM 里有一个概念叫 TCP，也就是 Target Capability Profile，用来描述某个 model/harness 组合具备哪些 primitive capabilities。我的项目借用了这个思想：从 skill 文本中派生 SCR，也就是 Skill Capability Requirement，再把 SCR 和 SkVM 的 TCP profiles 做比较。

但我需要强调：SkillScope 是 SkVM-inspired 的 EDA dashboard，不是 SkVM compiler/runtime 的复现。我关注的是分析、可视化和解释。

## 第 4 页：研究问题

PPT 内容：

列出 7 个问题：

1. skills 最常要求哪些 primitive capabilities？
2. 不同来源 skills 的结构和风险有什么差异？
3. 哪些 model/harness 组合更兼容？
4. fragility 更多来自 model mismatch 还是 harness mismatch？
5. 哪些 primitives 是 bottleneck？
6. 环境依赖是否是主要风险？
7. 能否用共现、PCA、聚类发现 skill 家族和异常点？

对应讲稿章节：

- 第 1 节

讲稿：

围绕这个背景，我设置了几个探索性问题。第一，skills 最常要求哪些 primitive capabilities。第二，不同来源、不同类型的 skills 在结构和风险上有什么差异。第三，哪些 model/harness 组合更适合当前 skills corpus。第四，skill fragility 更多来自模型能力，还是来自 harness 的工具支持。

同时，我也关注环境依赖，例如 CLI、GitHub、runtime、API key 是否会成为风险。最后，我希望通过共现矩阵、PCA 和聚类这样的多变量 EDA 方法，看看能不能发现 skill 家族、异常点和高风险区域。

这些问题不是一个单一预测任务，而是典型的探索性分析：通过数据和可视化逐步发现结构、关系和异常。

## 第 5 页：数据来源与当前数据快照

PPT 内容：

数据卡片：

- 1,739 skills
- 25 TCP profiles
- 3 harnesses: `bare-agent`, `hermes`, `openclaw`
- 12 models
- 20 LLM-assisted SCR annotations

Source mix：

- `local.cc-switch`: 1,455
- `skvm.benchmark`: 106
- `public.github`: 96
- `local.agents`: 68
- `local.codex`: 14

对应讲稿章节：

- 第 2 节

讲稿：

当前数据主要来自三路 skill corpus。第一路是本机 local skills，包括 `.cc-switch`、`.agents`、`.codex` 等目录下的 `SKILL.md`。第二路是 SkVM benchmark skills，用来和论文数据保持对齐。第三路是 public GitHub skills，我实现了 `collect_public_skills.py`，通过 GitHub code search 采样公开的 `SKILL.md`。

当前快照一共有 1,739 个 skills，其中 `local.cc-switch` 是主体，有 1,455 条；SkVM benchmark 有 106 条；public GitHub 样本有 96 条。除此之外，我还导入了 SkVM-data 中 25 个 TCP profiles，覆盖 3 个 harness 和 12 个模型。

这里要特别区分：TCP 是 SkVM-data 导入的官方目标能力数据，而 SCR 是本项目从 skill 文本中派生的能力需求标签。

## 第 6 页：数据处理与分析流程

PPT 内容：

流程图：

```text
Skill Markdown
-> Feature Extraction
-> Taxonomy
-> SCR Extraction
-> Optional LLM SCR
-> SCR/TCP Gap
-> Advanced EDA
-> Dashboard
```

底部列技术栈：

- Python scripts
- Vue 3 + Vite + TypeScript
- ECharts
- Static JSON dashboard data

对应讲稿章节：

- 第 3 节

讲稿：

整个 pipeline 可以分成七步。首先收集不同来源的 `SKILL.md`，统一转成 JSON。然后解析 markdown、frontmatter、标题、代码块和步骤信号。

接着做特征提取，包括文本长度、词数、section 数、code block 数、step count、是否包含 branching、loop、verification，以及工具和依赖证据。之后做 taxonomy 分类，把 skills 分成 tool-reference、procedural、generative、mixed，并提取 domain tags。

然后是 SCR extraction。项目先用规则方法提取 primitive requirements，再对部分 SkVM benchmark skills 使用 LLM API 做辅助标注。当前已经合并了 20 条 `rule+llm` SCR annotations。

最后，把 SCR 和 TCP profiles 比较，计算 gap，再生成 dashboard 数据。

## 第 7 页：SCR / TCP / Gap 指标解释

PPT 内容：

定义：

- SCR: Skill Capability Requirement
- TCP: Target Capability Profile
- Level: L0-L3
- Gap:

```text
gap(skill, target, primitive)
= max(0, required_level - provided_level)
```

示例：

- skill requires `tool.github` L3
- target provides `tool.web` L1
- gap = 2

对应讲稿章节：

- 第 3 节

讲稿：

这一页解释核心指标。SCR 表示一个 skill 对能力的需求，例如需要执行 shell、读写文件、生成文档、调用 GitHub、做数据分析等。TCP 表示某个 model/harness 组合提供的能力等级。

能力等级分为 L0 到 L3。L0 表示没有能力，L1 表示基础能力，L2 表示标准多步骤能力，L3 表示复杂组合能力，通常包含分支、验证或多工具协作。

gap 的计算很直接：如果 skill 要求的等级高于 target 提供的等级，就产生差值。例如 skill 需要 `tool.github` L3，但目标环境只支持近似的 web/tool 能力 L1，那么 gap 就是 2。通过把所有 primitives 的 gap 聚合，就能得到 skill 对某个 target 的 portability risk。

## 第 8 页：Findings：核心发现总览

PPT 内容：

放 Findings 页面截图或复刻卡片：

- Most common capability: `follow.procedure`
- Largest bottleneck: `doc.generate`
- Best target: `deepseek-v4-pro / openclaw`
- Dependency footprint: `1107/1739`
- Dominant mismatch axis: `harness`
- LLM SCR: `20`

对应讲稿章节：

- 第 5 节

讲稿：

Findings 页面是 dashboard 首页，它把研究问题直接转成结论卡片。当前最常见的 primitive 是 `follow.procedure`，出现在 1,496 个 skills 中，占 86.0%。这说明大部分 skills 都包含过程性操作，不只是静态说明。

最大的 portability bottleneck 是 `doc.generate`，aggregate SCR/TCP gap 为 18,068。这说明结构化输出、长文本生成和文档生成，在不同 target profiles 之间存在明显能力差距。

当前最兼容的 target profile 是 `deepseek-v4-pro / openclaw`，平均 gap 是 0.339。环境依赖方面，有 1,107 个 skills，也就是 63.7%，提到了 dependencies、credentials、packages 或 environment setup。

这一页的作用是先给出结论，再用后面的模块解释结论如何产生。

## 第 9 页：Skills：语料画像与样本下钻

PPT 内容：

展示 `Skills` 页截图：

- Source mix
- Taxonomy
- Code languages
- Risk radar
- Risk-ranked skills + detail panel

重点标注：

- Source mix 已包含 `public.github`
- Risk-ranked skills 只在 Skills 页出现
- detail panel 显示 evidence

对应讲稿章节：

- 第 6 节

讲稿：

Skills 页面负责 corpus overview 和样本级下钻。Source mix 展示不同来源的数量分布，现在包含 local、SkVM benchmark 和 public GitHub 三类来源。Taxonomy 图展示不同 skill 类型，例如 tool-reference、procedural、generative 和 mixed。

Code languages 图分析 fenced code blocks 里的语言，帮助判断 skills 是偏普通文档，还是包含脚本和代码片段。

这一页底部还有 Risk-ranked skills 表格。点击某个 skill 后，右侧 detail panel 会显示它的 taxonomy、长度、steps、code blocks、risk profile、top primitives 和 evidence。这个设计很重要，因为 EDA 不能只看统计图，还要能回到原始样本解释异常。

## 第 10 页：Primitives：能力需求结构

PPT 内容：

展示 Primitives 页面 3-4 个图：

- Primitive Level Heatmap
- Primitive Demand Ranking
- Workflow Complexity Map
- Bottleneck Primitives

对应讲稿章节：

- 第 7 节

讲稿：

Primitives 页面专门分析 skill capability requirements。Primitive Level Heatmap 的横轴是 L1、L2、L3，纵轴是 primitive，颜色越深表示某个 primitive 在某个等级上出现越多。

这个图回答的不只是“需要什么能力”，还包括“需要到什么复杂度”。例如某个 primitive 如果大量集中在 L3，就说明它经常涉及复杂组合、验证或多步骤流程。

Workflow Complexity Map 用 step count 和 primitive diversity 组成散点图，可以帮助发现复杂工作流和异常点。Bottleneck Primitives 则结合 TCP profiles，展示哪些 primitives 造成的 portability gap 最大。

这个模块说明，skills 的能力需求是可以被拆解、统计和比较的。

## 第 11 页：Risks：迁移风险与环境风险

PPT 内容：

展示 Risks 页面：

- Model x Harness Portability Heatmap
- Target Compatibility
- Risk Components
- Dependency / Environment Risk
- Rewrite / Compilation Priority

对应讲稿章节：

- 第 8 节

讲稿：

Risks 页面回答 portability 和 fragility 问题。Model x Harness heatmap 的横轴是模型，纵轴是 harness，颜色表示平均 SCR/TCP gap。这个图说明，skill 是否可迁移并不是只由模型决定，也不是只由 harness 决定，而是两者组合的结果。

Risk Components 把风险拆成 model mismatch、harness mismatch、environment mismatch 和 overall risk。当前数据中 model mismatch 和 harness mismatch 很接近，但 harness 略高，说明运行框架和工具支持不能忽略。

Dependency / Environment Risk 统计 system cli、version control、web/browser、runtime、credentials、package managers 等风险类别。最后 Rewrite / Compilation Priority 给出综合排名，帮助判断如果未来要重写或编译 skills，应该优先处理哪些样本。

## 第 12 页：Advanced EDA：共现、矩阵、PCA 与聚类

PPT 内容：

展示 Advanced EDA 页面：

- Primitive co-occurrence matrix
- Taxonomy x primitive Sankey
- Source x language heatmap
- Skill x primitive matrix
- Length / step histogram
- PCA / k-means clustering map

对应讲稿章节：

- 第 9 节

讲稿：

Advanced EDA 页面补充了更典型的探索性分析方法。Primitive co-occurrence matrix 用来观察哪些 primitives 经常一起出现，比如 procedure、verification、constraints 和 tool use 是否形成组合模式。

Taxonomy x primitive Sankey 展示 skill 类型如何流向能力需求。Source x language heatmap 比较不同来源中的代码语言分布。Skill x primitive matrix 则选取高风险或 primitive-dense 的 skills，展示单个 skill 的能力需求画像。

最后是 PCA / Clustering Map。我用结构特征和 SCR primitive 特征构造向量，包括文本长度、词数、section 数、code block 数、step 数、dependency 数、tool 数、branching、loop、verification，以及 top primitives 的 required level。然后做标准化，用 PCA 投影到二维，再用 k-means 做粗聚类。

这里的 PCA 和聚类不是用于预测，而是用于探索 skill 家族、异常点和高风险区域。

## 第 13 页：与 SkVM 的对齐和边界

PPT 内容：

三列：

- Implemented
  - skill collection
  - SCR extraction
  - TCP import
  - gap analysis
  - dashboard visualization
- Partial
  - primitive mapping
  - environment risk
  - concurrency signals
- Out of scope
  - AOT compilation
  - JIT code solidification
  - adaptive recompilation
  - runtime speedup evaluation

对应讲稿章节：

- 第 10 节

讲稿：

这一页用于说明项目和 SkVM 论文的关系。已实现的部分包括：把 skills 当作自然语言程序来分析，提取 derived SCR，导入 SkVM TCP profiles，计算 SCR/TCP gap，检测 environment risk，并用 dashboard 可视化。

部分近似的地方包括 primitive mapping。因为项目 primitive catalog 和 SkVM primitive catalog 不完全一致，所以有些 project primitives 只能映射到最接近的 SkVM primitive。此外，environment binding 在本项目中是风险检测，而不是自动生成 setup scripts。

未实现的部分包括 AOT compilation、JIT code solidification、adaptive recompilation、runtime scheduling，以及 task-level completion、token 和 speedup evaluation。所以本项目准确定位是 SkVM-inspired EDA dashboard。

## 第 14 页：结论、局限与未来工作

PPT 内容：

主要结论：

- Skills 高度 workflow 化
- 环境依赖很常见
- Portability 与 model/harness pair 强相关
- `doc.generate` 等 primitives 是 bottleneck
- 多变量 EDA 能发现 skill 家族和异常点

局限：

- SCR 主要是规则 + 少量 LLM 辅助
- public sample 只有 96 条
- primitive mapping 近似
- PCA/k-means 只用于探索
- 未实现 SkVM runtime/compiler

未来工作：

- 扩大 public sample
- 人工验证 SCR sample
- 更完整的 embedding / clustering
- task-level evaluation

对应讲稿章节：

- 第 11-13 节

讲稿：

综合当前分析，我得到几个主要结论。第一，skills 高度 workflow 化，`follow.procedure`、`follow.verify` 和 `follow.constraints` 的出现频率都很高。第二，很多 skills 不只是文本说明，而是包含代码片段、工具链和外部服务依赖。第三，portability risk 和 model/harness pair 强相关。第四，environment mismatch 是重要风险，很多 skills 都依赖 CLI、GitHub、runtime、credentials 或 package managers。

局限方面，SCR 主要是规则派生，并辅以 20 条 LLM 标注，不是人工金标；public GitHub 样本目前是 96 条，只能做初步探索；PCA 和 k-means 也只是用于发现结构，不用于预测。

未来可以扩大 public sample，做人工 SCR validation，引入更完整的 embedding clustering，并进一步做 task-level evaluation。

## 第 15 页：总结与答辩收束

PPT 内容：

一句话总结：

> SkillScope turns skills from prompt-like files into analyzable natural-language programs.

三点贡献：

- 数据化：收集并结构化 skills
- 可解释：SCR/TCP gap + evidence traceability
- 可探索：dashboard + heatmap + Sankey + PCA/clustering

结束语：

- Questions?

对应讲稿章节：

- 第 14 节

讲稿：

最后总结一下，SkillScope 的核心价值是把原本隐藏在 skill 文本里的能力假设和运行风险变成可观察、可比较、可解释的分析结果。

从数据角度，它把 skills 从 prompt-like files 转成结构化数据；从分析角度，它用 SCR/TCP gap 分析 portability；从可视化角度，它提供了从 findings、risk heatmap 到 PCA/clustering 的多层探索方式。

因此，这个项目不仅展示了 skills 生态中的结构和风险，也为未来的 skill rewriting、compiler optimization 和 agent runtime adaptation 提供了数据基础。我的展示到这里，谢谢老师。

## 现场 Dashboard 演示建议

15 分钟版本建议最多演示 3 次：

1. 第 8 页后切到 `Findings`，停留 20 秒，说明结论卡片。
2. 第 11 页切到 `Risks`，停留 30 秒，指一下 model x harness heatmap 和 dependency risk。
3. 第 12 页切到 `Advanced EDA`，停留 30 秒，展示 PCA/clustering map 或 Sankey。

如果老师追问某个样本，再切到 `Skills` 页，点 `Risk-ranked skills` 中的一个样本看 detail panel。

## 备用问答

**问：你是不是复现了 SkVM？**

答：不是。我的项目是 SkVM-inspired EDA dashboard。它借用了 SkVM 对 skills、primitive capabilities 和 TCP profiles 的视角，但没有实现 compiler/runtime。

**问：SCR 标签可靠吗？**

答：SCR 主要是规则派生标签，适合探索性分析，但不是人工金标。当前我已经接入 LLM API，对 20 条 SkVM benchmark skills 合并了 `rule+llm` 辅助标注；后续还需要人工 validation sample 审核。

**问：public skills 样本够不够？**

答：当前 public GitHub sample 是 96 条，可以支持初步对比，但不能代表完整公共 skills 生态。它的价值主要是证明 pipeline 已经可以接入公开样本。

**问：为什么使用 PCA 和 k-means？**

答：它们用于多变量探索，不用于预测。PCA 帮助把结构特征和 primitive 特征投影到二维，k-means 帮助观察粗略 skill 家族和异常区域。

**问：这个项目和课程的 EDA 关系是什么？**

答：项目包含多源数据整合、特征工程、分布分析、共现分析、热力图、桑基图、散点图、降维、聚类、交互式过滤和样本级 drill-down，完整覆盖了探索性数据分析和可视化的主要方法。
