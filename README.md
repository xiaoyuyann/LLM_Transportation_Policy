# LLM-FFT: Addressing the Alignment Problem in Transportation Policy-Making

This repository accompanies the paper:

> **Addressing the alignment problem in transportation policy making: an LLM approach**

The project uses Large Language Models (LLMs) to simulate community-level transportation policy preferences across city neighborhoods. Each neighborhood is represented by an LLM agent that evaluates policy trade-offs and submits a ranked or approval vote. Votes are aggregated using **Instant Runoff Voting (IRV)** to identify the community-preferred policy.

---

## Overview

The simulation models a city-wide referendum over transportation policy packages. Each package combines three levers:

| Policy dimension | Options |
|---|---|
| Transit fare (per ride) | \$0.75 / \$1.25 / \$1.75 |
| Dedicated sales tax | 0.5% / 1.0% / 1.5% |
| Driving fee (per trip) | \$0.00 / \$0.50 / \$1.00 |

This gives **27 candidate packages for Chicago** and **24 for Houston** (based on city-specific modeling by planning agencies).

Each community agent considers:
1. Disposable income of its residents
2. Discretionary consumption patterns
3. Accessibility by car vs. transit

---

## Repository Structure

```
LLM-FFT/
├── simulate.py              # Main entry point (CLI)
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
│
├── data/
│   ├── policy_chicago.csv   # 27 policy options for Chicago (indices 0–26)
│   ├── CA_info/             # Per-community demographic JSON files (Chicago only)
│   │   ├── rogers_park.json
│   │   ├── hyde_park.json
│   │   └── ...              # 77 files total (one per Chicago community area)
│   └── policy_houston.csv   # 24 policy options for Houston (indices 1–24)
│
├── src/
│   ├── config.py            # Community lists, city metadata, prompt templates
│   ├── llm_client.py        # Unified OpenAI / Anthropic API wrapper
│   ├── voting.py            # IRV and approval-vote aggregation
│   └── simulation.py        # Round-by-round simulation orchestration
│
└── results/                 # Created at runtime; one subfolder per experiment
    └── <city>_<model>_<mode>/
        ├── run_config.json
        ├── round_1/
        │   ├── responses/           # One JSON file per community agent
        │   ├── combined_voting_results.csv
        │   └── irv_summary.json
        ├── round_2/ ...
        └── winning_policy_summary.json
```

---

## Requirements

- Python 3.11+
- An OpenAI API key (for GPT-4o experiments)
- An Anthropic API key (for Claude experiments)

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

Set up API keys:

```bash
cp .env.example .env
# Edit .env and fill in OPENAI_API_KEY and/or ANTHROPIC_API_KEY
```

> **Every time you open a new terminal session**, re-activate the environment before running experiments:
> ```bash
> source .venv/bin/activate
> ```

---

## Running experiments

All experiments are launched through a single CLI:

```bash
python simulate.py \
  --city   <chicago|houston> \
  --model  <model_name> \
  --mode   <ranked|approval|average> \
  --rounds <N> \
  [--output <path>]
```

### Arguments

| Argument | Description |
|---|---|
| `--city` | `chicago` (77 communities, 27 policies) or `houston` (88 neighborhoods, 27 policies) |
| `--model` | `gpt-4o-2024-08-06` or `claude-sonnet-4-5-20250929` |
| `--mode` | `ranked` — per-community ranked top-5 → IRV; `approval` — per-community approve up to 5 (no rank); `approval-all` — per-community approve any number (no limit); `average` — single average-citizen agent |
| `--rounds` | Number of independent simulation rounds (default: 10) |
| `--info` | Inject per-community demographic data into the prompt (CHI-know variant). Only for `--city chicago`. Reads from `data/CA_info/`. |
| `--output` | Output directory (default: `results/<city>_<model_short>_<mode>`, or `..._info` when `--info` is set) |

---

## Reproducing paper experiments

The eight main experimental conditions from the paper can be reproduced with the following commands. Each command runs 10 independent rounds.

### Chicago experiments

```bash
# 1. Chicago — GPT-4o — ranked voting (community agents)
python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode ranked --rounds 10

# 2. Chicago — Claude-3.5-Sonnet — ranked voting (community agents)
python simulate.py --city chicago --model claude-sonnet-4-5-20250929 --mode ranked --rounds 10

# 3. Chicago — GPT-4o — ranked voting WITH local demographic info (CHI-know)
python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode ranked --rounds 10 --info

# 4. Chicago — Claude-3.5-Sonnet — ranked voting WITH local demographic info (CHI-know)
python simulate.py --city chicago --model claude-sonnet-4-5-20250929 --mode ranked --rounds 10 --info

# 5. Chicago — GPT-4o — approval voting, up to 5 (community agents, no ranking)
python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode approval --rounds 10

# 6. Chicago — Claude-3.5-Sonnet — approval voting, up to 5 (community agents, no ranking)
python simulate.py --city chicago --model claude-sonnet-4-5-20250929 --mode approval --rounds 10

# 7. Chicago — GPT-4o — all-approval voting, unlimited (community agents, no ranking)
python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode approval-all --rounds 10

# 8. Chicago — Claude-3.5-Sonnet — all-approval voting, unlimited (community agents, no ranking)
python simulate.py --city chicago --model claude-sonnet-4-5-20250929 --mode approval-all --rounds 10

# 9. Chicago — GPT-4o — average-citizen baseline (single agent)
python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode average --rounds 10

# 10. Chicago — Claude-3.5-Sonnet — average-citizen baseline (single agent)
python simulate.py --city chicago --model claude-sonnet-4-5-20250929 --mode average --rounds 10
```

