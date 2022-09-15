from django.urls import path
from .views import CardsListView, CardsDetailView

app_name = 'cards'

urlpatterns = [
    path('<str:empresa>/', CardsListView.as_view(), name='lista'),
    # path('<str:empresa>/<int:pk>/', CardsDetailView.as_view(), name='detalhe'),
    path('<str:empresa>/<str:nome>/', CardsDetailView.as_view(), name='detalhe'),
]