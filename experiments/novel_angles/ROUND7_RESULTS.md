# Round 7: waveform networks and fusion

Fresh scoring on reused prepared recordings, not an independent replication. See the [protocol](ROUND7_PROTOCOL.md).
Negative paired-minus-single EER favors pairing. The intervals are unadjusted, crossed-identity bootstrap intervals.
FRR and FAR are measured at the frozen cutoffs; EER summarizes score discrimination independently of those cutoffs.

| Cohort | Lowest new paired EER | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | Best Round 5 model | Round 5 paired EER | EER gap, pp |
|---|---|---:|---:|---:|---:|---|---:|---:|
| ds007176 | Score stacker | 12.36% | 37.03% | 4.84% | -4.35 [-6.58, -2.12] | Tangent-SVM | 15.06% | -2.70 |
| RestCog | Score stacker | 19.51% | 57.07% | 3.02% | -2.81 [-3.87, -1.86] | Logistic | 22.45% | -2.94 |
| Dortmund, two-day sensitivity analysis | Score rank mean | 20.59% | 76.55% | 1.73% | -6.05 [-7.08, -5.05] | Logistic | 19.86% | +0.73 |
| WBCIC-SHU, modified-duration three-day | Feature fusion | 27.92% | 44.17% | 12.50% | -2.50 [-11.07, +3.64] | ExtraTrees | 27.20% | +0.71 |

Winner and EER gap comparisons are descriptive; a smaller point estimate is not evidence of superiority.
All four gates are relative to the paired-versus-single study criteria, except the held-out FAR upper bound; even an all-gate pass does not establish usability.

- **All study gates passed:** Dortmund, two-day sensitivity analysis / ShallowConvNet.
- **Pairing EER interval favored pairing in each cohort:** no new model.
- **Lower paired EER point estimate than the Round 5 winner:** ds007176 / Score stacker; ds007176 / Feature fusion; RestCog / Score rank mean; RestCog / Score stacker; RestCog / Feature fusion; RestCog / Separate-state fusion.

| Cohort | Best waveform model | Its paired EER | EEGNet v4 paired EER | Separate minus joint paired EER, pp |
|---|---|---:|---:|---:|
| ds007176 | DeepConvNet | 38.86% | 41.49% | +1.47 |
| RestCog | DeepConvNet | 42.00% | 47.04% | -0.84 |
| Dortmund, two-day sensitivity analysis | DeepConvNet | 36.45% | 42.79% | +0.44 |
| WBCIC-SHU, modified-duration three-day | DeepConvNet | 40.42% | 45.62% | +2.08 |

## ds007176

29 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds007176.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 41.49% | 92.71% | 3.37% | -0.82 [-1.80, +0.12] | +26.43 | Fail | Pass | Fail | Fail | Fail |
| ShallowConvNet | 42.28% | 92.24% | 2.67% | -1.19 [-2.32, +0.02] | +27.22 | Fail | Pass | Fail | Fail | Fail |
| DeepConvNet | 38.86% | 90.01% | 2.48% | -3.07 [-4.63, -1.65] | +23.80 | Pass | Pass | Fail | Fail | Fail |
| Score rank mean | 19.10% | 58.15% | 3.66% | -3.67 [-5.42, -2.21] | +4.04 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 12.36% | 37.03% | 4.84% | -4.35 [-6.58, -2.12] | -2.70 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 13.65% | 43.14% | 4.11% | -4.85 [-7.28, -2.55] | -1.41 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 18.93% | 62.28% | 3.24% | -3.63 [-6.18, -1.56] | +3.87 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 20.40% | 61.96% | 3.03% | -1.94 [-3.40, -0.64] | +5.34 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Tangent-SVM | 15.06% | 36.93% | 7.15% | -4.23 [-7.09, -1.84] | — | — | — | — | — | — |

## RestCog

60 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds004148.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 47.04% | 98.26% | 1.22% | -1.16 [-1.90, -0.22] | +24.59 | Pass | Pass | Fail | Fail | Fail |
| ShallowConvNet | 42.69% | 94.18% | 2.30% | -0.92 [-1.88, -0.11] | +20.24 | Pass | Pass | Fail | Fail | Fail |
| DeepConvNet | 42.00% | 95.19% | 1.59% | -3.65 [-5.17, -2.56] | +19.56 | Pass | Pass | Fail | Fail | Fail |
| Score rank mean | 21.84% | 74.39% | 2.29% | -3.25 [-4.40, -2.11] | -0.60 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 19.51% | 57.07% | 3.02% | -2.81 [-3.87, -1.86] | -2.94 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 19.73% | 65.23% | 2.48% | -3.55 [-5.19, -2.22] | -2.72 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 23.06% | 76.20% | 2.17% | -1.55 [-2.96, -0.53] | +0.62 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 22.22% | 71.72% | 2.39% | -2.22 [-4.15, -0.94] | -0.23 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Logistic | 22.45% | 80.97% | 2.46% | -2.10 [-3.13, -0.95] | — | — | — | — | — | — |

