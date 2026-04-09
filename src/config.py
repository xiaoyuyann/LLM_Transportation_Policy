"""
City-level configuration: community lists, policy CSV paths, baseline travel data,
and prompt templates for Chicago and Houston.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent / "data"

POLICY_CSV = {
    "chicago": DATA_DIR / "policy_chicago.csv",
    "houston": DATA_DIR / "policy_houston.csv",
}

# ---------------------------------------------------------------------------
# Community lists
# ---------------------------------------------------------------------------

CHICAGO_COMMUNITIES = [
    "Rogers Park", "West Ridge", "Uptown", "Lincoln Square", "North Center",
    "Lake View", "Lincoln Park", "Near North Side", "Edison Park", "Norwood Park",
    "Jefferson Park", "Forest Glen", "North Park", "Albany Park", "Portage Park",
    "Irving Park", "Dunning", "Montclare", "Belmont Cragin", "Hermosa",
    "Avondale", "Logan Square", "Humboldt Park", "West Town", "Austin",
    "West Garfield Park", "East Garfield Park", "Near West Side", "North Lawndale",
    "South Lawndale", "Lower West Side", "Loop", "Near South Side", "Armour Square",
    "Douglas", "Oakland", "Fuller Park", "Grand Boulevard", "Kenwood",
    "Washington Park", "Hyde Park", "Woodlawn", "South Shore", "Chatham",
    "Avalon Park", "South Chicago", "Burnside", "Calumet Heights", "Roseland",
    "Pullman", "South Deering", "East Side", "West Pullman", "Riverdale",
    "Hegewisch", "Garfield Ridge", "Archer Heights", "Brighton Park", "McKinley Park",
    "Bridgeport", "New City", "West Elsdon", "Gage Park", "Clearing",
    "West Lawn", "Chicago Lawn", "West Englewood", "Englewood",
    "Greater Grand Crossing", "Ashburn", "Auburn Gresham", "Beverly",
    "Washington Heights", "Mount Greenwood", "Morgan Park", "O'Hare", "Edgewater",
]

HOUSTON_COMMUNITIES = [
    "Willowbrook", "Greater Greenspoint", "Carverdale", "Fairbanks / Northwest Crossing",
    "Greater Inwood", "Acres Home", "Hidden Valley", "Westbranch", "Addicks / Park Ten",
    "Spring Branch West", "Langwood", "Central Northwest (formerly Near Northwest)",
    "Independence Heights", "Lazybrook / Timbergrove", "Greater Heights", "Memorial",
    "Eldridge / West Oaks", "Briar Forest", "Westchase",
    "Mid-West (formerly Woodlake/Briarmeadow)", "Greater Uptown",
    "Washington Avenue Coalition / Memorial Park", "Afton Oaks / River Oaks",
    "Neartown / Montrose", "Alief", "Sharpstown", "Gulfton", "West University Place",
    "Westwood", "Braeburn", "Meyerland", "Braeswood", "Medical Center",
    "Astrodome Area", "South Main", "Brays Oaks (formerly Greater Fondren S.W.)",
    "Westbury", "Willow Meadows / Willowbend", "Fondren Gardens", "Central Southwest",
    "Fort Bend / Houston", "IAH Airport", "Kingwood", "Lake Houston",
    "Northside / Northline", "Jensen", "East Little York / Homestead",
    "Trinity / Houston Gardens", "East Houston", "Settegast", "Northside Village",
    "Kashmere Gardens", "El Dorado / Oates Prairie", "Hunterwood", "Greater Fifth Ward",
    "Denver Harbor / Port Houston", "Pleasantville Area", "Northshore",
    "Clinton Park / Tri-Community", "Fourth Ward", "Downtown", "Midtown",
    "Second Ward", "Greater Eastwood", "Harrisburg / Manchester",
    "Museum Park (formerly Binz)", "Greater Third Ward", "Greater OST / South Union",
    "Gulfgate Riverview / Pine Valley", "Pecan Park", "Sunnyside", "South Park",
    "Golfcrest / Bellfort / Reveille", "Park Place", "Meadowbrook / Allendale",
    "South Acres / Crestmont Park", "Minnetex", "Greater Hobby Area", "Edgebrook",
    "South Belt / Ellington", "Clear Lake", "Magnolia Park", "MacGregor",
    "Spring Branch North", "Spring Branch Central", "Spring Branch East",
    "Greenway / Upper Kirby", "Lawndale / Wayside",
]

COMMUNITIES = {
    "chicago": CHICAGO_COMMUNITIES,
    "houston": HOUSTON_COMMUNITIES,
}

# ---------------------------------------------------------------------------
# City metadata used in prompts
# ---------------------------------------------------------------------------

CITY_META = {
    "chicago": {
        "num_communities": "seventy-seven",
        "num_policies": 27,
        "policy_index_range": "0 to 26",
        "agency": "Chicago Metropolitan Agency for Planning (CMAP)",
        "baseline": {
            "fare": 1.25,
            "tax_pct": 1.0,
            "driver_fee": 0.00,
            "car_time_min": 21,
            "transit_time_min": 58.8,
            "car_cost": 5.43,
            "transit_cost": 1.25,
        },
    },
    "houston": {
        "num_communities": "eighty-eight",
        "num_policies": 27,
        "policy_index_range": "0 to 26",
        "agency": "Houston city planning agency",
        "baseline": {
            "fare": 1.25,
            "tax_pct": 1.0,
            "driver_fee": 0.00,
            "car_time_min": 25,
            "transit_time_min": 60.77,
            "car_cost": 7.19,
            "transit_cost": 1.25,
        },
    },
}

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

# ---- Ranked voting (per-community, top-5 ranked) --------------------------

SYSTEM_PROMPT_RANKED = {
    "chicago": """\
