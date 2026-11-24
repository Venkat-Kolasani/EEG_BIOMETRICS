"""Render the Round 7 results from aggregate artifacts."""
import argparse
import json
from pathlib import Path

from round7 import BACKBONES, MODELS


ROOT = Path(__file__).resolve().parent
COHORT_LABELS = {
    "ds007176": "ds007176",
    "ds004148": "RestCog",
    "ds005385": "Dortmund, two-day sensitivity analysis",
    "wbcic-shu": "WBCIC-SHU, modified-duration three-day",
}
GATES = ("directional_eer_gain", "frr_margin", "far_margin", "far_control")


def load_results(root=ROOT):
    return {slug: json.loads((root / f"round7-{slug}.json").read_text()) for slug in COHORT_LABELS}


def percent(metric):
    return f"{100 * metric['point']:.2f}%"


def interval(metric):
    return "{point:+.2f} [{low:+.2f}, {high:+.2f}]".format(**{k: 100 * v for k, v in metric.items()})


def metric_cells(metrics, delta):
    return " | ".join([*(percent(metrics[k]) for k in ("eer", "frr", "far")), interval(delta)])


def render(results):
    lines = [
        "# Round 7: waveform networks and fusion",
        "",
        "Fresh scoring on reused prepared recordings, not an independent replication. See the [protocol](ROUND7_PROTOCOL.md).",
        "Negative paired-minus-single EER favors pairing. The intervals are unadjusted, crossed-identity bootstrap intervals.",
        "FRR and FAR are measured at the frozen cutoffs; EER summarizes score discrimination independently of those cutoffs.",
        "",
        "| Cohort | Lowest new paired EER | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | Best Round 5 model | Round 5 paired EER | EER gap, pp |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for slug, label in COHORT_LABELS.items():
        d = results[slug]
        baseline = d["round5_best"]
        winner = min(MODELS, key=lambda m: d["metrics"][f"{m}/pair/late"]["eer"]["point"])
        cells = metric_cells(d["metrics"][f"{winner}/pair/late"], d["comparisons"][f"{winner}/pair-minus-single"]["eer"])
        gap = 100 * d["against_round5_best_eer"][winner]
        lines.append(f"| {label} | {winner} | {cells} | {baseline['model']} | {percent(baseline['metrics']['eer'])} | {gap:+.2f} |")
    lines.extend(["", "Winner and EER gap comparisons are descriptive; a smaller point estimate is not evidence of superiority.",
                  "All four gates are relative to the paired-versus-single study criteria, except the held-out FAR upper bound; even an all-gate pass does not establish usability.",
                  ""])
    all_gates = [f"{COHORT_LABELS[slug]} / {m}" for slug, d in results.items() for m in MODELS
                 if d["criteria"][m]["all"]]
    directional = [m for m in MODELS if all(d["criteria"][m]["directional_eer_gain"] for d in results.values())]
    wins = [f"{COHORT_LABELS[slug]} / {m}" for slug, d in results.items() for m in MODELS
            if d["against_round5_best_eer"][m] < 0]
    lines.extend([
        "- **All study gates passed:** " + ("; ".join(all_gates) if all_gates else "no new model–cohort result") + ".",
        "- **Pairing EER interval favored pairing in each cohort:** " + (", ".join(directional) or "no new model") + ".",
        "- **Lower paired EER point estimate than the Round 5 winner:** " + ("; ".join(wins) or "no new model–cohort result") + ".",
        "",
        "| Cohort | Best waveform model | Its paired EER | EEGNet v4 paired EER | Separate minus joint paired EER, pp |",
        "|---|---|---:|---:|---:|",
    ])
    for slug, label in COHORT_LABELS.items():
        metrics = results[slug]["metrics"]
        def eer(model):
            return metrics[f"{model}/pair/late"]["eer"]
        best = min(BACKBONES, key=lambda m: eer(m)["point"])
        gap = 100 * (eer("Separate-state fusion")["point"] - eer("Joint-state scores")["point"])
        lines.append(f"| {label} | {best} | {percent(eer(best))} | {percent(eer(BACKBONES[0]))} | {gap:+.2f} |")
    lines.append("")
    for slug, label in COHORT_LABELS.items():
        d = results[slug]
        baseline = d["round5_best"]
        lines.extend([f"## {label}", "",
                      f"{d['subjects']} people; {d['rotations']} rotations; {d['probe_windows_per_state']} probe windows per state; "
                      f"{d['enrollment_windows']} total enrollment windows. [Aggregate JSON](round7-{slug}.json).",
                      "",
                      "| Model | Paired EER | FRR | FAR | Pairing Δ EER, pp (95% CI) | EER gap vs. Round 5 best, pp | EER gate | FRR margin | FAR margin | FAR upper bound | All |",
                      "|---|---:|---:|---:|---:|---:|---|---|---|---|---|"])
        for m in MODELS:
            cells = metric_cells(d["metrics"][f"{m}/pair/late"], d["comparisons"][f"{m}/pair-minus-single"]["eer"])
            gates = " | ".join("Pass" if d["criteria"][m][g] else "Fail" for g in (*GATES, "all"))
            lines.append(f"| {m} | {cells} | {100 * d['against_round5_best_eer'][m]:+.2f} | {gates} |")
        cells = metric_cells(baseline["metrics"], baseline["delta"])
        lines.extend([f"| Round 5: {baseline['model']} | {cells} | — | — | — | — | — | — |", ""])
    lines.extend([
        "## Interpretation limits",
        "",
        "- The waveform results apply to the fixed verification adaptation and training schedule, not to broader EEGNet or ConvNet performance.",
        "- The rank average and stacker reuse the cutoff calibration fold; the stacker also fits on that fold's genuine claimant scores. Neither sees final impostors or late data during fitting.",
        "- The eye-state models share an enrollment budget, not a per-model sample size: each separate fit uses half the joint model's training rows.",
        "- Dortmund and WBCIC-SHU differ in schedule and duration. These are not interchangeable replications or a demonstration of secure deployment.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "ROUND7_RESULTS.md"
    result = render(load_results())
    if args.check:
        if path.read_text() != result:
            raise SystemExit(f"{path.name} differs from aggregate artifacts")
        print(f"Verified {len(COHORT_LABELS)} cohort winners, {len(COHORT_LABELS) * len(MODELS)} new model rows and all Round 5 comparator rows.")
    else:
        path.write_text(result)


if __name__ == "__main__":
    main()
