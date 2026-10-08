import os
import base64

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin

from email.message import EmailMessage

from django.conf import settings

from django.shortcuts import (
    render,
    redirect,
)

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


# ========================================
# Gmail API
# ========================================

from google.oauth2.credentials import Credentials

from google.auth.transport.requests import (
    Request,
)

from googleapiclient.discovery import (
    build,
)


from .forms import (
    SignUpForm,
    LoginForm,
    PasswordResetForm,
    NewPasswordForm,
    ProfileForm,
)



# ========================================
# Gmail APIでメールを送信
# ========================================

def send_gmail(
    to_email,
    subject,
    body
):

    # ====================================
    # token.json の場所を決める
    # ====================================

    # Render本番環境
    render_token_path = (
        "/etc/secrets/token.json"
    )


    if os.path.exists(
        render_token_path
    ):

        token_path = (
            render_token_path
        )


    # ローカル環境
    else:

        token_path = (
            settings.BASE_DIR
            / "token.json"
        )


    # ====================================
    # token.json を読み込む
    # ====================================

    creds = (
        Credentials
        .from_authorized_user_file(
            str(token_path),
            [
                "https://www.googleapis.com/auth/gmail.send"
            ]
        )
    )


    # ====================================
    # アクセストークンが
    # 期限切れだった場合
    # ====================================

    if (
        creds.expired
        and
        creds.refresh_token
    ):

        creds.refresh(
            Request()
        )


    # ====================================
    # Gmail APIを使う準備
    # ====================================

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )


    # ====================================
    # メールを作成
    # ====================================

    email_message = EmailMessage()


    # 送信先
    email_message[
        "To"
    ] = to_email


    # 送信元
    email_message[
        "From"
    ] = settings.GMAIL_FROM_EMAIL


    # 件名
    email_message[
        "Subject"
    ] = subject


    # 本文
    email_message.set_content(
        body
    )


    # ====================================
    # Gmail APIで扱える形式に変換
    # ====================================

    encoded_message = (
        base64
        .urlsafe_b64encode(
            email_message.as_bytes()
        )
        .decode()
    )


    # ====================================
    # メール送信
    # ====================================

    service.users().messages().send(
        userId="me",
        body={
            "raw":
                encoded_message
        }
    ).execute()



# ========================================
# 新規登録
# ========================================

class SignUpView(View):

    def get(
        self,
        request
    ):

        form = SignUpForm()


        return render(
            request,
            "accounts/signup.html",
            {
                "form":
                    form
            }
        )



    def post(
        self,
        request
    ):

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
                "form":
                    form
            }
        )



# ========================================
# ログイン
# ========================================

class LoginView(View):

    def get(
        self,
        request
    ):

        form = LoginForm()


        return render(
            request,
            "accounts/login.html",
            {
                "form":
                    form
            }
        )



    def post(
        self,
        request
    ):

        form = LoginForm(
            request.POST
        )


        if form.is_valid():

            email = (
                form.cleaned_data[
                    "email"
                ]
            )


            password = (
                form.cleaned_data[
                    "password"
                ]
            )


            # ====================================
            # メールアドレスからユーザー検索
            # ====================================

            user_data = (
                User.objects
                .filter(
                    email__iexact=email
                )
                .first()
            )


            # ユーザーが存在しない
            if user_data is None:

                form.add_error(
                    None,
                    (
                        "メールアドレスまたは"
                        "パスワードが正しくありません。"
                    )
                )


            else:

                # ====================================
                # パスワード認証
                # ====================================

                user = authenticate(
                    request,
                    username=
                        user_data.username,
                    password=
                        password
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
                    (
                        "メールアドレスまたは"
                        "パスワードが正しくありません。"
                    )
                )


        return render(
            request,
            "accounts/login.html",
            {
                "form":
                    form
            }
        )



# ========================================
# ログアウト
# ========================================

class LogOutView(View):

    def post(
        self,
        request
    ):

        logout(
            request
        )


        return redirect(
            "AIapp:index"
        )



# ========================================
# パスワード再設定
# メールアドレス入力画面
# ========================================

class PasswordResetView(View):

    def get(
        self,
        request
    ):

        form = PasswordResetForm()


        return render(
            request,
            "accounts/password_reset.html",
            {
                "form":
                    form
            }
        )



    def post(
        self,
        request
    ):

        form = PasswordResetForm(
            request.POST
        )


        if form.is_valid():

            email = (
                form.cleaned_data[
                    "email"
                ]
            )


            # ====================================
            # メールアドレスからユーザー検索
            # ====================================

            user = (
                User.objects
                .filter(
                    email__iexact=email
                )
                .first()
            )


            # ====================================
            # ユーザーが存在する場合だけ
            # リセットメールを送信
            # ====================================

            if user is not None:


                # ====================================
                # ユーザーIDをURL用に変換
                # ====================================

                uid = (
                    urlsafe_base64_encode(
                        force_bytes(
                            user.pk
                        )
                    )
                )


                # ====================================
                # 一時的なリセットトークン作成
                # ====================================

                token = (
                    default_token_generator
                    .make_token(
                        user
                    )
                )


                # ====================================
                # パスワード再設定URLのパス
                # ====================================

                reset_path = reverse(
                    (
                        "accounts:"
                        "password_reset_confirm"
                    ),
                    kwargs={
                        "uidb64":
                            uid,

                        "token":
                            token,
                    }
                )


                # ====================================
                # 完全なURLを作成
                # ====================================

                reset_url = (
                    request
                    .build_absolute_uri(
                        reset_path
                    )
                )


                # ====================================
                # メール件名
                # ====================================

                subject = (
                    "ChatBoy パスワード再設定"
                )


                # ====================================
                # メール本文
                # ====================================

                message = f"""
ChatBoyのパスワード再設定を受け付けました。

以下のURLから新しいパスワードを設定してください。

{reset_url}

このメールに心当たりがない場合は、
このメールを無視してください。

ChatBoy
"""


                # ====================================
                # Gmail APIでメール送信
                # ====================================

                send_gmail(
                    user.email,
                    subject,
                    message
                )


            # ====================================
            # ユーザーが存在しなくても
            # 同じ完了画面へ
            # ====================================

            return redirect(
                "accounts:password_reset_done"
            )


        return render(
            request,
            "accounts/password_reset.html",
            {
                "form":
                    form
            }
        )



