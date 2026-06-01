# SkillScope 可视化图表讲解指南

这份文档用于 15 分钟答辩时讲 Dashboard 各模块的代表性可视化图。每个图都按四点组织：

- 图表内容：图上是什么。
- 分析意义：为什么要看它。
- 可得结论：当前数据支持什么判断。
- 讲稿示例：答辩时可以怎么说。

## 1. Findings 模块

### 1.1 Findings Cards

图表内容：

- 一组结论卡片，每张卡片对应一个研究问题。
- 当前包括最常见 primitive、最大 bottleneck、风险最高来源、风险最高 taxonomy、最佳 target profile、环境依赖 footprint、verification-heavy workflow、dominant mismatch axis。

分析意义：

- 这是整个 dashboard 的“结论索引”。
- 它把后面复杂图表先压缩成几个可讨论的核心发现。
- 适合答辩开头先建立听众对项目结果的整体印象。

可得结论：

- 当前最常见能力需求是 `follow.constraints`，说明 skills 高度 workflow 化。
- 最大 portability bottleneck 是 `doc.generate`，说明文档生成和结构化输出是跨 target 的主要短板之一。
- 环境依赖覆盖 1,105 / 1,739 个 skills，说明 environment mismatch 是常见风险。
- 当前 dominant mismatch axis 是 harness，说明运行框架和工具支持不能忽略。

讲稿示例：

“Findings 页面不是普通图表堆叠，而是把研究问题直接转成结论卡片。比如这里可以看到，`follow.constraints` 出现在 1,680 个 skills 中，占 96.6%，说明 skills 普遍包含约束遵守和过程性操作。`doc.generate` 是最大的 gap bottleneck，说明文档生成和结构化输出在不同 target profiles 上最容易产生迁移问题。”

## 2. Skills 模块

### 2.1 Source Mix

图表内容：

- 柱状图。
- 横轴是 skill 来源，例如 `local.cc-switch`、`skvm.benchmark`、`public.github`、`local.agents`、`local.codex`。
- 纵轴是对应来源的 skill 数量。

分析意义：

- 用于说明当前语料由哪些来源构成。
- 可以判断分析结论主要受哪个来源影响。
- 加入 public GitHub sample 后，可以初步比较本机 skills、论文 benchmark skills 和公开样本。

可得结论：

- 当前 corpus 以 `local.cc-switch` 为主，说明本机 skill 生态是主要分析对象。
- `skvm.benchmark` 提供与论文对齐的参考样本。
- `public.github` 有 96 条，是公开样本的初步补充，但还不能代表完整公共生态。

讲稿示例：

“Source mix 图回答的是数据基础问题：我到底分析了哪些来源。可以看到当前最大来源是本机 `.cc-switch` skills，另外有 SkVM benchmark 和 96 条 public GitHub skills。这个图提醒我们，当前结果主要反映本机 skill 生态，同时已经具备公开样本对比的入口。”

### 2.2 Taxonomy

图表内容：

- 环形饼图。
- 展示 `tool-reference`、`procedural`、`generative`、`mixed` 等类型比例。

分析意义：

- 用于观察 skill 的功能角色分布。
- 判断 corpus 是偏工具说明、流程执行，还是内容生成。

可得结论：

- 如果 `tool-reference` 和 `procedural` 占比较高，说明 skills 更多是在描述工具使用和工作流执行。
- 这支持“skills 是自然语言程序，而不是普通文本知识库”的项目叙事。

讲稿示例：

“Taxonomy 图把 skill 分成工具引用、流程型、生成型和混合型。它的意义是看 skills 的角色结构。如果 tool-reference 和 procedural 很多，就说明这些 skills 更像操作规程和工具说明，而不是单纯的知识卡片。”

### 2.3 Code Languages

图表内容：

- 横向柱状图。
- 展示 fenced code blocks 中检测到的语言，例如 bash、python、typescript、javascript、plain 等。

分析意义：

- 判断 skills 是否嵌入了可执行或半可执行的代码片段。
- 反映技能对编程语言和工具链的依赖。

可得结论：

- 如果 bash、python、typescript 等语言出现频繁，说明 skills 与实际工程工具链联系紧密。
- 这也解释了为什么 environment risk 和 harness risk 很重要。

