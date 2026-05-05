# SkillScope 中文展示讲稿

## 0. 开场

各位老师好，我这次《探索性数据分析与可视化技术》课程项目的题目是 **SkillScope: LLM Agent Skills 的探索性分析与可视化**。

这个项目受 SkVM 论文启发。SkVM 的核心观点是：现在很多 LLM agent 系统都会使用 skills，而 skills 不应该只被看成普通 prompt 或补充上下文。很多 skills 其实包含多步骤工作流、工具调用、代码片段、依赖配置、验证步骤和运行环境假设。因此，它们更像一种 **自然语言程序**。

我的项目不是复现 SkVM 的编译器和运行时，而是从探索性数据分析的角度出发，把 skills 当作一种新的数据对象，分析它们的结构、能力需求、工具依赖和迁移风险，并用 dashboard 的形式进行交互式可视化。

## 1. 背景与问题

随着 LLM agent 的发展，skills 正在成为一种重要的复用单位。比如一个 skill 可以告诉 agent 如何做代码审查、如何使用 GitHub、如何生成文档、如何分析数据，或者如何调用某个工具链。

但是当前 skills 的使用存在几个问题。

第一，skills 经常被直接塞进模型上下文里，系统并不会真正理解这个 skill 对模型能力和运行环境有什么要求。

第二，不同模型和不同 agent harness 的能力并不一样。一个 skill 在某个模型和 harness 上能工作，不代表换一个模型或换一个运行框架还能正常工作。

第三，很多 skills 依赖外部环境，比如 Python、Node、npm、pip、Git、GitHub、API key、浏览器、Docker 等。如果环境不匹配，skill 可能会失败，或者让 agent 花很多额外 token 去诊断和修复环境。

所以我的项目主要想回答以下几个研究问题：

1. skills 最常要求哪些 primitive capabilities？
2. 不同来源和不同类型的 skills，在结构和风险上有什么差异？
3. 哪些 model/harness 组合更适合运行当前 skills corpus？
4. skill fragility 更多来自 model mismatch，还是 harness mismatch？
5. 哪些 primitive capabilities 最容易成为 portability bottleneck？
6. 环境依赖是不是 skills 迁移风险的重要来源？
7. 哪些 skills 应该被优先重写、优化或者未来编译？

这些问题正好对应探索性数据分析的目标：不是先假设一个确定答案，而是通过数据和可视化逐步发现结构、异常、模式和关系。

## 2. 数据来源

当前项目主要使用三类数据。

第一类是本机 local skills，包括 `.cc-switch`、`.agents`、`.codex` 等目录下的 `SKILL.md` 文件。这部分数据可以反映我本机 agent skills 生态的实际情况。

第二类是 SkVM benchmark skills。SkVM-data 中提供了一批 benchmark skills 和 task 数据，我把其中的 skills 导入到项目中，作为和论文更直接对齐的参考样本。

第三类是 SkVM TCP profiles。TCP 的意思是 Target Capability Profile，也就是某个 model/harness 组合具备哪些 primitive capabilities，以及对应能力等级。当前项目导入了 25 个 TCP profiles，覆盖 3 个 harness 和 12 个模型。

这里有一个非常重要的区分：

- **TCP profiles 是从 SkVM-data 导入的官方数据。**
- **SCR labels 是本项目从 skill 文本中派生出来的标签。**

SCR 的意思是 Skill Capability Requirement，也就是一个 skill 对 primitive capability 的需求。比如一个 skill 如果要求执行 shell 命令、读写文件、调用 GitHub、生成 Python 代码，那么它就会有对应的 primitive requirement。

## 3. 分析流程

整个项目的数据处理流程可以概括为：

`Skill Markdown -> Feature Extraction -> Taxonomy -> SCR Extraction -> SCR/TCP Gap -> Dashboard`

第一步是收集和标准化 skills，把不同来源的 `SKILL.md` 转成统一 JSON 记录。

第二步是做结构特征提取，包括：

- 字符数和词数
- markdown section 数
- code block 数
- step count
- 是否包含 branching
- 是否包含 loop
- 是否包含 verification
- 工具证据
- 依赖证据

第三步是 taxonomy 分类，把 skills 初步分为：

