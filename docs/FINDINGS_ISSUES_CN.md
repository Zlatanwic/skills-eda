# Findings 数据一致性问题清单

> **状态：已解决（2026-05-27）。** 本清单中的全部不一致已按文末「修复建议」统一对齐到 `findings.json` / `environment.json` / `portability.json` 真值，涉及 `PPT_OUTLINE_CN.md`、`FINDINGS.md`、`VISUALIZATION_GUIDE_CN.md`、`CHINESE_PRESENTATION_SCRIPT.md`、`DEMO_SCRIPT.md`。本文保留作为变更记录。

本文记录 findings 结论卡片与各讲稿/文档之间的数据不一致问题。

**结论先行**：`data/dashboard/findings.json` 是脚本（`build_dashboard_data.py` 的 `build_findings()`）从底层数据最新算出的真值，dashboard 直接读它。但所有人写的讲稿/文档（`FINDINGS.md`、`PPT_OUTLINE_CN.md`、`VISUALIZATION_GUIDE_CN.md`、`CHINESE_PRESENTATION_SCRIPT.md`、`DEMO_SCRIPT.md`）仍停留在旧版本数据，没有跟着重算后的 `findings.json` 更新。更严重的是，PPT 第 8 页**卡片**和**讲稿正文**对同一条 finding 给出两个不同答案。

数据真值以 `findings.json` 为准。

---

## 真值 vs 文档对照表

| Finding | findings.json（当前真值） | 文档/讲稿（旧值） | 是否一致 |
|---|---|---|---|
| Most common capability | `follow.constraints`，1680，**96.6%** | `follow.procedure`，1496，**86.0%** | ❌ primitive 和数字都不同 |
| Largest bottleneck gap | `doc.generate`，**18150** | `doc.generate`，**18068** | ❌ gap 分数不同 |
| Best target profile gap | `deepseek-v4-pro / openclaw`，**0.344** | 0.339 | ❌ |
| Environment dependency footprint | **1105/1739**，**63.5%** | **1107/1739**，**63.7%** | ❌ |
| Verification-heavy workflows | **1448/1739**，83.3% | 1368，83.3%（FINDINGS.md） | ❌ count 自相矛盾 |
| Riskiest source | `local.codex`，0.234，15 skills | （PPT 未列出） | — |
| Riskiest taxonomy | `tool-reference`，0.214 | `tool-reference`，0.214 | ✅ |
| Dominant mismatch axis | `harness`（model 0.136 / harness 0.143，margin 0.007） | `harness` | ✅ |

---

## 问题逐条说明

### 问题 1（最严重）：Most common capability 在卡片内自相矛盾

- `findings.json`：`follow.constraints`，1680 skills，96.6%。
- `PPT_OUTLINE_CN.md` 第 243 行卡片：`follow.constraints`（✅ 与真值一致）。
- `PPT_OUTLINE_CN.md` 第 256 行讲稿正文：「最常见的 primitive 是 `follow.procedure`，出现在 1,496 个 skills 中，占 86.0%」（❌ 与同页卡片矛盾，也与真值矛盾）。

**同一页 PPT，卡片说 `follow.constraints`，讲稿说 `follow.procedure`。** 答辩时如果照讲稿念，会和屏幕上卡片打架。

涉及旧值 `follow.procedure / 1496 / 86.0%` 的位置：
- `FINDINGS.md:19`
- `PPT_OUTLINE_CN.md:256`
- `VISUALIZATION_GUIDE_CN.md:27, 34`
- `CHINESE_PRESENTATION_SCRIPT.md:117`
- `DEMO_SCRIPT.md:39`

### 问题 2：环境依赖 1107 vs 1105、63.7% vs 63.5%

- 真值：1105/1739，63.5%。
- 旧值 `1107 / 63.7%` 出现在：
  - `PPT_OUTLINE_CN.md:246`（卡片）、`260`（讲稿）
  - `FINDINGS.md:53`
  - `VISUALIZATION_GUIDE_CN.md:299`
  - `CHINESE_PRESENTATION_SCRIPT.md:123`

### 问题 3：Best target gap 0.339 vs 0.344

- 真值：0.344。
- 旧值 0.339 出现在 `FINDINGS.md:39`、`PPT_OUTLINE_CN.md:260`、`CHINESE_PRESENTATION_SCRIPT.md:121`。

### 问题 4：Largest bottleneck gap 18068 vs 18150

- 真值：18150。
- 旧值 18068 出现在 `FINDINGS.md:31`、`PPT_OUTLINE_CN.md:258`。

### 问题 5：Verification 卡片 count 自相矛盾

- `findings.json`：1448/1739，83.3%（1448 ÷ 1739 ≈ 83.3%，内部自洽）。
- `FINDINGS.md:25`：1368 skills，83.3%（1368 ÷ 1739 ≈ 78.7%，count 与百分比对不上）。

旧文档的 1368 是错的，真值 1448 才与 83.3% 自洽。

### 问题 6：LLM SCR = 20 不是一条 finding

- `PPT_OUTLINE_CN.md:248` 把 `LLM SCR: 20` 列进 findings 卡片。
- `findings.json` 里没有这一条——它是独立统计 tile（rule+llm 合并标注数），不属于 8 条 findings。
- 这条数字本身（20）没错，但归类位置容易让人以为它是 findings 卡片之一。

### 问题 7：口径混用 follow.constraints vs follow.procedure

部分文档把「最常见 primitive」叙事建立在 `follow.procedure`（86.0%）上，但真值的 top primitive 是 `follow.constraints`（96.6%）。在「skills 高度 workflow 化」的论述里（如 `PPT_OUTLINE_CN.md:437`、`VISUALIZATION_GUIDE_CN.md:144,165`），两个 primitive 经常并列出现，本身不算错；但只要单独引用「最常见 = X」就必须统一到 `follow.constraints`，否则与卡片冲突。

---

## 修复建议

统一以 `findings.json` 为准，把以下旧值全部替换：

1. `follow.procedure / 1496 / 86.0%` → `follow.constraints / 1680 / 96.6%`（凡是指「最常见 primitive」处）
2. `1107 / 63.7%` → `1105 / 63.5%`
3. `0.339` → `0.344`
4. `18068` → `18150`
5. `FINDINGS.md` verification count `1368` → `1448`
6. PPT 第 8 页讲稿正文改用 `follow.constraints`，与同页卡片对齐
7. PPT 第 8 页把 `LLM SCR: 20` 单独标为「独立统计 tile」，不计入 8 条 findings

待用户确认后再执行批量替换。