## Dortmund, two-day sensitivity analysis

128 people; 20 rotations; 24 probe windows per state; 32 total enrollment windows. [Aggregate JSON](round7-ds005385.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 42.79% | 95.81% | 1.12% | -2.42 [-3.18, -1.59] | +22.93 | Pass | Pass | Pass | Fail | Fail |
| ShallowConvNet | 40.20% | 95.65% | 0.64% | -1.91 [-2.49, -1.39] | +20.33 | Pass | Pass | Pass | Pass | Pass |
| DeepConvNet | 36.45% | 94.03% | 1.44% | -5.83 [-7.12, -4.65] | +16.58 | Pass | Pass | Pass | Fail | Fail |
| Score rank mean | 20.59% | 76.55% | 1.73% | -6.05 [-7.08, -5.05] | +0.73 | Pass | Pass | Fail | Fail | Fail |
| Score stacker | 23.56% | 69.36% | 2.22% | -5.71 [-6.85, -4.41] | +3.69 | Pass | Pass | Fail | Fail | Fail |
| Feature fusion | 21.17% | 68.55% | 1.79% | -4.61 [-5.92, -3.37] | +1.31 | Pass | Pass | Fail | Fail | Fail |
| Joint-state scores | 20.65% | 76.97% | 1.73% | -3.56 [-4.56, -2.43] | +0.79 | Pass | Pass | Fail | Fail | Fail |
| Separate-state fusion | 21.09% | 75.32% | 1.73% | -2.83 [-3.87, -1.84] | +1.23 | Pass | Pass | Fail | Fail | Fail |
| Round 5: Logistic | 19.86% | 83.36% | 1.25% | -3.83 [-4.85, -2.88] | — | — | — | — | — | — |

## WBCIC-SHU, modified-duration three-day

10 people; 20 rotations; 6 probe windows per state; 8 total enrollment windows. [Aggregate JSON](round7-wbcic-shu.json).

| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |
|---|---:|---:|---:|---:|---:|---|---|---|---|---|
| EEGNet v4 | 45.62% | 80.83% | 9.79% | -0.63 [-4.47, +5.28] | +18.42 | Fail | Fail | Fail | Fail | Fail |
| ShallowConvNet | 45.42% | 80.83% | 8.75% | +0.00 [-5.17, +3.29] | +18.21 | Fail | Fail | Fail | Fail | Fail |
| DeepConvNet | 40.42% | 73.33% | 11.46% | -3.75 [-7.27, +1.71] | +13.21 | Fail | Fail | Fail | Fail | Fail |
| Score rank mean | 28.92% | 65.00% | 8.54% | -2.47 [-8.68, +2.30] | +1.72 | Fail | Fail | Fail | Fail | Fail |
| Score stacker | 28.33% | 47.08% | 17.92% | -5.42 [-10.42, +0.00] | +1.13 | Fail | Fail | Fail | Fail | Fail |
| Feature fusion | 27.92% | 44.17% | 12.50% | -2.50 [-11.07, +3.64] | +0.71 | Fail | Pass | Fail | Fail | Fail |
| Joint-state scores | 29.58% | 57.50% | 13.12% | -2.50 [-6.92, +1.30] | +2.38 | Fail | Fail | Fail | Fail | Fail |
| Separate-state fusion | 31.67% | 57.92% | 13.54% | +0.42 [-5.91, +4.40] | +4.46 | Fail | Pass | Fail | Fail | Fail |
| Round 5: ExtraTrees | 27.20% | 62.92% | 10.21% | -0.94 [-4.11, +4.08] | — | — | — | — | — | — |

## Interpretation limits

- The waveform results apply to the fixed verification adaptation and training schedule, not to broader EEGNet or ConvNet performance.
- The rank average and stacker reuse the cutoff calibration fold; the stacker also fits on that fold's genuine claimant scores. Neither sees final impostors or late data during fitting.
- The eye-state models share an enrollment budget, not a per-model sample size: each separate fit uses half the joint model's training rows.
- Dortmund and WBCIC-SHU differ in schedule and duration. These are not interchangeable replications or a demonstration of secure deployment.
