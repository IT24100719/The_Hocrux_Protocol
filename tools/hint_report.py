#!/usr/bin/env python3
"""Hint-usage report for grading.

Every hint unlock (now including HX-01, since its hints are costed) is recorded
in CTFd's `unlocks` table. This prints, per player, how many hints they opened,
how many points that cost them, and on which stages — plus an optional per-hint
breakdown. Reads straight from the database via `docker compose exec db psql`,
so it needs no admin token.

    python tools/hint_report.py            # one row per player
    python tools/hint_report.py --detail   # one row per hint unlocked
"""
import subprocess
import sys

SUMMARY = """
SELECT u.name AS player,
       CASE WHEN u.hidden THEN 'yes' ELSE '' END AS hidden,
       count(un.id)                         AS hints_used,
       coalesce(sum(h.cost), 0)             AS points_spent,
       coalesce(string_agg(DISTINCT 'HX-0' || h.challenge_id, ', '
                           ORDER BY 'HX-0' || h.challenge_id), '-') AS stages_hinted
FROM users u
LEFT JOIN unlocks un ON un.user_id = u.id AND un.type = 'hints'
LEFT JOIN hints  h  ON h.id = un.target
WHERE u.type = 'user'
GROUP BY u.name, u.hidden
ORDER BY hints_used DESC, u.name;
"""

DETAIL = """
SELECT u.name AS player,
       'HX-0' || h.challenge_id AS stage,
       h.cost,
       un.date
FROM unlocks un
JOIN users u ON u.id = un.user_id
JOIN hints h ON h.id = un.target
WHERE un.type = 'hints'
ORDER BY u.name, un.date;
"""


def main():
    query = DETAIL if "--detail" in sys.argv[1:] else SUMMARY
    cmd = ["docker", "compose", "exec", "-T", "db",
           "psql", "-U", "ctfd", "-d", "ctfd", "-c", query]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("docker not found — run this from the repo root with the stack up.")
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit("psql query failed (is the stack up? is the db user 'ctfd'?)")
    print("Hint usage" + (" (per hint)" if "--detail" in sys.argv[1:] else " (per player)"))
    print(r.stdout)


if __name__ == "__main__":
    main()
