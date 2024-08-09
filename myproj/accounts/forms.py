from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth.forms import AuthenticationForm


# crispy_forms 라이브러리를 사용해 커스텀 로그인 폼을 정의
class LoginForm(AuthenticationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "password")
    helper.add_input(Submit("submit", "로그인", css_class="w-100"))