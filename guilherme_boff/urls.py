from django.urls import path
from .views import Home

app_name = 'guilherme_boff'

urlpatterns = [
    path('', Home.as_view(), name='home'),
]