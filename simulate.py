#!/usr/bin/env python3
"""
LLM-FFT: Addressing the Alignment Problem in Transportation Policy-Making

Entry point for running the multi-agent LLM policy voting simulation.

Examples:
    # Chicago, GPT-4o, ranked voting, 10 rounds
    python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode ranked --rounds 10

    # Chicago, Claude, ranked voting, 10 rounds
    python simulate.py --city chicago --model claude-3-5-sonnet-20241022 --mode ranked --rounds 10

    # Chicago, GPT-4o, approval voting (up to 5), 10 rounds
    python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode approval --rounds 10

    # Chicago, Claude, all-approval voting (unlimited approvals), 10 rounds
    python simulate.py --city chicago --model claude-3-5-sonnet-20241022 --mode approval-all --rounds 10

    # Chicago, Claude, average-citizen baseline, 10 rounds
    python simulate.py --city chicago --model claude-3-5-sonnet-20241022 --mode average --rounds 10

    # Houston, GPT-4o, ranked voting, 10 rounds
    python simulate.py --city houston --model gpt-4o-2024-08-06 --mode ranked --rounds 10

    # Houston, Claude, ranked voting, 10 rounds
    python simulate.py --city houston --model claude-3-5-sonnet-20241022 --mode ranked --rounds 10
"""

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run LLM-FFT transportation policy voting simulation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--city",
        required=True,
        choices=["chicago", "houston"],
        help="City to simulate (chicago: 77 communities, 27 policies; houston: 88 neighborhoods, 24 policies).",
    )
    parser.add_argument(
        "--model",
        required=True,
        help=(
            "LLM model name. "
            "OpenAI: 'gpt-4o-2024-08-06'. "
            "Anthropic: 'claude-3-5-sonnet-20241022'."
        ),
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["ranked", "approval", "approval-all", "average"],
        help=(
            "Voting mode. "
            "'ranked': each community ranks top-5 policies; aggregated via IRV. "
            "'approval': each community approves up to 5 policies (no ranking); aggregated by plurality. "
            "'approval-all': each community approves any number of policies (no limit, no ranking); aggregated by plurality. "
            "'average': a single average-citizen agent votes instead of per-community agents."
        ),
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=10,
        help="Number of independent simulation rounds (default: 10).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output directory. "
            "Defaults to 'results/<city>_<model_short>_<mode>'."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Build default output path if not specified
    if args.output is None:
        model_short = args.model.split("-")[0]  # e.g., "gpt" or "claude"
        args.output = f"results/{args.city}_{model_short}_{args.mode}"

    print(f"LLM-FFT Simulation")
    print(f"  City:   {args.city}")
    print(f"  Model:  {args.model}")
    print(f"  Mode:   {args.mode}")
    print(f"  Rounds: {args.rounds}")
    print(f"  Output: {args.output}")
    print()

    # Lazy import to avoid loading API keys before args are parsed
    from src.simulation import run_simulation

    run_simulation(
        city=args.city,
        model_name=args.model,
        mode=args.mode,
        rounds=args.rounds,
        output_dir=args.output,
    )


if __name__ == "__main__":
    main()
