<script setup lang="ts">
import { computed, ref } from "vue";
import EChart, { type ChartOption } from "./components/EChart.vue";
import FilterBar from "./components/FilterBar.vue";
import MetricCard from "./components/MetricCard.vue";
import PortabilityPanel from "./components/PortabilityPanel.vue";
import SkillDetail from "./components/SkillDetail.vue";
import SkillTable from "./components/SkillTable.vue";
import { useDashboardData } from "./composables/useDashboardData";
import type {
  CountItem,
  DashboardSummary,
  EnvironmentSummary,
  FindingItem,
  ModelHarnessContribution,
  PortabilitySummary,
  PrioritizedSkill,
  RiskGroup,
  SkillIndexRecord,
  SkvmAlignment,
} from "./types";

type PageKey = "findings" | "skills" | "risks" | "primitives" | "alignment";

function barOption(title: string, items: CountItem[], color: string): ChartOption {
  return {
    color: [color],
    tooltip: { trigger: "axis" },
    grid: { left: 12, right: 12, top: 24, bottom: 36, containLabel: true },
    xAxis: {
      type: "category",
      data: items.map((item) => item.name),
      axisLabel: { interval: 0, rotate: items.length > 6 ? 28 : 0, color: "#6a6a6a" },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#6a6a6a" },
      splitLine: { lineStyle: { color: "#ebebeb" } },
    },
    series: [{ name: title, type: "bar", data: items.map((item) => item.count), barMaxWidth: 28 }],
  };
}

function horizontalBarOption(title: string, items: CountItem[], color: string): ChartOption {
  const displayItems = [...items].slice(0, 12).reverse();
  return {
    color: [color],
    tooltip: { trigger: "axis" },
    grid: { left: 132, right: 18, top: 12, bottom: 18 },
    xAxis: {
      type: "value",
      axisLabel: { color: "#6a6a6a" },
      splitLine: { lineStyle: { color: "#ebebeb" } },
    },
    yAxis: {
      type: "category",
      data: displayItems.map((item) => item.name),
      axisLabel: { color: "#3f3f3f" },
      axisTick: { show: false },
    },
    series: [{ name: title, type: "bar", data: displayItems.map((item) => item.count), barMaxWidth: 18 }],
  };
}

function pieOption(items: CountItem[]): ChartOption {
  return {
    tooltip: { trigger: "item" },
    color: ["#ff385c", "#222222", "#6a6a6a", "#ffd1da"],
    legend: { bottom: 0, textStyle: { color: "#6a6a6a" } },
    series: [
      {
        type: "pie",
        radius: ["46%", "70%"],
        center: ["50%", "44%"],
        data: items.map((item) => ({ name: item.name, value: item.count })),
        label: { color: "#3f3f3f" },
      },
    ],
  };
}

function radarOption(skill: SkillIndexRecord | null): ChartOption {
  const risk = skill?.risks ?? {
    model_mismatch: 0,
    harness_mismatch: 0,
    environment_mismatch: 0,
    overall: 0,
  };
  return {
    tooltip: {},
    radar: {
      indicator: [
        { name: "model", max: 1 },
        { name: "harness", max: 1 },
        { name: "env", max: 1 },
        { name: "overall", max: 1 },
      ],
      radius: "62%",
      splitLine: { lineStyle: { color: "#dddddd" } },
      axisLine: { lineStyle: { color: "#dddddd" } },
      axisName: { color: "#6a6a6a" },
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value: [
              risk.model_mismatch,
              risk.harness_mismatch,
              risk.environment_mismatch,
              risk.overall,
            ],
            name: skill?.name ?? "No skill selected",
            areaStyle: { opacity: 0.18 },
            itemStyle: { color: "#ff385c" },
            lineStyle: { color: "#ff385c" },
          },
        ],
      },
    ],
  };
}

function riskGroupOption(title: string, items: RiskGroup[]): ChartOption {
  const displayItems = [...items].sort((a, b) => b.avg_risk - a.avg_risk).slice(0, 12).reverse();
  return {
    color: ["#ff385c"],
    tooltip: {
      trigger: "axis",
      formatter: (params: unknown) => {
        const item = Array.isArray(params) ? (params[0] as { dataIndex: number }) : null;
        const group = item ? displayItems[item.dataIndex] : null;
        return group ? `${group.name}<br/>Avg risk: ${Math.round(group.avg_risk * 100)}<br/>Skills: ${group.count}` : "";
      },
    },
    grid: { left: 132, right: 24, top: 12, bottom: 18 },
    xAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#6a6a6a" },
      splitLine: { lineStyle: { color: "#ebebeb" } },
    },
    yAxis: {
      type: "category",
      data: displayItems.map((item) => item.name),
      axisLabel: { color: "#3f3f3f" },
      axisTick: { show: false },
    },
    series: [{ name: title, type: "bar", data: displayItems.map((item) => Math.round(item.avg_risk * 100)), barMaxWidth: 18 }],
  };
}

