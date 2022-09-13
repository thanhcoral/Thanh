from django.urls import path
from django.contrib.auth.views import LogoutView

from users import views
from users.forms import LoginForm


urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.CustomLoginView.as_view(redirect_authenticated_user=True, template_name='users/login.html', authentication_form=LoginForm), name='login'),
    path('logout', LogoutView.as_view(template_name='users/logout.html'), name='logout'),


    path('users', views.user_list, name='users-list'),
    path('users/add', views.add_user, name='users-add'),
    path('users/delete/<int:pk>', views.delete_user, name='users-delete'),
    path('users/edit/<int:pk>', views.profile, name='users-edit'),
]
