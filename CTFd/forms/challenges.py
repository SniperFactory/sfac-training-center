from wtforms import MultipleFileField, SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class ChallengeSearchForm(BaseForm):
    field = SelectField(
        "검색",
        choices=[
            ("name", "이름"),
            ("id", "ID"),
            ("category", "카테고리"),
            ("type", "유형"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("파라미터", validators=[InputRequired()])
    submit = SubmitField("찾기")


class ChallengeFilesUploadForm(BaseForm):
    file = MultipleFileField(
        "파일업로드",
        description="컨트롤+클릭 또는 Cmd+클릭을 사용하여 여러 파일을 첨부합니다.",
        validators=[InputRequired()],
    )
    submit = SubmitField("업로드")
