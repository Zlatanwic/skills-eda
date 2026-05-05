<script setup lang="ts">
const props = defineProps<{
  sources: string[];
  taxonomies: string[];
  selectedSource: string;
  selectedTaxonomy: string;
  search: string;
  totalCount: number;
  filteredCount: number;
}>();

const emit = defineEmits<{
  sourceChange: [value: string];
  taxonomyChange: [value: string];
  searchChange: [value: string];
  clear: [];
}>();

const examples = ["skvm", "tool.github", "python", "doc.generate", "browser"];
</script>

<template>
  <div class="filter-bar" role="search">
    <label>
      Source
      <select :value="props.selectedSource" @change="emit('sourceChange', ($event.target as HTMLSelectElement).value)">
        <option value="all">All sources</option>
        <option v-for="source in props.sources" :key="source" :value="source">{{ source }}</option>
      </select>
    </label>
    <label>
      Taxonomy
      <select :value="props.selectedTaxonomy" @change="emit('taxonomyChange', ($event.target as HTMLSelectElement).value)">
        <option value="all">All types</option>
        <option v-for="taxonomy in props.taxonomies" :key="taxonomy" :value="taxonomy">{{ taxonomy }}</option>
      </select>
    </label>
    <label class="search-field">
      Analysis filter
      <input
        :value="props.search"
        placeholder="Try: tool.github, skvm, python, browser, doc.generate"
        @input="emit('searchChange', ($event.target as HTMLInputElement).value)"
      />
    </label>
    <button type="button" class="search-orb" aria-label="Apply analysis filter">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
        <circle cx="10.5" cy="10.5" r="6.5" />
        <line x1="15.5" y1="15.5" x2="20" y2="20" />
      </svg>
    </button>
    <div class="filter-summary">
      <span>Showing {{ props.filteredCount.toLocaleString() }} of {{ props.totalCount.toLocaleString() }} skills</span>
      <button
        v-if="props.search || props.selectedSource !== 'all' || props.selectedTaxonomy !== 'all'"
        type="button"
        class="clear-filter"
        @click="emit('clear')"
      >
        Clear
      </button>
    </div>
    <div class="quick-chips" aria-label="Example filters">
      <button v-for="example in examples" :key="example" type="button" @click="emit('searchChange', example)">
        {{ example }}
      </button>
    </div>
  </div>
</template>
