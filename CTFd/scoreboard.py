from flask import Blueprint, render_template

from CTFd.utils import config
from CTFd.utils.config.visibility import scores_visible
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers import get_infos
from CTFd.utils.scores import get_standings
from CTFd.utils.user import is_admin

scoreboard = Blueprint("scoreboard", __name__)


@scoreboard.route("/scoreboard")
@check_account_visibility
@check_score_visibility
def listing():
    infos = get_infos()

    if config.is_scoreboard_frozen():
        infos.append("스코어 보드가 현재 비활성화 되었습니다.")

    if is_admin() is True and scores_visible() is False:
        infos.append("스코어 보드를 현재 관리자가 확인중입니다")

    standings = get_standings()
    return render_template("scoreboard.html", standings=standings, infos=infos)