讲稿示例：

“Code Languages 图说明 skills 不是纯自然语言说明。很多 skills 里嵌入 bash、python 或 typescript 代码块，这意味着 agent 不仅要理解文本，还要能生成、执行或修改代码。因此这类 skill 的迁移风险会受到运行环境和工具支持影响。”

### 2.4 Risk-ranked Skills + Skill Detail

图表内容：

- 左侧是按 overall risk 排序的 skill 表格。
- 右侧是选中 skill 的 detail panel。
- detail panel 包括 taxonomy、features、risk radar、top primitives、evidence。

分析意义：

- 支持从总体统计回到单个样本。
- 让风险分数具备 evidence traceability，不是黑箱结论。

可得结论：

- 高风险 skill 往往同时具有较多 primitives、工具依赖、环境依赖或复杂 workflow。
- 通过 evidence 可以检查规则或 LLM SCR 是否合理。

讲稿示例：

“这个表格用于样本级下钻。EDA 不应该只停留在总体图表，还要能回到原始样本解释异常。点击一个高风险 skill 后，右侧会展示它的 primitive evidence 和 risk profile，这样可以验证分数是不是有文本依据。”

## 3. Primitives 模块

### 3.1 Primitive Level Heatmap

图表内容：

- 热力图。
- 横轴是能力等级 L1、L2、L3。
- 纵轴是 primitive。
- 颜色越深表示该 primitive 在该 level 上出现越多。

分析意义：

- 不只分析“需要哪些能力”，还分析“需要到什么复杂度”。
- 区分简单需求和复杂多步骤需求。

可得结论：

- `follow.constraints`、`follow.procedure`、`follow.verify` 等 primitive 频繁出现，说明 skills 普遍要求约束遵守、步骤执行和结果验证。
- 如果某些 primitive 在 L3 上颜色较深，说明这些能力通常涉及复杂组合、验证或多工具协作。

讲稿示例：

“Primitive Level Heatmap 的重点是等级。一个 primitive 出现很多并不一定意味着它复杂，但如果它大量集中在 L2 或 L3，就说明 skill 对这个能力有较高要求。这个图能帮助我们把能力需求从频率进一步细分到复杂度。”

### 3.2 Primitive Demand Ranking

图表内容：

- 横向柱状图。
- 展示出现次数最多的 primitive requirements。

分析意义：

- 找出 skill 生态中最普遍的能力需求。
- 回答“skills 最常要求模型或 agent 做什么”。

可得结论：

- 当前 workflow 类 primitive 非常突出，如 `follow.constraints`、`follow.procedure`、`follow.verify`。
- 这说明 skills 普遍要求模型按流程、按规则、带验证地行动。

讲稿示例：

“Primitive Demand Ranking 是最直接的能力需求排名。它说明当前 corpus 中最常见的不是单纯代码生成，而是 procedure、verification 和 constraints。这说明 skill 的核心不是知识，而是可执行流程和约束。”

### 3.3 Workflow Complexity Map

图表内容：

- 散点图。
- 横轴是 step count。
- 纵轴是 primitive diversity。
- 每个点代表一个 skill。

分析意义：

- 观察 workflow 复杂度和能力需求多样性之间的关系。
- 发现异常复杂 skill 或高风险 skill 家族。

可得结论：

- 右上角的点通常表示步骤多、primitive 种类也多，这类 skill 对模型和 harness 要求更高。
- 左上角可能表示文本短但能力需求密集的 skill，也值得检查。

讲稿示例：

“这个散点图把 workflow complexity 可视化。横轴越靠右说明步骤越多，纵轴越高说明涉及的 primitive 越多。右上角的 skill 往往是最复杂的，它们也更可能成为迁移风险或重写优先对象。”

### 3.4 Bottleneck Primitives

图表内容：

- 横向柱状图。
- 展示 SCR/TCP gap 聚合后最大的 primitive bottlenecks。

分析意义：

- 不只是看 primitive 出现频率，而是看哪些 primitive 真正造成 portability gap。
- 帮助定位跨模型和跨 harness 的薄弱能力。

