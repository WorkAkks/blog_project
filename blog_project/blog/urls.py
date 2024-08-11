from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/<str:username>/', views.user_profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('post_list/', views.post_list, name='post_list'),
    path('create_post/', views.create_post, name='create_post'),
    path('subscribe/<int:user_id>/', views.subscribe, name='subscribe'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('view_private_post/<int:post_id>/', views.view_private_post, name='view_private_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('subscription_list/', views.subscription_list, name='subscription_list'),
    path('unsubscribe/<int:user_id>/', views.unsubscribe, name='unsubscribe'),
]