<script setup lang="ts">
import type { SkillIndexRecord } from "../types";

const props = defineProps<{
  skill: SkillIndexRecord | null;
}>();

function riskEntries(skill: SkillIndexRecord) {
  return Object.entries(skill.risks);
}

function evidenceItems(skill: SkillIndexRecord) {
  const items = [
    ...skill.scr.requirements.flatMap((requirement) =>
      requirement.evidence.map((item) => `${requirement.primitive}: ${item}`),
    ),
    ...skill.features.tool_evidence.map((item) => `tool signal: ${item}`),
    ...skill.features.dependency_evidence.map((item) => `dependency signal: ${item}`),
  ];

  if (skill.features.step_count > 0) {
    items.push(`structural signal: ${skill.features.step_count} procedure steps detected`);
  }
  if (skill.features.section_count > 0) {
    items.push(`structural signal: ${skill.features.section_count} markdown sections`);
  }
  if (skill.features.has_branching) {
    items.push("structural signal: branching or conditional instructions");
  }
  if (skill.features.has_loop) {
    items.push("structural signal: iterative or repeated workflow");
  }
  if (skill.features.has_verification) {
    items.push("structural signal: verification or checking instructions");
  }

  return [...new Set(items)].slice(0, 12);
}
</script>

<template>
  <aside v-if="!props.skill" class="panel detail-panel empty">
    <h2>Select a skill</h2>
    <p>Click a row to inspect extracted structure, SCR requirements, and risk evidence.</p>
  </aside>

  <aside v-else class="panel detail-panel">
    <div class="panel-header">
      <div>
        <h2>{{ props.skill.name }}</h2>
        <p>{{ props.skill.source }}</p>
      </div>
      <strong class="risk-pill">{{ Math.round(props.skill.risks.overall * 100) }}</strong>
    </div>

    <p v-if="props.skill.description" class="description">{{ props.skill.description }}</p>

    <div class="detail-grid">
      <span>Type</span>
      <strong>{{ props.skill.taxonomy.primary_type }}</strong>
      <span>Length</span>
      <strong>{{ props.skill.features.char_count.toLocaleString() }} chars</strong>
      <span>Steps</span>
      <strong>{{ props.skill.features.step_count }}</strong>
      <span>Code blocks</span>
      <strong>{{ props.skill.features.code_block_count }}</strong>
    </div>

    <h3>Risk profile</h3>
    <div class="risk-bars">
      <div v-for="[name, value] in riskEntries(props.skill)" :key="name" class="risk-bar">
        <span>{{ name.replace("_", " ") }}</span>
        <div><i :style="{ width: `${Math.round(value * 100)}%` }" /></div>
        <strong>{{ Math.round(value * 100) }}</strong>
      </div>
    </div>

    <h3>Top primitives</h3>
    <div v-if="props.skill.scr.requirements.length" class="tag-list">
      <span v-for="requirement in props.skill.scr.requirements.slice(0, 12)" :key="requirement.primitive">
        {{ requirement.primitive }} L{{ requirement.level }}
      </span>
    </div>
    <p v-else class="muted-note">
      No SCR primitives extracted. This usually means the current rule pass found structure, but no named capability
      primitive; run LLM SCR or inspect the structural evidence below.
    </p>

    <h3>Evidence</h3>
    <ul v-if="evidenceItems(props.skill).length" class="evidence-list">
      <li v-for="item in evidenceItems(props.skill)" :key="item">
        {{ item }}
      </li>
    </ul>
    <p v-else class="muted-note">No evidence signals were extracted for this skill.</p>
  </aside>
</template>
