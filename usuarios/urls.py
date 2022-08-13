from django.urls import path
from .views import LoginView, RegistrarView, LogoutView

app_name = 'usuarios'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registrar/', RegistrarView.as_view(), name='registrar'),
    path('logout/', LogoutView.as_view(), name='logout'),
]