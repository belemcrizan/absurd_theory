"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import aggregate, ensemble, summarize
from .config import SimulationConfig
from .io import write_json, write_trace
from .noise import load_empirical_noise
from .plotting import plot_dashboard, plot_metric_comparison, plot_response_comparison
from .simulation import simulate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="absurd-theory",
        description="Simulate and try to falsify the Wave-Induced Observability Shell hypothesis.",
    )
    parser.add_argument("--config", default="configs/default.json")
    parser.add_argument("--output", default="results/run")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--runs", type=int, default=32)
    parser.add_argument("--noise-csv", default=None)
    parser.add_argument("--noise-column", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = SimulationConfig.from_json(args.config)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    empirical = None
    if args.noise_csv:
        empirical = load_empirical_noise(args.noise_csv, args.noise_column)

    representative = simulate(config, seed=args.seed, model="wios", empirical_noise=empirical)
    write_trace(representative, output / "wios_trace.csv")
    plot_dashboard(representative, output / "wios_dashboard.png")

    metric_rows = ensemble(
        config, runs=args.runs, seed=args.seed, empirical_noise=empirical
    )
    summary = aggregate(metric_rows)
    write_json(
        {
            "status": "toy_model_only_not_empirical_evidence",
            "seed": args.seed,
            "runs_per_model": args.runs,
            "config": config.to_dict(),
            "representative_wios": summarize(representative, config).to_dict(),
            "ensemble": summary,
        },
        output / "summary.json",
    )

    result_sets = {
        model: [
            simulate(config, seed=args.seed + offset, model=model, empirical_noise=empirical)
            for offset in range(args.runs)
        ]
        for model in ("wios", "instrumental_null")
    }
    plot_response_comparison(result_sets, config, output / "pulse_response.png")
    plot_metric_comparison(metric_rows, output / "model_comparison.png")
    print(f"Wrote reproducible artifacts to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
