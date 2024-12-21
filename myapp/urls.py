from django.urls import path
from . import views

urlpatterns = [
    path('', views.getData),
    path('/add_text',views.InputView_Text.post),
    path('/add_user',views.user_signup.post),
    path('/login_user',views.user_login.post),
]
