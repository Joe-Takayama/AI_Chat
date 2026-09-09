from django.urls import path
from views import IndexView

app_name = 'AIapp'

urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),
]