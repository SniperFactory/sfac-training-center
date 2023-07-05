from flask_babel import lazy_gettext as _l
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import TeamFieldEntries, TeamFields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST
from CTFd.utils.user import get_current_team


def build_custom_team_fields(
    form_cls,
    include_entries=False,
    fields_kwargs=None,
    field_entries_kwargs=None,
    blacklisted_items=("affiliation", "website"),
):
    if fields_kwargs is None:
        fields_kwargs = {}
    if field_entries_kwargs is None:
        field_entries_kwargs = {}

    fields = []
    new_fields = TeamFields.query.filter_by(**fields_kwargs).all()
    user_fields = {}

    # Only include preexisting values if asked
    if include_entries is True:
        for f in TeamFieldEntries.query.filter_by(**field_entries_kwargs).all():
            user_fields[f.field_id] = f.value

    for field in new_fields:
        if field.name.lower() in blacklisted_items:
            continue

        form_field = getattr(form_cls, f"fields[{field.id}]")

        # Add the field_type to the field so we know how to render it
        form_field.field_type = field.field_type

        # Only include preexisting values if asked
        if include_entries is True:
            initial = user_fields.get(field.id, "")
            form_field.data = initial
            if form_field.render_kw:
                form_field.render_kw["data-initial"] = initial
            else:
                form_field.render_kw = {"data-initial": initial}

        fields.append(form_field)
    return fields


def attach_custom_team_fields(form_cls, **kwargs):
    new_fields = TeamFields.query.filter_by(**kwargs).all()
    for field in new_fields:
        validators = []
        if field.required:
            validators.append(InputRequired())

        if field.field_type == "text":
            input_field = StringField(
                field.name, description=field.description, validators=validators
            )
        elif field.field_type == "boolean":
            input_field = BooleanField(
                field.name, description=field.description, validators=validators
            )

        setattr(form_cls, f"fields[{field.id}]", input_field)


class TeamJoinForm(BaseForm):
    name = StringField(_l("Team Name"), validators=[InputRequired()])
    password = PasswordField(_l("Team Password"), validators=[InputRequired()])
    submit = SubmitField(_l("Join"))


def TeamRegisterForm(*args, **kwargs):
    class _TeamRegisterForm(BaseForm):
        name = StringField(_l("Team Name"), validators=[InputRequired()])
        password = PasswordField(_l("Team Password"), validators=[InputRequired()])
        submit = SubmitField(_l("Create"))

        @property
        def extra(self):
            return build_custom_team_fields(
                self, include_entries=False, blacklisted_items=()
            )

    attach_custom_team_fields(_TeamRegisterForm)
    return _TeamRegisterForm(*args, **kwargs)


def TeamSettingsForm(*args, **kwargs):
    class _TeamSettingsForm(BaseForm):
        name = StringField(
            _l("팀 명"),
            description=_l("보여질 팀 명"),
        )
        password = PasswordField(
            _l("팀 새 비밀번호"), description=_l("새 팀 비밀번호를 입력하세요")
        )
        confirm = PasswordField(
            _l("현재 팀 비밀번호"),
            description=_l(
                "팀 비밀번호를 변경하려면 현재 팀 비밀번호를 입력하세요"
            ),
        )
        affiliation = StringField(
            _l("소속"),
            description=_l(
                "다른 참가자에게 공개되는 팀 소속"
            ),
        )
        website = URLField(
            _l("웹사이트"),
            description=_l("다른 참가자에게 공개되는 팀 웹사이트"),
        )
        country = SelectField(
            _l("국가"),
            choices=SELECT_COUNTRIES_LIST,
            description=_l("다른 참가자에게 공개되는 팀 국가"),
        )
        submit = SubmitField(_l("Submit"))

        @property
        def extra(self):
            fields_kwargs = _TeamSettingsForm.get_field_kwargs()
            return build_custom_team_fields(
                self,
                include_entries=True,
                fields_kwargs=fields_kwargs,
                field_entries_kwargs={"team_id": self.obj.id},
            )

        def get_field_kwargs():
            team = get_current_team()
            field_kwargs = {"editable": True}
            if team.filled_all_required_fields is False:
                # Show all fields
                field_kwargs = {}
            return field_kwargs

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    field_kwargs = _TeamSettingsForm.get_field_kwargs()
    attach_custom_team_fields(_TeamSettingsForm, **field_kwargs)

    return _TeamSettingsForm(*args, **kwargs)


class TeamCaptainForm(BaseForm):
    # Choices are populated dynamically at form creation time
    captain_id = SelectField(
        _l("팀장"), choices=[], validators=[InputRequired()]
    )
    submit = SubmitField("제출")


class TeamSearchForm(BaseForm):
    field = SelectField(
        "검색",
        choices=[
            ("name", "이름"),
            ("id", "ID"),
            ("affiliation", "소속"),
            ("website", "웹사이트"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("파라미터", validators=[InputRequired()])
    submit = SubmitField("검색")


class PublicTeamSearchForm(BaseForm):
    field = SelectField(
        _l("검색"),
        choices=[
            ("name", _l("이름")),
            ("affiliation", _l("소속")),
            ("website", _l("웹사이트")),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField(_l("파라미터"), validators=[InputRequired()])
    submit = SubmitField(_l("검색"))


class TeamBaseForm(BaseForm):
    name = StringField(_l("Team Name"), validators=[InputRequired()])
    email = EmailField(_l("Email"))
    password = PasswordField(_l("Password"))
    website = URLField(_l("Website"))
    affiliation = StringField(_l("Affiliation"))
    country = SelectField(_l("Country"), choices=SELECT_COUNTRIES_LIST)
    hidden = BooleanField(_l("Hidden"))
    banned = BooleanField(_l("Banned"))
    submit = SubmitField(_l("Submit"))


def TeamCreateForm(*args, **kwargs):
    class _TeamCreateForm(TeamBaseForm):
        pass

        @property
        def extra(self):
            return build_custom_team_fields(self, include_entries=False)

    attach_custom_team_fields(_TeamCreateForm)

    return _TeamCreateForm(*args, **kwargs)


def TeamEditForm(*args, **kwargs):
    class _TeamEditForm(TeamBaseForm):
        pass

        @property
        def extra(self):
            return build_custom_team_fields(
                self,
                include_entries=True,
                fields_kwargs=None,
                field_entries_kwargs={"team_id": self.obj.id},
            )

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    attach_custom_team_fields(_TeamEditForm)

    return _TeamEditForm(*args, **kwargs)


class TeamInviteForm(BaseForm):
    link = URLField(_l("Invite Link"))


class TeamInviteJoinForm(BaseForm):
    submit = SubmitField(_l("Join"))