function riskBreakdownOption(skills: SkillIndexRecord[]): ChartOption {
  const items = [
    { name: "model", value: average(skills.map((skill) => skill.risks.model_mismatch)) },
    { name: "harness", value: average(skills.map((skill) => skill.risks.harness_mismatch)) },
    { name: "environment", value: average(skills.map((skill) => skill.risks.environment_mismatch)) },
    { name: "overall", value: average(skills.map((skill) => skill.risks.overall)) },
  ];
  return {
    color: ["#222222"],
    tooltip: { trigger: "axis" },
    grid: { left: 48, right: 16, top: 20, bottom: 36 },
    xAxis: { type: "category", data: items.map((item) => item.name), axisLabel: { color: "#6a6a6a" }, axisTick: { show: false } },
    yAxis: { type: "value", max: 100, axisLabel: { color: "#6a6a6a" }, splitLine: { lineStyle: { color: "#ebebeb" } } },
    series: [{ name: "avg risk", type: "bar", data: items.map((item) => Math.round(item.value * 100)), barMaxWidth: 32 }],
  };
}

function targetGapOption(portability: PortabilitySummary | null): ChartOption {
  const displayItems = [...(portability?.target_ranking ?? [])].slice(0, 12).reverse();
  return {
    color: ["#ff385c"],
    tooltip: { trigger: "axis" },
    grid: { left: 168, right: 24, top: 12, bottom: 18 },
    xAxis: { type: "value", axisLabel: { color: "#6a6a6a" }, splitLine: { lineStyle: { color: "#ebebeb" } } },
    yAxis: {
      type: "category",
      data: displayItems.map((item) => `${item.model.split("/").pop()} / ${item.harness}`),
      axisLabel: { color: "#3f3f3f" },
      axisTick: { show: false },
    },
    series: [{ name: "avg gap", type: "bar", data: displayItems.map((item) => item.avg_gap), barMaxWidth: 18 }],
  };
}

function modelHarnessHeatmapOption(portability: PortabilitySummary | null): ChartOption {
  const matrix = portability?.target_matrix ?? [];
  const harnesses = [...new Set(matrix.map((item) => item.harness))].sort();
  const models = [...new Set(matrix.map((item) => item.model))].sort();
  const data = matrix.map((item) => [
    models.indexOf(item.model),
    harnesses.indexOf(item.harness),
    item.avg_gap,
    item.skill_count,
  ]);
  const maxValue = Math.max(...matrix.map((item) => item.avg_gap), 1);
  return {
    tooltip: {
      position: "top",
      formatter: (params: unknown) => {
        const value = (params as { data: [number, number, number, number] }).data;
        return `${models[value[0]]?.split("/").pop()}<br/>${harnesses[value[1]]}<br/>Avg gap: ${value[2]}<br/>Skills: ${value[3]}`;
      },
    },
    grid: { left: 96, right: 28, top: 24, bottom: 110 },
    xAxis: {
      type: "category",
      data: models.map((model) => model.split("/").pop()),
      axisLabel: { color: "#6a6a6a", rotate: 35 },
      splitArea: { show: true },
    },
    yAxis: {
      type: "category",
      data: harnesses,
      axisLabel: { color: "#3f3f3f" },
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: false,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      inRange: { color: ["#ffffff", "#ffd1da", "#ff385c", "#e00b41"] },
      textStyle: { color: "#6a6a6a" },
    },
    series: [{ name: "avg gap", type: "heatmap", data, label: { show: false } }],
  };
}

function primitiveLevelHeatmapOption(items: CountItem[]): ChartOption {
  const topPrimitives = countBy(
    items.map((item) => item.name.split(":L")[0]),
    (primitive) => primitive,
  )
    .slice(0, 14)
    .map((item) => item.name);
  const levels = ["L1", "L2", "L3"];
  const lookup = new Map(items.map((item) => [item.name, item.count]));
  const data = topPrimitives.flatMap((primitive, y) =>
    levels.map((level, x) => [x, y, lookup.get(`${primitive}:${level}`) ?? 0]),
  );
  const maxValue = Math.max(...data.map((item) => Number(item[2])), 1);
  return {
    tooltip: {
      position: "top",
      formatter: (params: unknown) => {
        const dataItem = (params as { data: [number, number, number] }).data;
        return `${topPrimitives[dataItem[1]]} ${levels[dataItem[0]]}<br/>${dataItem[2]} skills`;
      },
    },
    grid: { left: 142, right: 24, top: 28, bottom: 42 },
    xAxis: { type: "category", data: levels, splitArea: { show: true }, axisLabel: { color: "#6a6a6a" } },
    yAxis: { type: "category", data: topPrimitives, splitArea: { show: true }, axisLabel: { color: "#3f3f3f" } },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: false,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      inRange: { color: ["#fff5f7", "#ffd1da", "#ff385c", "#e00b41"] },
      textStyle: { color: "#6a6a6a" },
    },
    series: [{ name: "primitive levels", type: "heatmap", data, label: { show: false }, emphasis: { itemStyle: { borderColor: "#222222" } } }],
  };
}

