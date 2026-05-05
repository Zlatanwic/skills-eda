<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts/core";
import { BarChart, HeatmapChart, LineChart, PieChart, RadarChart, ScatterChart } from "echarts/charts";
import { GridComponent, LegendComponent, RadarComponent, TooltipComponent, VisualMapComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsCoreOption } from "echarts/core";

echarts.use([
  BarChart,
  HeatmapChart,
  LineChart,
  PieChart,
  RadarChart,
  ScatterChart,
  GridComponent,
  LegendComponent,
  RadarComponent,
  TooltipComponent,
  VisualMapComponent,
  CanvasRenderer,
]);

export type ChartOption = EChartsCoreOption;

const props = defineProps<{
  option: ChartOption;
  className?: string;
}>();

const container = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  if (!container.value) return;
  chart = echarts.init(container.value, undefined, { renderer: "canvas" });
  chart.setOption(props.option);
  resizeObserver = new ResizeObserver(() => chart?.resize());
  resizeObserver.observe(container.value);
});

watch(
  () => props.option,
  (option) => {
    chart?.setOption(option, true);
  },
  { deep: true },
);

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  chart?.dispose();
});
</script>

<template>
  <div ref="container" :class="className ?? 'chart'" />
</template>