You are a representative from one of the seventy-seven communities in the City of Chicago. \
On behalf your community, you will be participating in a referendum in which representatives \
from all communities vote on a set of transportation policy proposals. You are allowed to \
choose up to five proposals and submit your vote as a ranked list of proposals. Remember \
you must act in the best interests of your community.
Think step by step and submit the top five policy proposals in a descending order of preference. \
Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<summary of the disposable income of the community area>",
    "discretionary_consumption": "<summary of the discretionary consumption of the community area>",
    "accessibility": "<summary of the accessibility to resources and services by different modes of transportation in the community area>",
    "decision_rationale": "<rationale of the ranked voting decision, showing factors that influence the tradeoffs and ranking rationale, think step by step>"
  }},
  "vote": [<rank1>, <rank2>, <rank3>, <rank4>, <rank5>]
}}
* The vote list must contain 5 distinct integers from 0 to 26.
* No additional keys, no Markdown, no code fences.\
""",
    "houston": """\
You are a representative from one of the eighty-eight super neighborhoods in Houston. \
On behalf your community, you will be participating in a referendum in which representatives \
from all neighborhoods vote on a set of transportation policy proposals. You are allowed to \
choose up to five proposals and submit your vote as a ranked list of proposals. Remember \
you must act in the best interests of your neighborhood.
Think step by step and submit the top five policy proposals in a descending order of preference. \
Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<one-sentence summary of the disposable income of the super neighborhood>",
    "discretionary_consumption": "<one-sentence summary of the discretionary consumption of the super neighborhood>",
    "accessibility": "<one-sentence summary of the accessibility to resources and services by different modes of transportation in the super neighborhood>",
    "decision_rationale": "<rationale of the ranked voting decision, showing factors that influence the tradeoffs and ranking rationale, think step by step>"
  }},
  "vote": [<rank1>, <rank2>, <rank3>, <rank4>, <rank5>]
}}
* The vote list must contain 5 distinct integers from 0 to 26.
* No additional keys, no Markdown, no code fences.\
""",
}

# ---- Approval voting (per-community, approve up to 5, no ranking) ---------

SYSTEM_PROMPT_APPROVAL = {
    "chicago": """\
You are a representative from one of the seventy-seven communities in the City of Chicago. \
On behalf your community, you will be participating in a referendum in which representatives \
from all communities vote on a set of transportation policy proposals. You are allowed to \
choose up to five proposals without specific rank. Remember you must act in the best \
interests of your community.
Think step by step and submit the indexes of the five approved policy proposals among the \
27 policy proposals which fit the community area's interest. Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<short summary of the disposable income of the community area>",
    "discretionary_consumption": "<short summary of the discretionary consumption of the community area>",
    "accessibility": "<short summary of the accessibility to resources and services by different modes of transportation in the community area>",
    "decision_rationale": "<rationale of the approval voting decision, showing factors that influence the tradeoffs, think step by step>"
  }},
  "vote": [<policy_index1>, <policy_index2>, ..., <policy_index5>]
}}
* Each item in vote must be a distinct integer from 0 to 26, no rank is required.
* No additional keys, no Markdown, no code fences.\
""",
    "houston": """\
