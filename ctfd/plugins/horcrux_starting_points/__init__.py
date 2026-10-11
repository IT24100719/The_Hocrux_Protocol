"""Horcrux starting-points plugin.

Grants every newly-registered PLAYER a fixed "welcome" award (default 100
points) so that:
  * early paid hints are affordable from a standing start, and
  * HX-01's hints can carry a cost like every other stage (so using them is
    reflected in the score AND logged in the `unlocks` audit table) without
    leaving a brand-new player unable to reach them.

The grant is uniform, so it does not change relative ranking — it only raises
the floor. Hint spending is what differentiates scores.

Amount is read from the HORCRUX_START_POINTS env var (default 100); set it to 0
to disable. Admins never receive the grant. Existing accounts are NOT back-filled
(the award fires on insert only) — grant those once by hand if needed.
"""
import datetime
import os

from sqlalchemy import event

from CTFd.models import Awards, Users


def load(app):
    try:
        grant = int(os.environ.get("HORCRUX_START_POINTS", "100"))
    except (TypeError, ValueError):
        grant = 100
    if grant <= 0:
        app.logger.info("[horcrux] starting-points plugin disabled (grant<=0)")
        return

    @event.listens_for(Users, "after_insert")
    def _grant_starting_points(mapper, connection, user):
        # Players only — never admins.
        if getattr(user, "type", "user") == "admin":
            return
        connection.execute(
            Awards.__table__.insert().values(
                user_id=user.id,
                team_id=getattr(user, "team_id", None),
                type="standard",
                name="Starting balance",
                description="Welcome points so early hints are reachable.",
                value=grant,
                category="welcome",
                date=datetime.datetime.utcnow(),
            )
        )

    app.logger.info("[horcrux] starting-points plugin loaded (grant=%d)" % grant)
