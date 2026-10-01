from django import forms

class ChatForm(forms.Form):

    message = forms.CharField(
        label="",
        max_length=4000,
        widget=forms.TextInput(
            attrs={
                "class": "message-input",
                "placeholder": "メッセージを入力",
                "autocomplete": "off",
            }
        )
    )