- tool-reference
- procedural
- generative
- mixed

同时也会提取 domain tags，比如 code、data、document、web、security、research、agent、cloud 等。

第四步是 SCR extraction。项目使用规则方法识别 primitive requirements，并给出 level 和 evidence。Level 分为 L1、L2、L3，分别代表基础需求、标准多步骤需求和复杂组合需求。

第五步是 portability gap 分析。对于每个 skill，我会把它的 SCR 和每个 SkVM TCP profile 比较，计算：

`gap(skill, target, primitive) = max(0, required_level - provided_level)`

也就是说，如果 skill 要求某个 primitive 是 L3，但目标 model/harness 只支持 L1，那么这个 primitive 就会产生 gap。

最后，把所有分析结果生成 dashboard JSON，用 Vue 3、Vite、TypeScript 和 ECharts 做成交互式可视化网站。

## 4. Dashboard 总体布局

Dashboard 顶部有全局过滤器，可以按 source、taxonomy 和关键词进行筛选。筛选会影响下方所有统计图、风险分析和 skill detail。

当前页面分为五个主要模块：

1. Findings
2. Skills
3. Risks
4. Primitives
5. Alignment

底部还有一个 risk-ranked skill table 和右侧 skill detail panel，用于查看单个 skill 的具体证据。

## 5. Findings 模块

`Findings` 是默认首页，它不是单纯展示图表，而是把主要研究问题直接转成结论卡片。

目前这个页面展示了几个核心发现。

第一个发现是：`follow.procedure` 是最常见的 primitive，出现在 1,427 个 skills 中，占 86.9%。这说明大部分 skills 都不是简单知识片段，而是包含步骤和工作流的自然语言程序。

第二个发现是：`doc.generate` 是最大的 portability bottleneck，aggregate SCR/TCP gap 达到 17,059。这说明文档生成、结构化输出和长文本生成在不同 target profile 之间可能存在明显能力差距。

第三个发现是：当前最兼容的 target profile 是 `deepseek-v4-pro / openclaw`，平均 gap 是 0.341。这说明同一个 skill corpus 在不同 model/harness 组合上的兼容性差别很大。

第四个发现是：有 1,038 个 skills，也就是 63.2%，提到了 dependencies、credentials、packages 或 environment setup。这说明环境依赖不是边缘问题，而是 skills 生态中的常见风险。

第五个发现是：dashboard 会计算 model mismatch 和 harness mismatch 的平均贡献，用于回答“到底是模型能力问题更大，还是 harness 支持问题更大”。

这个模块解决的问题是：它让展示不是从一堆图开始，而是先给出可讨论的结论，再通过后续页面解释这些结论是怎么来的。

## 6. Skills 模块

`Skills` 页面是 corpus overview 和基础结构分析。

这里的第一个图是 Source mix，用于展示不同来源 skills 的数量分布。它回答的问题是：当前 corpus 主要由哪些来源构成？本机 skills 和 SkVM benchmark skills 的比例如何？

第二个图是 Taxonomy，用饼图展示 tool-reference、procedural、generative、mixed 等类型的分布。它帮助我们理解 skills 的角色结构：有些 skills 偏工具说明，有些偏流程控制，有些偏内容生成。

第三个图是 Primitive capability demand，展示当前筛选条件下最常见的 derived SCR primitives。这个图和 Findings 中的第一个结论相互对应，能说明哪些能力需求在 skills 中最普遍。

第四个图是 Code languages，用于分析 fenced code blocks 中出现的语言类型，例如 bash、python、typescript、javascript 等。这部分回答的是：skills 是否更像普通文档，还是包含大量代码和脚本片段？

第五个图是 Selected skill risk radar。当用户选择一个 skill 后，可以看到它在 model mismatch、harness mismatch、environment mismatch 和 overall risk 上的风险结构。

这个模块的作用是给出 corpus 的基本画像，包括来源、类型、代码片段和能力需求分布。

## 7. Primitives 模块

`Primitives` 页面专门分析 skill capability requirements。

第一个核心图是 **Primitive Level Heatmap**。横轴是 L1、L2、L3，纵轴是 primitive。颜色越深表示对应 primitive 在该 level 上出现越多。

