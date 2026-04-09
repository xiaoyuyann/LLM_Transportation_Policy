"""
Voting aggregation methods.

- Instant Runoff Voting (IRV): used for ranked ballots (ranked and average modes).
- Approval voting: used for approval ballots (each approved policy gets one vote,
  winner is the most-approved policy).
"""

import json
from collections import Counter
from pathlib import Path


def run_irv(votes: list[list[int]]) -> dict:
    """
    Run Instant Runoff Voting on a list of ranked ballots.

    Args:
        votes: List of ranked vote lists, e.g. [[3, 1, 7, 0, 5], [1, 3, ...], ...]
               Each inner list is one voter's preference from most to least preferred.

    Returns:
        dict with keys:
          - winning_policy (int): index of the winning policy
          - rounds (list): per-IRV-round vote counts
          - summary (str): human-readable result description
    """
    votes = [list(v) for v in votes]  # defensive copy
    irv_history = []
    irv_round = 1

    while True:
        first_choices = [ballot[0] for ballot in votes if ballot]
        if not first_choices:
            break

        vote_counts = Counter(first_choices)
        total = sum(vote_counts.values())

        irv_history.append({
            "irv_round": irv_round,
            "vote_counts": dict(vote_counts),
            "total_votes": total,
        })

        # Check for majority winner
        winner, top_count = vote_counts.most_common(1)[0]
        if top_count > total / 2:
            return {
                "winning_policy": winner,
                "rounds": irv_history,
                "summary": f"Policy {winner} won with {top_count}/{total} votes in IRV round {irv_round}.",
            }

        # Eliminate the candidate(s) with fewest first-choice votes
        min_votes = min(vote_counts.values())
        to_eliminate = {c for c, cnt in vote_counts.items() if cnt == min_votes}
        votes = [[v for v in ballot if v not in to_eliminate] for ballot in votes]
        irv_round += 1


def run_approval(votes: list[list[int]]) -> dict:
    """
    Run approval-vote aggregation (plurality count over approved policies).

    Args:
        votes: List of approval vote lists, e.g. [[3, 1, 7, 0, 5], ...]
               Order within each list does not matter.

    Returns:
        dict with keys:
          - winning_policy (int): most-approved policy
          - approval_counts (dict): per-policy approval count
          - summary (str): human-readable result description
    """
    all_approved = [policy for ballot in votes for policy in ballot]
    counts = Counter(all_approved)
    winner, count = counts.most_common(1)[0]
    return {
        "winning_policy": winner,
        "approval_counts": dict(counts),
        "summary": f"Policy {winner} won with {count} approvals.",
    }


def save_irv_summary(result: dict, output_path: str | Path) -> None:
    Path(output_path).write_text(json.dumps(result, indent=2))


def load_irv_summaries(base_dir: str | Path, round_dirs: list[str]) -> list[dict]:
    """Load IRV summary JSON files from multiple round directories."""
    summaries = []
    for rdir in round_dirs:
        irv_path = Path(base_dir) / rdir / "irv_summary.json"
        if irv_path.exists():
            summaries.append(json.loads(irv_path.read_text()))
        else:
            print(f"[WARN] IRV summary not found: {irv_path}")
    return summaries


def summarize_across_rounds(base_dir: str | Path, round_dirs: list[str]) -> dict:
    """
    Aggregate IRV winners across all rounds and save a summary JSON.

    Returns a dict with winning counts per policy and the overall most-frequent winner.
    """
    summaries = load_irv_summaries(base_dir, round_dirs)
    winners = [s["winning_policy"] for s in summaries if "winning_policy" in s]
    counts = Counter(winners)
    most_common, most_common_count = counts.most_common(1)[0] if counts else (None, 0)

    summary = {
        "total_rounds": len(round_dirs),
        "rounds_with_results": len(winners),
        "winning_policy_counts": dict(counts),
        "round_winners": [
            {"round_dir": rd, "winning_policy": s.get("winning_policy")}
            for rd, s in zip(round_dirs, summaries)
        ],
        "most_frequent_winner": most_common,
        "most_frequent_winner_count": most_common_count,
    }

    out_path = Path(base_dir) / "winning_policy_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"Winning policy summary saved to {out_path}")
    return summary
