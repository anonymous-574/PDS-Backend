from django.urls import path
from . import views

urlpatterns = [
    path('', views.getData),
    path('/add_text',views.InputView_Text.post),
    path('/add_image',views.InputView_Image.post)
]
