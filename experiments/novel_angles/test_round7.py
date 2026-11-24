import unittest
from unittest.mock import patch

import numpy as np
import torch
from torch import nn

from render_round7 import ROOT, load_results, render
from round4 import variant_rows
from round5 import COHORTS
from round6 import previous
from round7 import (ANCHORS, BACKBONES, MODELS, embeddings, feature_scores, score_fusion, state_scores,
                    waveform_fit, waveform_scores)


class Round7Test(unittest.TestCase):
    def test_waveform_fit_and_embedding_keep_prepared_scale(self):
        wave = np.broadcast_to(np.array([-1., 1.], dtype=np.float32), (2, 3, 1, 2))
        model = nn.Sequential(nn.Flatten(), nn.Linear(2, 2))
        batches = []
        model.register_forward_pre_hook(lambda _, args: batches.append(args[0].detach().numpy().copy()))
        with patch("round7.backbone", return_value=model):
            waveform_fit(BACKBONES[0], wave)
        embeddings(model, wave)
        self.assertEqual(len(batches), 9)
        for batch in batches:
            np.testing.assert_array_equal(batch, wave.reshape(-1, 1, 2))

    def test_stacker_and_frozen_cutoff_ignore_late_and_final_test_scores(self):
        rng = np.random.default_rng(11)
        split = tuple(np.array(ids) for ids in ([0, 1], [2, 3], [4, 5], [6]))
        original = rng.normal(size=(4, 5, 2, 6, 2))
        changed = original.copy()
        changed[:, :, 1] = rng.normal(10, 1, changed[:, :, 1].shape)
        changed[:, 4, 0] = -99.
        changed[:, 2, 0, :, 1] = -100.
        changed[:, 3, 0, :, 0] = -100.
        for base, variant in zip(score_fusion(original, 2), score_fusion(changed, 2), strict=True):
            np.testing.assert_array_equal(base[:2, 0], variant[:2, 0])
            np.testing.assert_array_equal(
                variant_rows(base, split, "attempt")["late"][:, 4],
                variant_rows(variant, split, "attempt")["late"][:, 4],
            )

    def test_rank_mean_retains_equal_rank_sums(self):
        scores = np.empty((2, 3, 2, 3, 1))
        scores[:, :2] = np.arange(1, 7).reshape(2, 1, 3, 1)
        scores[0, 2, 1, :, 0] = [0, 1, 2]
        scores[1, 2, 1, :, 0] = [4, 3, 2]
        scores[:, 2, 0] = 7
        fused, _ = score_fusion(scores, 2)
        np.testing.assert_array_equal(fused[2, 1, :, 0], np.full(3, 4 / 12))

    def test_waveform_fits_receive_only_reference_enrollment(self):
        wave = np.random.default_rng(7).normal(size=(5, 4, 2, 6, 2, 5)).astype(np.float32)
        split = tuple(np.array(ids) for ids in ([0], [1, 2], [3], [4]))
        baseline = wave[split[1], :2, :, :2].reshape(2, 8, 2, 5)
        with patch("round7.waveform_fit") as fit, patch("round7.embeddings", side_effect=lambda _, x: x[..., 0]):
            result = waveform_scores(wave, split, [3, 0, 4], 6, 8)
        self.assertEqual(tuple(result), BACKBONES)
        for call, name in zip(fit.call_args_list, BACKBONES, strict=True):
            self.assertEqual(call.args[0], name)
            np.testing.assert_array_equal(call.args[1], baseline)
        self.assertEqual(result[BACKBONES[0]].shape, (3, 2, 12, 1))

    def test_state_fusion_uses_same_windows_and_matches_by_rank(self):
        wave = np.broadcast_to(np.arange(12).reshape(1, 1, 2, 6, 1), (5, 3, 2, 6, 1))
        split = tuple(np.array(ids) for ids in ([0], [1, 2], [3], [4]))
        with patch("round7.binary_score", side_effect=lambda _, query: query[..., 0]) as fit:
            joint, separate = state_scores(wave, split, [3, 0, 4], 6, 8)
        self.assertEqual([len(call.args[0]) for call in fit.call_args_list], [16, 8, 8])
        expected = [.5, 2.5, 4.5, 6.5, 8.5, 10.5, 3., 4., 5., 6., 7., 8.]
        np.testing.assert_array_equal(joint[0, 0, :, 0], expected)
        np.testing.assert_array_equal(separate, joint)

    def test_feature_fusion_fits_only_claimant_and_reference_enrollment(self):
        rng = np.random.default_rng(23)
        split = tuple(np.array(ids) for ids in ([0], [1, 2], [3], [4]))
        arrays = {k: rng.normal(size=(5, 3, 2, 6, width))
                  for k, width in (("spectral", 2), ("connectivity", 3), ("logcov", 4))}
        changed = {k: v.copy() for k, v in arrays.items()}
        for v in changed.values():
            v[:, 1:] += 202
            v[3:] -= 100
        with patch("round7.binary_score", side_effect=lambda _, query, widths: query[..., 0]) as fit:
            feature_scores(arrays, split, [3, 0, 4], 6, 8)
            feature_scores(changed, split, [3, 0, 4], 6, 8)
        first, second = [call.args for call in fit.call_args_list]
        np.testing.assert_array_equal(first[0], second[0])
        self.assertEqual(first[2], [2, 3, 4])
        self.assertEqual(first[0].shape, (16, 9))
        self.assertFalse(np.array_equal(first[1], second[1]))

    def test_report_values_and_reference_anchors(self):
        results = load_results()
        self.assertEqual((ROOT / "ROUND7_RESULTS.md").read_text(), render(results))
        for slug, data in results.items():
            with self.subTest(slug=slug):
                self.assertEqual((data["subjects"], data["probe_windows_per_state"], data["enrollment_windows"]),
                                 COHORTS[slug])
                self.assertEqual(set(data["criteria"]), {*MODELS, *ANCHORS})
                old = previous(slug)
                baseline = min(old["criteria"], key=lambda m: old["metrics"][f"{m}/pair/late"]["eer"]["point"])
                self.assertEqual(data["round5_best"]["model"], baseline)
                self.assertEqual(data["round5_best"]["metrics"], old["metrics"][f"{baseline}/pair/late"])
                self.assertEqual(data["round5_best"]["delta"], old["comparisons"][f"{baseline}/pair-minus-single"]["eer"])
                for m in ANCHORS:
                    self.assertEqual(data["criteria"][m], old["criteria"][m])
                    for arm in ("single", "pair"):
                        key = f"{m}/{arm}/late"
                        self.assertEqual(data["metrics"][key], old["metrics"][key])
                    key = f"{m}/pair-minus-single"
                    self.assertEqual(data["comparisons"][key], old["comparisons"][key])
                for m in MODELS:
                    self.assertEqual(data["against_round5_best_eer"][m],
                                     data["metrics"][f"{m}/pair/late"]["eer"]["point"]
                                     - old["metrics"][f"{baseline}/pair/late"]["eer"]["point"])
                self.assertEqual(data["scorers"] > 1, data["serial_anchor_matched"])


if __name__ == "__main__":
    unittest.main()