function dependencyCategories(skill: SkillIndexRecord): string[] {
  const text = [
    ...skill.features.dependency_evidence,
    ...skill.features.tool_evidence,
    ...Object.keys(skill.features.code_languages),
  ].join(" ").toLowerCase();
  const categories = [
    { name: "credentials", tokens: ["api key", "token", "secret", "credential", "env var", "environment variable"] },
    { name: "package managers", tokens: ["pip install", "npm install", "pnpm install", "yarn add", "package", "requirements.txt", "package.json"] },
    { name: "system cli", tokens: ["bash", "shell", "powershell", "cli", "curl", "wget", "docker"] },
    { name: "web/browser", tokens: ["browser", "playwright", "web", "api"] },
    { name: "version control", tokens: ["git", "github", "gh "] },
    { name: "runtime", tokens: ["python", "node", "npm", "uv", "pip"] },
  ];
  const hits = categories.filter((category) => category.tokens.some((token) => text.includes(token))).map((category) => category.name);
  if (hits.length > 0) return hits;
  return skill.features.dependency_count > 0 ? ["implicit"] : [];
}

function buildEnvironmentSummary(skills: SkillIndexRecord[]): EnvironmentSummary {
  const categoryCounts = countBy(skills.flatMap((skill) => dependencyCategories(skill)), (category) => category);
  const topEnvironmentRiskSkills = [...skills]
    .sort(
      (a, b) =>
        b.risks.environment_mismatch - a.risks.environment_mismatch ||
        b.features.dependency_count - a.features.dependency_count ||
        b.features.tool_count - a.features.tool_count,
    )
    .slice(0, 30)
    .map((skill) => ({
      skill_id: skill.skill_id,
      name: skill.name,
      source: skill.source,
      dependency_count: skill.features.dependency_count,
      tool_count: skill.features.tool_count,
      env_risk: skill.risks.environment_mismatch,
    }));

  return {
    avg_dependency_count: Number(average(skills.map((skill) => skill.features.dependency_count)).toFixed(2)),
    avg_tool_count: Number(average(skills.map((skill) => skill.features.tool_count)).toFixed(2)),
    dependency_skill_count: skills.filter((skill) => skill.features.dependency_count > 0).length,
    env_risk_skill_count: skills.filter((skill) => skill.risks.environment_mismatch >= 0.4).length,
    dependency_categories: categoryCounts,
    top_environment_risk_skills: topEnvironmentRiskSkills,
  };
}

function buildModelHarnessContribution(skills: SkillIndexRecord[]): ModelHarnessContribution {
  const avgModel = Number(average(skills.map((skill) => skill.risks.model_mismatch)).toFixed(3));
  const avgHarness = Number(average(skills.map((skill) => skill.risks.harness_mismatch)).toFixed(3));
  const dominantAxis = avgModel > avgHarness ? "model" : avgHarness > avgModel ? "harness" : "balanced";
  return {
    avg_model_mismatch: avgModel,
    avg_harness_mismatch: avgHarness,
    dominant_axis: dominantAxis,
    margin: Number(Math.abs(avgModel - avgHarness).toFixed(3)),
    interpretation:
      dominantAxis === "model"
        ? "Model mismatch contributes more to average risk."
        : dominantAxis === "harness"
          ? "Harness mismatch contributes more to average risk."
          : "Model and harness mismatch are approximately balanced.",
  };
}

function priorityScore(skill: SkillIndexRecord): number {
  const primitivePressure = Math.min(1, skill.scr.requirements.length / 24);
  const complexity = Math.min(1, skill.features.step_count / 20 + skill.features.code_block_count / 20);
  const confidenceGap = 1 - skill.scr.confidence;
  return Number(
    Math.min(
      1,
      skill.risks.overall * 0.38 +
        skill.risks.environment_mismatch * 0.22 +
        primitivePressure * 0.16 +
        complexity * 0.14 +
        confidenceGap * 0.1,
    ).toFixed(3),
  );
}

function buildPrioritization(skills: SkillIndexRecord[]): PrioritizedSkill[] {
  return [...skills]
    .sort((a, b) => priorityScore(b) - priorityScore(a))
    .slice(0, 50)
    .map((skill) => ({
      skill_id: skill.skill_id,
      name: skill.name,
      source: skill.source,
      taxonomy: skill.taxonomy.primary_type,
      priority_score: priorityScore(skill),
      overall_risk: skill.risks.overall,
      environment_mismatch: skill.risks.environment_mismatch,
      primitive_count: skill.scr.requirements.length,
      scr_confidence: skill.scr.confidence,
      step_count: skill.features.step_count,
      code_block_count: skill.features.code_block_count,
      reason: "high gap/risk, environment pressure, primitive diversity, complexity, or low SCR confidence",
    }));
}

