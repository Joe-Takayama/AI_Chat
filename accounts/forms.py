from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# ========================================
# 新規登録
# ========================================

class SignUpForm(UserCreationForm):

    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "パスワードを入力してください",
            }
        )
    )

    password2 = forms.CharField(
        label="パスワード（再確認）",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "パスワードを再入力してください",
            }
        )
    )


    class Meta:

        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "ユーザー名を入力してください",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "auth-input",
                    "placeholder": "メールアドレスを入力してください",
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["username"].label = "ユーザー名"
        self.fields["email"].label = "メールアドレス"
        self.fields["password1"].label = "パスワード"
        self.fields["password2"].label = "パスワード（再確認）"


    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "このメールアドレスは既に使用されています。"
            )

        return email



# ========================================
# ログイン
# ========================================

class LoginForm(forms.Form):

    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "例: example@gmail.com",
            }
        ),
    )

    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "",
            }
        ),
    )



# ========================================
# パスワード再設定
# メールアドレス入力
# ========================================

class PasswordResetForm(forms.Form):

    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(
            attrs={
                "class": "password-reset-input",
                "placeholder": "例: admin@gmail.com",
                "autocomplete": "email",
            }
        ),
    )



# ========================================
# 新しいパスワード
# ========================================

class NewPasswordForm(forms.Form):

    new_password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(
            attrs={
                "class": "password-new-input",
                "autocomplete": "new-password",
            }
        ),
    )


    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput(
            attrs={
                "class": "password-new-input",
                "autocomplete": "new-password",
            }
        ),
    )


    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get(
            "new_password1"
        )

        password2 = cleaned_data.get(
            "new_password2"
        )


        if (
            password1
            and password2
            and password1 != password2
        ):

            self.add_error(
                "new_password2",
                "パスワードが一致していません。"
            )


        return cleaned_data


# ========================================
# プロフィール更新
# ========================================

class ProfileForm(forms.Form):

    username = forms.CharField(
        label="ユーザー名",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "profile-input",
                "placeholder": "ユーザー名を入力",
            }
        )
    )

    password1 = forms.CharField(
        label="パスワード",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "profile-input",
            }
        )
    )

    password2 = forms.CharField(
        label="パスワード（確認）",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "profile-input",
            }
        )
    )


    def __init__(
        self,
        *args,
        user=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.user = user


        if user:

            self.fields[
                "username"
            ].initial = user.username


    def clean_username(self):

        username = self.cleaned_data[
            "username"
        ]

        if (
            User.objects
            .filter(
                username__iexact=username
            )
            .exclude(
                pk=self.user.pk
            )
            .exists()
        ):

            raise forms.ValidationError(
                "このユーザー名は既に使用されています。"
            )


        return username


    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get(
            "password1"
        )

        password2 = cleaned_data.get(
            "password2"
        )


        if (
            password1
            or
            password2
        ):

            if password1 != password2:

                self.add_error(
                    "password2",
                    "パスワードが一致していません。"
                )


        return cleaned_data