这个图回答的问题是：skills 不仅需要哪些能力，还需要这些能力达到什么复杂度等级。比如某个 primitive 如果大量集中在 L3，就说明它往往不是简单调用，而是复杂、多步骤、需要验证或组合的能力需求。

第二个图是 **Primitive Demand Ranking**。它展示当前 corpus 中最常见的 primitives，例如 `follow.procedure`、`follow.verify`、`follow.constraints`、`tool.git`、`doc.generate` 等。

第三个图是 **Workflow Complexity Map**。横轴是 step count，纵轴是 primitive diversity。每个点是一个 skill。这个图可以帮助发现复杂工作流和异常点：比如有些 skill 步骤很多，同时 primitive 也很多，说明它可能对模型和 harness 都有较高要求。

第四个图是 **Bottleneck Primitives**。它不是单纯统计出现频率，而是结合 TCP profiles 之后，展示哪些 primitive 造成的 aggregate gap 最大。

这个模块解决的问题是：它把 skills 的“能力需求结构”可视化出来，让我们能看到 skills 作为自然语言程序到底依赖哪些底层能力。

## 8. Risks 模块

`Risks` 页面主要回答 portability 和 fragility 问题。

第一个图是 **Model x Harness Portability Heatmap**。横轴是模型，纵轴是 harness，每个格子的颜色表示平均 SCR/TCP gap。颜色越深，说明这个 model/harness 组合对当前 skills corpus 的支持越弱。

这个图非常关键，因为它说明 portability 不是只看模型，也不是只看 harness，而是两者组合的结果。

第二个图是 **Risk by Source**。它展示不同来源 skills 的平均风险。这个图可以帮助判断某些来源的 skills 是否更复杂、更依赖工具或更容易迁移失败。

第三个图是 **Target Compatibility**。它把所有 target profiles 按平均 gap 排序，让我们直观看到哪些 model/harness pair 最兼容、哪些最不兼容。

第四个图是 **Risk Components**。它把风险拆成 model mismatch、harness mismatch、environment mismatch 和 overall risk。这样可以避免只看一个总分，而是知道风险到底来自哪里。

第五个面板是 **Model vs Harness Contribution**。它直接计算平均 model mismatch 和平均 harness mismatch，并给出 dominant axis。这个面板对应项目最重要的问题之一：skill fragility 到底更受模型影响，还是更受运行框架影响？

第六个区域是 **Dependency / Environment Risk**。它统计 environment risk categories，例如：

- system cli
- version control
- web/browser
- runtime
- credentials
- package managers

这个专区回答的问题是：哪些环境依赖类型最常见？哪些 skills 对环境最敏感？

第七个区域是 **Rewrite / Compilation Priority**。这里不是只列最高风险 skills，而是用一个综合 priority score 排名。这个 score 结合了：

- overall risk
- environment mismatch
- primitive diversity
- workflow complexity
- SCR confidence gap

它解决的问题是：如果后续要重写、优化或编译 skills，应该从哪些 skills 开始。

## 9. Alignment 模块

`Alignment` 页面用于说明本项目和 SkVM 论文之间的关系。

这个页面非常重要，因为我的项目不是 SkVM 的完整复现，而是 SkVM-inspired EDA dashboard。

页面中分成三类：

第一类是已经实现的部分：

- 把 skills 当作可分析的自然语言程序
- 提取 derived SCR
- 导入 SkVM TCP profiles
- 计算 SCR/TCP gap
- 检测 environment risk
- 做 dashboard 可视化

第二类是部分近似的部分：

- 项目 primitive catalog 不是论文 primitive catalog 的完全复刻
- project primitives 被映射到最接近的 SkVM primitive ids
- environment binding 被简化成风险检测，而不是生成 setup scripts
- concurrency extraction 被简化成 `agent.parallel` 和复杂度信号，而不是真正生成 DAG

第三类是未实现的部分：

- AOT compilation
- target-specific skill variants
- environment-binding setup scripts
- concurrency DAG extraction
- JIT code solidification
- adaptive recompilation
- task-level completion rate、token、speedup evaluation

这个页面解决的问题是：它明确限定项目范围，避免把 EDA dashboard 误讲成 SkVM compiler/runtime，同时也说明未来可以怎么扩展。