function buildFindings(
  skills: SkillIndexRecord[],
  summary: DashboardSummary,
  portability: PortabilitySummary | null,
): FindingItem[] {
  const total = skills.length || 1;
  const topPrimitive = summary.capabilities.primitive_counts[0];
  const topBottleneck = portability?.primitive_bottleneck[0];
  const riskiestSource = [...summary.risks.by_source].sort((a, b) => b.avg_risk - a.avg_risk)[0];
  const riskiestTaxonomy = [...summary.risks.by_taxonomy].sort((a, b) => b.avg_risk - a.avg_risk)[0];
  const bestTarget = portability?.target_ranking[0];
  const dependencyCount = summary.environment.dependency_skill_count;
  const verificationCount = skills.filter((skill) => skill.features.has_verification).length;
  const modelHarness = summary.model_harness_contribution;

  return [
    {
      title: "Most common capability",
      value: topPrimitive?.name ?? "n/a",
      detail: topPrimitive ? `${topPrimitive.count.toLocaleString()} skills (${((topPrimitive.count / total) * 100).toFixed(1)}%) require this primitive.` : "No primitive data.",
      question: "What capability requirements are most common?",
    },
    {
      title: "Largest portability bottleneck",
      value: topBottleneck?.primitive ?? "n/a",
      detail: topBottleneck ? `Aggregated SCR/TCP gap score: ${topBottleneck.gap_sum.toLocaleString()}.` : "No TCP gap data.",
      question: "Which primitive capabilities become bottlenecks most often?",
    },
    {
      title: "Riskiest source",
      value: riskiestSource?.name ?? "n/a",
      detail: riskiestSource ? `Average overall risk is ${riskiestSource.avg_risk.toFixed(3)} across ${riskiestSource.count.toLocaleString()} skills.` : "No source risk data.",
      question: "Do skills from different sources have different structures and risks?",
    },
    {
      title: "Riskiest taxonomy",
      value: riskiestTaxonomy?.name ?? "n/a",
      detail: riskiestTaxonomy ? `Average overall risk is ${riskiestTaxonomy.avg_risk.toFixed(3)}.` : "No taxonomy risk data.",
      question: "How do skill taxonomy and primitive requirements relate?",
    },
    {
      title: "Best target profile",
      value: bestTarget ? `${bestTarget.model.split("/").pop()} / ${bestTarget.harness}` : "n/a",
      detail: bestTarget ? `Lowest average gap is ${bestTarget.avg_gap.toFixed(3)} across ${bestTarget.skill_count.toLocaleString()} skills.` : "No target profile data.",
      question: "Which model/harness pairs are most compatible with the corpus?",
    },
    {
      title: "Environment dependency footprint",
      value: `${dependencyCount.toLocaleString()}/${skills.length.toLocaleString()}`,
      detail: `${((dependencyCount / total) * 100).toFixed(1)}% of skills mention dependencies, credentials, packages, or environment setup.`,
      question: "Are environment dependencies a major portability risk?",
    },
    {
      title: "Verification-heavy workflows",
      value: `${verificationCount.toLocaleString()}/${skills.length.toLocaleString()}`,
      detail: `${((verificationCount / total) * 100).toFixed(1)}% of skills include test/check/verify signals.`,
      question: "How procedural are skills?",
    },
    {
      title: "Dominant mismatch axis",
      value: modelHarness.dominant_axis,
      detail: `Model avg ${modelHarness.avg_model_mismatch.toFixed(3)}, harness avg ${modelHarness.avg_harness_mismatch.toFixed(3)}; margin ${modelHarness.margin.toFixed(3)}.`,
      question: "Is model mismatch or harness mismatch stronger?",
    },
  ];
}

function primitiveDiversityOption(skills: SkillIndexRecord[]): ChartOption {
  const points = skills.slice(0, 500).map((skill) => [
    skill.features.step_count,
    skill.scr.requirements.length,
    Math.round(skill.risks.overall * 100),
    skill.name,
  ]);
  return {
    color: ["#ff385c"],
    tooltip: {
      formatter: (params: unknown) => {
        const value = (params as { value: [number, number, number, string] }).value;
        return `${value[3]}<br/>Steps: ${value[0]}<br/>Primitives: ${value[1]}<br/>Risk: ${value[2]}`;
      },
    },
    grid: { left: 52, right: 20, top: 24, bottom: 42 },
    xAxis: { name: "steps", type: "value", axisLabel: { color: "#6a6a6a" }, splitLine: { lineStyle: { color: "#ebebeb" } } },
    yAxis: { name: "primitives", type: "value", axisLabel: { color: "#6a6a6a" }, splitLine: { lineStyle: { color: "#ebebeb" } } },
    series: [{ type: "scatter", data: points, symbolSize: 8, itemStyle: { opacity: 0.58 } }],
  };
}

