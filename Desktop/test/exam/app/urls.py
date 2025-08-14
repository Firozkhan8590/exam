
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<str:code>/", views.redirect_url, name="redirect"),
    path("delete/<int:id>/", views.delete_url, name="delete_url"),
]