from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを入力してください',
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを再入力してください',
        })
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'ユーザー名を入力してください',
            }),


            'email': forms.EmailInput(attrs={
                'placeholder': 'メールアドレスを入力してください',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'ユーザー名'
        self.fields['email'].label = 'メールアドレス'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（再確認）'

    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(
            email_iexact=email
        ).exists():
            raise forms.ValidationError(
                'このメールアドレスは既に使用されています。'
            )
        return email

class LoginForm(forms.Form):

    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            'placeholder': '例: example@gmail.com'
        }),
    )

    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワードを入力してください'
        }),
    )
