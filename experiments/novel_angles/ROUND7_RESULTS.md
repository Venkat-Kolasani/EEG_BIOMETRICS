# Round 7: waveform networks and fusion

Fresh scoring on reused prepared recordings, not an independent replication. See the [protocol](ROUND7_PROTOCOL.md).
These are the corrected reruns on the notebook's dimensionless, standardized waveforms, without the erroneous volts-to-microvolts conversion in the initial run.
Negative paired-minus-single EER favors pairing. The intervals are unadjusted, crossed-identity bootstrap intervals.
FRR and FAR are measured at the frozen cutoffs; EER summarizes score discrimination independently of those cutoffs.

| Cohort | Lowest new paired EER | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | Best Round 5 model | Round 5 paired EER | EER gap, pp |
|---|---|---:|---:|---:|---:|---|---:|---:|
| ds007176 | Score stacker | 12.31% | 37.46% | 4.85% | -4.22 [-6.48, -2.31] | Tangent-SVM | 15.06% | -2.75 |
| RestCog | Score stacker | 19.53% | 57.40% | 2.82% | -2.76 [-3.86, -1.65] | Logistic | 22.45% | -2.92 |
| Dortmund, two-day sensitivity analysis | Joint-state scores | 20.65% | 76.97% | 1.73% | -3.56 [-4.56, -2.43] | Logistic | 19.86% | +0.79 |
| WBCIC-SHU, modified-duration three-day | Feature fusion | 27.92% | 44.17% | 12.50% | -2.50 [-11.07, +3.64] | ExtraTrees | 27.20% | +0.71 |

Winner and EER gap comparisons are descriptive; a smaller point estimate is not evidence of superiority.
All four gates are relative to the paired-versus-single study criteria, except the held-out FAR upper bound; even an all-gate pass does not establish usability.

- **All study gates passed:** Dortmund, two-day sensitivity analysis / ShallowConvNet.
- **Pairing EER interval favored pairing in each cohort:** Score stacker.
- **Lower paired EER point estimate than the Round 5 winner:** ds007176 / Score stacker; ds007176 / Feature fusion; RestCog / Score rank mean; RestCog / Score stacker; RestCog / Feature fusion; RestCog / Separate-state fusion.

| Cohort | Best waveform model | Its paired EER | EEGNet v4 paired EER | Separate minus joint paired EER, pp |
|---|---|---:|---:|---:|
| ds007176 | DeepConvNet | 39.33% | 49.07% | +1.47 |
| RestCog | DeepConvNet | 42.08% | 49.59% | -0.84 |
| Dortmund, two-day sensitivity analysis | DeepConvNet | 36.77% | 43.08% | +0.44 |
| WBCIC-SHU, modified-duration three-day | DeepConvNet | 38.12% | 48.12% | +2.08 |

## ds007176

29 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds007176.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 49.07% | 95.65% | 3.24% | +0.00 [-0.87, +1.19] | +34.01 | Fail | Pass | Fail | Fail | Fail |
| ShallowConvNet | 42.28% | 92.49% | 2.72% | -1.26 [-2.26, +0.09] | +27.22 | Fail | Pass | Fail | Fail | Fail |
| DeepConvNet | 39.33% | 89.30% | 2.60% | -2.41 [-4.02, -1.18] | +24.27 | Pass | Pass | Fail | Fail | Fail |
| Score rank mean | 19.20% | 61.67% | 3.56% | -3.72 [-5.62, -1.69] | +4.14 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 12.31% | 37.46% | 4.85% | -4.22 [-6.48, -2.31] | -2.75 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 13.65% | 43.14% | 4.11% | -4.85 [-7.28, -2.55] | -1.41 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 18.93% | 62.28% | 3.24% | -3.63 [-6.18, -1.56] | +3.87 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 20.40% | 61.96% | 3.03% | -1.94 [-3.40, -0.64] | +5.34 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Tangent-SVM | 15.06% | 36.93% | 7.15% | -4.23 [-7.09, -1.84] | — | — | — | — | — | — |

## RestCog

