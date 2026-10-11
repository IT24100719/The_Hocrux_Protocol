#!/usr/bin/env python3
"""Finale capstone-quiz report for grading.

The quiz is never scored to the player — only the pass/fail ending is shown. The
horcrux_finale plugin records each attempt server-side; this prints, per player,
their first-try score, best score, number of attempts, and whether they ever
passed. Reads the database via `docker compose exec db psql`, no token needed.

    python tools/finale_report.py
"""
import subprocess
import sys

QUERY = """
SELECT u.name AS player,
       f.attempts,
       f.first_correct || '/' || f.total AS first_try,
       f.best_correct  || '/' || f.total AS best,
       CASE WHEN f.ever_passed THEN 'PASS' ELSE 'fail' END AS result,
       f.last_date
FROM horcrux_finale f
JOIN users u ON u.id = f.user_id
WHERE u.type = 'user'
ORDER BY f.ever_passed DESC, f.best_correct DESC, u.name;
"""


def main():
    cmd = ["docker", "compose", "exec", "-T", "db",
           "psql", "-U", "ctfd", "-d", "ctfd", "-c", QUERY]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("docker not found — run this from the repo root with the stack up.")
    if r.returncode != 0:
        # most common cause: nobody has reached the finale yet (table empty is fine,
        # but a missing table means the plugin image hasn't been rebuilt)
        sys.stderr.write(r.stderr)
        sys.exit("query failed — is the stack up and the horcrux_finale plugin loaded?")
    print("Finale capstone-quiz results (per player)")
    print(r.stdout)


if __name__ == "__main__":
    main()
