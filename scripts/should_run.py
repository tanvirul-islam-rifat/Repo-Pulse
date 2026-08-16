#!/usr/bin/env python3
"""Decide whether this scheduled run should actually collect data + commit.

Each UTC day gets a random target commit count between 1 and 5, seeded by
the date string. Since every run on the same day derives the same seed, they
all independently compute the same target and the same set of "chosen"
slots out of the day's candidates -- no shared state or coordination needed
between runs.
"""

import os
import random
import sys
from datetime import datetime, timezone

# Must match the cron schedule in track.yml, in the same order.
SLOTS = [
    "0 0 * * *",
    "0 3 * * *",
    "0 6 * * *",
    "0 9 * * *",
    "0 12 * * *",
    "0 15 * * *",
    "0 18 * * *",
    "0 21 * * *",
]

MIN_TARGET = 1
MAX_TARGET = 5


def decide(date_str, schedule):
    if schedule not in SLOTS:
        return True, None, None  # unrecognized trigger (e.g. manual) -> just run

    slot_index = SLOTS.index(schedule)
    rng = random.Random(date_str)
    target = rng.randint(MIN_TARGET, MAX_TARGET)
    selected = set(rng.sample(range(len(SLOTS)), target))
    return slot_index in selected, target, sorted(selected)


def main():
    schedule = os.environ.get("CRON_SCHEDULE", "").strip()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not schedule:
        print("Manual trigger (workflow_dispatch) - running", file=sys.stderr)
        print("run=true")
        return

    chosen, target, selected = decide(date_str, schedule)
    print(
        f"date={date_str} schedule='{schedule}' target={target} "
        f"selected_slots={selected} chosen={chosen}",
        file=sys.stderr,
    )
    print(f"run={'true' if chosen else 'false'}")


if __name__ == "__main__":
    main()
