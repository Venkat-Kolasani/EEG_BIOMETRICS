"""Locked cross-session waveform and fusion comparison."""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn
from torch.nn import functional as F

from benchmark import cosine
from loop2 import kit_module, load_features, mixed_probes, recording_arrays
from round4 import variant_rows
from round5 import (ARMS, COHORTS, average_probes, donor_slots, enrollment, evaluate, labels,
                    logs_of_covariance)
from round6 import audited_rotations, calibration_ranks, previous, targeted_scores


BACKBONES = ("EEGNet v4", "ShallowConvNet", "DeepConvNet")
FUSIONS = ("Score rank mean", "Score stacker", "Feature fusion", "Joint-state scores", "Separate-state fusion")
ANCHORS = ("Cosine", "Logistic", "Tangent-SVM")
MODELS = (*BACKBONES, *FUSIONS)
SEED = 42


def recording(job):
    return recording_arrays(job, waveform=True, connectivity=True)


def backbone(name, channels, samples, classes):
    from braindecode.models import Deep4Net, EEGNet, ShallowFBCSPNet

    common = dict(n_chans=channels, n_times=samples, n_outputs=classes, sfreq=50)
    if name == BACKBONES[0]:
        return EEGNet(**common, kernel_length=25, depthwise_kernel_length=7, final_layer_with_constraint=True)
    if name == BACKBONES[1]:
        return ShallowFBCSPNet(**common, filter_time_length=5, pool_time_length=15, pool_time_stride=3)
    if name == BACKBONES[2]:
        return Deep4Net(**common, filter_time_length=2, filter_length_2=2, filter_length_3=2, filter_length_4=2)
    raise ValueError(name)


def waveform_tensor(wave):
    return torch.from_numpy(np.ascontiguousarray(wave.reshape(-1, *wave.shape[-2:])))


def waveform_fit(name, enrolled):
    torch.manual_seed(SEED)
    channels, samples = enrolled.shape[-2:]
    net = backbone(name, channels, samples, len(enrolled))
    optimizer = torch.optim.Adam(net.parameters(), lr=.001)
    x = waveform_tensor(enrolled)
    y = torch.arange(len(enrolled)).repeat_interleave(enrolled.shape[1])
    for _ in range(8):
        for idx in torch.randperm(len(y)).split(64):
            optimizer.zero_grad()
            loss = F.cross_entropy(net(x[idx]), y[idx])
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite enrollment loss: {name}")
            loss.backward()
            optimizer.step()
    net.final_layer = nn.Flatten()
    return net.eval()


def embeddings(net, wave):
    x = waveform_tensor(wave)
    with torch.inference_mode():
        z = torch.cat([F.normalize(net(batch)) for batch in x.split(64)])
    if not torch.isfinite(z).all():
        raise FloatingPointError("Nonfinite waveform embedding")
    return z.numpy().reshape(*wave.shape[:-2], -1)


def waveform_scores(wave, split, subjects, windows, budget):
    claim, reference, _, _ = split
    channels, samples = wave.shape[-2:]
    enrolled = enrollment(wave.reshape(*wave.shape[:4], -1), budget).reshape(-1, budget, channels, samples)
    query = wave[subjects, -2:, :, :windows]
    scores = {}
    for name in BACKBONES:
        net = waveform_fit(name, enrolled[reference])
        template = embeddings(net, enrolled[claim]).mean(axis=1)
        probes = mixed_probes(embeddings(net, query), windows)
        scores[name] = cosine(np.concatenate([probes[arm] for arm in ARMS], axis=2), template)
    return scores