function countBy<T>(items: T[], getKey: (item: T) => string | string[]): CountItem[] {
  const counts = new Map<string, number>();
  for (const item of items) {
    const keys = getKey(item);
    for (const key of Array.isArray(keys) ? keys : [keys]) {
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

function average(items: number[]): number {
  if (items.length === 0) return 0;
  return items.reduce((sum, item) => sum + item, 0) / items.length;
}

function buildFilteredSummary(skills: SkillIndexRecord[]): DashboardSummary {
  const primitiveCounts = countBy(skills.flatMap((skill) => skill.scr.requirements), (requirement) => requirement.primitive);
  const primitiveLevelCounts = countBy(
    skills.flatMap((skill) => skill.scr.requirements),
    (requirement) => `${requirement.primitive}:L${requirement.level}`,
  );
  const codeLanguageCounts = countBy(
    skills.flatMap((skill) =>
      Object.entries(skill.features.code_languages).flatMap(([language, count]) =>
        Array.from({ length: count }, () => language),
      ),
    ),
    (language) => language,
  );
  const toolCounts = countBy(skills.flatMap((skill) => skill.features.tool_evidence), (tool) => tool);
  const dependencyCounts = countBy(skills.flatMap((skill) => skill.features.dependency_evidence), (dependency) => dependency);

  const riskBySource = countBy(skills, (skill) => skill.source).map((item) => ({
    name: item.name,
    count: item.count,
    avg_risk: Number(average(skills.filter((skill) => skill.source === item.name).map((skill) => skill.risks.overall)).toFixed(3)),
  }));
  const riskByTaxonomy = countBy(skills, (skill) => skill.taxonomy.primary_type).map((item) => ({
    name: item.name,
    count: item.count,
    avg_risk: Number(
      average(skills.filter((skill) => skill.taxonomy.primary_type === item.name).map((skill) => skill.risks.overall)).toFixed(3),
    ),
  }));
  const topRisky = [...skills].sort((a, b) => b.risks.overall - a.risks.overall).slice(0, 50);

  return {
    overview: {
      skill_count: skills.length,
      source_counts: countBy(skills, (skill) => skill.source),
      taxonomy_counts: countBy(skills, (skill) => skill.taxonomy.primary_type),
      domain_counts: countBy(skills, (skill) => skill.taxonomy.domains),
      length_buckets: [],
      avg_char_count: Number(average(skills.map((skill) => skill.features.char_count)).toFixed(2)),
      avg_code_blocks: Number(average(skills.map((skill) => skill.features.code_block_count)).toFixed(2)),
      avg_steps: Number(average(skills.map((skill) => skill.features.step_count)).toFixed(2)),
    },
    capabilities: { primitive_counts: primitiveCounts, primitive_level_counts: primitiveLevelCounts },
    code_tools: { code_language_counts: codeLanguageCounts, tool_counts: toolCounts, dependency_counts: dependencyCounts },
    risks: {
      by_source: riskBySource,
      by_taxonomy: riskByTaxonomy,
      top_risky_skills: topRisky.map((skill) => ({
        skill_id: skill.skill_id,
        name: skill.name,
        source: skill.source,
        taxonomy: skill.taxonomy.primary_type,
        domains: skill.taxonomy.domains,
        risk: skill.risks,
        primitive_count: skill.scr.requirements.length,
        path_or_url: skill.path_or_url,
      })),
    },
    environment: buildEnvironmentSummary(skills),
    model_harness_contribution: buildModelHarnessContribution(skills),
    prioritization: buildPrioritization(skills),
    validation_sample: [],
    skvm_alignment: {
      implemented: [],
      partial: [],
      out_of_scope: [],
      primitive_mapping: [],
    },
    findings: [],
  };
}

function buildFilteredPortability(skills: SkillIndexRecord[], global: PortabilitySummary): PortabilitySummary {
  const bottleneckCounts = new Map<string, number>();
  const targetGaps = new Map<string, { harness: string; model: string; values: number[] }>();
  const topRisky = [...skills]
    .map((skill) => ({
      skill_id: skill.skill_id,
      name: skill.name,
      fleet_gap: skill.portability?.evaluations?.reduce((sum, evaluation) => sum + evaluation.total_gap, 0) ?? skill.risks.overall,
    }))
    .sort((a, b) => b.fleet_gap - a.fleet_gap)
    .slice(0, 25);

  for (const skill of skills) {
    for (const item of skill.portability?.bottleneck_primitives ?? []) {
      bottleneckCounts.set(item.primitive, (bottleneckCounts.get(item.primitive) ?? 0) + item.gap_sum);
    }
    for (const evaluation of skill.portability?.evaluations ?? []) {
      const current = targetGaps.get(evaluation.profile_id) ?? {
        harness: evaluation.harness,
        model: evaluation.model,
        values: [],
      };
      current.values.push(evaluation.total_gap);
      targetGaps.set(evaluation.profile_id, current);
    }
  }

  const targetRows = [...targetGaps.entries()]
    .map(([profile_id, item]) => ({
      profile_id,
      harness: item.harness,
      model: item.model,
      avg_gap: Number(average(item.values).toFixed(3)),
      skill_count: item.values.length,
    }));

  return {
    ...global,
    primitive_bottleneck: [...bottleneckCounts.entries()]
      .map(([primitive, gap_sum]) => ({ primitive, gap_sum }))
      .sort((a, b) => b.gap_sum - a.gap_sum)
      .slice(0, 20),
    target_ranking: [...targetRows].sort((a, b) => a.avg_gap - b.avg_gap),
    target_matrix: targetRows.map(({ harness, model, avg_gap, skill_count }) => ({ harness, model, avg_gap, skill_count })),
    top_risky_skills: topRisky,
  };
}

const loadState = useDashboardData();
const activePage = ref<PageKey>("findings");
const source = ref("all");
const taxonomy = ref("all");
const search = ref("");
const selectedSkill = ref<SkillIndexRecord | null>(null);

const dashboardData = computed(() => (loadState.value.status === "ready" ? loadState.value.data : null));

const filteredSkills = computed(() => {
  const data = dashboardData.value;
  if (!data) return [];
  const query = search.value.trim().toLowerCase();
  return data.skills
    .filter((skill) => source.value === "all" || skill.source === source.value)
    .filter((skill) => taxonomy.value === "all" || skill.taxonomy.primary_type === taxonomy.value)
    .filter((skill) => {
      if (!query) return true;
      const haystack = [
        skill.name,
        skill.description,
        skill.source,
        skill.taxonomy.primary_type,
        ...skill.taxonomy.domains,
        ...skill.scr.requirements.map((requirement) => requirement.primitive),
        ...skill.features.tool_evidence,
        ...skill.features.dependency_evidence,
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    })
    .sort((a, b) => b.risks.overall - a.risks.overall);
});

const sources = computed(() => {
  const data = dashboardData.value;
  if (!data) return [];
  return [...new Set(data.skills.map((skill) => skill.source))].sort();
});

const taxonomies = computed(() => {
  const data = dashboardData.value;
  if (!data) return [];
  return [...new Set(data.skills.map((skill) => skill.taxonomy.primary_type))].sort();
});

const activeSkill = computed(() => {
  if (selectedSkill.value && filteredSkills.value.some((skill) => skill.skill_id === selectedSkill.value?.skill_id)) {
    return selectedSkill.value;
  }
  return filteredSkills.value[0] ?? null;
});

const filteredSummary = computed(() => buildFilteredSummary(filteredSkills.value));
const filteredPortability = computed(() => {
  const data = dashboardData.value;
  if (!data) return null;
  return buildFilteredPortability(filteredSkills.value, data.portability);
});
const filteredFindings = computed(() => buildFindings(filteredSkills.value, filteredSummary.value, filteredPortability.value));
const skvmAlignment = computed<SkvmAlignment | null>(() => dashboardData.value?.summary.skvm_alignment ?? null);

function clearFilters() {
  source.value = "all";
  taxonomy.value = "all";
  search.value = "";
}
</script>

<template>
  <main v-if="loadState.status === 'loading'" class="status-screen">Loading SkillScope data...</main>

  <main v-else-if="loadState.status === 'error'" class="status-screen">
    <h1>Data not found</h1>
    <p>{{ loadState.message }}</p>
    <p>Run the full pipeline and check that JSON files exist under public/data.</p>
  </main>

  <template v-else>
    <nav class="top-nav" aria-label="Main">
      <a class="wordmark" href="#">skillscope</a>
      <div class="product-tabs">
        <button type="button" class="tab" :class="{ active: activePage === 'findings' }" @click="activePage = 'findings'">
          Findings
        </button>
        <button type="button" class="tab" :class="{ active: activePage === 'skills' }" @click="activePage = 'skills'">Skills</button>
        <button type="button" class="tab" :class="{ active: activePage === 'risks' }" @click="activePage = 'risks'">
          Risks <span class="new-tag">New</span>
        </button>
        <button type="button" class="tab" :class="{ active: activePage === 'primitives' }" @click="activePage = 'primitives'">
          Primitives <span class="new-tag">New</span>
        </button>
        <button type="button" class="tab" :class="{ active: activePage === 'alignment' }" @click="activePage = 'alignment'">
          Alignment
        </button>
      </div>
      <div class="nav-utilities">
        <span class="ghost">Docs</span>
        <span class="ghost">GitHub</span>
        <span class="ghost" aria-label="Account">S</span>
      </div>
    </nav>

    <main class="app-shell">
      <header class="app-header">
        <div>
          <p class="eyebrow">SkillScope</p>
          <h1>LLM Agent Skills Explorer</h1>
          <p>
            Explore local and SkVM skills as natural-language programs - structure,
            taxonomy, primitive requirements, and portability risk.
          </p>
        </div>
        <FilterBar
          :sources="sources"
          :taxonomies="taxonomies"
          :selected-source="source"
          :selected-taxonomy="taxonomy"
          :search="search"
          :total-count="dashboardData?.skills.length ?? 0"
          :filtered-count="filteredSkills.length"
          @source-change="source = $event"
          @taxonomy-change="taxonomy = $event"
          @search-change="search = $event"
          @clear="clearFilters"
        />
      </header>

      <section class="metric-grid">
        <MetricCard
          label="Skills"
          :value="filteredSummary.overview.skill_count.toLocaleString()"
          :detail="`${dashboardData?.skills.length.toLocaleString()} total corpus`"
        />
        <MetricCard
          label="TCP profiles"
          :value="(filteredPortability?.profile_count ?? 0).toLocaleString()"
          :detail="`${filteredPortability?.harnesses.length ?? 0} harnesses`"
        />
        <MetricCard label="Avg steps" :value="filteredSummary.overview.avg_steps.toFixed(1)" detail="procedure signals" />
        <MetricCard
          label="Avg code blocks"
          :value="filteredSummary.overview.avg_code_blocks.toFixed(1)"
          detail="embedded fragments"
        />
      </section>

      <section v-if="activePage === 'findings'" class="findings-grid">
        <article v-for="finding in filteredFindings" :key="finding.title" class="finding-card">
          <p class="finding-question">{{ finding.question }}</p>
          <h2>{{ finding.title }}</h2>
          <strong>{{ finding.value }}</strong>
          <p>{{ finding.detail }}</p>
        </article>
      </section>

      <section v-else-if="activePage === 'skills'" class="dashboard-grid">
        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Source mix</h2>
              <p>Imported local and SkVM skill roots.</p>
            </div>
          </div>
          <EChart :option="barOption('skills', filteredSummary.overview.source_counts, '#ff385c')" />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Taxonomy</h2>
              <p>Rule-derived primary types.</p>
            </div>
          </div>
          <EChart :option="pieOption(filteredSummary.overview.taxonomy_counts)" />
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Primitive capability demand</h2>
              <p>Top derived SCR primitives across the current corpus.</p>
            </div>
          </div>
          <EChart
            :option="horizontalBarOption('skills', filteredSummary.capabilities.primitive_counts.slice(0, 15), '#222222')"
            class-name="chart tall"
          />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Code languages</h2>
              <p>Detected fenced code blocks.</p>
            </div>
          </div>
          <EChart :option="horizontalBarOption('blocks', filteredSummary.code_tools.code_language_counts, '#ff385c')" />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Selected skill risk</h2>
              <p>Model, harness, and environment mismatch.</p>
            </div>
          </div>
          <EChart :option="radarOption(activeSkill)" />
        </section>

        <PortabilityPanel
          v-if="filteredPortability"
          :portability="filteredPortability"
          :active-skill="activeSkill"
        />
      </section>

      <section v-else-if="activePage === 'risks'" class="dashboard-grid">
        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Model x Harness portability heatmap</h2>
              <p>Average SCR/TCP gap by target profile; lower is more portable.</p>
            </div>
          </div>
          <EChart :option="modelHarnessHeatmapOption(filteredPortability)" class-name="chart tall" />
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Risk by source</h2>
              <p>Average overall risk for each imported corpus.</p>
            </div>
          </div>
          <EChart :option="riskGroupOption('avg risk', filteredSummary.risks.by_source)" class-name="chart tall" />
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Target compatibility</h2>
              <p>Lower average gap means better SCR/TCP alignment.</p>
            </div>
          </div>
          <EChart :option="targetGapOption(filteredPortability)" class-name="chart tall" />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Risk components</h2>
              <p>Model, harness, environment, and total risk.</p>
            </div>
          </div>
          <EChart :option="riskBreakdownOption(filteredSkills)" />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Model vs harness contribution</h2>
              <p>{{ filteredSummary.model_harness_contribution.interpretation }}</p>
            </div>
            <span>{{ filteredSummary.model_harness_contribution.dominant_axis }}</span>
          </div>
          <div class="detail-grid">
            <span>Model mismatch</span>
            <strong>{{ filteredSummary.model_harness_contribution.avg_model_mismatch.toFixed(3) }}</strong>
            <span>Harness mismatch</span>
            <strong>{{ filteredSummary.model_harness_contribution.avg_harness_mismatch.toFixed(3) }}</strong>
            <span>Margin</span>
            <strong>{{ filteredSummary.model_harness_contribution.margin.toFixed(3) }}</strong>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Risk by taxonomy</h2>
              <p>Which skill types are more fragile.</p>
            </div>
          </div>
          <EChart :option="riskGroupOption('avg risk', filteredSummary.risks.by_taxonomy)" />
        </section>

        <PortabilityPanel
          v-if="filteredPortability"
          :portability="filteredPortability"
          :active-skill="activeSkill"
        />

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Dependency / Environment Risk</h2>
              <p>Signals for packages, credentials, runtimes, browsers, CLI tools, and external services.</p>
            </div>
            <span>{{ filteredSummary.environment.env_risk_skill_count }} high env risk</span>
          </div>
          <EChart
            :option="horizontalBarOption('skills', filteredSummary.environment.dependency_categories, '#ff385c')"
            class-name="chart tall"
          />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Dependency evidence</h2>
              <p>Most frequent dependency words and setup hints.</p>
            </div>
          </div>
          <EChart :option="horizontalBarOption('skills', filteredSummary.code_tools.dependency_counts, '#222222')" />
        </section>

        <section class="panel env-list-panel">
          <div class="panel-header">
            <div>
              <h2>High environment-risk skills</h2>
              <p>Skills with dependency and tool setup pressure.</p>
            </div>
          </div>
          <div class="rank-list">
            <button
              v-for="skill in filteredSummary.environment.top_environment_risk_skills.slice(0, 8)"
              :key="skill.skill_id"
              type="button"
              class="rank-row"
              @click="selectedSkill = filteredSkills.find((item) => item.skill_id === skill.skill_id) ?? selectedSkill"
            >
              <span>
                <strong>{{ skill.name }}</strong>
                <small>{{ skill.source }} / deps {{ skill.dependency_count }} / tools {{ skill.tool_count }}</small>
              </span>
              <b>{{ Math.round(skill.env_risk * 100) }}</b>
            </button>
          </div>
        </section>

        <section class="panel wide env-list-panel">
          <div class="panel-header">
            <div>
              <h2>Rewrite / compilation priority</h2>
              <p>Composite ranking using risk, environment pressure, SCR confidence, primitive diversity, and workflow complexity.</p>
            </div>
          </div>
          <div class="rank-list">
            <button
              v-for="skill in filteredSummary.prioritization.slice(0, 10)"
              :key="skill.skill_id"
              type="button"
              class="rank-row"
              @click="selectedSkill = filteredSkills.find((item) => item.skill_id === skill.skill_id) ?? selectedSkill"
            >
              <span>
                <strong>{{ skill.name }}</strong>
                <small>{{ skill.taxonomy }} / primitives {{ skill.primitive_count }} / SCR {{ skill.scr_confidence.toFixed(2) }}</small>
              </span>
              <b>{{ Math.round(skill.priority_score * 100) }}</b>
            </button>
          </div>
        </section>
      </section>

      <section v-else-if="activePage === 'primitives'" class="dashboard-grid">
        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Primitive level heatmap</h2>
              <p>Derived SCR demand split by required capability level.</p>
            </div>
          </div>
          <EChart :option="primitiveLevelHeatmapOption(filteredSummary.capabilities.primitive_level_counts)" class-name="chart tall" />
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Primitive demand ranking</h2>
              <p>The most common capability requirements in the filtered corpus.</p>
            </div>
          </div>
          <EChart :option="horizontalBarOption('skills', filteredSummary.capabilities.primitive_counts.slice(0, 18), '#222222')" class-name="chart tall" />
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Workflow complexity map</h2>
              <p>Step count vs primitive diversity, colored by SkillScope style.</p>
            </div>
          </div>
          <EChart :option="primitiveDiversityOption(filteredSkills)" class-name="chart tall" />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Bottleneck primitives</h2>
              <p>Capability gaps aggregated over TCP profiles.</p>
            </div>
          </div>
          <EChart
            :option="horizontalBarOption(
              'gap',
              (filteredPortability?.primitive_bottleneck ?? []).map((item) => ({ name: item.primitive, count: item.gap_sum })),
              '#ff385c',
            )"
          />
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <h2>Selected skill risk</h2>
              <p>Inspect how a skill's risks align with its primitives.</p>
            </div>
          </div>
          <EChart :option="radarOption(activeSkill)" />
        </section>
      </section>

      <section v-else class="dashboard-grid">
        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>SkVM paper alignment</h2>
              <p>What this EDA project implements versus what remains compiler/runtime work.</p>
            </div>
          </div>
          <div class="alignment-columns" v-if="skvmAlignment">
            <div>
              <h3>Implemented</h3>
              <ul>
                <li v-for="item in skvmAlignment.implemented" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div>
              <h3>Partial</h3>
              <ul>
                <li v-for="item in skvmAlignment.partial" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div>
              <h3>Out of scope</h3>
              <ul>
                <li v-for="item in skvmAlignment.out_of_scope" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="panel wide">
          <div class="panel-header">
            <div>
              <h2>Primitive mapping</h2>
              <p>Project SCR primitives mapped to the closest SkVM TCP primitive ids.</p>
            </div>
            <span>{{ skvmAlignment?.primitive_mapping.length ?? 0 }} mappings</span>
          </div>
          <div class="mapping-grid" v-if="skvmAlignment">
            <div v-for="item in skvmAlignment.primitive_mapping" :key="item.project_primitive">
              <strong>{{ item.project_primitive }}</strong>
              <span>{{ item.skvm_primitive }}</span>
            </div>
          </div>
        </section>

        <section class="panel wide env-list-panel">
          <div class="panel-header">
            <div>
              <h2>SCR validation sample</h2>
              <p>Generated sample for manual review; current labels remain unreviewed unless edited.</p>
            </div>
            <span>{{ dashboardData?.summary.validation_sample.length ?? 0 }} records</span>
          </div>
          <div class="rank-list">
            <button
              v-for="item in dashboardData?.summary.validation_sample.slice(0, 10)"
              :key="item.skill_id"
              type="button"
              class="rank-row"
              @click="selectedSkill = filteredSkills.find((skill) => skill.skill_id === item.skill_id) ?? selectedSkill"
            >
              <span>
                <strong>{{ item.name }}</strong>
                <small>{{ item.source }} / {{ item.taxonomy }} / {{ item.primitive_count }} primitives</small>
              </span>
              <b>{{ Math.round(item.scr_confidence * 100) }}</b>
            </button>
          </div>
        </section>
      </section>

      <section class="workspace-grid">
        <SkillTable
          :skills="filteredSkills"
          :selected-skill-id="activeSkill?.skill_id ?? null"
          @select="selectedSkill = $event"
        />
        <SkillDetail :skill="activeSkill" />
      </section>
    </main>

    <footer class="app-footer">
      <div class="legal">
        <span>(c) 2026 SkillScope - Built on local and SkVM skill corpora</span>
        <span>Inspiration: Airbnb design language</span>
      </div>
    </footer>
  </template>
</template>
