export interface CountItem {
  name: string;
  count: number;
}

export interface OverviewSummary {
  skill_count: number;
  source_counts: CountItem[];
  taxonomy_counts: CountItem[];
  domain_counts: CountItem[];
  length_buckets: CountItem[];
  avg_char_count: number;
  avg_code_blocks: number;
  avg_steps: number;
}

export interface PrimitiveSummary {
  primitive_counts: CountItem[];
  primitive_level_counts: CountItem[];
}

export interface CodeToolsSummary {
  code_language_counts: CountItem[];
  tool_counts: CountItem[];
  dependency_counts: CountItem[];
}

export interface FindingItem {
  title: string;
  value: string;
  detail: string;
  question: string;
}

export interface EnvironmentRiskSkill {
  skill_id: string;
  name: string;
  source: string;
  dependency_count: number;
  tool_count: number;
  env_risk: number;
}

export interface EnvironmentSummary {
  avg_dependency_count: number;
  avg_tool_count: number;
  dependency_skill_count: number;
  env_risk_skill_count: number;
  dependency_categories: CountItem[];
  top_environment_risk_skills: EnvironmentRiskSkill[];
}

export interface ModelHarnessContribution {
  avg_model_mismatch: number;
  avg_harness_mismatch: number;
  dominant_axis: string;
  margin: number;
  interpretation: string;
}

export interface PrioritizedSkill {
  skill_id: string;
  name: string;
  source: string;
  taxonomy: string;
  priority_score: number;
  overall_risk: number;
  environment_mismatch: number;
  primitive_count: number;
  scr_confidence: number;
  step_count: number;
  code_block_count: number;
  reason: string;
}

export interface ValidationSampleItem {
  skill_id: string;
  name: string;
  source: string;
  taxonomy: string;
  scr_confidence: number;
  primitive_count: number;
  top_primitives: Array<{ primitive: string; level: number; evidence: string[] }>;
  manual_status: string;
  manual_notes: string;
}

export interface SkvmAlignment {
  implemented: string[];
  partial: string[];
  out_of_scope: string[];
  primitive_mapping: Array<{ project_primitive: string; skvm_primitive: string }>;
}

export interface AdvancedEdaSummary {
  primitive_cooccurrence: {
    primitives: string[];
    cells: Array<[number, number, number]>;
  };
  taxonomy_primitive_sankey: {
    nodes: Array<{ name: string }>;
    links: Array<{ source: string; target: string; value: number }>;
  };
  source_language_heatmap: {
    sources: string[];
    languages: string[];
    cells: Array<[string, string, number]>;
  };
  skill_primitive_matrix: {
    skills: Array<{ skill_id: string; name: string; source: string; risk: number }>;
    primitives: string[];
    cells: Array<[number, number, number]>;
  };
  length_histogram: CountItem[];
  step_histogram: CountItem[];
  pca_projection: {
    method: string;
    features: string[];
    points: Array<{
      skill_id: string;
      name: string;
      source: string;
      taxonomy: string;
      risk: number;
      x: number;
      y: number;
      cluster: number;
    }>;
  };
}

export interface RiskScore {
  model_mismatch: number;
  harness_mismatch: number;
  environment_mismatch: number;
  overall: number;
}

export interface RiskGroup {
  name: string;
  avg_risk: number;
  count: number;
}

export interface RiskySkill {
  skill_id: string;
  name: string;
  source: string;
  taxonomy: string;
  domains: string[];
  risk: RiskScore;
  primitive_count: number;
  path_or_url: string;
}

export interface RisksSummary {
  by_source: RiskGroup[];
  by_taxonomy: RiskGroup[];
  top_risky_skills: RiskySkill[];
}

export interface DashboardSummary {
  overview: OverviewSummary;
  capabilities: PrimitiveSummary;
  code_tools: CodeToolsSummary;
  risks: RisksSummary;
  environment: EnvironmentSummary;
  model_harness_contribution: ModelHarnessContribution;
  prioritization: PrioritizedSkill[];
  validation_sample: ValidationSampleItem[];
  skvm_alignment: SkvmAlignment;
  advanced: AdvancedEdaSummary;
  findings: FindingItem[];
}

export interface SkillFeatureSet {
  char_count: number;
  word_count: number;
  line_count: number;
  section_count: number;
  code_block_count: number;
  code_line_count: number;
  code_languages: Record<string, number>;
  step_count: number;
  dependency_count: number;
  tool_count: number;
  has_branching: boolean;
  has_loop: boolean;
  has_verification: boolean;
  tool_evidence: string[];
  dependency_evidence: string[];
}

export interface SkillTaxonomy {
  primary_type: string;
  scores: Record<string, number>;
  domains: string[];
  confidence: number;
}

export interface ScrRequirement {
  primitive: string;
  level: number;
  method: string;
  confidence: number;
  evidence: string[];
}

export interface SkillScr {
  method: string;
  confidence: number;
  requirements: ScrRequirement[];
}

export interface SkillPortability {
  best_target: { harness: string; model: string; total_gap: number } | null;
  worst_target: { harness: string; model: string; total_gap: number } | null;
  bottleneck_primitives: PortabilityRecord[];
  evaluations?: PortabilityEvaluation[];
}

export interface SkillIndexRecord {
  skill_id: string;
  name: string;
  source: string;
  path_or_url: string;
  description: string;
  features: SkillFeatureSet;
  taxonomy: SkillTaxonomy;
  scr: SkillScr;
  risks: RiskScore;
  portability?: SkillPortability;
}

export interface PortabilityRecord {
  primitive: string;
  gap_sum: number;
}

export interface PortabilityEvaluation {
  profile_id: string;
  harness: string;
  model: string;
  total_gap: number;
  max_gap: number;
  missing_count: number;
  hard_gap_count: number;
}

export interface TargetRankingItem {
  profile_id: string;
  harness: string;
  model: string;
  avg_gap: number;
  skill_count: number;
}

export interface TargetMatrixItem {
  harness: string;
  model: string;
  avg_gap: number;
  skill_count: number;
}

export interface TopRiskyItem {
  skill_id: string;
  name: string;
  fleet_gap: number;
}

export interface PortabilitySummary {
  profile_count: number;
  harnesses: string[];
  models: string[];
  primitive_bottleneck: PortabilityRecord[];
  target_ranking: TargetRankingItem[];
  target_matrix: TargetMatrixItem[];
  top_risky_skills: TopRiskyItem[];
}

export interface DashboardData {
  summary: DashboardSummary;
  skills: SkillIndexRecord[];
  portability: PortabilitySummary;
}
