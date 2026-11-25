# Initial scientific policies

**Every policy below is an initial policy, needs geologist review.** These rules are implementation defaults for a small pilot, not accepted reporting standards, resource estimation procedures, or JORC/NI 43-101 guidance.

## Below-detection assays

- Preserve the reported value, unit, `below_detection` flag, and original `detection_limit`.
- For trend, IDW, and kriging inputs only, a sample is represented as `detection_limit / 2` when all its primary assays are flagged below detection, every assay is in `g/t`, and every primary assay has the same detection limit.
- The derived input is identified as `grade_basis='below_detection_half_dl'`. Results expose imputation counts and a warning.
- Do not infer a value when detection limits disagree, the unit is not `g/t`, or below-detection and quantified primary assays are mixed. Such samples do not enter grade-based processing until reviewed.
- Raw assay records are not overwritten by the derived value.

## QA/QC blocking and waivers

- A failed, pending, or unassessed blank, standard, or duplicate blocks samples in its batch. A QA control with no batch is project-wide.
- A sample with no primary-assay batch, or with any unbatched primary assay, is conservatively considered project-wide for QA/QC blocking.
- A batch-specific waiver applies only to the same batch and only to samples carrying that batch. A project-wide waiver (no batch) may waive project-wide controls.
- Only a project owner or global administrator may create or revoke a waiver. The reason, creator username, UTC time, batch scope, revocation metadata, and audit event are retained.
- Active and revoked waiver history contributes to the processing input hash. Results carry a warning whenever a waiver allows data into processing.

## Conflicting results

- Do not silently select between distinct primary assays for a sample. Conflicting primary assays and inconsistent below-detection limits are excluded from grade-based processing pending review.
- The sample list may show the most recently received raw assay, but also exposes assay status and never treats that latest value as an approved grade when results conflict.

## Interpretation limits

- Trend, IDW, and kriging are exploratory outputs. They are not resource/reserve estimates and do not establish economic viability.
- Surface samples remain separate from drillhole collars and downhole intervals. No downhole grade is plotted at a collar coordinate without a validated desurvey workflow.
