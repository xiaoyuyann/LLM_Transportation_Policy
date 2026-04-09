"""
Core simulation logic.

One simulation run consists of multiple rounds. In each round:
  1. Each community agent (or a single average-citizen agent) is queried via LLM.
  2. Individual responses are saved as JSON files.
  3. All responses are compiled into a CSV.
  4. Votes are aggregated (IRV for ranked/average modes, approval counting for approval mode).

Usage (called from simulate.py):
    run_simulation(city, model_name, mode, rounds, output_dir)
"""

import ast
import json
import os
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from .config import (
    AVERAGE_PROMPT_TEMPLATE,
    CITY_META,
    COMMUNITIES,
    POLICY_CSV,
    SYSTEM_PROMPT_APPROVAL,
    SYSTEM_PROMPT_APPROVAL_ALL,
    SYSTEM_PROMPT_AVERAGE,
    SYSTEM_PROMPT_RANKED,
    USER_PROMPT_TEMPLATE,
)
from .llm_client import LLMClient
from .voting import run_approval, run_irv, save_irv_summary, summarize_across_rounds

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sanitize_filename(name: str) -> str:
    """Convert a community name to a safe filename (lowercase, underscores)."""
    name = name.replace("/", "&")
    name = re.sub(r"[^\w\s&-]", "", name)
    return name.replace(" ", "_").lower()


def _load_policy_list(city: str) -> tuple[pd.DataFrame, list[str]]:
    """Load the policy CSV and format each row as a human-readable string."""
    df = pd.read_csv(POLICY_CSV[city]).reset_index(drop=True)

    # Chicago uses 0-indexed policies; Houston uses 1-indexed (as in the CSV 'index' column)
    index_col = df["index"] if "index" in df.columns else df.index

    policy_strings = [
        (
            f"{int(idx)}. Tax: {row['tax_percentage']}%, "
            f"Fare: ${row['fare']}/ride, "
            f"Driving Fee: ${row['driver_fee']}/trip "
            f"| Car {row['drive_time_min']} min (${row['drive_cost']}) "
            f"| Transit {row['bus_time_min']} min (${row['bus_cost']})"
        )
        for idx, (_, row) in zip(index_col, df.iterrows())
    ]
    return df, policy_strings


def _load_community_info(community: str, info_dir: Path) -> str:
    """
    Load demographic/census JSON for a community and format it for the prompt.
    Returns an empty string if no info file exists (graceful degradation).
    """
    filename = f"{community.lower().replace(' ', '_').replace('/', '&')}.json"
    path = info_dir / filename
    if not path.exists():
        # Try a simpler sanitization (spaces→underscores, drop special chars)
        plain = community.lower().replace(' ', '_').replace('/', '_').replace("'", '')
        filename_plain = f"{plain}.json"
        path = info_dir / filename_plain
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return (
                "Community demographic data (census):\n"
                + json.dumps(data, indent=2, ensure_ascii=False)
            )
        except Exception as exc:
            print(f"  [WARN] Could not read info for {community}: {exc}")
    else:
        print(f"  [WARN] No info file found for {community} (looked for {filename})")
    return ""


