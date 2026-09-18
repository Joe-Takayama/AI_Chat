from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views import View

from .forms import SignUpForm, LoginForm

# 新規登録ビュー
class SignUpView(View):

    def get(self, request):

        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()
            login(request, user)

            return redirect('AIapp:index')
        return render(request, 'accounts/signup.html', {'form': form})


# ログインビュー
class LoginView(View):

    def get(self, request):

        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):

        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']

            password = form.cleaned_data['password']

            user_data = User.objects.filter(email__iexact=email).first()

            if user_data is not None:

                form.add_error(None, 'メールアドレスまたは正しくありません。')

            else:
                user = authenticate(request, username=user_data.username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('accounts:index')

                else:
                    form.add_error(None, 'メールアドレスまたは正しくありません。')

        return render(request, 'accounts/login.html', {'form': form})


class LogOutView(View):

    def get(self, request):
        logout(request)

        return render('accounts:login')        
