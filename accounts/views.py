from django.shortcuts import render, redirect

from django.contrib.auth import (
    login,
    authenticate,
    logout,
)

from django.contrib.auth.models import User

from django.contrib.auth.tokens import (
    default_token_generator,
)

from django.contrib.auth.password_validation import (
    validate_password,
)

from django.core.exceptions import ValidationError

from django.core.mail import send_mail

from django.urls import reverse

from django.utils.encoding import (
    force_bytes,
    force_str,
)

from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)

from django.views import View


from .forms import (
    SignUpForm,
    LoginForm,
    PasswordResetForm,
    NewPasswordForm,
)



# ========================================
# 新規登録
# ========================================

class SignUpView(View):

    def get(self, request):

        form = SignUpForm()

        return render(
            request,
            "accounts/signup.html",
            {
                "form": form
            }
        )


    def post(self, request):

        form = SignUpForm(
            request.POST
        )


        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            return redirect(
                "AIapp:index"
            )


        return render(
            request,
            "accounts/signup.html",
            {
                "form": form
            }
        )



# ========================================
# ログイン
# ========================================

class LoginView(View):

    def get(self, request):

        form = LoginForm()

        return render(
            request,
            "accounts/login.html",
            {
                "form": form
            }
        )


    def post(self, request):

        form = LoginForm(
            request.POST
        )


        if form.is_valid():

            email = form.cleaned_data[
                "email"
            ]

            password = form.cleaned_data[
                "password"
            ]


            user_data = User.objects.filter(
                email__iexact=email
            ).first()


            if user_data is None:

                form.add_error(
                    None,
                    "メールアドレスまたはパスワードが正しくありません。"
                )


            else:

                user = authenticate(
                    request,
                    username=user_data.username,
                    password=password
                )


                if user is not None:

                    login(
                        request,
                        user
                    )

                    return redirect(
                        "AIapp:index"
                    )


                form.add_error(
                    None,
                    "メールアドレスまたはパスワードが正しくありません。"
                )


        return render(
            request,
            "accounts/login.html",
            {
                "form": form
            }
        )



# ========================================
# ログアウト
# ========================================

class LogOutView(View):

    def post(self, request):

        logout(request)

        return redirect(
            "AIapp:index"
        )



# ========================================
# パスワード再設定
# メールアドレス入力画面
# ========================================

class PasswordResetView(View):

    def get(self, request):

        form = PasswordResetForm()

        return render(
            request,
            "accounts/password_reset.html",
            {
                "form": form
            }
        )


    def post(self, request):

        form = PasswordResetForm(
            request.POST
        )


        if form.is_valid():

            email = form.cleaned_data[
                "email"
            ]


            # ==================================
            # メールアドレスからユーザー検索
            # ==================================

            user = User.objects.filter(
                email__iexact=email
            ).first()


            # ==================================
            # ユーザーが存在する場合だけ
            # メールを作成
            # ==================================

            if user is not None:

                # ユーザーIDをURL用文字列に変換
                uid = urlsafe_base64_encode(
                    force_bytes(
                        user.pk
                    )
                )


                # 一時的な再設定トークンを作成
                token = (
                    default_token_generator
                    .make_token(user)
                )


                # URLを作る
                reset_path = reverse(
                    "accounts:password_reset_confirm",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    }
                )


                # 完全なURLにする
                reset_url = (
                    request.build_absolute_uri(
                        reset_path
                    )
                )


                # ==================================
                # メール本文
                # ==================================

                subject = (
                    "ChatBoy パスワード再設定"
                )


                message = f"""
                    ChatBoyのパスワード再設定を受け付けました。

                    以下のURLから新しいパスワードを設定してください。

                    {reset_url}

                    このメールに心当たりがない場合は、
                    このメールを無視してください。

                    ChatBoy
                """


                # ==================================
                # メール送信
                # ==================================

                send_mail(
                    subject,
                    message,
                    None,
                    [user.email],
                )


            # ==================================
            # ユーザーが存在しなくても
            # 同じ完了画面へ
            # ==================================

            return redirect(
                "accounts:password_reset_done"
            )


        return render(
            request,
            "accounts/password_reset.html",
            {
                "form": form
            }
        )



# ========================================
# メール送信完了
# ========================================

class PasswordResetDoneView(View):

    def get(self, request):

        return render(
            request,
            "accounts/password_reset_done.html"
        )



# ========================================
# 新しいパスワード設定
# ========================================

class PasswordResetConfirmView(View):

    def get(
        self,
        request,
        uidb64,
        token
    ):

        user = self.get_user(
            uidb64
        )


        # ==================================
        # URLが正しいか確認
        # ==================================

        if (
            user is not None
            and
            default_token_generator
            .check_token(
                user,
                token
            )
        ):

            validlink = True

            form = NewPasswordForm()


        else:

            validlink = False

            form = None


        return render(
            request,
            "accounts/password_reset_confirm.html",
            {
                "form": form,
                "validlink": validlink,
            }
        )



    def post(
        self,
        request,
        uidb64,
        token
    ):

        user = self.get_user(
            uidb64
        )


        # URLが無効
        if (
            user is None
            or
            not default_token_generator
            .check_token(
                user,
                token
            )
        ):

            return render(
                request,
                "accounts/password_reset_confirm.html",
                {
                    "form": None,
                    "validlink": False,
                }
            )


        form = NewPasswordForm(
            request.POST
        )


        if form.is_valid():

            new_password = (
                form.cleaned_data[
                    "new_password1"
                ]
            )


            # ==================================
            # Djangoのパスワード安全チェック
            # ==================================

            try:

                validate_password(
                    new_password,
                    user=user
                )


            except ValidationError as e:

                for error in e.messages:

                    form.add_error(
                        "new_password1",
                        error
                    )


            else:

                # ==================================
                # 新しいパスワードを設定
                # ==================================

                user.set_password(
                    new_password
                )

                user.save()


                # ログイン画面へ
                return redirect(
                    "accounts:login"
                )


        return render(
            request,
            "accounts/password_reset_confirm.html",
            {
                "form": form,
                "validlink": True,
            }
        )



    # ====================================
    # URLのuidからユーザー取得
    # ====================================

    def get_user(
        self,
        uidb64
    ):

        try:

            uid = force_str(
                urlsafe_base64_decode(
                    uidb64
                )
            )


            user = User.objects.get(
                pk=uid
            )


            return user


        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):

            return None