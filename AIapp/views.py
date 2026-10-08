from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.views import View

from .forms import ChatForm
from .agent import ask_ai
from .models import Chat, Message


# ========================================
# 履歴のタイトルを作る
# ========================================

def make_history_title(message):

    title = message.strip()

    # 長すぎる場合は20文字まで
    if len(title) > 20:

        return title[:20] + "..."

    return title



# ========================================
# チャット画面
# ========================================

class IndexView(View):

    def get(self, request):

        form = ChatForm()


        # ====================================
        # ログイン済みの場合
        # ====================================

        if request.user.is_authenticated:

            # --------------------------------
            # サイドバーに表示する履歴
            # --------------------------------

            chat_histories = (
                Chat.objects
                .filter(
                    user=request.user
                )
                .order_by(
                    "-updated_at"
                )
            )


            # --------------------------------
            # 現在開いているチャットID
            # --------------------------------

            current_chat_id = (
                request.session.get(
                    "current_chat_id"
                )
            )


            messages = []


            # --------------------------------
            # 過去チャットを開いている場合
            # --------------------------------

            if current_chat_id:

                chat = (
                    Chat.objects
                    .filter(
                        id=current_chat_id,
                        user=request.user
                    )
                    .first()
                )


                if chat:

                    messages = list(

                        chat.messages
                        .order_by(
                            "created_at"
                        )
                        .values(
                            "role",
                            "content"
                        )
                    )


                else:

                    request.session.pop(
                        "current_chat_id",
                        None
                    )


        # ====================================
        # 未ログインの場合
        # ====================================

        else:

            chat_histories = []

            messages = (
                request.session.get(
                    "chat_messages",
                    []
                )
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



    def post(self, request):

        form = ChatForm(
            request.POST
        )


        if form.is_valid():

            message = (
                form.cleaned_data[
                    "message"
                ]
            )


            # ====================================
            # ログイン済みの場合
            # ====================================

            if request.user.is_authenticated:

                # --------------------------------
                # 現在のチャットID
                # --------------------------------

                current_chat_id = (
                    request.session.get(
                        "current_chat_id"
                    )
                )


                chat = None


                # --------------------------------
                # 既存チャットを開いている場合
                # --------------------------------

                if current_chat_id:

                    chat = (
                        Chat.objects
                        .filter(
                            id=current_chat_id,
                            user=request.user
                        )
                        .first()
                    )


                # --------------------------------
                # 新しいチャットの場合
                # --------------------------------

                if chat is None:

                    chat = Chat.objects.create(

                        user=request.user,

                        title=make_history_title(
                            message
                        )
                    )


                    request.session[
                        "current_chat_id"
                    ] = chat.id


                # ====================================
                # ユーザーのメッセージをDBへ保存
                # ====================================

                Message.objects.create(
                    chat=chat,
                    role="user",
                    content=message
                )


                # ====================================
                # Geminiの前回の会話ID
                # ====================================

                previous_interaction_id = (
                    chat.previous_interaction_id
                )


                try:

                    ai_message, interaction_id = (
                        ask_ai(
                            message,
                            previous_interaction_id
                        )
                    )


                    # ====================================
                    # AIの回答をDBへ保存
                    # ====================================

                    Message.objects.create(
                        chat=chat,
                        role="assistant",
                        content=ai_message
                    )


                    # ====================================
                    # Geminiの会話IDをDBへ保存
                    # ====================================

                    chat.previous_interaction_id = (
                        interaction_id
                    )


                    # updated_atも更新される
                    chat.save()


                except Exception as e:

                    print(e)


                    Message.objects.create(
                        chat=chat,
                        role="assistant",
                        content=(
                            "AIからの回答を"
                            "取得できませんでした。"
                        )
                    )


                    # updated_atを更新
                    chat.save()


                return redirect(
                    "AIapp:index"
                )


            # ====================================
            # 未ログインの場合
            # ====================================

            else:

                messages = (
                    request.session.get(
                        "chat_messages",
                        []
                    )
                )


                # --------------------------------
                # ユーザーのメッセージ
                # --------------------------------

                messages.append(
                    {
                        "role": "user",
                        "content": message,
                    }
                )


                previous_interaction_id = (
                    request.session.get(
                        "previous_interaction_id"
                    )
                )


                try:

                    ai_message, interaction_id = (
                        ask_ai(
                            message,
                            previous_interaction_id
                        )
                    )


                    # --------------------------------
                    # AIの回答
                    # --------------------------------

                    messages.append(
                        {
                            "role": "assistant",
                            "content": ai_message,
                        }
                    )


                    request.session[
                        "previous_interaction_id"
                    ] = interaction_id


                except Exception as e:

                    print(e)


                    messages.append(
                        {
                            "role": "assistant",
                            "content": (
                                "AIからの回答を"
                                "取得できませんでした。"
                            ),
                        }
                    )


                request.session[
                    "chat_messages"
                ] = messages


                return redirect(
                    "AIapp:index"
                )


        # ====================================
        # フォームにエラーがある場合
        # ====================================

        if request.user.is_authenticated:

            chat_histories = (
                Chat.objects
                .filter(
                    user=request.user
                )
                .order_by(
                    "-updated_at"
                )
            )

            messages = []

        else:

            chat_histories = []

            messages = (
                request.session.get(
                    "chat_messages",
                    []
                )
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

        # ====================================
        # ログイン済み
        # ====================================

        if request.user.is_authenticated:

            # DBに履歴は残っているので
            # 現在開いているチャットIDだけ消す

            request.session.pop(
                "current_chat_id",
                None
            )


        # ====================================
        # 未ログイン
        # ====================================

        else:

            request.session.pop(
                "chat_messages",
                None
            )

            request.session.pop(
                "previous_interaction_id",
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

        # ====================================
        # 未ログインならログイン画面へ
        # ====================================

        if not request.user.is_authenticated:

            return redirect(
                "accounts:login"
            )


        # ====================================
        # 自分のチャットだけ取得
        # ====================================

        chat = get_object_or_404(
            Chat,
            id=chat_id,
            user=request.user
        )


        # ====================================
        # 開くチャットIDをセッションに保存
        # ====================================

        request.session[
            "current_chat_id"
        ] = chat.id


        return redirect(
            "AIapp:index"
        )   