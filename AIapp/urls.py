from django.urls import path

from .views import (
    IndexView,
    NewChatView,
    ChatHistoryView,
)


app_name = 'AIapp'


urlpatterns = [

    path(
        'index/',
        IndexView.as_view(),
        name='index'
    ),

    path(
        'new_chat/',
        NewChatView.as_view(),
        name='new_chat'
    ),

    path(
        'chat/<str:chat_id>/',
        ChatHistoryView.as_view(),
        name='chat_history'
    ),

]