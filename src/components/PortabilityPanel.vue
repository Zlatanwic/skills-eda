<script setup lang="ts">
import { computed } from "vue";
import type { PortabilitySummary, SkillIndexRecord } from "../types";

const props = defineProps<{
  portability: PortabilitySummary;
  activeSkill: SkillIndexRecord | null;
}>();

const maxGap = computed(() => Math.max(props.portability.primitive_bottleneck[0]?.gap_sum ?? 1, 1));
</script>

<template>
  <section class="panel wide">
    <div class="panel-header">
      <div>
        <h2>Portability Risk</h2>
        <p>SCR vs TCP - bottleneck primitives and target rankings.</p>
      </div>
      <span>{{ props.portability.profile_count }} profiles</span>
    </div>

    <div class="portability-grid">
      <div>
        <h3>Primitive bottleneck</h3>
        <div class="portability-bars">
          <div v-for="item in props.portability.primitive_bottleneck.slice(0, 6)" :key="item.primitive" class="portability-bar">
            <span>{{ item.primitive }}</span>
            <div><i :style="{ width: `${Math.min(100, (item.gap_sum / maxGap) * 100)}%` }" /></div>
            <strong>{{ item.gap_sum }}</strong>
          </div>
        </div>
      </div>

      <div>
        <h3>Target ranking (lowest gap first)</h3>
        <div class="target-list">
          <div v-for="target in props.portability.target_ranking.slice(0, 5)" :key="target.profile_id" class="target-row">
            <div class="target-meta">
              <strong>{{ target.model.split("/").pop() }}</strong>
              <small>{{ target.harness }}</small>
            </div>
            <span class="target-gap">{{ target.avg_gap.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <div v-if="props.activeSkill" class="skill-portability">
        <h3>Selected skill</h3>
        <div class="detail-grid">
          <span>Best target</span>
          <strong>{{ props.activeSkill.portability?.best_target?.model?.split("/").pop() ?? "n/a" }}</strong>
          <span>Harness</span>
          <strong>{{ props.activeSkill.portability?.best_target?.harness ?? "n/a" }}</strong>
          <span>Worst target</span>
          <strong>{{ props.activeSkill.portability?.worst_target?.model?.split("/").pop() ?? "n/a" }}</strong>
          <span>Harness</span>
          <strong>{{ props.activeSkill.portability?.worst_target?.harness ?? "n/a" }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>
