from django.urls import path
from .views import Home

app_name = 'guilherme_leal'

urlpatterns = [
    path('', Home.as_view(), name='home'),
]