可得结论：

- `doc.generate` 是当前最大 bottleneck。
- `reason.plan`、`data.parse`、`data.transform`、`tool.github` 也属于高 gap primitive。
- 这些能力是未来 skill rewriting 或 runtime adaptation 的优先方向。

讲稿示例：

“Bottleneck Primitives 和前面的 demand ranking 不一样。Demand ranking 看的是出现频率，而 bottleneck 看的是和 TCP profile 比较后的 gap。当前最大的 bottleneck 是 `doc.generate`，说明文档生成和结构化输出最容易在目标能力不足时出问题。”

## 4. Risks 模块

### 4.1 Model x Harness Portability Heatmap

图表内容：

- 热力图。
- 横轴是 model。
- 纵轴是 harness。
- 颜色表示平均 SCR/TCP gap。

分析意义：

- 同时观察 model 和 harness 对 portability 的影响。
- 避免把问题简单归因于“模型强不强”。

可得结论：

- `deepseek-v4-pro / openclaw` 当前平均 gap 最低，是最兼容 target。
- 不同 model/harness 组合差异明显，说明 portability 是组合属性。
- harness 变化可能显著影响工具和运行环境相关 skills。

讲稿示例：

“这个 heatmap 是 Risks 页最关键的图。横轴是模型，纵轴是 harness，颜色越深表示平均 gap 越大。它说明 skill portability 不是只由模型决定，也不是只由 harness 决定，而是 model/harness pair 的组合结果。”

### 4.2 Target Compatibility

图表内容：

- 横向柱状图。
- 将 target profiles 按平均 gap 排序。

分析意义：

- 直接回答哪个 target 最兼容，哪个 target 风险最高。
- 便于做运行目标选择。

可得结论：

- 低平均 gap 的 target 更适合当前 corpus。
- 高平均 gap 的 target 可能需要 skill rewriting、能力补齐或更强 harness。

讲稿示例：

“Target Compatibility 图把所有 target profiles 按平均 gap 排序。它的实用意义很直接：如果我要选择一个环境运行这批 skills，应该优先选择 gap 更低的组合。”

### 4.3 Risk Components

图表内容：

- 柱状图。
- 展示 model mismatch、harness mismatch、environment mismatch、overall risk 的平均值。

分析意义：

- 分解总风险来源。
- 避免只看 overall risk 而不知道风险来自哪里。

可得结论：

- 当前 model mismatch 和 harness mismatch 接近，但 harness 略高。
- environment mismatch 也是独立风险来源，尤其对工具链密集型 skills。

讲稿示例：

“Risk Components 图把风险拆开看。这样我们不是只说某个 skill 风险高，而是能进一步判断它是模型能力不足、harness 支持不足，还是环境依赖太重。”

### 4.4 Dependency / Environment Risk

图表内容：

- 横向柱状图。
- 展示 dependency categories，如 system cli、version control、web/browser、runtime、credentials、package managers。

分析意义：

- 衡量 skills 对外部运行环境的依赖。
- 解释为什么同一个 skill 在不同机器或 harness 上可能失败。

可得结论：

- 当前 63.5% skills 提到依赖、凭据、包或环境配置。
- system CLI、Git/version control、web/browser、runtime 是高频环境风险。
- environment mismatch 是 skills 迁移问题的重要组成部分。

讲稿示例：

“Dependency / Environment Risk 图说明，skill 迁移不是纯模型问题。很多 skills 需要 CLI、GitHub、浏览器、runtime 或 API key。如果目标环境没有这些依赖，即使模型本身足够强，skill 仍然可能失败。”

### 4.5 Rewrite / Compilation Priority

图表内容：

- 排名列表。
- 综合 overall risk、environment mismatch、primitive diversity、workflow complexity、SCR confidence gap。

分析意义：

- 把 EDA 结果转成行动建议。
- 指出哪些 skills 最值得优先检查、重写或未来编译。

可得结论：

- 高 priority skills 通常是风险高、依赖重、能力需求多或抽取置信度低。
- 这些样本可以作为后续优化的入口。

讲稿示例：

“这个列表让分析不只停留在描述阶段，而是转成下一步行动。如果未来要做 skill rewriting 或 compiler optimization，可以优先从这些高 priority skills 开始。”

