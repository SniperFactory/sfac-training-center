from flask_babel import lazy_gettext as _l
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.forms.users import (
    attach_custom_user_fields,
    attach_registration_code_field,
    build_custom_user_fields,
    build_registration_code_field,
)


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField(
            _l("닉네임"), validators=[InputRequired()], render_kw={"autofocus": True}
        )
        email = EmailField(_l("이메일"), validators=[InputRequired()])
        password = PasswordField(_l("패스워드"), validators=[InputRequired()])
        submit = SubmitField(_l("생성"))

        @property
        def extra(self):
            return build_custom_user_fields(
                self, include_entries=False, blacklisted_items=()
            ) + build_registration_code_field(self)

    attach_custom_user_fields(_RegistrationForm)
    attach_registration_code_field(_RegistrationForm)

    return _RegistrationForm(*args, **kwargs)


class LoginForm(BaseForm):
    name = StringField(
        _l("유저네임 혹은 이메일"),
        validators=[InputRequired()],
        render_kw={"autofocus": True},
    )
    password = PasswordField(_l("패스워드"), validators=[InputRequired()])
    submit = SubmitField(_l("로그인"))


class ConfirmForm(BaseForm):
    submit = SubmitField(_l("재전송되었습니다."))


class ResetPasswordRequestForm(BaseForm):
    email = EmailField(
        _l("Email"), validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_l("제출"))


class ResetPasswordForm(BaseForm):
    password = PasswordField(
        _l("Password"), validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_l("제출"))
