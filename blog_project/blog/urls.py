from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('create_post/', views.create_post, name='create_post'),
    path('post_detail/', views.post_detail, name='post_detail')
]