from django.shortcuts import render, redirect
from django.views import View

from .forms import ChatForm
from .agent import ask_ai

class IndexView(View):
    def get(self, request):

        form = ChatForm()

        messages = request.session.get(
            "chat_messages",
            []
        )

        context = {
            "form": form,
            "messages": messages,
        }

        return render(request, 'AIapp/index.html', context)

    def post(self, request):

        form = ChatForm(request.POST)

        messages = request.session.get(
            "chat_messages",
            []
        )

        if form.is_valid():

            # forms.pyでチェック済みのメッセージ
            message = form.cleaned_data["message"]

            # ユーザーのメッセージを追加
            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )

            # Gemini側で前回の会話を引き継ぐためのID
            previous_interaction_id = request.session.get(
                "previous_interaction_id"
            )

            try:

                ai_message, interaction_id = ask_ai(
                    message,
                    previous_interaction_id
                )

                # ChatBoyの回答を追加
                messages.append(
                    {
                        "role": "assistant",
                        "content": ai_message,
                    }
                )

                # 次回の会話用に保存
                request.session[
                    "previous_interaction_id"
                ] = interaction_id

            except Exception:

                messages.append(
                    {
                        "role": "assistant",
                        "content": "AIからの回答を取得できませんでした。",
                    }
                )

            # 表示用の会話をセッションに保存
            request.session[
                "chat_messages"
            ] = messages

            return redirect("AIapp:index")

        # formsが不正だった場合
        context = {
            "form": form,
            "messages": messages,
        }

        return render(request, "AIapp/index.html", context)
