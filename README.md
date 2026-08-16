# Repo Pulse

A scheduled data collector that snapshots GitHub repo stats (stars, forks, open issues, watchers) four times a day and logs them to CSV, building a real time-series dataset with zero manual effort.

## Overview

Point it at any list of public repos and it checks in on them every 6 hours, appending one row per repo per run to `data/<owner>__<repo>.csv`. Over weeks and months this turns into a genuine dataset you can chart, analyze, or feed into a forecasting model — not filler commits, actual observed data.

Pick repos with enough real activity (large, popular, frequently-starred projects) and there's almost always a genuine change to commit at each run — no need to fabricate one.

## How it works

1. A GitHub Actions workflow runs on a cron schedule (00:00, 06:00, 12:00, 18:00 UTC) or on demand.
2. `scripts/track_repos.py` reads the repo list from `repos.txt`, hits the GitHub REST API for each one, and appends a timestamped row to that repo's CSV.
3. The workflow commits and pushes `data/` only if something actually changed, so there are no empty commits.

## Setup

1. Push this repo to your own GitHub account.
2. Edit `repos.txt` — one `owner/repo` per line. Include your own repos if you want to track their growth too.
3. In your repo's **Settings → Actions → General → Workflow permissions**, make sure "Read and write permissions" is selected (needed so the workflow can push commits).
4. That's it — the workflow starts running on its own schedule. You can also trigger a run manually from the **Actions** tab (`workflow_dispatch`).

## Data

Each tracked repo gets its own CSV under `data/`:

```
timestamp,stars,forks,open_issues,watchers
2026-08-16T00:00:00Z,100,10,2,5
2026-08-16T08:00:00Z,101,10,2,5
```

## Technical Architecture

- **Language/runtime:** Python 3.11, `requests` for HTTP
- **Scheduling:** GitHub Actions `schedule` triggers (cron), plus manual `workflow_dispatch`
- **Storage:** flat CSV files, one per repo, append-only
- **Auth:** uses the Actions-provided `GITHUB_TOKEN` automatically — no secrets to configure, and it raises the API rate limit well above what unauthenticated requests get

## Core Engineering Practices

- Idempotent commits: a `git diff --staged --quiet` check means a run with no new data makes no commit
- One repo's fetch failure doesn't block the others; the job only fails if every fetch fails
- Uses `subscribers_count` for "watchers," not the API's misleadingly-named `watchers_count` field (which is actually just star count)
- No hardcoded secrets — token is injected via the Actions runtime

## Author

Rifat — BSc Computer Science, BRAC University
GitHub: [tanvirul-islam-rifat](https://github.com/tanvirul-islam-rifat)
