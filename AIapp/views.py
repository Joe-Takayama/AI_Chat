import uuid

from django.shortcuts import render, redirect
from django.views import View

from .forms import ChatForm
from .agent import ask_ai


# ========================================
# 履歴のタイトルを作る
# ========================================

def make_history_title(messages):

    for message in messages:

        if message["role"] == "user":

            title = message["content"].strip()

            # 長すぎる場合は20文字まで
            if len(title) > 20:

                return title[:20] + "..."

            return title

    return "新しいチャット"



# ========================================
# 現在のチャットを履歴に保存
# ========================================

def save_chat_history(request, messages):

    # 未ログインなら履歴保存しない
    if not request.user.is_authenticated:
        return


    # 現在のチャットID
    chat_id = request.session.get(
        "current_chat_id"
    )


    # まだIDがなければ新しく作る
    if chat_id is None:

        chat_id = str(
            uuid.uuid4()
        )

        request.session[
            "current_chat_id"
        ] = chat_id


    # 今まで保存されている履歴
    chat_histories = request.session.get(
        "chat_histories",
        []
    )


    # 現在のチャット情報
    chat_data = {
        "id": chat_id,
        "title": make_history_title(messages),
        "messages": messages,
        "previous_interaction_id":
            request.session.get(
                "previous_interaction_id"
            ),
    }


    # 同じチャットIDがすでにあれば削除
    # ↓
    # 最新状態に置き換えるため
    chat_histories = [
        chat
        for chat in chat_histories
        if chat["id"] != chat_id
    ]


    # 最新チャットを一番上へ
    chat_histories.insert(
        0,
        chat_data
    )


    # セッションに保存
    request.session[
        "chat_histories"
    ] = chat_histories



# ========================================
# チャット画面
# ========================================

class IndexView(View):

    def get(self, request):

        form = ChatForm()


        # 現在表示中の会話
        messages = request.session.get(
            "chat_messages",
            []
        )


        # サイドバー用の履歴
        if request.user.is_authenticated:

            chat_histories = request.session.get(
                "chat_histories",
                []
            )

        else:

            chat_histories = []


        context = {
            "form": form,
            "messages": messages,
            "chat_histories": chat_histories,
        }


        return render(
            request,
            "AIapp/index.html",
            context
        )


    def post(self, request):

        form = ChatForm(
            request.POST
        )


        messages = request.session.get(
            "chat_messages",
            []
        )


        if form.is_valid():

            message = form.cleaned_data[
                "message"
            ]


            # ==============================
            # ユーザーのメッセージ
            # ==============================

            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )


            # Gemini側の前回の会話ID
            previous_interaction_id = (
                request.session.get(
                    "previous_interaction_id"
                )
            )


            try:

                ai_message, interaction_id = ask_ai(
                    message,
                    previous_interaction_id
                )


                # ==============================
                # ChatBoyの回答
                # ==============================

                messages.append(
                    {
                        "role": "assistant",
                        "content": ai_message,
                    }
                )


                # Geminiの会話IDを保存
                request.session[
                    "previous_interaction_id"
                ] = interaction_id


            except Exception as e:

                print(e)


                messages.append(
                    {
                        "role": "assistant",
                        "content":
                            "AIからの回答を取得できませんでした。",
                    }
                )


            # ==============================
            # 現在の会話を保存
            # ==============================

            request.session[
                "chat_messages"
            ] = messages


            # ==============================
            # サイドバー履歴にも保存
            # ==============================

            save_chat_history(
                request,
                messages
            )


            return redirect(
                "AIapp:index"
            )


        # フォームエラーの場合
        chat_histories = request.session.get(
            "chat_histories",
            []
        )


        context = {
            "form": form,
            "messages": messages,
            "chat_histories": chat_histories,
        }


        return render(
            request,
            "AIapp/index.html",
            context
        )



# ========================================
# 新しいチャット
# ========================================

class NewChatView(View):

    def get(self, request):

        # 現在表示している会話
        messages = request.session.get(
            "chat_messages",
            []
        )


        # 現在の会話を消す前に
        # 履歴へ保存しておく
        if messages:

            save_chat_history(
                request,
                messages
            )


        # ==============================
        # 現在のチャットだけリセット
        # ==============================

        request.session.pop(
            "chat_messages",
            None
        )

        request.session.pop(
            "previous_interaction_id",
            None
        )

        request.session.pop(
            "current_chat_id",
            None
        )


        return redirect(
            "AIapp:index"
        )



# ========================================
# 過去のチャットを開く
# ========================================

class ChatHistoryView(View):

    def get(
        self,
        request,
        chat_id
    ):

        # 未ログインならログイン画面へ
        if not request.user.is_authenticated:

            return redirect(
                "accounts:login"
            )


        chat_histories = request.session.get(
            "chat_histories",
            []
        )


        # 対象のチャットを探す
        for chat in chat_histories:

            if chat["id"] == chat_id:

                # このチャットを現在のチャットにする
                request.session[
                    "current_chat_id"
                ] = chat["id"]


                request.session[
                    "chat_messages"
                ] = chat["messages"]


                previous_interaction_id = (
                    chat.get(
                        "previous_interaction_id"
                    )
                )


                if previous_interaction_id:

                    request.session[
                        "previous_interaction_id"
                    ] = previous_interaction_id

                else:

                    request.session.pop(
                        "previous_interaction_id",
                        None
                    )


                break


        return redirect(
            "AIapp:index"
        )