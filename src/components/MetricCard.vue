<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  detail: string;
}>();
</script>

<template>
  <section class="metric-card">
    <span class="metric-label">{{ label }}</span>
    <strong class="metric-value">{{ value }}</strong>
    <small class="metric-detail">{{ detail }}</small>
  </section>
</template>
