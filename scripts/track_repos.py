#!/usr/bin/env python3
"""Fetch current stats for a list of GitHub repos and append a timestamped
snapshot to a CSV file per repo. Meant to run on a schedule (see
.github/workflows/track.yml) so the data/ folder builds a real time series.
"""

import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPOS_FILE = Path("repos.txt")
DATA_DIR = Path("data")
API_URL = "https://api.github.com/repos/{full_name}"


def load_repos():
    if not REPOS_FILE.exists():
        sys.exit(f"Missing {REPOS_FILE}")
    repos = []
    for line in REPOS_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            repos.append(line)
    return repos


def fetch_stats(full_name, token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(API_URL.format(full_name=full_name), headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        # subscribers_count is the real "watch" count; watchers_count is
        # actually just a duplicate of stargazers_count in the GitHub API.
        "watchers": data["subscribers_count"],
    }


def append_row(full_name, row):
    DATA_DIR.mkdir(exist_ok=True)
    csv_path = DATA_DIR / f"{full_name.replace('/', '__')}.csv"
    is_new = not csv_path.exists()
    with csv_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    repos = load_repos()
    if not repos:
        sys.exit("repos.txt has no repos listed")

    failures = 0
    for full_name in repos:
        try:
            row = fetch_stats(full_name, token)
        except requests.RequestException as e:
            print(f"Failed to fetch {full_name}: {e}", file=sys.stderr)
            failures += 1
            continue
        append_row(full_name, row)
        print(f"{full_name}: {row}")

    if failures == len(repos):
        sys.exit("All repo fetches failed")


if __name__ == "__main__":
    main()
