# EEG biometric follow-up: chronological verification under eye-state shift

This is an exploratory study on OpenNeuro ds007176 v1.0.1, not a rerun or replacement of the original pipeline. See [REPORT.md](REPORT.md) for prior results, the literature screen, and paper recommendations. The public repository has verified preprocessing FIFs for five participants; the prior full-cohort notebook and rerun kits were not accessible here. The new full-cohort pilot uses exact v1.0.1 raw inputs and a different, lightweight preprocessing pipeline. It **does not** share the original model, features, scores, or numerical baseline. Do not compare numbers across pipelines as method deltas.

## Reproduce

Tested using Python 3.12, MNE 1.13.2, NumPy 2.5.5, SciPy 1.18.1 and scikit-learn 1.9.1. Use a clean Python environment with those versions. Set BLAS thread counts to avoid oversubscription; allow about 18 GiB for raw files and under 1 GiB for the feature cache. Run from this directory:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
git clone --depth 1 --branch 1.0.1 https://github.com/OpenNeuroDatasets/ds007176 ~/ds007176-v1.0.1
python -B fetch_raw.py ~/ds007176-v1.0.1
python -B extract.py ~/ds007176-v1.0.1 ~/eeg-novel-raw --source raw --workers 6
python -B benchmark.py ~/eeg-novel-raw results.csv
python -B refine.py ~/eeg-novel-raw follow-up-contrasts.csv
python -B extract.py ../../preprocessed_dataset ~/eeg-novel-recipe --source epochs
python -B diagnose.py ~/eeg-novel-raw ~/ds007176-v1.0.1 --recipe-cache ~/eeg-novel-recipe > diagnostics.json
python -B -m unittest discover -s . -v
```

The downloader checks newly fetched bytes against the pinned git-annex SHA-256 keys, using public OpenNeuro S3. Use a fresh cache when changing the source or preprocessing. The cache files contain subject-level EEG features and are not tracked; output tables and diagnostics are aggregate only. If you have the verified full-cohort FIFs, point `extract.py --source epochs` at them and use a separate cache and output filename. The five included subjects do not support the four-role verification benchmark.

## Protocol

- Require V0, V1, V2 and exactly one of V3/V4, each with CE and OE. Raw pilot: 250 Hz, common average reference, 1–45 Hz, non-overlapping 5 s windows, recording-local log-RMS MAD rejection, then epoch-by-channel standardization. Features: five log relative powers (2–44 Hz), shrinkage correlation tangent vectors, approximate log-log spectral slopes excluding the alpha band, or signed imaginary alpha coherency. The slope estimate is **not** a formal periodic/aperiodic decomposition, and sensor-level coherency is **not** source connectivity.
- Four seeded rotations of disjoint identity groups: claimant, reference cohort, V2 calibrating impostor, unseen scoring impostor. Each identity acts in each role once; another enrolled claimant never serves as an impostor for that rotation. The V2-unseen row uses withheld impostor identities at the calibration visit; the late row uses these same unseen impostor identities at the later visit. Genuine comparisons use actual claimant attempts, not impostor-group identities.
- Fit templates at V0/V1 using 40/80/160 clean seconds total. The default 160 s spends 80 s/visit, split equally across states for mixed/paired enrollment. Attempt duration is 10 s of usable EEG (two within-state 5 s windows, or one from each condition for paired probes). Both the paired-mean and pooled single-state arms use every one of the same first 24 retained windows per state exactly once, for 24 attempts per arm. Paired probes combine equal retained-window indices from **separate resting recordings**, not eye-onset transitions; task switching time is not counted. Rejected raw windows can leave gaps between retained segments.
- Set one threshold per fold and configuration at at-most 1% V2 empirical impostor FAR; compare pooled with two thresholds requiring an eye-state label. Later thresholds never move. Z uses old background scores against claimants; T uses current probe against old background templates, and S averages both. The background never includes V2 calibration or scored subjects in the same fold. Historical condition alignment uses V0/V1 reference subjects only. Contemporaneous visit/condition alignment uses independent donors from the exact nominal visit (V3 and V4 kept separate); if a fold has no donor at the probe visit, that probe is not scored in this arm. This requires extra contemporaneous acquisition and is not an on-device subject-only method.
- FRR and realized FAR are rates at the frozen decision point; EER summarizes the pooled ROC independently of that threshold and is not a forecast of deployment error. Report percentile intervals from 500 global subject resamples, with claimant weights on genuine attempts and claimant × impostor weights on impostor attempts. Models, background, role partition and already-fitted thresholds remain fixed in the bootstrap; intervals are conditional and do **not** cover full calibration/model-selection uncertainty. Paired contrasts use shared bootstrap draws. The additional leave-one-calibrator diagnostic stress-tests sensitivity not captured by these intervals.
- Adaptation scores prespecified early late-visit windows before allowing accepted scores to update templates; evaluation uses the other half of the visit. Each state has a separate copy of the originally mixed template for this pilot. The simulation uses zero-effort impostors, not synthetic or targeted attacks, and provides no security guarantee.
- Small channel panels are post-hoc channel subsets of full-cap preprocessing, not authentic reduced-electrode hardware experiments. FRR/FAR trade-offs should be validated on raw subsets with appropriate re-referencing and on real devices.
