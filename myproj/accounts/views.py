from django.shortcuts import render
from django.contrib.auth.views import LoginView
# login
class LoginView(LoginView):
    pass
login = LoginView.as_view()