## 5. Advanced EDA 模块

### 5.1 Primitive Co-occurrence Matrix

图表内容：

- 共现热力图。
- 横轴和纵轴都是 primitive。
- 颜色表示两个 primitives 在同一个 skill 中共同出现的次数。

分析意义：

- 发现能力需求的组合模式。
- 观察哪些 primitives 常常成组出现。

可得结论：

- procedure、verification、constraints 往往共同出现。
- tool use 相关 primitive 可能和 environment binding、file operation、Git/GitHub 等共同出现。
- skills 的能力需求不是单点，而是组合结构。

讲稿示例：

“Co-occurrence Matrix 用来看 primitive 之间的搭配关系。如果两个 primitives 经常在同一个 skill 中出现，说明它们可能构成一种常见 skill 模式。例如 procedure 和 verification 同时出现，说明很多 skills 既要求执行步骤，也要求检查结果。”

### 5.2 Taxonomy x Primitive Sankey

图表内容：

- 桑基图。
- 左侧是 taxonomy，如 tool-reference、procedural、generative、mixed。
- 右侧是 primitives。
- 连线粗细表示数量。

分析意义：

- 展示 skill 类型如何流向能力需求。
- 连接 taxonomy 和 SCR 两套标签体系。

可得结论：

- tool-reference 类型更容易流向 tool、file、package、GitHub 等 primitive。
- procedural 类型更容易流向 follow.procedure、follow.verify、follow.constraints。
- generative 类型更容易流向 doc.generate、code generation 等 primitive。

讲稿示例：

“Sankey 图把 taxonomy 和 primitive 连接起来。它回答的是：不同类型的 skill 到底需要哪些底层能力。这样 taxonomy 就不是孤立标签，而是可以解释能力需求差异的结构变量。”

### 5.3 Source x Language Heatmap

图表内容：

- 热力图。
- 横轴是代码语言。
- 纵轴是 source。
- 颜色表示某来源中该语言 code block 的数量。

分析意义：

- 比较不同来源的代码和工具链风格。
- 观察本机 skills、SkVM benchmark、public GitHub sample 是否有不同技术偏好。

可得结论：

- 某些来源可能更偏 shell 或 python。
- 本机 skills 如果工程工具链更重，会在 CLI/script 语言上更突出。
- public sample 可以作为初步外部对照。

讲稿示例：

“Source x Language Heatmap 让我们比较不同来源的技术风格。比如某个来源如果 bash 或 python code block 很多，就说明它更偏脚本和工程自动化；如果 plain 或 markdown 更多，则更偏说明文档。”

### 5.4 Skill x Primitive Matrix

图表内容：

- 矩阵热力图。
- 纵轴是沿 overall risk 谱分层均匀取样的 36 个 skills，按风险从高到低排序（顶部最高风险，底部最低风险）。
- 横轴是 top primitives。
- 颜色表示 required level（L1/L2/L3）。

选样说明：

- 早期版本只取风险最高的 36 个 skills，但它们的 primitive level 几乎全部饱和在 L3，矩阵退化成单一颜色、信息量为零。
- 改为沿风险谱分层均匀取样后，L1/L2/L3 的等级差异得以显现，全量分布大致是 L3 占 3/4、L2 占 1/4、L1 极少。

分析意义：

- 从单个 skill 角度查看能力需求画像。
- 借助风险梯度观察「越高风险的 skill 是否越倾向于把多个 primitives 顶到 L3」。

可得结论：

- 高风险 skills 在多个 primitives 上达到 L3，低风险 skills 更多停留在 L2，矩阵呈现顶部偏深、底部偏浅的梯度。
- 顶部高风险 skills 可能需要重写、拆分或编译优化。
- 同一风险区间的 skills 往往形成相似能力需求模式。

讲稿示例：

“Skill x Primitive Matrix 是从样本层面看能力需求。每一行是一个 skill，每一列是一个 primitive，颜色表示等级。这里我特意沿风险谱做了分层取样而不是只取最高风险样本——因为最高风险的 skills 等级几乎都饱和在 L3，全取它们矩阵会变成一片纯色；分层之后就能看到从顶部高风险偏 L3、到底部低风险偏 L2 的梯度，这样矩阵才真正反映出能力需求的差异。”