# ========================================
# メール送信完了
# ========================================

class PasswordResetDoneView(View):

    def get(
        self,
        request
    ):

        return render(
            request,
            (
                "accounts/"
                "password_reset_done.html"
            )
        )



# ========================================
# 新しいパスワード設定
# ========================================

class PasswordResetConfirmView(View):

    # ====================================
    # セッションに保存するときの名前
    # ====================================

    SESSION_TOKEN_NAME = "password_reset_token"


    # ====================================
    # パスワード変更画面を表示
    # ====================================

    def get(
        self,
        request,
        uidb64,
        token
    ):

        user = self.get_user(
            uidb64
        )


        # ====================================
        # ユーザーが存在しない
        # ====================================

        if user is None:

            return render(
                request,
                "accounts/password_reset_confirm.html",
                {
                    "form": None,
                    "validlink": False,
                }
            )


        # ====================================
        # メールのURLから最初にアクセスした場合
        # ====================================

        if token != "set-password":

            # トークンが正しいか確認
            if default_token_generator.check_token(
                user,
                token
            ):

                # ====================================
                # 本物のトークンをセッションに保存
                # ====================================

                request.session[
                    self.SESSION_TOKEN_NAME
                ] = token


                # ====================================
                # URLから本物のトークンを消す
                # ====================================

                return redirect(
                    "accounts:password_reset_confirm",
                    uidb64=uidb64,
                    token="set-password"
                )


            # ====================================
            # トークンが間違っている
            # ====================================

            return render(
                request,
                "accounts/password_reset_confirm.html",
                {
                    "form": None,
                    "validlink": False,
                }
            )


        # ====================================
        # set-password URLに来た場合
        # ====================================

        session_token = request.session.get(
            self.SESSION_TOKEN_NAME
        )


        # ====================================
        # セッションに保存したトークンを確認
        # ====================================

        if (
            session_token
            and
            default_token_generator.check_token(
                user,
                session_token
            )
        ):

            form = NewPasswordForm()


            return render(
                request,
                "accounts/password_reset_confirm.html",
                {
                    "form": form,
                    "validlink": True,
                }
            )


        # ====================================
        # セッションのトークンが無効
        # ====================================

        return render(
            request,
            "accounts/password_reset_confirm.html",
            {
                "form": None,
                "validlink": False,
            }
        )



    # ====================================
    # パスワード変更
    # ====================================

    def post(
        self,
        request,
        uidb64,
        token
    ):

        user = self.get_user(
            uidb64
        )


        # ====================================
        # セッションから本物のトークン取得
        # ====================================

        session_token = request.session.get(
            self.SESSION_TOKEN_NAME
        )


        # ====================================
        # URL・ユーザー・トークンを確認
        # ====================================

        if (
            token != "set-password"
            or
            user is None
            or
            not session_token
            or
            not default_token_generator.check_token(
                user,
                session_token
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


        # ====================================
        # 入力されたパスワードを取得
        # ====================================

        form = NewPasswordForm(
            request.POST
        )


        if form.is_valid():

            new_password = (
                form.cleaned_data[
                    "new_password1"
                ]
            )


            # ====================================
            # Djangoのパスワード安全チェック
            # ====================================

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

                # ====================================
                # 新しいパスワード設定
                # ====================================

                user.set_password(
                    new_password
                )

                user.save()


                # ====================================
                # 使用済みトークンをセッションから削除
                # ====================================

                request.session.pop(
                    self.SESSION_TOKEN_NAME,
                    None
                )


                # ====================================
                # ログイン画面へ
                # ====================================

                return redirect(
                    "accounts:login"
                )


        # ====================================
        # フォーム入力エラー
        # ====================================

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


# ========================================
# プロフィール更新
# ========================================

class ProfileView(
    LoginRequiredMixin,
    View
):

    login_url = "accounts:login"


    def get(
        self,
        request
    ):

        form = ProfileForm(
            user=request.user
        )


        return render(
            request,
            "accounts/profile.html",
            {
                "form": form
            }
        )


    def post(
        self,
        request
    ):

        form = ProfileForm(
            request.POST,
            user=request.user
        )


        if form.is_valid():

            user = request.user


            username = (
                form.cleaned_data[
                    "username"
                ]
            )

            password = (
                form.cleaned_data[
                    "password1"
                ]
            )


            # ==============================
            # パスワードを変更する場合
            # ==============================

            if password:

                try:

                    validate_password(
                        password,
                        user=user
                    )


                except ValidationError as e:

                    for error in e.messages:

                        form.add_error(
                            "password1",
                            error
                        )


            # ==============================
            # エラーがなければ更新
            # ==============================

            if not form.errors:

                user.username = username


                if password:

                    user.set_password(
                        password
                    )


                user.save()


                # パスワード変更後も
                # ログイン状態を維持
                if password:

                    update_session_auth_hash(
                        request,
                        user
                    )


                # ==========================
                # 更新後トップ画面へ
                # ==========================

                return redirect(
                    "AIapp:index"
                )


        return render(
            request,
            "accounts/profile.html",
            {
                "form": form
            }
        )