### Houston experiments

```bash
# 11. Houston — GPT-4o — ranked voting (neighborhood agents)
python simulate.py --city houston --model gpt-4o-2024-08-06 --mode ranked --rounds 10

# 12. Houston — Claude-3.5-Sonnet — ranked voting (neighborhood agents)
python simulate.py --city houston --model claude-sonnet-4-5-20250929 --mode ranked --rounds 10

# 13. Houston — GPT-4o — all-approval voting, unlimited (neighborhood agents)
python simulate.py --city houston --model gpt-4o-2024-08-06 --mode approval-all --rounds 10

# 14. Houston — Claude-3.5-Sonnet — all-approval voting, unlimited (neighborhood agents)
python simulate.py --city houston --model claude-sonnet-4-5-20250929 --mode approval-all --rounds 10
```

---

## Output format

### Per-round outputs

**`responses/<community_name>.json`** — raw LLM response for each community:
```json
{
  "community_area": "Hyde Park",
  "thinking": {
    "disposable_income": "...",
    "discretionary_consumption": "...",
    "accessibility": "...",
    "decision_rationale": "..."
  },
  "vote": [3, 7, 12, 0, 19]
}
```

**`combined_voting_results.csv`** — all community votes compiled:

| community_area | vote | rank1 | rank2 | rank3 | rank4 | rank5 | ... |
|---|---|---|---|---|---|---|---|
| Hyde Park | [3, 7, 12, 0, 19] | 3 | 7 | 12 | 0 | 19 | ... |

**`irv_summary.json`** — IRV result for this round:
```json
{
  "winning_policy": 7,
  "rounds": [...],
  "summary": "Policy 7 won with 41/77 votes in IRV round 3."
}
```

### Cross-round summary

**`winning_policy_summary.json`** — aggregated winners across all rounds:
```json
{
  "total_rounds": 10,
  "winning_policy_counts": {"7": 6, "3": 4},
  "most_frequent_winner": 7,
  "most_frequent_winner_count": 6
}
```

---

## Voting modes explained

### CHI-know variant (`--info`)

Adding `--info` to any Chicago experiment injects real census and demographic data for each community area directly into its agent's prompt. The data comes from `data/CA_info/<community>.json` and includes:

```json
{
  "Population": { "Total Population": 29559, ... },
  "Race": { "White (Non-Hispanic)": 44.9, ... },
  "Car Ownership": { "No Vehicle": 43.4, "1 Vehicle": 45.7, ... },
  "Travel Mode": { "Drive Alone": 22.2, "Transit": 22.5, ... },
  "Income": { "<$25,000": 23.6, "$150,000+": 19.2, ... }
}
```

This tests whether grounding agents with factual local data changes their policy preferences compared to relying on the LLM's parametric knowledge alone.

---

### Ranked voting (`--mode ranked`)

Each community agent returns 5 policies in preference order. All ballots are aggregated using **Instant Runoff Voting (IRV)**:
1. Count first-choice votes.
2. If any policy has > 50% of votes, it wins.
3. Otherwise, eliminate the least-popular policy and redistribute its votes to the next preference.
4. Repeat until a majority winner emerges.

### Approval voting (`--mode approval`)

Each community agent approves **up to 5** policies without ranking them. The policy with the most total approvals wins (plurality).

### All-approval voting (`--mode approval-all`)

Each community agent approves **any number** of policies it genuinely supports — there is no cap. This removes the artificial constraint of picking exactly 5 and allows communities to express broader or narrower preference sets. The policy with the most total approvals wins (plurality). This is the unrestricted counterpart to `approval`.

### Average-citizen baseline (`--mode average`)

A single LLM agent representing "the average resident" of the city votes, instead of 77/88 separate community agents. This serves as a baseline to measure how much the per-community disaggregation affects the result.

---

## Policy data format

`data/policy_chicago.csv` (indices 0–26):

| index | tax_percentage | fare | driver_fee | drive_time_min | bus_time_min | drive_cost | bus_cost |
|---|---|---|---|---|---|---|---|
| 0 | 0.5 | 0.75 | 0.00 | 25.5 | 68.72 | 5.43 | 0.75 |
| 1 | 0.5 | 0.75 | 0.50 | 19.11 | 57.43 | 5.93 | 0.75 |
| ... | | | | | | | |

`data/policy_houston.csv` (indices 0–26): same schema as Chicago, with 27 policy combinations including the `driver_fee = $0.00` baseline option.

---

## Citation

If you use this code or data, please cite the accompanying paper.

Feel free to reach out if you have any questions, suggestions, or want to collaborate!
