import { onMounted, ref } from "vue";
import type { DashboardData, DashboardSummary, PortabilitySummary, SkillIndexRecord } from "../types";

export type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: DashboardData };

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function loadJson<T>(url: string, retries = 12): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const response = await fetch(`${url}?v=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`${url} returned ${response.status}`);
      return response.json() as Promise<T>;
    } catch (error) {
      lastError = error;
      if (attempt < retries) await delay(Math.min(1200, 250 * (attempt + 1)));
    }
  }
  throw lastError instanceof Error ? lastError : new Error(`Failed to load ${url}`);
}

export function useDashboardData() {
  const state = ref<LoadState>({ status: "loading" });

  onMounted(() => {
    let cancelled = false;

    async function load() {
      while (!cancelled) {
        try {
          const [summary, skills, portability] = await Promise.all([
            loadJson<DashboardSummary>("/data/summary.json"),
            loadJson<SkillIndexRecord[]>("/data/skills_index.json"),
            loadJson<PortabilitySummary>("/data/portability.json"),
          ]);
          if (!cancelled) {
            state.value = { status: "ready", data: { summary, skills, portability } };
          }
          return;
        } catch (error) {
          console.warn("Dashboard data is not ready yet; retrying", error);
          state.value = { status: "loading" };
          await delay(1500);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  });

  return state;
}
