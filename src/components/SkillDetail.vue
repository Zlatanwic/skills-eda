<script setup lang="ts">
import type { SkillIndexRecord } from "../types";

const props = defineProps<{
  skill: SkillIndexRecord | null;
}>();

function riskEntries(skill: SkillIndexRecord) {
  return Object.entries(skill.risks);
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
    <div class="tag-list">
      <span v-for="requirement in props.skill.scr.requirements.slice(0, 12)" :key="requirement.primitive">
        {{ requirement.primitive }} L{{ requirement.level }}
      </span>
    </div>

    <h3>Evidence</h3>
    <ul class="evidence-list">
      <li
        v-for="item in [...props.skill.features.tool_evidence, ...props.skill.features.dependency_evidence].slice(0, 10)"
        :key="item"
      >
        {{ item }}
      </li>
    </ul>
  </aside>
</template>