def _build_community_prompt(
    city: str,
    community: str,
    policy_options_str: str,
    mode: str,
    info_dir: Path | None = None,
) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) for a single community agent.

    If info_dir is provided, demographic data from that directory is injected
    into the user prompt (CHI-know / with-info variant).
    """
    meta = CITY_META[city]
    b = meta["baseline"]

    community_label = "super neighborhood" if city == "houston" else "community area"

    if mode == "approval":
        system = SYSTEM_PROMPT_APPROVAL[city]
    elif mode == "approval-all":
        system = SYSTEM_PROMPT_APPROVAL_ALL[city]
    else:
        system = SYSTEM_PROMPT_RANKED[city]

    community_info = ""
    if info_dir is not None:
        community_info = _load_community_info(community, info_dir)

    user = USER_PROMPT_TEMPLATE.format(
        num_communities=meta["num_communities"],
        num_policies=meta["num_policies"],
        agency=meta["agency"],
        baseline_fare=b["fare"],
        baseline_tax=b["tax_pct"],
        baseline_fee=b["driver_fee"],
        baseline_car_time=b["car_time_min"],
        baseline_car_cost=b["car_cost"],
        baseline_transit_time=b["transit_time_min"],
        baseline_transit_cost=b["transit_cost"],
        policy_options=policy_options_str,
        community=community,
        community_label=community_label,
        policy_index_range=meta["policy_index_range"],
        community_info=community_info,
    )
    return system, user


def _build_average_prompt(city: str, policy_options_str: str) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) for the average-citizen agent."""
    meta = CITY_META[city]
    b = meta["baseline"]
    city_name = city.title()

    system = SYSTEM_PROMPT_AVERAGE[city]
    user = AVERAGE_PROMPT_TEMPLATE.format(
        city_name=city_name,
        num_policies=meta["num_policies"],
        agency=meta["agency"],
        baseline_fare=b["fare"],
        baseline_tax=b["tax_pct"],
        baseline_fee=b["driver_fee"],
        baseline_car_time=b["car_time_min"],
        baseline_car_cost=b["car_cost"],
        baseline_transit_time=b["transit_time_min"],
        baseline_transit_cost=b["transit_cost"],
        policy_options=policy_options_str,
        policy_index_range=meta["policy_index_range"],
    )
    return system, user


# ---------------------------------------------------------------------------
# Per-round simulation
# ---------------------------------------------------------------------------


def _run_community_round(
    city: str,
    client: LLMClient,
    mode: str,
    policy_options_str: str,
    round_dir: Path,
    info_dir: Path | None = None,
) -> None:
    """Query every community agent and save individual JSON responses."""
    communities = COMMUNITIES[city]
    for community in communities:
        print(f"  Processing {community} ...")
        system, user = _build_community_prompt(city, community, policy_options_str, mode, info_dir)
        response = client.complete(system, user)
        if response and {"community_area", "thinking", "vote"} <= response.keys():
            _save_response(community, response, round_dir)
        else:
            print(f"  [WARN] Invalid or missing response for {community}")


def _run_average_round(
    city: str,
    client: LLMClient,
    policy_options_str: str,
    round_dir: Path,
    round_idx: int,
) -> None:
    """Query the average-citizen agent and save the response."""
    system, user = _build_average_prompt(city, policy_options_str)
    print(f"  Querying average-citizen agent ...")
    response = client.complete(system, user)
    if response and {"community_area", "thinking", "vote"} <= response.keys():
        out_path = round_dir / f"avg_response_{round_idx}.json"
        out_path.write_text(json.dumps(response, indent=2, ensure_ascii=False))
        print(f"  Saved: {out_path.name}")
    else:
        print(f"  [WARN] Invalid or missing response from average-citizen agent")


def _save_response(community: str, data: dict, round_dir: Path) -> None:
    safe = _sanitize_filename(community)
    path = round_dir / "responses" / f"{safe}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Compile + aggregate
# ---------------------------------------------------------------------------


def _compile_community_responses(city: str, round_dir: Path) -> Path:
    """
    Read all per-community JSON responses and write a combined CSV.

    Returns the path to the generated CSV file.
    """
    communities = COMMUNITIES[city]
    rows = []
    for community in communities:
        safe = _sanitize_filename(community)
        path = round_dir / "responses" / f"{safe}.json"
        if not path.exists():
            print(f"  [WARN] Missing response file: {path.name}")
            continue
        try:
            data = json.loads(path.read_text())
            vote = data["vote"]
            row = {
                "community_area": data["community_area"],
                "disposable_income": data["thinking"]["disposable_income"],
                "discretionary_consumption": data["thinking"]["discretionary_consumption"],
                "accessibility": data["thinking"]["accessibility"],
                "decision_rationale": data["thinking"]["decision_rationale"],
                "vote": vote,
            }
            for i, v in enumerate(vote[:5], start=1):
                row[f"rank{i}"] = v
            rows.append(row)
        except Exception as exc:
            print(f"  [ERROR] Reading {path.name}: {exc}")

    csv_path = round_dir / "combined_voting_results.csv"
    if rows:
        pd.DataFrame(rows).to_csv(csv_path, index=False)
        print(f"  Compiled {len(rows)} responses -> {csv_path.name}")
    else:
        print("  [WARN] No responses compiled.")
    return csv_path


