#!/usr/bin/env python3
"""Google Business Profile Review Rating Goal Calculator.

Calculates the exact number of 5-star reviews required to reach higher
displayed star ratings on Google Maps and Google Search.

Google display rule:
Google displays average ratings rounded to one decimal place, rounding the
.x5 boundary DOWN (e.g. 4.75 -> 4.7, 4.76 -> 4.8). To display target rating T,
the true average only needs to cross the lower threshold (T - 0.05).

Formula:
    threshold = T - 0.05
    needed = floor((threshold * n - sum) / (5.0 - threshold)) + 1
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional


def calculate_rating_goals(
    current_rating: float,
    review_count: int,
    target_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate 5-star reviews needed to reach milestone display thresholds."""
    if review_count <= 0:
        raise ValueError("Review count must be greater than zero.")
    if current_rating < 1.0 or current_rating > 5.0:
        raise ValueError("Current rating must be between 1.0 and 5.0.")

    n = review_count
    total_sum = current_rating * n

    # Google displays average rounded to one decimal, rounding .x5 down.
    displayed_tenths = math.ceil(round(current_rating * 1000) / 100 - 0.5)
    displayed_rating = displayed_tenths / 10.0

    milestones: List[Dict[str, Any]] = []

    if target_rating is not None:
        targets_tenths = [int(round(target_rating * 10))]
    else:
        targets_tenths = list(range(displayed_tenths + 1, 51))

    for t in targets_tenths:
        target = t / 10.0
        if target > 5.0 or target <= displayed_rating:
            continue

        threshold = (t - 0.5) / 10.0
        raw = (threshold * n - total_sum) / (5.0 - threshold)
        needed = max(0, math.floor(raw + 1e-9) + 1)
        total_after = n + needed
        projected_avg = (total_sum + 5.0 * needed) / total_after

        if needed <= 10:
            feasibility = "Easy"
        elif needed <= 50:
            feasibility = "Moderate"
        else:
            feasibility = "Challenging"

        milestones.append(
            {
                "target_rating": round(target, 1),
                "threshold": round(threshold, 3),
                "reviews_needed": needed,
                "total_reviews_after": total_after,
                "projected_average": round(projected_avg, 3),
                "feasibility": feasibility,
            }
        )

    return {
        "current_rating": round(current_rating, 2),
        "displayed_rating": round(displayed_rating, 1),
        "review_count": n,
        "is_max_rating": len(milestones) == 0,
        "milestones": milestones,
    }


def format_markdown_table(data: Dict[str, Any]) -> str:
    """Format calculation results into a human-readable markdown table."""
    curr = data["current_rating"]
    disp = data["displayed_rating"]
    count = data["review_count"]

    lines = [
        f"### Google Reviews Rating Goal Plan",
        f"",
        f"- **Current Average:** {curr:.2f}* (Google displays **{disp:.1f}***)",
        f"- **Current Reviews:** {count:,}",
        f"",
    ]

    if data["is_max_rating"]:
        lines.append("Profile already displays **5.0***. No higher threshold to reach.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Target Rating | 5* Reviews Needed | Total Reviews After | Projected Avg | Feasibility |",
            "|:---:|:---:|:---:|:---:|:---:|",
        ]
    )

    for m in data["milestones"]:
        t = m["target_rating"]
        needed = m["reviews_needed"]
        after = m["total_reviews_after"]
        proj = m["projected_average"]
        feas = m["feasibility"]
        lines.append(
            f"| **{t:.1f}*** | **{needed:,}** | {after:,} | {proj:.3f}* | {feas} |"
        )

    lines.append("")
    lines.append(
        "> Note: Calculations assume all new reviews are 5-star ratings and account for Google rounding .x5 downward."
    )
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate 5-star Google reviews needed to reach higher displayed ratings."
    )
    parser.add_argument(
        "--rating",
        type=float,
        required=True,
        help="Current average star rating (e.g. 4.6)",
    )
    parser.add_argument(
        "--reviews",
        type=int,
        required=True,
        help="Current total number of reviews (e.g. 82)",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=None,
        help="Optional specific target rating (e.g. 4.8)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of markdown",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        results = calculate_rating_goals(
            current_rating=args.rating,
            review_count=args.reviews,
            target_rating=args.target,
        )
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown_table(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