def score_fusion(scores, ncal):
    counts = np.stack([calibration_ranks(s, ncal) for s in scores], axis=-1)
    windows, nclaim, nmodels = counts.shape[-3:]
    denom = ncal * windows
    rank_mean = counts.sum(axis=-1) / (denom * nmodels)
    rank = counts / denom
    output = []
    for target in range(nclaim):
        features = rank[..., target, :]
        impostor = features[:ncal, 0].reshape(-1, nmodels)
        genuine = features[ncal + target, 0]
        x = np.concatenate([impostor, genuine])
        y = np.repeat([0, 1], [len(impostor), len(genuine)])
        stacker = LogisticRegression(C=1., class_weight="balanced", random_state=SEED).fit(x, y)
        output.append(stacker.predict_proba(features.reshape(-1, nmodels))[:, 1].reshape(features.shape[:-1]))
    return rank_mean, np.stack(output, axis=-1)


def binary_score(x, query, block_widths=None):
    scale = StandardScaler().fit(x)
    train, probe = scale.transform(x), scale.transform(query.reshape(-1, x.shape[-1]))
    if block_widths is not None:
        weights = np.repeat(1 / np.sqrt(block_widths), block_widths).astype(train.dtype)
        train *= weights
        probe *= weights
    model = LogisticRegression(C=1., max_iter=500, random_state=SEED).fit(train, labels(len(train) // 2))
    return model.predict_proba(probe)[:, 1].reshape(query.shape[:-1])


def feature_scores(arrays, split, subjects, windows, budget):
    claim, reference, _, _ = split
    blocks = [arrays[k].reshape(*arrays[k].shape[:4], -1) for k in ("spectral", "connectivity", "logcov")]
    trained = [enrollment(block, budget) for block in blocks]
    probes = [average_probes(block, subjects, windows) for block in blocks]
    center = trained[-1][reference].mean(axis=(0, 1))
    trained[-1] = trained[-1] - center
    probes[-1] = probes[-1] - center
    train, probe = np.concatenate(trained, axis=-1), np.concatenate(probes, axis=-1)
    widths = [x.shape[-1] for x in trained]
    return np.stack([binary_score(np.vstack([train[t], train[donor_slots(reference, t, budget)]]), probe, widths)
                     for t in claim], axis=-1)


def state_scores(spectral, split, subjects, windows, budget):
    claim, reference, _, _ = split
    data = enrollment(spectral, budget)
    query = spectral[subjects, -2:, :, :windows]
    visits = spectral.shape[1] - 2
    state = np.tile(np.repeat(np.arange(2), budget // (2 * visits)), visits)
    joint, separate = [], []
    for target in claim:
        donor = data[donor_slots(reference, target, budget)]
        joint.append(binary_score(np.vstack([data[target], donor]), query))
        separate.append(np.stack([binary_score(np.vstack([data[target, state == j], donor[state == j]]),
                                               query[:, :, j]) for j in range(2)], axis=2))
    result = []
    for values in (joint, separate):
        arms = mixed_probes(np.stack(values, axis=-1), windows)
        result.append(np.concatenate([arms[arm] for arm in ARMS], axis=2))
    return result


def score_rotation(arrays, split, windows, budget):
    claim, _, cal, test = split
    subjects = np.r_[cal, claim, test]
    (_, scores), = targeted_scores(arrays, split, (windows,), windows, budget)
    scores.update(waveform_scores(arrays["waveform"], split, subjects, windows, budget))
    scores["Feature fusion"] = feature_scores(arrays, split, subjects, windows, budget)
    x = arrays["svm"].reshape(*arrays["svm"].shape[:4], -1)
    scores["Joint-state scores"], scores["Separate-state fusion"] = state_scores(x, split, subjects, windows, budget)
    result = {}
    for arm, index in (("single", slice(None, windows)), ("pair", slice(windows, None))):
        values = {name: score[:, :, index] for name, score in scores.items()}
        values["Score rank mean"], values["Score stacker"] = score_fusion(
            [values[m] for m in (*ANCHORS, BACKBONES[0])], len(cal))
        for name, score in values.items():
            if not np.isfinite(score).all():
                raise FloatingPointError(f"Nonfinite scores: {name}")
            result[name, arm, "late"] = variant_rows(score, split, "attempt")["late"]
    return result


def worker_init(arrays):
    global ROTATION_ARRAYS
    ROTATION_ARRAYS = arrays
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def worker(split, windows, budget):
    return score_rotation(ROTATION_ARRAYS, split, windows, budget)


def ledger_digest(ledger):
    digest = sha256()
    for key in sorted(ledger):
        digest.update("/".join(key).encode())
        digest.update(ledger[key].tobytes())
    return digest.hexdigest()


def summarize(ledgers, n, established):
    rng = np.random.default_rng(177)
    weights = np.vstack([np.ones(n, int), rng.multinomial(n, np.full(n, 1 / n), size=500)])
    result = evaluate(ledgers, weights, pairwise=False)
    for m in ANCHORS:
        for arm in ("single", "pair"):
            key = f"{m}/{arm}/late"
            assert result["metrics"][key] == established["metrics"][key], key
        key = f"{m}/pair-minus-single"
        assert result["comparisons"][key] == established["comparisons"][key], key
    baseline = min(established["criteria"], key=lambda m: established["metrics"][f"{m}/pair/late"]["eer"]["point"])
    metrics = established["metrics"][f"{baseline}/pair/late"]
    result["round5_best"] = dict(model=baseline, metrics=metrics,
                                 delta=established["comparisons"][f"{baseline}/pair-minus-single"]["eer"])
    result["against_round5_best_eer"] = {m: result["metrics"][f"{m}/pair/late"]["eer"]["point"] - metrics["eer"]["point"]
                                         for m in MODELS}
    return result


def run(args):
    start = perf_counter()
    n, windows, budget = COHORTS[args.cohort]
    notebook = Path(__file__).resolve().parents[2] / "07_complete_results_all_models_all_sessions.ipynb"
    _, _, visits, arrays, _ = load_features(args.fifs, args.cohort, args.kit, notebook, args.workers,
                                           expected_people=n, windows=windows, enrollment_windows=budget,
                                           reader=recording)
    if args.cohort == "ds007176":
        groups = kit_module(args.kit).identity_groups([int(v[-1]) for v in visits[:, -1]])
    else:
        groups = np.array_split(np.random.default_rng(SEED).permutation(n), 5)
        groups = [tuple(sorted(g)) for g in groups]
    splits = audited_rotations(groups, n)
    arrays["logcov"] = logs_of_covariance(arrays.pop("cov"))
    print(f"Prepared {n} identities in {perf_counter() - start:.1f}s", flush=True)
    ledgers = defaultdict(list)
    run_one = partial(worker, windows=windows, budget=budget)

    def append(results):
        first_digest = None
        for i, result in enumerate(results, 1):
            if i == 1:
                first_digest = ledger_digest(result)
            for key, value in result.items():
                ledgers[key].append(value)
            print(f"Scored rotation {i}/{len(splits)} in {perf_counter() - start:.1f}s", flush=True)
        return first_digest

    if args.scorers > 1:
        with ProcessPoolExecutor(args.scorers, mp_context=get_context("fork"), initializer=worker_init,
                                 initargs=(arrays,)) as pool:
            digest = append(pool.map(run_one, splits))
        worker_init(arrays)
        assert ledger_digest(run_one(splits[0])) == digest, "Parallel rotation differs from serial"
        print(f"Parallel rotation 1 matched serial: {digest}", flush=True)
    else:
        worker_init(arrays)
        digest = append(map(run_one, splits))
    result = summarize(ledgers, n, previous(args.cohort))
    result.update(dataset=args.cohort, subjects=n, probe_windows_per_state=windows, enrollment_windows=budget,
                  rotations=len(splits), draws=500, seed=SEED, scorers=args.scorers, rotation1_ledger_sha256=digest,
                  serial_anchor_matched=args.scorers > 1, elapsed_seconds=perf_counter() - start)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", choices=tuple(COHORTS))
    for name in ("fifs", "kit", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--scorers", type=int, default=1)
    args = parser.parse_args()
    result = run(args)
    partial_output = args.output.with_suffix(".partial")
    partial_output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    partial_output.replace(args.output)
    print(f"Completed {len(MODELS)} new model rows: {args.output.name}", flush=True)


if __name__ == "__main__":
    main()