## 10. Skill Detail 与 Evidence Traceability

页面下方有一个 risk-ranked skill table。用户点击某个 skill 后，右侧会显示它的 detail panel。

Detail panel 包括：

- skill name 和 source
- taxonomy
- length、steps、code blocks
- risk profile
- top primitives
- evidence list

这个设计的意义是：dashboard 不只是给一个黑箱分数，而是让用户能追溯到 skill 文本里的 evidence。例如为什么某个 skill 被认为需要 `tool.git`，为什么它有 environment risk，为什么它有 verification signal。

这符合探索性数据分析中的一个重要原则：不仅要看到统计结果，还要能回到原始样本检查异常和证据。

## 11. 得出的主要结论

综合当前分析，可以得到以下结论。

第一，skills 高度 workflow 化。`follow.procedure` 和 `follow.verify` 的出现频率很高，说明大部分 skills 都包含步骤、约束和验证逻辑。

第二，skills 不只是文本说明，很多 skills 包含代码片段、工具链和外部服务依赖。因此分析 skills 时，不能只看自然语言内容，还要看 code/tool/dependency signals。

第三，portability risk 和 model/harness pair 强相关。不同 target profile 对同一批 skills 的平均 gap 差异明显。

第四，environment mismatch 是重要风险。大量 skills 提到 CLI、Git/GitHub、browser、runtime、credentials 和 package managers。

第五，某些 primitive 是主要 bottleneck，例如 `doc.generate`、`reason.plan`、`data.parse`、`data.transform` 和 `tool.github`。这些能力应该成为后续 skill rewriting 或 compiler optimization 的重点。

第六，dashboard 可以给出优先重写或编译的 skills 排名，这让分析结果不只是描述性统计，还能转化成实际行动建议。

## 12. 这个项目解决了什么问题

这个项目主要解决了四个问题。

第一，它把 skills 从“普通 prompt 文件”转化成了可分析的数据对象。

第二，它把 skill 内部的结构、能力需求、工具依赖和环境假设显性化。

第三，它把 skill requirements 和 target capabilities 连接起来，用 SCR/TCP gap 来分析 portability。

第四，它用交互式可视化支持探索：用户可以过滤来源、类型、关键词，可以查看不同图表，也可以点击单个 skill 检查证据。

从课程角度看，这个项目体现了探索性数据分析和可视化技术的几个核心点：

- 多来源数据整合
- 特征工程
- 分类和标签提取
- 分布分析
- 排名分析
- 热力图分析
- 散点图分析
- 交互式过滤
- 样本级 drill-down
- 从图表到结论的叙事组织

## 13. 局限性

这个项目也有一些限制。

第一，SCR labels 是规则派生的，不是官方标注，因此存在噪声。项目已经生成了 validation sample，但还需要进一步人工验证。

第二，primitive mapping 是近似的。因为项目 primitive catalog 和 SkVM primitive catalog 不是完全一致，所以某些 project primitives 只能映射到最接近的 SkVM primitive。

第三，public skills crawling 还没有实现。目前主要比较 local skills 和 SkVM benchmark skills。

第四，environment risk 是 keyword-based，适合 EDA 阶段发现模式，但不能直接作为最终因果结论。

第五，本项目没有复现 SkVM 的 AOT compilation、JIT code solidification、adaptive recompilation，也没有跑 task-level completion rate、token reduction 或 speedup evaluation。

所以更准确地说，SkillScope 是一个 **SkVM-inspired exploratory dashboard**，而不是 SkVM compiler/runtime 的复现。

## 14. 结束语

总结来说，本项目把 LLM agent skills 当作自然语言程序进行探索性分析。通过结构特征、taxonomy、SCR primitive requirements、SkVM TCP profiles、portability gap 和 environment risk 的可视化，我们可以理解 skills 生态中最常见的能力需求、最脆弱的迁移点，以及哪些 skills 应该优先被重写或未来编译。

这个项目的价值在于：它把原本隐藏在 skill 文本里的能力假设和运行风险变成了可观察、可比较、可解释的分析结果，为后续 skill rewriting、compiler optimization 和 agent runtime adaptation 提供了数据基础。

以上就是我的展示，谢谢老师。
