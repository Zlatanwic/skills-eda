# SCR Validation Plan

The dashboard currently uses derived SCR labels. These labels are useful for exploratory analysis, but they should be validated before making strong claims.

## Generated Sample

The pipeline writes a review sample to:

- `data/dashboard/validation_sample.json`
- `public/data/validation_sample.json`

The sample contains 60 records selected from:

- low SCR confidence skills,
- high-risk skills,
- at least one skill from each available source,
- additional corpus examples to fill the target size.

Each record includes:

- `skill_id`
- `name`
- `source`
- `taxonomy`
- `scr_confidence`
- `primitive_count`
- top extracted primitives and evidence
- `manual_status`
- `manual_notes`

## Manual Review Rubric

For each sampled skill, inspect the original skill text and answer:

1. Are the extracted primitives reasonable?
2. Are any important primitives missing?
3. Are any extracted primitives false positives?
4. Are the levels L1/L2/L3 roughly appropriate?
5. Is the evidence traceable to the skill text?

Suggested manual status values:

- `pass`: primitives and levels are broadly reasonable.
- `minor_issue`: mostly correct, but one or two primitive/level issues.
- `major_issue`: many wrong or missing primitives.
- `unclear`: not enough evidence or ambiguous skill content.

## Metrics To Report

For a course project, a lightweight validation report is enough:

- number of reviewed samples,
- pass / minor / major / unclear counts,
- common false positives,
- common false negatives,
- rule improvements made after review.

## Current Status

The sample is generated automatically, but manual adjudication has not been completed yet. The final report should describe SCR quality as a limitation unless review is performed.