You are a representative from one of the eighty-eight super neighborhoods in Houston. \
On behalf your community, you will be participating in a referendum in which representatives \
from all neighborhoods vote on a set of transportation policy proposals. You are allowed to \
choose up to five proposals without specific rank. Remember you must act in the best \
interests of your neighborhood.
Think step by step and submit the indexes of the five approved policy proposals among the \
27 policy proposals which fit the neighborhood's interest. Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<one-sentence summary of the disposable income of the super neighborhood>",
    "discretionary_consumption": "<one-sentence summary of the discretionary consumption of the super neighborhood>",
    "accessibility": "<one-sentence summary of the accessibility to resources and services by different modes of transportation in the super neighborhood>",
    "decision_rationale": "<rationale of the approval voting decision, think step by step>"
  }},
  "vote": [<policy_index1>, <policy_index2>, ..., <policy_index5>]
}}
* Each item in vote must be a distinct integer from 0 to 26, no rank is required.
* No additional keys, no Markdown, no code fences.\
""",
}

# ---- All-approval voting (per-community, approve any number, no ranking) ---

SYSTEM_PROMPT_APPROVAL_ALL = {
    "chicago": """\
You are a representative from one of the seventy-seven communities in the City of Chicago. \
On behalf your community, you will be participating in a referendum in which representatives \
from all communities vote on a set of transportation policy proposals. You should vote for \
all policy proposals you genuinely approve of — there is no limit on how many you may select. \
Remember you must act in the best interests of your community.
Think step by step and submit the indexes of all approved policy proposals among the \
27 policy proposals which fit the community area's interest. Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<short summary of the disposable income of the community area>",
    "discretionary_consumption": "<short summary of the discretionary consumption of the community area>",
    "accessibility": "<short summary of the accessibility to resources and services by different modes of transportation in the community area>",
    "decision_rationale": "<rationale of the approval voting decision, showing factors that influence the tradeoffs, think step by step>"
  }},
  "vote": [<policy_index1>, <policy_index2>, ...]
}}
* Each item in vote must be a distinct integer from 0 to 26, no rank is required.
* Approve as many or as few policies as genuinely fit the community's interest.
* No additional keys, no Markdown, no code fences.\
""",
    "houston": """\
You are a representative from one of the eighty-eight super neighborhoods in Houston. \
On behalf your community, you will be participating in a referendum in which representatives \
from all neighborhoods vote on a set of transportation policy proposals. You should vote for \
all policy proposals you genuinely approve of — there is no limit on how many you may select. \
Remember you must act in the best interests of your neighborhood.
Think step by step and submit the indexes of all approved policy proposals among the \
27 policy proposals which fit the neighborhood's interest. Return a JSON object:
{{
  "community_area": "<name>",
  "thinking": {{
    "disposable_income": "<one-sentence summary of the disposable income of the super neighborhood>",
    "discretionary_consumption": "<one-sentence summary of the discretionary consumption of the super neighborhood>",
    "accessibility": "<one-sentence summary of the accessibility to resources and services by different modes of transportation in the super neighborhood>",
    "decision_rationale": "<rationale of the approval voting decision, think step by step>"
  }},
  "vote": [<policy_index1>, <policy_index2>, ...]
}}
* Each item in vote must be a distinct integer from 0 to 26, no rank is required.
* Approve as many or as few policies as genuinely fit the neighborhood's interest.
* No additional keys, no Markdown, no code fences.\
""",
}

# ---- Average citizen (single agent, ranked) --------------------------------

SYSTEM_PROMPT_AVERAGE = {
    "chicago": """\
You are a representative of the City of Chicago. You will be participating in a referendum \
in which you vote on a set of transportation policy proposals on behalf of an average Chicago \
resident. You are allowed to choose up to five proposals and submit your vote as a ranked list.
Think step by step and submit the top five policy proposals in a descending order of preference. \
Return a JSON object:
{{
  "community_area": "Chicago (average resident)",
  "thinking": {{
    "disposable_income": "<summary of the disposable income of the average Chicago resident>",
    "discretionary_consumption": "<summary of the discretionary consumption of the average Chicago resident>",
    "accessibility": "<summary of the accessibility to resources and services by different modes of transportation>",
    "decision_rationale": "<rationale of the ranked voting decision, think step by step>"
  }},
  "vote": [<rank1>, <rank2>, <rank3>, <rank4>, <rank5>]
}}
* The vote list must contain 5 distinct integers from 0 to 26.
* No additional keys, no Markdown, no code fences.\
""",
    "houston": """\
