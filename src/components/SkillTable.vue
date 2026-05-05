<script setup lang="ts">
import type { SkillIndexRecord } from "../types";

const props = defineProps<{
  skills: SkillIndexRecord[];
  selectedSkillId: string | null;
}>();

const emit = defineEmits<{
  select: [skill: SkillIndexRecord];
}>();
</script>

<template>
  <section class="panel skill-table-panel">
    <div class="panel-header">
      <div>
        <h2>Risk-ranked skills</h2>
        <p>Sorted by derived portability risk.</p>
      </div>
      <span>{{ props.skills.length }} shown</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Source</th>
            <th>Risk</th>
            <th>Primitives</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="skill in props.skills.slice(0, 80)"
            :key="skill.skill_id"
            :class="{ selected: props.selectedSkillId === skill.skill_id }"
            @click="emit('select', skill)"
          >
            <td>
              <strong>{{ skill.name }}</strong>
              <small>{{ skill.taxonomy.domains.slice(0, 4).join(", ") }}</small>
            </td>
            <td>{{ skill.taxonomy.primary_type }}</td>
            <td>{{ skill.source }}</td>
            <td>{{ Math.round(skill.risks.overall * 100) }}</td>
            <td>{{ skill.scr.requirements.length }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
