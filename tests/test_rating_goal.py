"""Tests for Google Business Profile review rating goal calculator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rating_goal.py"
sys.path.insert(0, str(ROOT / "scripts"))

from rating_goal import calculate_rating_goals


def test_known_calculation_milestones():
    # Test case: 4.6 star average with 82 reviews
    result = calculate_rating_goals(current_rating=4.6, review_count=82)

    assert result["current_rating"] == 4.6
    assert result["displayed_rating"] == 4.6
    assert result["review_count"] == 82
    assert not result["is_max_rating"]

    milestones = {m["target_rating"]: m for m in result["milestones"]}

    # Target 4.7 requires 12 5-star reviews
    assert milestones[4.7]["reviews_needed"] == 12
    assert milestones[4.7]["total_reviews_after"] == 94
    assert milestones[4.7]["projected_average"] >= 4.65

    # Target 4.8 requires 50 5-star reviews
    assert milestones[4.8]["reviews_needed"] == 50
    assert milestones[4.8]["total_reviews_after"] == 132
    assert milestones[4.8]["projected_average"] >= 4.75

    # Target 4.9 requires 137 5-star reviews
    assert milestones[4.9]["reviews_needed"] == 137
    assert milestones[4.9]["total_reviews_after"] == 219
    assert milestones[4.9]["projected_average"] >= 4.85

    # Target 5.0 requires 575 5-star reviews
    assert milestones[5.0]["reviews_needed"] == 575
    assert milestones[5.0]["total_reviews_after"] == 657
    assert milestones[5.0]["projected_average"] >= 4.95


def test_specific_target_rating():
    result = calculate_rating_goals(current_rating=4.2, review_count=50, target_rating=4.5)
    assert len(result["milestones"]) == 1
    m = result["milestones"][0]
    assert m["target_rating"] == 4.5
    # threshold for 4.5 is 4.45
    # raw = (4.45 * 50 - 210) / (5 - 4.45) = (222.5 - 210) / 0.55 = 12.5 / 0.55 = 22.72 -> 23
    assert m["reviews_needed"] == 23


def test_already_five_stars():
    result = calculate_rating_goals(current_rating=5.0, review_count=20)
    assert result["is_max_rating"] is True
    assert len(result["milestones"]) == 0


def test_invalid_arguments():
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_rating_goals(current_rating=4.5, review_count=0)

    with pytest.raises(ValueError, match="between 1.0 and 5.0"):
        calculate_rating_goals(current_rating=5.5, review_count=10)

    with pytest.raises(ValueError, match="between 1.0 and 5.0"):
        calculate_rating_goals(current_rating=0.8, review_count=10)


def test_cli_execution_json():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--rating", "4.6", "--reviews", "82", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    assert data["current_rating"] == 4.6
    assert data["review_count"] == 82
    assert len(data["milestones"]) == 4


def test_cli_execution_markdown():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--rating", "4.6", "--reviews", "82"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Google Reviews Rating Goal Plan" in proc.stdout
    assert "| Target Rating | 5* Reviews Needed |" in proc.stdout
    assert "4.7*" in proc.stdout