You are a representative of the City of Houston. You will be participating in a referendum \
in which you vote on a set of transportation policy proposals on behalf of an average Houston \
resident. You are allowed to choose up to five proposals and submit your vote as a ranked list.
Think step by step and submit the top five policy proposals in a descending order of preference. \
Return a JSON object:
{{
  "community_area": "Houston (average resident)",
  "thinking": {{
    "disposable_income": "<summary of the disposable income of the average Houston resident>",
    "discretionary_consumption": "<summary of the discretionary consumption of the average Houston resident>",
    "accessibility": "<summary of the accessibility to resources and services by different modes of transportation>",
    "decision_rationale": "<rationale of the ranked voting decision, think step by step>"
  }},
  "vote": [<rank1>, <rank2>, <rank3>, <rank4>, <rank5>]
}}
* The vote list must contain 5 distinct integers from 0 to 26.
* No additional keys, no Markdown, no code fences.\
""",
}

USER_PROMPT_TEMPLATE = """\
In the referendum, residents from all {num_communities} communities will vote on {num_policies} \
transportation policy proposals.
A policy proposal consists of three components: (i) transit fare policy, which may set a \
per-trip fare for riding transit to either $0.75, $1.25, or $1.75; (ii) tax policy, which \
may set a dedicated sales tax rate to either 0.5%, 1%, or 1.5%; and (iii) a driver-fee \
policy, which may set a per-trip fee for driving to either $0.00, $0.50, or $1.00.

You must pick the top five proposals and rank them from 1 to 5 according to how they serve \
your interest. Your interest should be defined by weighing the cost and benefits of each package.

The {agency} has estimated the travel times per trip by transit and driving corresponding to \
each policy, along with the corresponding fare and fees. You should also be aware that paying \
either fare for transit or a fee for driving will take a portion of your income away from \
other consumption (such as food, housing, clothing, vacation, tuition, etc.).

Background information:
1. The dedicated sales tax supports transit services. A higher tax means more transit funding, \
but also less disposable income. For example, a 1% tax on $20,000 annual spending costs $200/year.
2. Fare and driver fee revenues fund transit. Higher rates generally mean better service, \
but reduce spending power.
3. Driver fees and improved transit may shift drivers to transit, reducing congestion and emissions.

Current baseline policy:
  Transit fare: ${baseline_fare}/ride | Sales tax: {baseline_tax}% | Driving fee: ${baseline_fee}/trip
  Car travel: {baseline_car_time} min (${baseline_car_cost}/trip) | \
Transit: {baseline_transit_time} min (${baseline_transit_cost}/trip)

Candidate policy options (estimated by {agency}):
{policy_options}

Evaluate these {num_policies} policy combinations for the {community} {community_label}.
Consider:
  1. The disposable income of {community}
  2. The discretionary consumption of {community}
  3. The accessibility to resources and services by different modes of transportation in {community}

Return your top 5 ranked policies ({policy_index_range}) and reasoning as a JSON object.\
"""

AVERAGE_PROMPT_TEMPLATE = """\
In the referendum, you represent the average resident of {city_name} and will vote on \
{num_policies} transportation policy proposals.
A policy proposal consists of three components: (i) transit fare policy, which may set a \
per-trip fare for riding transit to either $0.75, $1.25, or $1.75; (ii) tax policy, which \
may set a dedicated sales tax rate to either 0.5%, 1%, or 1.5%; and (iii) a driver-fee \
policy, which may set a per-trip fee for driving to either $0.00, $0.50, or $1.00.

You must pick the top five proposals and rank them from 1 to 5 according to how they serve \
the interest of the average {city_name} resident.

Background information:
1. The dedicated sales tax supports transit services. A higher tax means more transit funding, \
but also less disposable income.
2. Fare and driver fee revenues fund transit. Higher rates generally mean better service, \
but reduce spending power.
3. Driver fees and improved transit may shift drivers to transit, reducing congestion and emissions.

Current baseline policy:
  Transit fare: ${baseline_fare}/ride | Sales tax: {baseline_tax}% | Driving fee: ${baseline_fee}/trip
  Car travel: {baseline_car_time} min (${baseline_car_cost}/trip) | \
Transit: {baseline_transit_time} min (${baseline_transit_cost}/trip)

Candidate policy options (estimated by {agency}):
{policy_options}

Evaluate these {num_policies} policy combinations for an average resident of {city_name}.
Consider:
  1. The disposable income of the average {city_name} resident
  2. The discretionary consumption of the average {city_name} resident
  3. The accessibility to resources and services by different modes of transportation in {city_name}

Return your top 5 ranked policies ({policy_index_range}) and reasoning as a JSON object.\
"""