def _aggregate_votes(csv_path: Path, mode: str, irv_output: Path) -> dict:
    """Read compiled CSV, aggregate votes, and save IRV/approval summary JSON."""
    df = pd.read_csv(csv_path)
    df["vote_list"] = df["vote"].apply(ast.literal_eval)
    votes = df["vote_list"].tolist()

    if mode in ("approval", "approval-all"):
        result = run_approval(votes)
    else:
        result = run_irv(votes)

    save_irv_summary(result, irv_output)
    winner = result["winning_policy"]
    print(f"  Winner: Policy {winner}  |  {result['summary']}")
    return result


def _compile_average_responses(round_dir: Path, round_idx: int) -> dict | None:
    """Load a single average-citizen response."""
    path = round_dir / f"avg_response_{round_idx}.json"
    if not path.exists():
        print(f"  [WARN] Average response not found: {path.name}")
        return None
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_simulation(
    city: str,
    model_name: str,
    mode: str,
    rounds: int,
    output_dir: str,
    use_info: bool = False,
) -> None:
    """
    Run the full LLM-based policy voting simulation.

    Args:
        city:       'chicago' or 'houston'
        model_name: LLM model identifier, e.g. 'gpt-4o-2024-08-06'
        mode:       'ranked' | 'approval' | 'approval-all' | 'average'
        rounds:     Number of independent simulation rounds
        output_dir: Root directory for all output files
        use_info:   If True, inject per-community demographic data (from data/CA_info/)
                    into the user prompt. Only supported for Chicago.
    """
    if city not in CITY_META:
        raise ValueError(f"Unknown city '{city}'. Choose from: {list(CITY_META)}")
    if mode not in ("ranked", "approval", "approval-all", "average"):
        raise ValueError(f"Unknown mode '{mode}'. Choose from: ranked, approval, approval-all, average")
    if use_info and city != "chicago":
        raise ValueError("--info is only supported for Chicago (data/CA_info/ contains Chicago data only).")

    info_dir: Path | None = None
    if use_info:
        info_dir = Path(__file__).parent.parent / "data" / "CA_info"
        if not info_dir.exists():
            raise FileNotFoundError(f"CA_info directory not found at {info_dir}")

    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Save run metadata
    meta_path = base_dir / "run_config.json"
    meta_path.write_text(
        json.dumps(
            {"city": city, "model": model_name, "mode": mode, "rounds": rounds, "use_info": use_info},
            indent=2,
        )
    )

    client = LLMClient(model_name=model_name, temperature=0)
    _, policy_options_str = _load_policy_list(city)
    policy_options_joined = "\n".join(policy_options_str)

    round_dirs = []
    for i in range(1, rounds + 1):
        round_name = f"round_{i}"
        round_dir = base_dir / round_name
        round_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- Round {i}/{rounds} ---")

        if mode == "average":
            _run_average_round(city, client, policy_options_joined, round_dir, i)
            # For average mode, compile a single-row CSV for consistency
            resp = _compile_average_responses(round_dir, i)
            if resp:
                vote = resp.get("vote", [])
                row = {
                    "community_area": resp.get("community_area", ""),
                    "disposable_income": resp.get("thinking", {}).get("disposable_income", ""),
                    "discretionary_consumption": resp.get("thinking", {}).get("discretionary_consumption", ""),
                    "accessibility": resp.get("thinking", {}).get("accessibility", ""),
                    "decision_rationale": resp.get("thinking", {}).get("decision_rationale", ""),
                    "vote": str(vote),
                }
                for j, v in enumerate(vote[:5], start=1):
                    row[f"rank{j}"] = v
                csv_path = round_dir / "combined_voting_results.csv"
                pd.DataFrame([row]).to_csv(csv_path, index=False)
                print(f"  Vote: {vote}")
        else:
            _run_community_round(city, client, mode, policy_options_joined, round_dir, info_dir)
            csv_path = _compile_community_responses(city, round_dir)
            irv_path = round_dir / "irv_summary.json"
            _aggregate_votes(csv_path, mode, irv_path)

        round_dirs.append(round_name)

    if mode != "average":
        print("\n--- Cross-round summary ---")
        summarize_across_rounds(base_dir, round_dirs)

    print(f"\nSimulation complete. Results saved to: {base_dir}")