60 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds004148.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 49.59% | 98.47% | 1.11% | -0.15 [-0.73, +0.40] | +27.14 | Fail | Pass | Fail | Fail | Fail |
| ShallowConvNet | 42.71% | 94.22% | 2.30% | -0.90 [-1.88, -0.08] | +20.26 | Pass | Pass | Fail | Fail | Fail |
| DeepConvNet | 42.08% | 95.33% | 1.62% | -3.56 [-5.08, -2.13] | +19.64 | Pass | Pass | Fail | Fail | Fail |
| Score rank mean | 22.36% | 77.47% | 1.94% | -3.01 [-3.98, -2.01] | -0.09 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 19.53% | 57.40% | 2.82% | -2.76 [-3.86, -1.65] | -2.92 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 19.73% | 65.23% | 2.48% | -3.55 [-5.19, -2.22] | -2.72 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 23.06% | 76.20% | 2.17% | -1.55 [-2.96, -0.53] | +0.62 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 22.22% | 71.72% | 2.39% | -2.22 [-4.15, -0.94] | -0.23 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Logistic | 22.45% | 80.97% | 2.46% | -2.10 [-3.13, -0.95] | — | — | — | — | — | — |

## Dortmund, two-day sensitivity analysis

128 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds005385.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 43.08% | 96.63% | 1.01% | -2.07 [-2.96, -1.42] | +23.21 | Pass | Pass | Pass | Fail | Fail |
| ShallowConvNet | 40.21% | 95.52% | 0.69% | -1.90 [-2.45, -1.24] | +20.34 | Pass | Pass | Pass | Pass | Pass |
| DeepConvNet | 36.77% | 93.99% | 1.51% | -5.65 [-6.92, -4.49] | +16.90 | Pass | Pass | Pass | Fail | Fail |
| Score rank mean | 20.90% | 77.03% | 1.68% | -5.68 [-6.77, -4.78] | +1.03 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 23.62% | 69.91% | 2.15% | -5.63 [-6.80, -4.32] | +3.76 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 21.17% | 68.55% | 1.79% | -4.61 [-5.92, -3.37] | +1.31 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 20.65% | 76.97% | 1.73% | -3.56 [-4.56, -2.43] | +0.79 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 21.09% | 75.32% | 1.73% | -2.83 [-3.87, -1.84] | +1.23 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Logistic | 19.86% | 83.36% | 1.25% | -3.83 [-4.85, -2.88] | — | — | — | — | — | — |

## WBCIC-SHU, modified-duration three-day

10 people; 20 rotations; 6 probe windows per state; 8 total enrollment windows. [Aggregate JSON](round7-wbcic-shu.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 48.12% | 90.83% | 9.79% | +0.00 [-4.44, +6.08] | +20.92 | Fail | Fail | Fail | Fail | Fail |
| ShallowConvNet | 45.83% | 84.58% | 8.96% | +0.42 [-3.52, +5.83] | +18.63 | Fail | Pass | Fail | Fail | Fail |
| DeepConvNet | 38.12% | 79.58% | 7.29% | -1.88 [-5.59, +2.93] | +10.92 | Fail | Fail | Fail | Fail | Fail |
| Score rank mean | 28.65% | 73.75% | 6.88% | -2.99 [-5.93, +1.35] | +1.45 | Fail | Fail | Fail | Fail | Fail |
| Score stacker | 29.58% | 48.33% | 17.08% | -5.83 [-11.84, -1.74] | +2.38 | Pass | Fail | Fail | Fail | Fail |
| Feature fusion | 27.92% | 44.17% | 12.50% | -2.50 [-11.07, +3.64] | +0.71 | Fail | Pass | Fail | Fail | Fail |
| Joint-state scores | 29.58% | 57.50% | 13.12% | -2.50 [-6.92, +1.30] | +2.38 | Fail | Fail | Fail | Fail | Fail |
| Separate-state fusion | 31.67% | 57.92% | 13.54% | +0.42 [-5.91, +4.40] | +4.46 | Fail | Pass | Fail | Fail | Fail |
| Round 5: ExtraTrees | 27.20% | 62.92% | 10.21% | -0.94 [-4.11, +4.08] | — | — | — | — | — | — |

## Interpretation limits

- The waveform results apply to the fixed verification adaptation and training schedule, not to broader EEGNet or ConvNet performance.
- The rank average and stacker reuse the cutoff calibration fold; the stacker also fits on that fold's genuine claimant scores. Neither sees final impostors or late data during fitting.
- The eye-state models share an enrollment budget, not a per-model sample size: each separate fit uses half the joint model's training rows.
- Dortmund and WBCIC-SHU differ in schedule and duration. These are not interchangeable replications or a demonstration of secure deployment.