### 5.5 Length / Step Histogram

图表内容：

- 两个直方图。
- Length histogram 展示文本长度分布。
- Step histogram 展示 step count 分布。

分析意义：

- 分析 skill 的基础分布形态。
- 发现长尾和异常复杂样本。

可得结论：

- skills 往往不是均匀分布，而是存在长尾。
- 少量特别长或步骤特别多的 skills 可能对上下文、模型推理和执行稳定性构成压力。

讲稿示例：

“直方图是最基础但很重要的 EDA 图。Length histogram 和 Step histogram 可以告诉我们 skill 的复杂度是不是长尾分布。长尾样本通常值得进一步检查，因为它们可能带来上下文长度、执行复杂度和 portability 风险。”

### 5.6 PCA / Clustering Map

图表内容：

- 二维散点图。
- 每个点是一个 skill。
- 坐标来自 PCA 投影。
- 颜色来自 k-means cluster。

分析意义：

- 将多维特征压缩到二维，用于观察 skill 家族和异常点。
- 特征包括结构特征、dependency/tool 信号、branching/verification 和 primitive levels。

可得结论：

- skills 可能形成若干簇，例如工具密集型、文档生成型、代码生成型、流程控制型。
- 远离主簇的点可能是异常 skill 或高复杂度 skill。
- PCA/k-means 不是预测模型，而是探索性结构发现工具。

讲稿示例：

“PCA / Clustering Map 是本项目中机器学习方法的部分。我用结构特征和 SCR primitive 特征构造向量，先标准化，再用 PCA 投影到二维，最后用 k-means 给出粗聚类。这个图不是为了预测，而是帮助发现 skill 家族、异常点和高风险区域。”

## 6. Alignment 模块

### 6.1 SkVM Paper Alignment

图表内容：

- 三列表格：
  - Implemented
  - Partial
  - Out of scope

分析意义：

- 明确本项目和 SkVM 论文的关系。
- 防止把 EDA dashboard 误讲成 compiler/runtime 复现。

可得结论：

- 本项目实现的是 skill analysis、SCR extraction、TCP comparison、gap visualization。
- AOT compilation、JIT solidification、adaptive recompilation、runtime speedup evaluation 不在范围内。

讲稿示例：

“Alignment 页面用于讲清楚边界。本项目采用 SkVM 的思想和 TCP 数据，但没有实现 SkVM compiler/runtime。我的贡献是把 SkVM 的能力需求和迁移风险视角转化成一个探索性数据分析 dashboard。”

### 6.2 Primitive Mapping

图表内容：

- 项目 primitive 与 SkVM primitive 的映射列表。

分析意义：

- 解释为什么 project SCR 可以和 SkVM TCP profiles 做 gap comparison。
- 说明 mapping 是近似的。

可得结论：

- 大部分 project primitives 可以映射到 SkVM primitives 或相近能力。
- 部分项目特有 primitive，如 `tool.github`、`data.visualize`、`runtime.env_bind`，是近似映射。

讲稿示例：

“Primitive Mapping 解释了 SCR/TCP 比较的桥梁。因为我的 primitive catalog 和 SkVM 不是完全一致，所以需要把 project primitive 映射到最接近的 SkVM primitive。这个 mapping 支持分析，但也构成项目局限之一。”

## 7. 总结讲法

如果答辩时间有限，每个模块可以只讲一个核心图：

- Findings：Finding cards。
- Skills：Source Mix + Skill Detail。
- Primitives：Primitive Level Heatmap。
- Risks：Model x Harness Heatmap。
- Advanced EDA：PCA / Clustering Map。
- Alignment：Implemented / Partial / Out of scope。

推荐串联方式：

“Findings 先给结论，Skills 说明数据从哪里来并能回到样本，Primitives 解释 skill 需要哪些能力，Risks 解释这些能力在不同 target 上为什么会失败，Advanced EDA 用共现和降维发现更复杂的多变量结构，Alignment 最后说明本项目与 SkVM 的关系和边界。”
