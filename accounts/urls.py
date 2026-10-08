from django.urls import path

from .views import SignUpView, LoginView, LogOutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, ProfileView


app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('profile/', ProfileView.as_view(), name='profile'),

]